const config = require('./config.json');
const glob = require('glob');
const path = require('path');

const { Client, Intents } = require('discord.js');

require('log-timestamp');

// Create a new client instance
const client = new Client({
  intents: [
    Intents.FLAGS.GUILD_MEMBERS,
    Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
    Intents.FLAGS.GUILD_MESSAGES,
    Intents.FLAGS.GUILDS,
  ],
  partials: [
    'CHANNEL',
    'GUILD_MEMBER',
    'MESSAGE',
    'REACTION',
    'USER',
  ],
});

// When the client is ready, run this code (only once)
client.once('ready', () => {
  console.log('Ready!');
});

client.on('error', err => {
  console.log('Global error handler called', err);
});

console.log('Loading extensions...');
glob.sync('./extensions/*.js').forEach(file => {
  try {
    console.log(`Loading ${file}`);
    const extension = require(path.resolve(file));
    extension.setup(client);
  } catch (error) {
    console.error(`Failed to load extension ${file}`, error);
  }
});

// Login to Discord with your client's token
console.log('Starting!');
client.login(config.discord.botsecret);
