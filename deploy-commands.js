const glob = require('glob');
const invariant = require('tiny-invariant');
const path = require('path');

const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { discord: discordCredentials } = require('./credentials.json');
const { GUILDS } = require('./common.js');

const schemas = {};
glob.sync('./extensions/*.js').forEach(file => {
  try {
    console.log(`Loading ${file}`);
    const extension = require(path.resolve(file));
    if (extension.commands?.length) {
      extension.commands.forEach(({ schema }) => {
        const { name } = schema;
        invariant(
          !schemas[schema.name],
          `Duplicate command name '${name}' found!`,
        );
        console.log(`  > Found command '${name}'`);
        schemas[name] = schema;
      });
    }
  } catch (error) {
    console.error(`Failed to load extension ${file}`, error);
  }
});

const clientId = discordCredentials.client_id;
const guildId = GUILDS['prod'];
const commands = Object.values(schemas).map(command => command.toJSON());

new REST({ version: '9' })
  .setToken(discordCredentials.botsecret)
  .put(Routes.applicationGuildCommands(clientId, guildId), { body: commands })
  .then(() => console.log('Successfully registered application commands.'))
  .catch(console.error);
