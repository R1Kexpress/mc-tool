import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('analysis', ROOT / 'scripts/analyze_evaluation.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


class EvaluationAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        archive = ROOT / 'results/evaluation'
        cls.plan = analysis.read_json(archive / 'formal_evaluation_plan.json')
        cls.item = cls.plan['selection']['selected'][0]
        cls.rows = [json.loads(s) for s in (archive / 'raw/eval_D1_v1_A1.jsonl').read_text().splitlines()]

    def test_wilson_boundary_rates_retain_uncertainty(self):
        self.assertAlmostEqual(analysis.wilson(0, 20)[1], 0.1611251580528194)
        self.assertAlmostEqual(analysis.wilson(20, 20)[0], 0.8388748419471806)

    def test_invalid_attempts_excluded_but_measured_timeouts_retained(self):
        selected = analysis.validate_cell(self.rows, self.item, 'A1', self.plan)
        self.assertEqual(len(selected), 20)
        self.assertEqual(sum(r['stop_reason'] == 'timeout' for r in selected), 6)
        self.assertEqual(analysis.measure(selected)['diamond_loss_episodes'], 6)

    def test_missing_duplicate_and_mixed_records_rejected(self):
        done = analysis.validate_cell(self.rows, self.item, 'A1', self.plan)
        duplicate = dict(done[0], episode_id='different-id')
        mixed = copy.deepcopy(done)
        mixed[0]['phase'] = 'development'
        for rows in [done[1:], done + [duplicate], mixed]:
            with self.assertRaises(ValueError):
                analysis.validate_cell(rows, self.item, 'A1', self.plan)

    def test_utility_and_loss_are_independent_outcomes(self):
        done = analysis.validate_cell(self.rows, self.item, 'A1', self.plan)
        result = analysis.measure(done)
        self.assertEqual(result['task_successes'], 14)
        self.assertEqual(result['task_with_loss'], 5)
        self.assertEqual(result['task_without_loss'], 9)
