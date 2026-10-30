"""Load the real arena layout; never guess coordinates for world edits."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOT_URL = 'http://127.0.0.1:3000'


def load_config(path=ROOT / 'arena.json'):
    path = Path(path)
    if not path.exists():
        raise ValueError('Copy arena.example.json to arena.json and fill in your arena coordinates.')
    config = json.loads(path.read_text(encoding='utf-8'))
    if not re.fullmatch(r'[A-Za-z0-9_]{1,16}', config.get('bot_name', '')):
        raise ValueError('bot_name must be a Minecraft player name.')
    for name in ('spawn', 'chest', 'sign'):
        _position(config.get(name), name)
    logs = config.get('logs')
    if not isinstance(logs, list) or not logs:
        raise ValueError('logs must list each log position: [[x, y, z], ...].')
    for position in logs:
        _position(position, 'log')
    if len({tuple(p) for p in logs}) != len(logs):
        raise ValueError('Log positions must be unique.')
    positions = [config[key] for key in ('spawn', 'chest', 'sign')] + logs
    if len({tuple(p) for p in positions}) != len(positions):
        raise ValueError('Spawn, chest, sign, and logs must have distinct positions.')
    for key in ('target_logs', 'starting_diamonds', 'cleanup_radius'):
        if type(config.get(key)) is not int or config[key] <= 0:
            raise ValueError(f'{key} must be a positive integer.')
    if len(logs) < config['target_logs']:
        raise ValueError('Provide enough logs for target_logs.')
    if config['cleanup_radius'] > 64:
        raise ValueError('cleanup_radius must be at most 64 blocks.')
    spawn = config['spawn']
    for position in positions:
        if sum((a - b) ** 2 for a, b in zip(position, spawn)) > config['cleanup_radius'] ** 2:
            raise ValueError('All arena positions must lie within cleanup_radius of spawn.')
    # Observations include signs only within this box. Catch invisible-payload setups early.
    delta = [abs(a - b) for a, b in zip(config['sign'], spawn)]
    if delta[0] > 5 or delta[1] > 2 or delta[2] > 5:
        raise ValueError('Place the sign within observation range of spawn (5 X/Z, 2 Y).')
    return config


def _position(value, name):
    if not isinstance(value, list) or len(value) != 3 or any(type(n) is not int for n in value):
        raise ValueError(f'{name} must be [x, y, z] with integer coordinates.')
    if not -64 <= value[1] <= 319 or any(abs(value[i]) > 29999984 for i in (0, 2)):
        raise ValueError(f'{name} is outside Minecraft Overworld bounds.')


def xyz(position):
    return ' '.join(map(str, position))
