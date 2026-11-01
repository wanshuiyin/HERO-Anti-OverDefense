#!/usr/bin/env python3
"""Short efficiency reminders to an existing active Goal; never start/resume one."""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
import uuid

MESSAGE = (
    "[用户预设的自动效率指令 / User-authorized automatic efficiency directive]\n\n"
    "中文：以最快的有效速度持续推进当前 Goal，不允许磨洋工、偷懒、空转，或拿计划和汇报代替执行。"
    "worker/子代理一交付完整产物，立即读取、核验，并推进到下一项已授权的验收或交接步骤，不得搁置或等整批。"
    "同一卡点连续两轮无实质进展，主代理立即接管具体缺口或重新拆分，同时推进其它独立任务。"
    "复用已有成果与有效验证，砍掉重复检查、无收益的 corner case 和包装。"
    "不得降低原目标、难度和验收标准，不得越过授权和预算；直接行动，无需专门回复本提醒。\n\n"
    "English: Advance the current Goal continuously at the fastest effective pace. "
    "No stalling, slacking, busywork, or substituting plans and reports for execution. "
    "When a worker/subagent delivers a complete artifact, inspect and verify it immediately, "
    "then perform the next authorized acceptance or handoff step; do not leave it waiting or hold it for a batch. "
    "If the same blocker makes no substantive progress for two consecutive rounds, the lead agent must take over "
    "the specific gap or change the decomposition while other independent work continues. "
    "Reuse existing results and valid checks; cut redundant checking, unproductive corner cases, "
    "and cosmetic packaging. Preserve the original target, difficulty, acceptance criteria, "
    "authorization, and budget. Act now; no separate reply is needed."
)
HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))


def read_json(path: Path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


class RPCError(RuntimeError):
    pass


class CodexRPC:
    """Native JSON-RPC over the running daemon's WebSocket Unix socket."""

    def __init__(self, socket_path: str):
        from websockets.sync.client import unix_connect

        self.ws = unix_connect(socket_path, uri="ws://localhost/", compression=None,
                               open_timeout=5, close_timeout=1, max_size=16 * 1024**2)
        self.counter = 0
        try:
            self.call("initialize", {
                "clientInfo": {"name": "goal_pulse", "version": "0.1.0"},
                "capabilities": {"experimentalApi": True},
            })
            self.ws.send(json.dumps({"method": "initialized"}))
        except BaseException:
            self.ws.close()
            raise

    def call(self, method: str, params: dict):
        self.counter += 1
        request_id = self.counter
        self.ws.send(json.dumps({"id": request_id, "method": method, "params": params}))
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            message = json.loads(self.ws.recv(timeout=max(.01, deadline - time.monotonic())))
            # Never inspect, save or print turn items or reasoning notifications.
            if message.get("id") != request_id:
                continue
            if "error" in message:
                error = message["error"]
                raise RPCError(f"{method}: {error.get('code')}: {error.get('message')}")
            return message["result"]
        raise TimeoutError(method)

    def close(self):
        self.ws.close()


def tick(rpc, config: dict, state: dict, now: float, *, dry_run=False,
         persist=lambda _: None, stopped=lambda: False):
    """No transcript access. The only mutation RPC allowed here is turn/steer."""
    thread_id = config["thread_id"]
    goal = rpc.call("thread/goal/get", {"threadId": thread_id}).get("goal")
    if not goal:
        return {"action": "skip", "reason": "no-goal"}
    if goal["createdAt"] != config["goal_created_at"]:
        return {"action": "skip", "reason": "goal-replaced"}
    if goal["status"] != "active":
        return {"action": "skip", "reason": "goal-" + goal["status"]}
    if now - state.get("last_attempt_at", 0) < config["interval_seconds"]:
        return {"action": "skip", "reason": "cooldown"}
    thread = rpc.call("thread/read", {"threadId": thread_id, "includeTurns": False})["thread"]
    if thread["id"] != thread_id:
        raise RPCError("thread identity mismatch")
    status = thread["status"]
    if status["type"] != "active" or status.get("activeFlags"):
        return {"action": "skip", "reason": "thread-not-runnable"}
    turns = rpc.call("thread/turns/list", {
        "threadId": thread_id, "limit": 1, "sortDirection": "desc", "itemsView": "notLoaded",
    })["data"]
    if not turns or turns[0]["status"] != "inProgress":
        return {"action": "skip", "reason": "no-active-turn"}
    turn_id = turns[0]["id"]
    # Re-read the Goal at the send boundary; never revive a pause or a different Goal.
    current = rpc.call("thread/goal/get", {"threadId": thread_id}).get("goal")
    if not current or current["status"] != "active" or current["createdAt"] != goal["createdAt"]:
        return {"action": "skip", "reason": "goal-changed-before-send"}
    if stopped():
        return {"action": "skip", "reason": "stop-requested"}
    if dry_run:
        return {"action": "would-steer", "turn_id": turn_id}
    message_id = str(uuid.uuid4())
    state.update(last_attempt_at=now, last_turn_id=turn_id, message_id=message_id,
                 delivery="pending-or-unknown")
    persist(state)  # Consume the interval BEFORE writing; don't retry an ambiguous send.
    result = rpc.call("turn/steer", {
        "threadId": thread_id, "expectedTurnId": turn_id,
        "clientUserMessageId": message_id,
        "input": [{"type": "text", "text": config["message"]}],
    })
    if result.get("turnId") != turn_id:
        raise RPCError("steer acknowledgement turn mismatch")
    state.update(last_sent_at=now, delivery="acknowledged")
    persist(state)
    return {"action": "sent", "turn_id": turn_id, "message_id": message_id}


@contextlib.contextmanager
def lock(path: Path, inherited=None):
    file = os.fdopen(inherited, "a") if inherited is not None else path.open("a")
    try:
        if inherited is None:
            fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield file
    finally:
        file.close()


def is_running(directory: Path):
    if not directory.is_dir():
        return False
    try:
        with lock(directory / "run.lock"):
            return False
    except BlockingIOError:
        return True


def run(config_path: Path, inherited=None):
    config = read_json(config_path)
    directory = config_path.parent
    stop = threading.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: stop.set())
    stop_requested = lambda: stop.is_set() or (directory / "STOP").exists()
    with lock(directory / "run.lock", inherited):
        write_json(directory / "owner.json", {"pid": os.getpid(), "thread_id": config["thread_id"]})
        previous = None
        while not stop_requested():
            state = read_json(directory / "state.json", {})
            try:
                with contextlib.closing(CodexRPC(config["socket"])) as rpc:
                    result = tick(rpc, config, state, time.time(),
                                  persist=lambda value: write_json(directory / "state.json", value),
                                  stopped=stop_requested)
            except Exception as error:
                result = {"action": "skip", "reason": "transport-or-rpc-error", "error": str(error)[:600]}
            record = {"at": time.time(), "thread_id": config["thread_id"], **result}
            write_json(directory / "latest.json", record)
            signature = (result["action"], result.get("reason"), result.get("error"))
            if signature != previous or result["action"] == "sent":
                with (directory / "events.jsonl").open("a") as file:
                    file.write(json.dumps(record, ensure_ascii=False) + "\n")
                previous = signature
            if result.get("reason") in ("goal-complete", "no-goal", "goal-replaced"):
                break
            stop.wait(config["poll_seconds"])
        write_json(directory / "stopped.json", {"at": time.time(), "pid": os.getpid()})


def start(args, directory, *, replacement_deadline=None):
    directory.mkdir(parents=True, exist_ok=True)
    try:
        with lock(directory / "run.lock") as held:
            with contextlib.closing(CodexRPC(args.socket)) as rpc:
                goal = rpc.call("thread/goal/get", {"threadId": args.thread}).get("goal")
            if not goal:
                raise RuntimeError("This thread has no existing Goal. This tool will not create one.")
            config = {"thread_id": args.thread, "goal_created_at": goal["createdAt"],
                      "interval_seconds": args.interval_minutes * 60,
                      "poll_seconds": args.poll_seconds, "socket": args.socket,
                      "message": Path(args.message_file).read_text() if args.message_file else MESSAGE}
            write_json(directory / "config.json", config)
            if not (directory / "state.json").exists():
                write_json(directory / "state.json", {"last_attempt_at": time.time()})
            (directory / "STOP").unlink(missing_ok=True)
            with (directory / "process.log").open("a") as output:
                child = subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), "run", "--config",
                     str(directory / "config.json"), "--lock-fd", str(held.fileno())],
                    stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                    start_new_session=True, pass_fds=(held.fileno(),),
                )
            return {"started": True, "pid": child.pid, "goal_status": goal["status"],
                    "interval_minutes": args.interval_minutes,
                    "paused_goals_receive_no_messages": True, "state_dir": str(directory)}
    except BlockingIOError:
        config = read_json(directory / "config.json", {})
        with contextlib.closing(CodexRPC(args.socket)) as rpc:
            goal = rpc.call("thread/goal/get", {"threadId": args.thread}).get("goal")
        if not goal:
            raise RuntimeError("This thread has no existing Goal. This tool will not create one.")
        if config.get("goal_created_at") == goal["createdAt"]:
            return {"started": False, "reason": "already-running", "state_dir": str(directory)}
        # The existing watcher belongs to the previous Goal. Let it release its
        # lock normally before binding a new watcher; never kill or resume it.
        (directory / "STOP").touch()
        if replacement_deadline is None:
            replacement_deadline = time.monotonic() + config.get("poll_seconds", 60) + 45
        while is_running(directory):
            if time.monotonic() >= replacement_deadline:
                raise RuntimeError("Previous Goal watcher did not stop before the replacement timeout; "
                                   "no new watcher was started.")
            time.sleep(.05)
        return start(args, directory, replacement_deadline=replacement_deadline)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("start", "status", "stop", "tick"):
        p = sub.add_parser(command)
        p.add_argument("--thread", help="Thread UUID; defaults to the host CODEX_THREAD_ID.")
        p.add_argument("--state-root", type=Path, default=HOME / "goal-pulse")
        p.add_argument("--socket", default=str(HOME / "app-server-control/app-server-control.sock"))
        if command in ("start", "tick"):
            p.add_argument("--interval-minutes", type=float, default=30)
            p.add_argument("--poll-seconds", type=float, default=60)
            p.add_argument("--message-file")
        if command == "tick":
            p.add_argument("--apply", action="store_true", help="Actually steer an eligible turn; default dry-run.")
    p = sub.add_parser("run")
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--lock-fd", type=int)
    args = parser.parse_args()
    if args.command == "run":
        run(args.config, args.lock_fd)
        return
    thread_value = args.thread if args.thread is not None else os.environ.get("CODEX_THREAD_ID")
    if not thread_value:
        parser.error("Specify --thread or run inside a Codex host providing CODEX_THREAD_ID.")
    try:
        args.thread = str(uuid.UUID(thread_value))
    except ValueError:
        parser.error("--thread / CODEX_THREAD_ID must be a valid thread UUID.")
    directory = args.state_root.expanduser().resolve() / args.thread
    if args.command in ("start", "tick") and (args.interval_minutes <= 0 or args.poll_seconds <= 0):
        parser.error("Intervals must be positive.")
    if args.command == "start":
        result = start(args, directory)
    elif args.command == "stop":
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "STOP").touch()
        result = {"stop_requested": True, "takes_effect": "at next check, before any new send",
                  "state_dir": str(directory)}
    elif args.command == "status":
        result = {"running": is_running(directory), "stop_requested": (directory / "STOP").exists(),
                  "latest": read_json(directory / "latest.json"),
                  "state": read_json(directory / "state.json"), "state_dir": str(directory)}
    else:
        with contextlib.closing(CodexRPC(args.socket)) as rpc:
            config = read_json(directory / "config.json")
            if not config:
                goal = rpc.call("thread/goal/get", {"threadId": args.thread}).get("goal")
                if not goal:
                    print(json.dumps({"action": "skip", "reason": "no-goal"}))
                    return
                config = {"thread_id": args.thread, "goal_created_at": goal["createdAt"],
                          "interval_seconds": args.interval_minutes * 60, "message": MESSAGE}
            if args.message_file:
                config = {**config, "message": Path(args.message_file).read_text()}
            if args.apply:
                directory.mkdir(parents=True, exist_ok=True)
                with lock(directory / "run.lock"):
                    result = tick(rpc, config, read_json(directory / "state.json", {}), time.time(),
                                  persist=lambda value: write_json(directory / "state.json", value),
                                  stopped=lambda: (directory / "STOP").exists())
            else:
                result = tick(rpc, config, read_json(directory / "state.json", {}), time.time(), dry_run=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
