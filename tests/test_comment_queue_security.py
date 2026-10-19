"""Local synthetic command/queue tests; never posts to any service.
Matthew X Murphy, https://MatthewxMurphy.com; https://builtnotbegged.com.
Existing distribution terms retained.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import shlex
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("queue_worker", Path(__file__).resolve().parents[1] / "scripts/process-comment-queue.py")
worker = importlib.util.module_from_spec(spec); spec.loader.exec_module(worker)

def item(identity="synthetic-item"):
    return {"id": identity, "slug": "$(touch /not-executed); ' \"", "owner": "owner;echo ignored", "status": "queued", "comment": {"combined": "$(ignored) ; `ignored` \n quoted text"}}

class QueueTests(unittest.TestCase):
    def test_untrusted_fields_are_single_inert_arguments(self):
        captured = {}
        def adapter(argv, **options):
            captured.update(argv=argv, options=options)
            self.assertTrue(Path(argv[-1].split("=", 1)[1]).is_file())
            self.assertEqual(Path(argv[-1].split("=", 1)[1]).stat().st_mode & 0o777, 0o600)
            return subprocess.CompletedProcess(argv, 0, '{"confirmed":true,"receipt_id":"synthetic-receipt"}', '')
        original = item()
        with patch.object(worker.subprocess, "run", adapter):
            ok, info = worker.run_post_command('/usr/local/bin/owned-adapter --slug "{slug}" --owner "{owner}" --body-file {comment_file}', original)
        self.assertTrue(ok)
        self.assertFalse(captured["options"]["shell"])
        self.assertEqual(captured["argv"][1], "--slug=" + original["slug"])
        self.assertEqual(captured["argv"][2], "--owner=" + original["owner"])
        self.assertFalse(Path(captured["argv"][-1].split("=", 1)[1]).exists())
    def test_shell_and_eval_and_dynamic_executables_denied(self):
        for command in ['sh -c "{comment_text}"', '/bin/sh -c "{comment_text}"', '/usr/bin/python3 -c "{comment_text}"', '{slug} --body {comment_file}']:
            with patch.object(worker.subprocess, "run") as run:
                self.assertFalse(worker.run_post_command(command, item())[0])
                run.assert_not_called()
    def test_formatted_program_script_and_option_positions_fail_closed(self):
        commands = [
            '{slug} --body-file {comment_file}',
            shlex.quote(sys.executable) + ' {slug} {owner} --body-file {comment_file}',
            shlex.quote(sys.executable) + ' /trusted/adapter.py {slug} {owner} --body-file {comment_file}',
            '/usr/bin/node {owner} --body-file {comment_file}',
            '/usr/bin/node /trusted/adapter.js --eval {slug} --body-file {comment_file}',
            '/usr/local/bin/owned-adapter --slug {comment_text} --body-file {comment_file}',
            '/usr/local/bin/owned-adapter --body-file {slug}',
        ]
        for command in commands:
            for slug in ['-c', '--eval', '/tmp/dynamic-adapter.py']:
                candidate = item(); candidate.update(slug=slug, owner='untrusted program source')
                with self.subTest(command=command, slug=slug), patch.object(worker.subprocess, 'run') as run:
                    self.assertFalse(worker.run_post_command(command, candidate)[0])
                    run.assert_not_called()

    def test_native_fixed_python_adapter_receives_leading_options_only_as_data(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); adapter = root/'adapter.py'; evidence = root/'arguments.json'; marker = root/'never-created'
            adapter.write_text('import json,sys\nfrom pathlib import Path\n'
                'args=dict(arg.split("=",1) for arg in sys.argv[1:])\n'
                'body=Path(args["--body-file"]).read_text()\n'
                'Path('+repr(str(evidence))+').write_text(json.dumps({"args":args,"body":body}))\n'
                'print(json.dumps({"confirmed":True,"receipt_id":"local-synthetic"}))\n')
            command = shlex.quote(sys.executable)+' '+shlex.quote(str(adapter))+' --slug {slug} --owner {owner} --body-file {comment_file}'
            candidate = item(); candidate.update(slug='-c', owner='--eval')
            candidate['comment']['combined'] = 'from pathlib import Path; Path('+repr(str(marker))+').touch()'
            self.assertTrue(worker.run_post_command(command, candidate)[0])
            received = json.loads(evidence.read_text())
            self.assertEqual(received['args']['--slug'], '-c')
            self.assertEqual(received['args']['--owner'], '--eval')
            self.assertEqual(received['body'].strip(), candidate['comment']['combined'])
            self.assertFalse(marker.exists())
            self.assertFalse(Path(received['args']['--body-file']).exists())

    def test_failed_adapter_and_unconfirmed_success_are_uncertain(self):
        for response in [subprocess.CompletedProcess([], 1, '', 'private error'), subprocess.CompletedProcess([], 0, 'posted', ''), subprocess.CompletedProcess([], 0, '{"confirmed":false}', '')]:
            with patch.object(worker.subprocess, "run", return_value=response):
                self.assertFalse(worker.run_post_command('/usr/local/bin/owned-adapter --body-file {comment_file}', item())[0])
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
            path = Path(td) / "queue.json"; old = item("interrupted"); old["status"] = "posting"
            payload = {"items": [old, item("first"), item("second")]}
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

    def test_repeated_source_identity_has_one_delivery_and_does_not_consume_unique_limit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.json"
            finding = {"slug":"synthetic-skill", "reasonCode":"review", "signalLevel":"medium"}
            other = {**finding, "slug":"another-skill"}
            payload = worker.generate_queue({"findings":[finding, dict(finding), other]}, path, 2, "medium")
            self.assertEqual([row["slug"] for row in payload["items"]], ["synthetic-skill", "another-skill"])
            with patch.object(worker, "run_post_command", return_value=(True, "synthetic-confirmed")) as run:
                worker.process_queue(payload, path, 2, "/synthetic/adapter")
                worker.process_queue(payload, path, 2, "/synthetic/adapter")
            self.assertEqual(run.call_count, 2)
            self.assertEqual({call.args[1]["slug"] for call in run.call_args_list}, {"synthetic-skill", "another-skill"})

    def test_duplicate_durable_identities_never_deliver_or_rewrite_receipts(self):
        for prior_status in ["queued", "posting", "uncertain", "posted"]:
            with self.subTest(status=prior_status), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "queue.json"
                previous = {**item(), "status":prior_status, "attempts":1, "postReceipt":"synthetic-receipt"}
                worker.save_json(path, {"items":[previous, item()]})
                before = path.read_bytes()
                with patch.object(worker, "run_post_command") as run:
                    with self.assertRaisesRegex(ValueError, "Duplicate queue identities"):
                        worker.process_queue({"items":[item("stale-default")]}, path, 2, "/synthetic/adapter")
                    with self.assertRaisesRegex(ValueError, "Duplicate queue identities"):
                        worker.generate_queue({"findings":[]}, path, 2, "medium")
                    run.assert_not_called()
                self.assertEqual(path.read_bytes(), before)

    def test_missing_or_nonstring_durable_identity_fails_before_any_attempt(self):
        for identity in [None, "", "   ", 7, True]:
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "queue.json"
                worker.save_json(path, {"items":[item("valid-first"), item(identity)]})
                before = path.read_bytes()
                with patch.object(worker, "run_post_command") as run:
                    with self.assertRaisesRegex(ValueError, "nonempty string identities"):
                        worker.process_queue({"items":[]}, path, 2, "/synthetic/adapter")
                    run.assert_not_called()
                self.assertEqual(path.read_bytes(), before)

if __name__ == '__main__': unittest.main()
