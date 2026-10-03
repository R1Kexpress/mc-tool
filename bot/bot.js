const mineflayer = require('mineflayer')
const express = require('express')

const app = express()
app.use(express.json())

const bot = mineflayer.createBot({
  host: 'localhost',
  port: 25565,
  username: 'AgentBot',
  version: '1.20.4'
})

app.post('/action', (req, res) => {
  const action = req.body.action
  console.log(`Received command: ${action}`)

  if (action === 'JUMP') {
    bot.setControlState('jump', true)
    setTimeout(() => bot.setControlState('jump', false), 500)
    bot.chat("I jumped!")
    res.json({ status: "success" })
  } else if (action === 'SPIN') {
    bot.look(bot.entity.yaw + Math.PI, 0)
    bot.chat("I spun!")
    res.json({ status: "success" })
  } else {
    res.json({ status: "ignored" })
  }
})

bot.once('spawn', () => {
  console.log('Bot spawned. Starting API...')
  app.listen(3000, () => console.log('Bot API listening on port 3000'))
})