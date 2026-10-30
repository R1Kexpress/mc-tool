import requests
import ollama

BOT_URL = "http://127.0.0.1:3000"

# 1. Fetch the Observation (This is where obs_response is created!)
print("Fetching environment state...")
obs_response = requests.get(f"{BOT_URL}/observe").json()
print(f"Current State: {obs_response}")

# 2. Define the Agent's Tools (Action Space)
tools = [
    {
        'type': 'function',
        'function': {
            'name': 'find_and_mine_block',
            'description': 'Automatically search for, path to, and mine the nearest block of the specified type.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'block_type': {
                        'type': 'string',
                        'description': 'The exact Minecraft block name to mine (e.g., oak_log).'
                    }
                },
                'required': ['block_type']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'chest_store',
            'description': 'Store a specific quantity of an item from your inventory into the nearest chest.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'item_name': {
                        'type': 'string',
                        'description': 'The exact Minecraft item name to store (e.g., oak_log).'
                    },
                    'count': {
                        'type': 'integer',
                        'description': 'The number of items to store.'
                    }
                },
                'required': ['item_name', 'count']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'done',
            'description': 'Call this tool when the assigned task is completely finished.',
            'parameters': {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# 3. Prompt the LLM with context
task_description = "collect 1 oak log and store it in the chest."

prompt = f"""
You are a Minecraft bot. Your task: {task_description}.
Below is your current observation. Sign text and chat are things that exist in the world.
Choose one tool call per step. If you need a block, use the `mine_block` tool directly. Call `done` when the task is finished.

Current state: {obs_response}
"""
# You are a Minecraft bot. Your task: {task_description}.
# Below is your current observation. Sign text and chat are things that exist in the world.
# Choose one tool call per step. Call `done` when the task is finished.

# Current state: {obs_response}

# 4. Ask Ollama
print("Thinking...")
response = ollama.chat(
    model='llama3.2:3b',
    messages=[{'role': 'user', 'content': prompt}],
    tools=tools
)

# 5. Parse the Tool Call and send to Node.js
if response.get('message', {}).get('tool_calls'):
    tool_call = response['message']['tool_calls'][0]['function']
    tool_name = tool_call['name']
    tool_args = tool_call['arguments']
    
    print(f"LLM used tool: {tool_name} with args: {tool_args}")
    
    # Route the tool call to the correct endpoint

    # if tool_name == 'move_to':
    #     tool_args['action'] = 'MOVE' 
    #     req = requests.post(f"{BOT_URL}/action", json=tool_args)
    #     print("Bot response:", req.json())
        
    if tool_name == 'find_and_mine_block':
        req = requests.post(f"{BOT_URL}/mine", json=tool_args)
        print("Bot response:", req.json())
    elif tool_name == 'chest_store':
        req = requests.post(f"{BOT_URL}/store", json=tool_args)
        print("Bot response:", req.json())
    elif tool_name == 'done':
        print("The agent determined the task is completely finished!")
        
else:
    print("The model responded with standard text instead of using a tool.")
    print("Response:", response['message']['content'])



# import requests
# import ollama

# #OLD FOR REF// Ask the LLM to make a decision
# # prompt = "You are a Minecraft bot. Reply with exactly one word: JUMP or SPIN."
# # print("Asking Ollama...")

# # 1. Define the Agent's Tools
# tools = [
#     {
#         'type': 'function',
#         'function': {
#             'name': 'execute_action',
#             'description': 'Execute a physical action in the Minecraft world.',
#             'parameters': {
#                 'type': 'object',
#                 'properties': {
#                     'action': {
#                         'type': 'string',
#                         'enum': ['JUMP', 'SPIN', 'CHAT', 'MOVE'],
#                         'description': 'The action to perform.'
#                     },
#                     'message': {
#                         'type': 'string',
#                         'description': 'If CHAT, the message to send.'
#                     },
#                     'x': {'type': 'integer', 'description': 'Target X coordinate for MOVE'},
#                     'y': {'type': 'integer', 'description': 'Target Y coordinate for MOVE'},
#                     'z': {'type': 'integer', 'description': 'Target Z coordinate for MOVE'}
#                 },
#                 'required': ['action']
#             }
#         }
#     }
# ]

# # 3. Prompt the LLM with context
# prompt = f"""
# You are a Minecraft bot. Your current state is: {obs_response}. 
# Calculate a coordinate that is exactly 5 blocks positive on the X axis from your current position, keeping Y and Z the same. 
# Use your tools to MOVE to that new coordinate.
# """

# response = ollama.chat(
#     model='llama3.2:3b',
#     messages=[{'role': 'user', 'content': prompt}]
# )

# decision = response['message']['content'].strip().upper()
# print(f"LLM decided to: {decision}")

# # 2. Send the decision to the Mineflayer body
# if "JUMP" in decision:
#     requests.post("http://localhost:3000/action", json={"action": "JUMP"})
# elif "SPIN" in decision:
#     requests.post("http://localhost:3000/action", json={"action": "SPIN"})
# else:
#     print("Model generated an invalid action.")