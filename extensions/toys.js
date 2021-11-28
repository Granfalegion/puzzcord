const { log, printUser, wrapErrors } = require('../common.js');

module.exports = {
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
        await message.reply('You\'re welcome!');
        log(guild, `'thanks obama' by ${printUser(actor)} in #${channel.name}`);
        return;
      }
    }));
  },
};
