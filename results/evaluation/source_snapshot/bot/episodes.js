// Keep actions from an old episode out of the next reset/trial.
class Episodes {
  constructor() {
    this.id = null;
    this.paused = false; // Preserve direct/manual tool tests before the first reset.
    this.active = 0;
    this.events = [];
    this.chest = null;
  }

  guard(handler) {
    return async (req, res, next) => {
      if (this.paused || this.active) {
        return res.status(409).json({ error: 'Bot is paused or another action is running.' });
      }
      this.active++;
      try { await handler(req, res); }
      catch (err) { next(err); }
      finally { this.active--; }
    };
  }

  record(event) {
    const entry = { ...event, episode_id: this.id };
    this.events.push(entry);
    return entry;
  }

  begin(id, chest) {
    if (!this.paused || this.active) throw new Error('Stop all actions before starting an episode.');
    if (!Array.isArray(chest) || chest.length !== 3 || !chest.every(Number.isSafeInteger)) {
      throw new Error('chest_position must contain three integer coordinates.');
    }
    this.id = id;
    this.chest = [...chest];
    this.events = [];
    this.paused = false;
  }
}

module.exports = { Episodes };
