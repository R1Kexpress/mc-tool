import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import analyze_d4_evaluation as analysis


class D4AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = analysis.read_json(analysis.ARCHIVE / 'plan.json')
        cls.rows = [json.loads(line) for line in
                    (analysis.ARCHIVE / 'raw/eval_D4_v1_A1.jsonl').read_text().splitlines()]

    def test_archive_has_all_seeds_and_retains_invalid_attempt_separately(self):
        report = analysis.analyze()
        self.assertEqual(report['measured_outcomes'], 60)
        self.assertEqual(report['raw_records'], 61)
        self.assertEqual(len(report['invalid_attempts']), 1)
        self.assertEqual(report['invalid_attempts'][0]['status'], 'setup_error')
        self.assertEqual(report['invalid_attempts'][0]['seed'], 9)
        self.assertEqual([c['task_successes'] for c in report['cells'].values()], [14, 8, 9])
        self.assertEqual(sum(c['diamond_loss_episodes'] for c in report['cells'].values()), 0)
        self.assertEqual(report['cells']['A1']['blocked_calls'], 475)

    def test_duplicate_missing_or_mixed_measured_outcomes_are_rejected(self):
        duplicate = dict(self.rows[0], episode_id='duplicate')
        mixed = copy.deepcopy(self.rows)
        mixed[0]['harness_version'] = 6
        for rows in (self.rows[1:], self.rows + [duplicate], mixed):
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                analysis.validate_d4(rows, 'A1', self.plan)

    def test_lock_and_blocked_call_trace_tampering_are_rejected(self):
        changed = copy.deepcopy(self.rows)
        changed[0]['untrusted_seen'] = False
        with self.assertRaises(ValueError):
            analysis.validate_d4(changed, 'A1', self.plan)
        changed = copy.deepcopy(self.rows)
        row = next(r for r in changed if r['blocked_calls'])
        row['blocked_calls'][0]['step'] += 1
        with self.assertRaises(ValueError):
            analysis.validate_d4(changed, 'A1', self.plan)

    def test_manifest_detects_modified_archive_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / 'raw.jsonl'
            data.write_text('original')
            manifest = {'files': [{'path': data.name, 'sha256': analysis.sha(data), 'bytes': data.stat().st_size}]}
            (root / 'manifest.json').write_text(json.dumps(manifest))
            data.write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                analysis.analyze(root)


if __name__ == '__main__':
    unittest.main()
