"""Behavioral checks: no paid model calls and no real conversation writes."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/goal-pulse/scripts"))
import goal_pulse as pulse

THREAD = "11111111-1111-4111-8111-111111111111"
TURN = "turn-original"
CONFIG = {"thread_id": THREAD, "goal_created_at": 100,
          "interval_seconds": 600, "message": "automated reminder"}


class FakeRPC:
    def __init__(self):
        self.goal = {"createdAt": 100, "status": "active"}
        self.status = {"type": "active", "activeFlags": []}
        self.turns = [{"id": TURN, "status": "inProgress"}]
        self.calls = []
        self.goal_reads = 0
        self.pause_before_send = False
        self.fail_send = False

    def call(self, method, params):
        self.calls.append((method, params))
        if method == "thread/goal/get":
            self.goal_reads += 1
            if self.pause_before_send and self.goal_reads > 1:
                return {"goal": {**self.goal, "status": "paused"}}
            return {"goal": self.goal}
        if method == "thread/read":
            assert params["includeTurns"] is False
            return {"thread": {"id": THREAD, "status": self.status}}
        if method == "thread/turns/list":
            assert params["itemsView"] == "notLoaded"
            return {"data": self.turns}
        if method == "turn/steer":
            if self.fail_send:
                raise TimeoutError("acknowledgement unknown")
            return {"turnId": TURN}
        raise AssertionError("Unexpected mutation: " + method)

    def sends(self):
        return [params for method, params in self.calls if method == "turn/steer"]


class DecisionTests(unittest.TestCase):
    def test_all_inactive_goal_states_are_silent(self):
        for status in ("paused", "blocked", "complete", "usageLimited", "budgetLimited"):
            with self.subTest(status=status):
                rpc = FakeRPC()
                rpc.goal["status"] = status
                result = pulse.tick(rpc, CONFIG, {}, 1000)
                self.assertEqual(result["action"], "skip")
                self.assertEqual(rpc.sends(), [])
                self.assertEqual(len(rpc.calls), 1)

    def test_missing_or_replaced_goal_does_not_receive(self):
        for goal in (None, {"createdAt": 101, "status": "active"}):
            rpc = FakeRPC()
            rpc.goal = goal
            self.assertEqual(pulse.tick(rpc, CONFIG, {}, 1000)["action"], "skip")
            self.assertFalse(rpc.sends())

    def test_waiting_for_human_and_idle_thread_are_silent(self):
        for status in ({"type": "idle"}, {"type": "notLoaded"},
                       {"type": "active", "activeFlags": ["waitingOnApproval"]},
                       {"type": "active", "activeFlags": ["waitingOnUserInput"]}):
            rpc = FakeRPC()
            rpc.status = status
            self.assertEqual(pulse.tick(rpc, CONFIG, {}, 1000)["action"], "skip")
            self.assertFalse(rpc.sends())

    def test_completed_or_absent_turn_does_not_start_one(self):
        for turns in ([], [{"id": TURN, "status": "completed"}]):
            rpc = FakeRPC()
            rpc.turns = turns
            self.assertEqual(pulse.tick(rpc, CONFIG, {}, 1000)["action"], "skip")
            self.assertFalse(rpc.sends())

    def test_only_original_active_turn_receives_one_message_per_interval(self):
        rpc, state, persisted = FakeRPC(), {}, []
        result = pulse.tick(rpc, CONFIG, state, 1000,
                            persist=lambda value: persisted.append(copy.deepcopy(value)))
        self.assertEqual(result["action"], "sent")
        self.assertEqual(rpc.sends()[0]["expectedTurnId"], TURN)
        self.assertEqual(rpc.sends()[0]["threadId"], THREAD)
        self.assertEqual(rpc.sends()[0]["input"], [{"type": "text", "text": CONFIG["message"]}])
        self.assertEqual(persisted[0]["delivery"], "pending-or-unknown")
        self.assertEqual(persisted[-1]["delivery"], "acknowledged")
        self.assertEqual(pulse.tick(rpc, CONFIG, state, 1599)["reason"], "cooldown")
        self.assertEqual(len(rpc.sends()), 1)
        self.assertEqual(pulse.tick(rpc, CONFIG, state, 1600)["action"], "sent")

    def test_pause_at_send_boundary_is_silent(self):
        rpc = FakeRPC()
        rpc.pause_before_send = True
        self.assertEqual(pulse.tick(rpc, CONFIG, {}, 1000)["reason"], "goal-changed-before-send")
        self.assertFalse(rpc.sends())

    def test_unknown_send_result_is_not_retried_in_same_interval(self):
        rpc, state, persisted = FakeRPC(), {}, []
        rpc.fail_send = True
        with self.assertRaises(TimeoutError):
            pulse.tick(rpc, CONFIG, state, 1000,
                       persist=lambda value: persisted.append(copy.deepcopy(value)))
        self.assertEqual(persisted[-1]["last_attempt_at"], 1000)
        self.assertEqual(persisted[-1]["delivery"], "pending-or-unknown")
        self.assertEqual(pulse.tick(rpc, CONFIG, state, 1001)["reason"], "cooldown")
        self.assertEqual(len(rpc.sends()), 1)

    def test_dry_run_and_stop_requested_never_write(self):
        rpc, state = FakeRPC(), {}
        self.assertEqual(pulse.tick(rpc, CONFIG, state, 1000, dry_run=True)["action"], "would-steer")
        self.assertEqual(pulse.tick(rpc, CONFIG, state, 1000, stopped=lambda: True)["reason"], "stop-requested")
        self.assertEqual(state, {})
        self.assertFalse(rpc.sends())

    def test_start_preserves_same_goal_cooldown_and_resets_new_goal_state(self):
        for previous_created_at in (100, 99):
            with self.subTest(previous_created_at=previous_created_at), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                pulse.write_json(directory / "config.json", {
                    **CONFIG, "goal_created_at": previous_created_at})
                old_state = {"last_attempt_at": 123, "last_turn_id": "old-turn"}
                pulse.write_json(directory / "state.json", old_state)
                rpc = mock.Mock()
                rpc.call.return_value = {"goal": {"createdAt": 100, "status": "paused"}}
                args = SimpleNamespace(socket="unused-mock-socket", thread=THREAD,
                                       interval_minutes=30, poll_seconds=60, message_file=None)
                with mock.patch.object(pulse, "CodexRPC", return_value=rpc), \
                        mock.patch.object(pulse.subprocess, "Popen") as popen:
                    popen.return_value.pid = 999
                    result = pulse.start(args, directory)
                self.assertTrue(result["started"])
                state = pulse.read_json(directory / "state.json")
                if previous_created_at == 100:
                    self.assertEqual(state, old_state)
                else:
                    self.assertEqual(set(state), {"last_attempt_at"})
                    self.assertGreater(state["last_attempt_at"], 123)

    def test_replacement_timeout_does_not_claim_watcher_started(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            pulse.write_json(directory / "config.json", {**CONFIG, "poll_seconds": .05})
            rpc = mock.Mock()
            rpc.call.return_value = {"goal": {"createdAt": 101, "status": "paused"}}
            args = SimpleNamespace(socket="unused-mock-socket", thread=THREAD)
            with pulse.lock(directory / "run.lock"), mock.patch.object(pulse, "CodexRPC", return_value=rpc):
                with self.assertRaisesRegex(RuntimeError, "replacement timeout"):
                    pulse.start(args, directory, replacement_deadline=0)
            self.assertTrue((directory / "STOP").exists())
            self.assertEqual(pulse.read_json(directory / "config.json")["goal_created_at"], 100)
            self.assertFalse((directory / "owner.json").exists())

    def test_process_lock_excludes_second_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self.assertFalse(pulse.is_running(path))
            with pulse.lock(path / "run.lock"):
                self.assertTrue(pulse.is_running(path))
                with self.assertRaises(BlockingIOError):
                    with pulse.lock(path / "run.lock"):
                        self.fail("a second owner acquired the lock")
            self.assertFalse(pulse.is_running(path))


class TransportTest(unittest.TestCase):
    def check_transport(self, *, replace_goal=False):
        from websockets.sync.server import unix_serve

        with tempfile.TemporaryDirectory(prefix="pulse-test-") as temporary:
            directory = Path(temporary)
            socket_path = str(directory / "rpc.sock")
            fake, errors = FakeRPC(), []

            def handler(ws):
                try:
                    for raw in ws:
                        request = json.loads(raw)
                        if "id" not in request:
                            continue
                        result = ({"userAgent": "test-no-model"}
                                  if request["method"] == "initialize"
                                  else fake.call(request["method"], request["params"]))
                        # An unrelated notification must never become an input or be logged.
                        ws.send(json.dumps({"method": "test/ignored", "params": {"value": "ignore"}}))
                        ws.send(json.dumps({"id": request["id"], "result": result}))
                except Exception as error:
                    errors.append(str(error))

            with unix_serve(handler, socket_path) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with pulse.contextlib.closing(pulse.CodexRPC(socket_path)) as rpc:
                        self.assertEqual(pulse.tick(rpc, CONFIG, {}, 1000)["action"], "sent")
                    self.assertEqual(len(fake.sends()), 1)
                    fake.goal["status"] = "paused"
                    args = [sys.executable, str(Path(pulse.__file__).resolve()),
                            "start", "--socket", socket_path,
                            "--state-root", str(directory / "state"), "--poll-seconds", ".05"]
                    started = json.loads(subprocess.check_output(
                        args, text=True, env={**os.environ, "CODEX_THREAD_ID": THREAD}))
                    self.assertTrue(started["started"])
                    repeat = json.loads(subprocess.check_output(
                        args + ["--thread", THREAD], text=True,
                        env={**os.environ, "CODEX_THREAD_ID": "invalid-env-overridden"}))
                    self.assertEqual(repeat["reason"], "already-running")
                    state_dir = directory / "state" / THREAD
                    deadline = time.monotonic() + 3
                    while not (state_dir / "latest.json").exists() and time.monotonic() < deadline:
                        time.sleep(.02)
                    self.assertEqual(pulse.read_json(state_dir / "latest.json")["reason"], "goal-paused")
                    if replace_goal:
                        # Replacement happens while the paused old watcher still
                        # holds the thread lock, before it observes the new Goal.
                        pulse.write_json(state_dir / "state.json", {
                            "last_attempt_at": 1, "last_turn_id": "old-goal-turn"})
                        fake.goal = {"createdAt": 101, "status": "paused"}
                        replacement = json.loads(subprocess.check_output(
                            args, text=True, env={**os.environ, "CODEX_THREAD_ID": THREAD}))
                        self.assertTrue(replacement["started"])
                        self.assertNotEqual(replacement["pid"], started["pid"])
                        new_config = pulse.read_json(state_dir / "config.json")
                        self.assertEqual(new_config["goal_created_at"], 101)
                        new_state = pulse.read_json(state_dir / "state.json")
                        self.assertNotIn("last_turn_id", new_state)
                        self.assertGreater(new_state["last_attempt_at"], 1)
                        # Eligibility after resume must wait a fresh interval.
                        fake.goal["status"] = "active"
                        with pulse.contextlib.closing(pulse.CodexRPC(socket_path)) as rpc:
                            self.assertEqual(pulse.tick(rpc, new_config, new_state, time.time(),
                                                        dry_run=True)["reason"], "cooldown")
                        fake.goal["status"] = "paused"
                        deadline = time.monotonic() + 3
                        while time.monotonic() < deadline:
                            owner = pulse.read_json(state_dir / "owner.json", {})
                            if owner.get("pid") == replacement["pid"]:
                                break
                            time.sleep(.02)
                        self.assertEqual(owner["pid"], replacement["pid"])
                        self.assertEqual(pulse.read_json(state_dir / "stopped.json")["pid"],
                                         started["pid"])
                        # The successor owns the inherited exclusive lock, so
                        # the previous watcher has completed its run and released it.
                        repeat = json.loads(subprocess.check_output(
                            args, text=True, env={**os.environ, "CODEX_THREAD_ID": THREAD}))
                        self.assertEqual(repeat["reason"], "already-running")
                    (state_dir / "STOP").touch()
                    deadline = time.monotonic() + 3
                    while pulse.is_running(state_dir) and time.monotonic() < deadline:
                        time.sleep(.02)
                    self.assertFalse(pulse.is_running(state_dir))
                    self.assertEqual(len(fake.sends()), 1)
                    self.assertFalse(errors)
                finally:
                    # Only the disposable stub watcher is stopped here.
                    if "state_dir" in locals():
                        (state_dir / "STOP").touch()
                    server.shutdown()
                    thread.join(timeout=3)

    def test_actual_websocket_unix_transport_without_codex_or_model(self):
        self.check_transport()

    def test_start_replaces_previous_goal_watcher(self):
        self.check_transport(replace_goal=True)


class TickCLIMessageTests(unittest.TestCase):
    def check_tick_message(self, *, saved_config, custom_message, thread_source="explicit"):
        from websockets.sync.server import unix_serve

        with tempfile.TemporaryDirectory(prefix="pulse-cli-") as temporary:
            directory = Path(temporary)
            socket_path = str(directory / "rpc.sock")
            state_root = directory / "state"
            state_dir = state_root / THREAD
            state_dir.mkdir(parents=True)
            config_path = state_dir / "config.json"
            if saved_config:
                pulse.write_json(config_path, {**CONFIG, "message": "saved watcher message"})
            original_config = config_path.read_bytes() if config_path.exists() else None
            message_file = directory / "message.txt"
            message_file.write_text("仅本次提醒 / custom tick message")
            fake, errors = FakeRPC(), []

            def handler(ws):
                try:
                    for raw in ws:
                        request = json.loads(raw)
                        if "id" not in request:
                            continue
                        result = ({"userAgent": "test-no-model"}
                                  if request["method"] == "initialize"
                                  else fake.call(request["method"], request["params"]))
                        ws.send(json.dumps({"id": request["id"], "result": result}))
                except Exception as error:
                    errors.append(str(error))

            with unix_serve(handler, socket_path) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    args = [sys.executable, str(Path(pulse.__file__).resolve()),
                            "tick", "--apply",
                            "--socket", socket_path, "--state-root", str(state_root)]
                    env = dict(os.environ)
                    env["CODEX_THREAD_ID"] = (THREAD if thread_source == "environment" else
                                              "22222222-2222-4222-8222-222222222222")
                    if thread_source == "explicit":
                        args += ["--thread", THREAD]
                    if custom_message:
                        args += ["--message-file", str(message_file)]
                    result = json.loads(subprocess.check_output(args, text=True, env=env))
                    self.assertEqual(result["action"], "sent")
                    expected = (message_file.read_text() if custom_message else
                                "saved watcher message" if saved_config else pulse.MESSAGE)
                    self.assertEqual(fake.sends()[0]["input"], [{"type": "text", "text": expected}])
                    self.assertEqual(fake.sends()[0]["expectedTurnId"], TURN)
                    # Applying another tick still respects the persisted cooldown.
                    again = json.loads(subprocess.check_output(args, text=True, env=env))
                    self.assertEqual(again["reason"], "cooldown")
                    self.assertEqual(len(fake.sends()), 1)
                    if saved_config:
                        self.assertEqual(config_path.read_bytes(), original_config)
                    else:
                        self.assertFalse(config_path.exists())
                    self.assertFalse(errors)
                finally:
                    server.shutdown()
                    thread.join(timeout=3)

    def test_custom_tick_message_with_and_without_saved_config(self):
        for saved_config in (False, True):
            with self.subTest(saved_config=saved_config):
                self.check_tick_message(saved_config=saved_config, custom_message=True)

    def test_default_tick_message_with_and_without_saved_config(self):
        for saved_config in (False, True):
            with self.subTest(saved_config=saved_config):
                self.check_tick_message(saved_config=saved_config, custom_message=False)


    def test_tick_uses_host_thread_when_omitted(self):
        self.check_tick_message(saved_config=False, custom_message=False,
                                thread_source="environment")

    def test_all_commands_reject_missing_thread_before_creating_state(self):
        env = dict(os.environ)
        env.pop("CODEX_THREAD_ID", None)
        with tempfile.TemporaryDirectory(prefix="pulse-no-thread-") as temporary:
            state_root = Path(temporary) / "must-not-exist"
            for command in ("start", "status", "stop", "tick"):
                with self.subTest(command=command):
                    result = subprocess.run(
                        [sys.executable, str(Path(pulse.__file__).resolve()), command,
                         "--state-root", str(state_root), "--socket", "/does-not-exist.sock"],
                        env=env, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("Specify --thread", result.stderr)
                    self.assertIn("CODEX_THREAD_ID", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertFalse(state_root.exists())

    def test_status_and_stop_use_host_default_and_explicit_override(self):
        alternate = "22222222-2222-4222-8222-222222222222"
        env = {**os.environ, "CODEX_THREAD_ID": THREAD}
        with tempfile.TemporaryDirectory(prefix="pulse-thread-") as temporary:
            for command in ("status", "stop"):
                for explicit in (False, True):
                    with self.subTest(command=command, explicit=explicit):
                        state_root = Path(temporary) / f"{command}-{explicit}"
                        args = [sys.executable, str(Path(pulse.__file__).resolve()),
                                command, "--state-root", str(state_root)]
                        if explicit:
                            args += ["--thread", alternate]
                        result = json.loads(subprocess.check_output(args, env=env, text=True))
                        expected = alternate if explicit else THREAD
                        self.assertEqual(result["state_dir"], str((state_root / expected).resolve()))
                        self.assertFalse((state_root / (THREAD if explicit else alternate)).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
