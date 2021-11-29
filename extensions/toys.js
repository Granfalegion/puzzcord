const { SlashCommandBuilder } = require('@discordjs/builders');
const { log, printUser, wrapErrors } = require('../common.js');

const plural = (num, noun) => num === 1 ? `1 ${noun}` : `${num} ${noun}s`;

module.exports = {
  commands: [
    {
      schema: new SlashCommandBuilder()
        .setName('hooray')
        .setDescription('Hooray!'),
      execute: async (interaction) => {
        await interaction.reply('🥳🎉🎊✨');
      },
    },
    {
      schema: new SlashCommandBuilder()
        .setName('isithuntyet')
        .setDescription('Is it hunt yet?'),
      execute: async (interaction) => {
        const start = new Date('14 Jan 2022, 12:00:00 EST');
        const now = new Date();
        if (now >= start) {
          await interaction.reply('Yes! 🎉');
          return;
        }
        const secondsLeft = Math.floor((start - now) / 1000);
        const left = [
          plural(Math.floor(secondsLeft / 86400), 'day'),
          plural(Math.floor(secondsLeft / 3600) % 24, 'hour'),
          plural(Math.floor(secondsLeft / 60) % 60, 'minute'),
          'and ' + plural(secondsLeft % 60, 'second'),
        ].join(', ');
        await interaction.reply(`No! ${left} left.`);
      },
    },
  ],
  setup: (client) => {
    client.on('messageCreate', wrapErrors(async (message) => {
      if (message.partial) {
        try {
          await message.fetch();
        } catch (error) {
          console.error(error);
          return;
        }
      }
      const { channel, content, guild } = message;
      const actor = message.member?.user;
      if (!content || !guild || !actor) {
        return;
      }
      if (/\b50\/50\b/i.test(content)) {
        await message.reply('Roll up your sleeves!');
        log(guild, `'50/50' by ${printUser(actor)} in #${channel.name}`);
        return;
      }
      if (/\bthanks,? obama\b/i.test(content)) {
        await message.reply("You're welcome!");
        log(guild, `'thanks obama' by ${printUser(actor)} in #${channel.name}`);
        return;
      }
    }));
  },
};
