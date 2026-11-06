"""Deterministic guards for the opt-in live evaluator; no model calls."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import probe


class EvidenceTests(unittest.TestCase):
    def test_non_event_json_and_string_messages_are_ignored(self):
        records = probe.events('"noise"\nnull\nnot json\n{"type":"system","message":"notice"}\n')
        self.assertEqual(len(records), 1)
        self.assertEqual(probe.tool_calls('claude', records), [])

    def test_glob_output_and_failed_reads_are_not_read_evidence(self):
        calls = [
            {'tool': 'glob', 'state': {'status': 'completed', 'output': '.agents/jstack/rules.md'}},
            {'tool': 'read', 'state': {'status': 'error', 'input': {'filePath': '.agents/jstack/rules.md'}}},
            {'type': 'command_execution', 'command': 'cat .agents/jstack/rules.md', 'status': 'completed', 'exit_code': 1},
        ]
        self.assertEqual(probe.read_trace(calls), '')

    def test_claude_read_requires_successful_tool_result(self):
        use = {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'r1', 'name': 'Read', 'input': {'file_path': 'notes.txt'}}]}}
        error = {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'r1', 'is_error': True}]}}
        success = {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'r1', 'content': 'facts'}]}}
        self.assertEqual(probe.tool_calls('claude', [use, error]), [])
        self.assertIn('notes.txt', probe.read_trace(probe.tool_calls('claude', [use, success])))

    def test_cursor_started_read_is_not_completed_read(self):
        started = {'tool_call': {'readToolCall': {'args': {'path': 'notes.txt'}}}}
        self.assertEqual(probe.read_trace([started]), '')
        completed = {'tool_call': {'readToolCall': {'args': {'path': 'notes.txt'}, 'result': {'success': {'content': 'facts'}}}}}
        self.assertIn('notes.txt', probe.read_trace([completed]))

    def test_real_client_event_formats_extract_final_answer(self):
        samples = {
            'claude': {'type': 'result', 'result': 'answer'},
            'cursor': {'type': 'result', 'result': 'answer'},
            'codex': {'item': {'type': 'agent_message', 'text': 'answer'}},
            'gemini': {'type': 'message', 'role': 'assistant', 'content': 'answer'},
            'opencode': {'type': 'text', 'part': {'text': 'answer'}},
        }
        for client, event in samples.items():
            with self.subTest(client=client):
                self.assertEqual(probe.final_text(client, [event]), 'answer')

    def test_plausible_answer_without_reads_cannot_pass_native_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'project'
            baseline = probe.fixture(root, 'native', False)
            stdout = json.dumps({'type': 'result', 'result': 'Expected delivery six weeks after photographs, estimated £4,000 excluding hosting, not a guaranteed deadline. SMOKE-ARGO-19'})
            result = probe.inspect(root, 'native', 'claude', stdout, baseline)
            self.assertTrue(result['checks']['commercial_terms_present'])
            self.assertFalse(result['checks']['reference_read'])
            self.assertFalse(result['checks']['source_read'])
            self.assertEqual(result['semantic_review'].split(';')[0], 'not run')

    def test_read_only_probe_detects_untracked_output_and_new_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'project'
            baseline = probe.fixture(root, 'review', False)
            (root / 'unsolicited.txt').write_text('unwanted edit')
            result = probe.inspect(root, 'review', 'claude', '', baseline)
            self.assertFalse(result['checks']['no_untracked_files'])
            probe.git(root, 'add', 'unsolicited.txt')
            probe.git(root, 'commit', '-qm', 'Unauthorized change')
            result = probe.inspect(root, 'review', 'claude', '', baseline)
            self.assertFalse(result['checks']['no_commit'])
            self.assertFalse(result['checks']['no_tracked_edits'])


if __name__ == '__main__':
    unittest.main()
