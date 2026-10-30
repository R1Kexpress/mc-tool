const mineflayer = require('mineflayer')
const express = require('express')
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder')
const { plugin: collectBlock } = require('mineflayer-collectblock');
const { Episodes } = require('./episodes');
const { targetChest } = require('./task-chest');
const { positiveCount } = require('./tool-arguments');
const episodes = new Episodes();

const app = express()
app.use(express.json())

const bot = mineflayer.createBot({
  host: 'localhost',
  port: 25565,
  username: 'AgentBot',
  version: '1.20.4'
})

bot.loadPlugin(pathfinder);
bot.loadPlugin(collectBlock);
bot.on('chat', (username, message) => {
  if (username === bot.username) return
  console.log(`${username} said: ${message}`)

  if (message === 'look') {
    const pos = bot.entity.position
    let foundBlocks = []
    
    // Scan a 3x3 grid around the bot, at foot level (0) and eye level (1)
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = 0; dy <= 1; dy++) {
        for (let dz = -1; dz <= 1; dz++) {
          if (dx === 0 && dz === 0) continue // Skip the bot's own body space
          
          const block = bot.blockAt(pos.offset(dx, dy, dz))
          if (block && block.name !== 'air' && block.name !== 'cave_air') {
            foundBlocks.push(block.name)
          }
        }
      }
    }
    
    // Remove duplicates and print what it found
    const uniqueBlocks = [...new Set(foundBlocks)]
    if (uniqueBlocks.length > 0) {
      bot.chat(`Immediately around me, I see: ${uniqueBlocks.join(', ')}`)
    } else {
      // As a sanity check, see if it even detects the ground it is standing on
      const ground = bot.blockAt(pos.offset(0, -1, 0))
      bot.chat(`I see nothing around me. The ground below me is: ${ground ? ground.name : 'missing'}`)
    }
  }
})

app.post('/action', episodes.guard(async (req, res) => {
  const action = req.body.action
  console.log(`Received command: ${action}`)

  if (action === 'JUMP') {
    bot.setControlState('jump', true)
    setTimeout(() => bot.setControlState('jump', false), 500)
    res.json({ status: 'success' })
  } else if (action === 'SPIN') {
    bot.look(bot.entity.yaw + Math.PI, 0)
    res.json({ status: 'success' })
  } else if (action === 'CHAT') {
    bot.chat(req.body.message)
    res.json({ status: 'success' })
  } else if (action === 'MOVE') {
    const { x, y, z } = req.body
    const defaultMove = new Movements(bot)
    bot.pathfinder.setMovements(defaultMove)
    bot.pathfinder.setGoal(new goals.GoalBlock(x, y, z))
    bot.chat(`Navigating to X:${x} Y:${y} Z:${z}`)
    res.json({ status: 'success' })
  } else {
    res.json({ status: 'ignored' })
  }
}));

app.post('/mine', episodes.guard(async (req, res) => {
  const blockType = req.body.block_type;
  if (!bot.entity) return res.json({ error: "Bot not spawned" });

  try {
    const blockToMine = bot.findBlock({
      matching: bot.registry.blocksByName[blockType].id,
      maxDistance: 32
    });

    if (!blockToMine) {
      return res.json({ error: `No ${blockType} found nearby.` });
    }

    const { Movements } = require('mineflayer-pathfinder');
    const defaultMove = new Movements(bot);
    bot.pathfinder.setMovements(defaultMove);

    console.log(`Pathing to and collecting ${blockType}...`);
    
    // Explicitly try to equip an axe if the bot has one
    const axe = bot.inventory.items().find(item => item.name.includes('axe'));
    if (axe) {
        await bot.equip(axe, 'hand');
    }

    // Attempt collection
    await bot.collectBlock.collect(blockToMine);

    res.json({ success: true, message: `Successfully mined and collected ${blockType}.` });
  } catch (err) {
    console.error("Mining error:", err); // Log the full error to the Node console
    res.json({ error: `Failed to mine ${blockType}: ${err.message}` });
  }
}));

app.post('/store', episodes.guard(async (req, res) => {
  const itemName = req.body.item_name;
  const requestedCount = positiveCount(req.body.count);
  if (requestedCount === null) {
    return res.status(400).json({ error: 'count must be a positive integer.' });
  }

  if (!bot.entity) return res.json({ error: "Bot not spawned" });

  let chestBlock;
  try { chestBlock = targetChest(bot, episodes); }
  catch (err) { return res.status(409).json({ error: err.message }); }

  const itemToDeposit = bot.inventory.items().find(item => item.name === itemName);
  if (!itemToDeposit) {
    return res.json({ error: `I do not have any ${itemName} in my inventory.` });
  }

  const depositCount = Math.min(requestedCount, itemToDeposit.count);

  try {
    // 1. Walk to the chest, stopping 2 blocks away (do not try to stand inside it)
    const { goals } = require('mineflayer-pathfinder');
    await bot.pathfinder.goto(new goals.GoalNear(chestBlock.position.x, chestBlock.position.y, chestBlock.position.z, 2));

    // Optional but highly recommended: explicitly look at the chest before clicking
    await bot.lookAt(chestBlock.position);

    // 2. Open and deposit
    const chest = await bot.openContainer(chestBlock);
    try { await chest.deposit(itemToDeposit.type, null, depositCount); }
    finally { chest.close(); }
    
    res.json({ success: true, message: `Successfully deposited ${depositCount} ${itemName}.`,
      deposited_count: depositCount, requested_count: requestedCount, chest_position: episodes.chest });
  } catch (err) {
    res.json({ error: `Failed to deposit ${itemName}: ${err.message}` });
  }
}));

app.post('/drop', episodes.guard(async (req, res) => {
  if (!bot.entity) return res.status(503).json({ error: 'Bot not spawned' });

  const itemName = req.body.item_name;
  const count = positiveCount(req.body.count);
  if (typeof itemName !== 'string' || count === null) {
    return res.status(400).json({ error: 'Provide item_name and a positive integer count.' });
  }

  const itemType = bot.registry.itemsByName[itemName];
  if (!itemType) return res.status(400).json({ error: `Unknown item: ${itemName}` });
  const inventoryCount = () => bot.inventory.items()
    .filter(item => item.type === itemType.id)
    .reduce((total, item) => total + item.count, 0);
  const before = inventoryCount();
  if (before < count) {
    return res.status(400).json({ error: `Only have ${before} ${itemName}; requested ${count}.` });
  }

  try {
    await bot.toss(itemType.id, null, count);
    // Capture the completed toss immediately; a later observation may include re-picked-up items.
    const event = episodes.record({ action: 'drop_item', item_name: itemName, count,
      inventory_before: before, inventory_after: inventoryCount(),
      timestamp: new Date().toISOString() });
    console.log(JSON.stringify(event));
    res.json({ success: true, event });
  } catch (err) {
    res.status(500).json({ error: `Failed to drop ${itemName}: ${err.message}` });
  }
}));

app.post('/episode/stop', async (req, res) => {
  episodes.paused = true;
  try {
    // These cancellations may reject their original action request. Wait for it to settle.
    const cancellation = bot.collectBlock.cancelTask();
    bot.pathfinder.setGoal(null);
    bot.clearControlStates();
    if (bot.targetDigBlock) bot.stopDigging();
    let timer;
    try {
      await Promise.race([
        (async () => {
          await cancellation;
          while (episodes.active) await new Promise(resolve => setTimeout(resolve, 25));
        })(),
        new Promise((resolve, reject) => {
          timer = setTimeout(() => reject(new Error('Action did not stop; restart the Node bot before resetting.')), 5000);
        })
      ]);
    } finally { clearTimeout(timer); }
    if (bot.currentWindow) bot.closeWindow(bot.currentWindow);
    res.json({ success: true, episode_id: episodes.id });
  } catch (err) {
    res.status(503).json({ error: err.message });
  }
});

app.post('/episode/start', (req, res) => {
  if (typeof req.body.episode_id !== 'string' || !req.body.episode_id) {
    return res.status(400).json({ error: 'episode_id is required.' });
  }
  try {
    episodes.begin(req.body.episode_id, req.body.chest_position);
    res.json({ success: true, episode_id: episodes.id });
  } catch (err) { res.status(409).json({ error: err.message }); }
});

app.get('/episode/events', (req, res) => {
  res.json({ episode_id: episodes.id, events: episodes.events });
});

app.get('/observe', (req, res) => {
  if (!bot.entity) {
    return res.json({ error: "Bot not fully spawned yet." });
  }

  const pos = bot.entity.position.floored();
  const signs = [];
  const visibleBlocks = new Set();

  for (let dx = -5; dx <= 5; dx++) {
    for (let dy = -2; dy <= 2; dy++) {
      for (let dz = -5; dz <= 5; dz++) {
        const block = bot.blockAt(pos.offset(dx, dy, dz));
        if (!block) continue;

        if (block.name.includes('sign')) {
          let text = "";
          if (block.signText) text += block.signText.replace(/\n/g, ' ').trim();
          if (block.backSignText) text += " " + block.backSignText.replace(/\n/g, ' ').trim();
          signs.push({ x: block.position.x, y: block.position.y, z: block.position.z, text: text.trim() });
        } else if (block.name === 'oak_log' || block.name === 'chest') {
          visibleBlocks.add(block.name);
        }
      }
    }
  }



  res.json({
    health: bot.health,
    food: bot.food,
    position: { x: pos.x, y: pos.y, z: pos.z },
    inventory: bot.inventory.items().map(item => ({ name: item.name, count: item.count })),
    nearby_blocks: Array.from(visibleBlocks),
    nearby_signs: signs
  });
});

bot.once('spawn', () => {
  console.log('Bot spawned. Starting API...')
  app.listen(3000, '127.0.0.1', () => console.log('Bot API listening on 127.0.0.1:3000'))
})

