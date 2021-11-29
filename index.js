const glob = require('glob');
const invariant = require('tiny-invariant');
const path = require('path');

const { Client, Intents } = require('discord.js');
const { log, printUser, wrapErrors } = require('./common.js');
const { discord: discordCredentials } = require('./credentials.json');

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
client.commands = {};
glob.sync('./extensions/*.js').forEach(file => {
  try {
    console.log(`Loading ${file}`);
    const { commands, setup } = require(path.resolve(file));
    if (setup) {
      setup(client);
    }
    if (commands && commands.length) {
      commands.forEach(command => {
        const name = command.schema.name;
        invariant(
          !client.commands[name],
          `Duplicate command name '${name}' found!`,
        );
        client.commands[name] = command;
      });
    }
  } catch (error) {
    console.error(`Failed to load extension ${file}`, error);
  }
});


// Handle all commands
client.on('interactionCreate', wrapErrors(async (interaction) => {
  if (!interaction.isCommand()) {
    return;
  }

  const { channel, commandName, guild, user } = interaction;
  const command = client.commands[commandName];
  if (!command) {
    return;
  }

  try {
    log(
      guild,
      `Command /${commandName} by ${printUser(user)} in #${channel?.name}`,
    );
    await command.execute(interaction);
  } catch (error) {
    await interaction.reply({
      content: 'There was an error while executing this command!',
      ephemeral: true,
    });
    throw error;
  }
}));

// Login to Discord with your client's token
console.log('Starting!');
client.login(discordCredentials.botsecret);
