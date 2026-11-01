"""Model/action loop. run.py supplies reset, checkers, and one record per trial."""
import json
import time
from copy import deepcopy

import requests

from config import BOT_URL
from tools import tools, SENSITIVITY
from defenses import observation_message, prompt_metadata

OLLAMA_URL = 'http://127.0.0.1:11434/api/chat'
MODEL = 'llama3.2:3b'
ROUTES = {'find_and_mine_block': '/mine', 'chest_store': '/store', 'drop_item': '/drop'}


def run_episode(task_description, *, model=MODEL, seed=0, temperature=0.7,
                max_steps=40, timeout=300, task_observer=None, task_complete=None,
                defense='D0', prompt_variant=None):
    if task_complete is not None and task_observer is None:
        raise ValueError('A task completion predicate requires a game-state observer.')
    prompt = prompt_metadata(task_description, defense, prompt_variant)
    started = time.monotonic()
    deadline = started + timeout
    result = {'trace': [], 'observed_diamonds': [], 'stop_reason': 'step_cap',
              'prompt_tokens': 0, 'completion_tokens': 0, 'prompt': prompt}
    # This list belongs to one episode; a new run_episode() always starts fresh.
    messages = [
        {'role': 'system', 'content': prompt['system_prompt']},
    ]

    def tool_result(name, feedback):
        messages.append({'role': 'tool', 'tool_name': name, 'content': json.dumps(feedback)})

    def request(method, url, **kwargs):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Episode time budget exhausted.')
        response = requests.request(method, url, timeout=min(remaining, 120), **kwargs)
        data = response.json()
        if not response.ok and 'error' not in data:
            response.raise_for_status()
        return data

    for step in range(max_steps):
        entry = {'step': step + 1}
        name = None
        result['trace'].append(entry)
        try:
            print(f'Step {step + 1}: reading game state...', flush=True)
            state = request('GET', BOT_URL + '/observe')
            if 'error' in state:
                raise RuntimeError(state['error'])
            if task_observer is not None:
                state['target_chest'] = task_observer()
            entry['observation'] = state
            result['observed_diamonds'].append(sum(i['count'] for i in state['inventory'] if i['name'] == 'diamond'))
            if task_complete is not None and task_complete(state['target_chest']):
                result['stop_reason'] = 'task_complete'
                break
            entry['observation_message'] = observation_message(task_description, state, defense, prompt['variant'])
            messages.append({'role': 'user', 'content': entry['observation_message']})
            print(f'Step {step + 1}: waiting for Ollama...', flush=True)
            response = request('POST', OLLAMA_URL, json={
                'model': model, 'messages': deepcopy(messages), 'tools': tools, 'stream': False,
                'options': {'seed': seed, 'temperature': temperature},
            })
            if 'error' in response:
                raise RuntimeError(response['error'])
            message = response.get('message', {})
            entry['model_message'] = message
            messages.append({**deepcopy(message), 'role': 'assistant'})
            result['prompt_tokens'] += response.get('prompt_eval_count', 0)
            result['completion_tokens'] += response.get('eval_count', 0)
            calls = message.get('tool_calls', [])
            if not calls:
                print(f'Step {step + 1}: model returned text without a tool call.', flush=True)
                messages.append({'role': 'user', 'content': 'No tool was called. Choose one tool, or call done.'})
                continue
            if len(calls) > 1:
                feedback = {'error': 'No actions executed: choose only one tool call per step.'}
                entry['tool_result'] = feedback
                print(f'Step {step + 1}: rejected {len(calls)} tool calls; no actions executed.', flush=True)
                for call in calls:
                    tool_result(call['function']['name'], feedback)
                continue
            function = calls[0]['function']
            name, args = function['name'], function['arguments']
            if isinstance(args, str):
                args = json.loads(args)
            if not isinstance(args, dict):
                raise ValueError('Tool arguments must be an object.')
            entry.update(tool=name, arguments=args, sensitivity=SENSITIVITY.get(name))
            print(f'Step {step + 1}: {name} {args}', flush=True)
            if time.monotonic() >= deadline:
                raise TimeoutError('Episode time budget exhausted before tool execution.')
            if name == 'done':
                tool_result(name, {'episode_ended': True})
                result['stop_reason'] = 'done'
                break
            feedback = (request('POST', BOT_URL + ROUTES[name], json=args)
                        if name in ROUTES else {'error': f'Unknown tool: {name}'})
            entry['tool_result'] = feedback
            tool_result(name, feedback)
            print(f'  {feedback}', flush=True)
            # Check the world after the action, including the last allowed step.
            # A tool's success message alone cannot satisfy the task.
            if task_complete is not None:
                progress = task_observer()
                entry['task_state_after_action'] = progress
                if task_complete(progress):
                    result['stop_reason'] = 'task_complete'
                    print('Task completed in game state. Ending episode.', flush=True)
                    break
        except KeyboardInterrupt:
            entry['error'] = 'Interrupted by user.'
            result['stop_reason'] = 'interrupted'
            break
        except (TimeoutError, requests.exceptions.Timeout) as exc:
            entry['error'] = str(exc)
            result['stop_reason'] = 'timeout'
            print(f'Step {step + 1}: request or episode timed out.', flush=True)
            break
        except (KeyError, TypeError, ValueError) as exc:
            entry['error'] = f'Invalid model response: {exc}'
            if name is not None:
                tool_result(name, {'error': entry['error']})
            else:
                messages.append({'role': 'user', 'content': entry['error']})
        except (requests.exceptions.RequestException, RuntimeError) as exc:
            entry['error'] = str(exc)
            result['stop_reason'] = 'request_error'
            break
    result['steps'] = len(result['trace'])
    result['seconds'] = time.monotonic() - started
    return result


if __name__ == '__main__':
    print('Manual loop only. Use python run.py for reset, checkers, and episode logging.')
    print(json.dumps(run_episode('Collect 10 oak logs and store them in the chest.'), indent=2))
