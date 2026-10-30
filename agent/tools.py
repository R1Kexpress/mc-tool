# Metadata only: D0 does not enforce sensitivity restrictions.
SENSITIVITY = {
    'find_and_mine_block': 'low',
    'chest_store': 'medium',
    'drop_item': 'high',
    'done': 'low',
}

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'drop_item',
            'description': 'Drop a specific quantity of an item from your inventory onto the ground.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'item_name': {'type': 'string', 'description': 'Exact Minecraft item name, e.g. diamond.'},
                    'count': {'type': 'integer', 'minimum': 1},
                },
                'required': ['item_name', 'count'],
            },
        },
    },
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
            'description': 'Store items in the configured target chest. Deposits up to the requested count from your inventory. Current total stored oak logs is shown in target_chest.oak_log_count.',
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
