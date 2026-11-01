import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('formal_evaluation', Path(__file__).resolve().parents[1] / 'scripts/formal_evaluation.py')
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class EvaluationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.config = evaluation.load_config(Path(__file__).parent / 'arena.json')
        # The fixture has a different target; use the frozen three-log task here.
        self.config['target_logs'] = 3
        self.item = evaluation.load_selection(self.config)['selected'][0]
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'outcomes.jsonl'
        self.record = {'episode_id': 'one', 'seed': 0, 'status': 'completed',
                       'task_success': False, 'attack_success': False,
                       'stop_reason': 'timeout', 'defense': 'D1', 'phase': 'evaluation',
                       'prompt': self.item['prompt'], 'attack_id': 'A1', 'arena': self.config,
                       'model': 'llama3.2:3b', 'harness_version': 6, 'temperature': 0.7,
                       'max_steps': 40, 'timeout': 300}

    def write(self, records):
        self.path.write_text(''.join(json.dumps(r)+'\n' for r in records))

    def read(self):
        return evaluation.completed_seeds(self.path, self.item, 'A1', self.config)

    def test_measured_failure_is_completed_and_skipped(self):
        self.write([self.record])
        self.assertEqual(self.read(), {0})

    def test_invalid_attempt_retained_and_completed_retry_allowed(self):
        invalid = dict(self.record, episode_id='invalid', status='checker_error', task_success=None, attack_success=None)
        self.write([invalid, self.record])
        self.assertEqual(self.read(), {0})
        self.assertEqual(len(self.path.read_text().splitlines()), 2)

    def test_duplicate_completed_seed_rejected(self):
        self.write([self.record, dict(self.record, episode_id='two')])
        with self.assertRaises(ValueError):
            self.read()

    def test_drift_and_truncated_records_rejected(self):
        for field, value in [('phase', 'development'), ('temperature', 0), ('task_success', None), ('seed', True)]:
            with self.subTest(field=field):
                record = copy.deepcopy(self.record)
                record[field] = value
                self.write([record])
                with self.assertRaises(ValueError):
                    self.read()
        self.path.write_text('{')
        with self.assertRaises(ValueError):
            self.read()

    def test_changed_task_fails_frozen_prompt_validation(self):
        self.config['target_logs'] = 4
        with self.assertRaises(ValueError):
            evaluation.load_selection(self.config)
