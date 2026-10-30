function targetChest(bot, episodes) {
  if (!episodes.chest) throw new Error('No task chest configured. Start a trial with run.py.');
  const position = bot.entity.position.clone();
  [position.x, position.y, position.z] = episodes.chest;
  const block = bot.blockAt(position);
  if (!block || block.name !== 'chest') {
    throw new Error(`Task chest missing or not loaded at ${episodes.chest.join(', ')}.`);
  }
  return block;
}

module.exports = { targetChest };
