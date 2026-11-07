"""Record a requested pause after the in-flight episode has saved."""
import json
from pathlib import Path
import driver

plan = json.loads((driver.OUT / 'plan.json').read_text())
if driver.source_hashes() != plan['source_sha256']:
    raise RuntimeError('Source drift detected during pause.')
lock = driver.OUT / 'runner.lock'
if lock.read_text().strip() != '28624':
    raise RuntimeError('Unexpected supervisor lock; refusing removal.')
progress = driver.progress(plan['arena'], plan['prompt'], 'paused')
driver.save(driver.OUT / 'pause.json', {
    'paused_at': driver.now(), 'reason': 'User requested stop for now.',
    'completed': progress['completed'], 'interruption_policy': 'Supervisor stopped; in-flight episode allowed to save normally.',
    'resume': 'Run the unchanged driver.py explicitly; completed seeds will be skipped.'})
lock.unlink()
print(json.dumps(progress, indent=2))
