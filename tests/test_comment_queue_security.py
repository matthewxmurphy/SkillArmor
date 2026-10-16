"""Local synthetic command/queue tests; never posts to any service.
Matthew X Murphy, https://MatthewxMurphy.com; https://builtnotbegged.com.
Existing distribution terms retained.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("queue_worker", Path(__file__).resolve().parents[1] / "scripts/process-comment-queue.py")
worker = importlib.util.module_from_spec(spec); spec.loader.exec_module(worker)

def item():
    return {"slug": "$(touch /not-executed); ' \"", "owner": "owner;echo ignored", "status": "queued", "comment": {"combined": "$(ignored) ; `ignored` \n quoted text"}}

class QueueTests(unittest.TestCase):
    def test_untrusted_fields_are_single_inert_arguments(self):
        captured = {}
        def adapter(argv, **options):
            captured.update(argv=argv, options=options)
            self.assertTrue(Path(argv[-1]).is_file())
            self.assertEqual(Path(argv[-1]).stat().st_mode & 0o777, 0o600)
            return subprocess.CompletedProcess(argv, 0, '{"confirmed":true,"receipt_id":"synthetic-receipt"}', '')
        original = item()
        with patch.object(worker.subprocess, "run", adapter):
            ok, info = worker.run_post_command('/usr/local/bin/owned-adapter --slug "{slug}" --text "{comment_text}" --file {comment_file}', original)
        self.assertTrue(ok)
        self.assertFalse(captured["options"]["shell"])
        self.assertEqual(captured["argv"][2], original["slug"])
        self.assertEqual(captured["argv"][4], original["comment"]["combined"])
        self.assertFalse(Path(captured["argv"][-1]).exists())
    def test_shell_and_eval_and_dynamic_executables_denied(self):
        for command in ['sh -c "{comment_text}"', '/bin/sh -c "{comment_text}"', '/usr/bin/python3 -c "{comment_text}"', '{slug} --body {comment_file}']:
            with patch.object(worker.subprocess, "run") as run:
                self.assertFalse(worker.run_post_command(command, item())[0])
                run.assert_not_called()
    def test_failed_adapter_and_unconfirmed_success_are_uncertain(self):
        for response in [subprocess.CompletedProcess([], 1, '', 'private error'), subprocess.CompletedProcess([], 0, 'posted', ''), subprocess.CompletedProcess([], 0, '{"confirmed":false}', '')]:
            with patch.object(worker.subprocess, "run", return_value=response):
                self.assertFalse(worker.run_post_command('/usr/local/bin/owned-adapter {comment_file}', item())[0])
    def test_uncertain_delivery_is_durable_and_never_auto_retried(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"; payload = {"items": [item()]}
            with patch.object(worker, "run_post_command", return_value=(False, "uncertain")) as run:
                result = worker.process_queue(payload, path, 1, '/usr/local/bin/adapter')
                self.assertEqual(result["items"][0]["status"], "uncertain")
                worker.process_queue(payload, path, 1, '/usr/local/bin/adapter')
                self.assertEqual(run.call_count, 1)
    def test_one_attempt_limit_and_interrupted_claim_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"; old = item(); old["status"] = "posting"
            payload = {"items": [old, item(), item()]}
            with patch.object(worker, "run_post_command", return_value=(False, "uncertain")) as run:
                result = worker.process_queue(payload, path, 1, '/usr/local/bin/adapter')
                self.assertEqual(run.call_count, 1)
                self.assertEqual([x['status'] for x in result['items']], ['uncertain', 'uncertain', 'queued'])
                self.assertEqual(result['postStats']['attemptedThisRun'], 1)
    def test_concurrent_worker_lock_rejects_second_owner(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"
            with worker.queue_lock(path):
                with self.assertRaises(BlockingIOError): worker.process_queue({"items":[]}, path, 1, '')

    def test_corrupt_persisted_state_cannot_restore_a_stale_queue(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"; path.write_text('{broken')
            with patch.object(worker, "run_post_command") as run:
                with self.assertRaises(ValueError): worker.process_queue({"items":[item()]}, path, 1, '/usr/local/bin/adapter')
                run.assert_not_called()
            self.assertEqual(path.read_text(), '{broken')
    def test_regeneration_retains_delivery_receipts_beyond_current_selection(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"
            previous = {**item(), "id":"synthetic-item", "status":"uncertain", "attempts":1, "postReceipt":"synthetic-receipt"}
            worker.save_json(path, {"items":[previous]})
            result = worker.generate_queue({"findings":[]}, path, 1, "medium")
            self.assertEqual(result["items"], [previous])

if __name__ == '__main__': unittest.main()
