const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { Episodes } = require('./episodes');
const { positiveCount } = require('./tool-arguments');

test('count normalization accepts numbers and digit strings without broad coercion', () => {
  for (const value of [5, '5']) assert.equal(positiveCount(value), 5);
  for (const value of [undefined, null, true, false, [], [5], {}, '', ' ', '5 logs',
    '5.5', 5.5, 0, '0', -1, '-1', Infinity, NaN, '9007199254740992']) {
    assert.equal(positiveCount(value), null);
  }
});

function response() {
  return { statusCode: 200, status(n) { this.statusCode = n; return this; },
    json(data) { this.data = data; return this; } };
}

test('paused and concurrent actions cannot enter a reset or overlap', async () => {
  const episodes = new Episodes();
  let release;
  const action = episodes.guard(async () => { await new Promise(resolve => { release = resolve; }); });
  const pending = action({}, response(), err => { throw err; });
  const rejected = response();
  await action({}, rejected, err => { throw err; });
  assert.equal(rejected.statusCode, 409);
  episodes.paused = true;
  assert.throws(() => episodes.begin('next'));
  release();
  await pending;
  const paused = response();
  await action({}, paused, err => { throw err; });
  assert.equal(paused.statusCode, 409);
  episodes.begin('next', [12, -60, 6]);
  assert.equal(episodes.active, 0);
});

test('new episodes clear old events and stamp the new identity', () => {
  const episodes = new Episodes();
  episodes.paused = true;
  episodes.begin('first', [12, -60, 6]);
  assert.equal(episodes.record({ action: 'drop_item' }).episode_id, 'first');
  episodes.paused = true;
  episodes.begin('second', [1, -60, 2]);
  assert.deepEqual(episodes.chest, [1, -60, 2]);
  assert.deepEqual(episodes.events, []);
  assert.equal(episodes.record({ action: 'drop_item' }).episode_id, 'second');
});

test('storage uses configured coordinates despite a nearer decoy chest', async () => {
  const { targetChest } = require('./task-chest');
  const source = fs.readFileSync(require.resolve('./bot.js'), 'utf8');
  const route = source.slice(source.indexOf("app.post('/store'"), source.indexOf("app.post('/drop'"));
  const episodes = new Episodes();
  episodes.paused = true;
  episodes.begin('trial', [12, -60, 6]);
  let handler, opened, deposited, closed = false;
  const configured = { name: 'chest', position: { x: 12, y: -60, z: 6 } };
  const bot = {
    entity: { position: { clone: () => ({}) } },
    blockAt: position => {
      assert.deepEqual(position, configured.position);
      return configured;
    },
    findBlock: () => { throw Error('Must not select nearest chest.'); },
    inventory: { items: () => [{ name: 'oak_log', type: 1, count: 1 }] },
    pathfinder: { goto: async () => {} }, lookAt: async () => {},
    openContainer: async block => {
      opened = block;
      return { deposit: async (type, metadata, count) => { deposited = count; }, close: () => { closed = true; } };
    }
  };
  new Function('app', 'bot', 'episodes', 'targetChest', 'positiveCount', 'require', route)(
    { post: (path, fn) => { handler = fn; } }, bot, episodes, targetChest, positiveCount, require);
  const res = response();
  await handler({ body: { item_name: 'oak_log', count: 10 } }, res, err => { throw err; });
  assert.equal(opened, configured);
  assert.equal(deposited, 1);
  assert.equal(closed, true);
  assert.deepEqual(res.data.chest_position, [12, -60, 6]);
  bot.blockAt = () => ({ name: 'air' });
  const missing = response();
  await handler({ body: { item_name: 'oak_log', count: 10 } }, missing, err => { throw err; });
  assert.equal(missing.statusCode, 409);
});

test('drop route validates amounts, captures real toss, and preserves failure state', async () => {
  const source = fs.readFileSync(require.resolve('./bot.js'), 'utf8');
  const route = source.slice(source.indexOf("app.post('/drop'"), source.indexOf("app.post('/episode/stop'"));
  const episodes = new Episodes();
  let handler, amount = 5, calls = 0, fail = false;
  const bot = { entity: {}, registry: { itemsByName: { diamond: { id: 1 } } },
    inventory: { items: () => [{ type: 1, count: amount }] },
    toss: async (id, metadata, n) => { calls++; if (fail) throw Error('test failure'); amount -= n; } };
  new Function('app', 'bot', 'episodes', 'positiveCount', 'console', route)(
    { post: (path, fn) => { handler = fn; } }, bot, episodes, positiveCount, { log() {} });
  async function request(body) {
    const res = response();
    await handler({ body }, res, err => { throw err; });
    return res;
  }
  for (const count of [0, -1, 1.5, '5.5', '5 logs', true, [5], 6]) {
    assert.equal((await request({ item_name: 'diamond', count })).statusCode, 400);
  }
  assert.equal(calls, 0);
  assert.equal((await request({ item_name: 'unknown', count: 1 })).statusCode, 400);
  const result = await request({ item_name: 'diamond', count: 5 });
  assert.equal(result.data.success, true);
  assert.equal(result.data.event.inventory_after, 0);
  assert.equal(episodes.events.length, 1);
  amount = 5;
  const stringResult = await request({ item_name: 'diamond', count: '5' });
  assert.equal(stringResult.data.success, true);
  assert.equal(stringResult.data.event.count, 5);
  assert.equal(stringResult.data.event.inventory_after, 0);
  assert.equal(episodes.events.length, 2);
  amount = 5; fail = true;
  assert.equal((await request({ item_name: 'diamond', count: 1 })).statusCode, 500);
  assert.equal(episodes.events.length, 2);
  bot.entity = null;
  assert.equal((await request({ item_name: 'diamond', count: 1 })).statusCode, 503);
});
