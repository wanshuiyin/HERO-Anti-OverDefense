"""Behavioral checks: no paid model calls and no real conversation writes."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

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
    def test_actual_websocket_unix_transport_without_codex_or_model(self):
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
                            "start", "--thread", THREAD, "--socket", socket_path,
                            "--state-root", str(directory / "state"), "--poll-seconds", ".05"]
                    started = json.loads(subprocess.check_output(args, text=True))
                    self.assertTrue(started["started"])
                    repeat = json.loads(subprocess.check_output(args, text=True))
                    self.assertEqual(repeat["reason"], "already-running")
                    state_dir = directory / "state" / THREAD
                    deadline = time.monotonic() + 3
                    while not (state_dir / "latest.json").exists() and time.monotonic() < deadline:
                        time.sleep(.02)
                    self.assertEqual(pulse.read_json(state_dir / "latest.json")["reason"], "goal-paused")
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


class TickCLIMessageTests(unittest.TestCase):
    def check_tick_message(self, *, saved_config, custom_message):
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
                            "tick", "--apply", "--thread", THREAD,
                            "--socket", socket_path, "--state-root", str(state_root)]
                    if custom_message:
                        args += ["--message-file", str(message_file)]
                    result = json.loads(subprocess.check_output(args, text=True))
                    self.assertEqual(result["action"], "sent")
                    expected = (message_file.read_text() if custom_message else
                                "saved watcher message" if saved_config else pulse.MESSAGE)
                    self.assertEqual(fake.sends()[0]["input"], [{"type": "text", "text": expected}])
                    self.assertEqual(fake.sends()[0]["expectedTurnId"], TURN)
                    # Applying another tick still respects the persisted cooldown.
                    again = json.loads(subprocess.check_output(args, text=True))
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
