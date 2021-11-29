const fs = require('fs');
const path = require('path');
const shuffle = require('shuffle-array');
const { SlashCommandBuilder } = require('@discordjs/builders');
const { MessageEmbed } = require('discord.js');

const haveyoutried = fs
  .readFileSync(
    path.resolve(__dirname, '../haveyoutried.txt'),
    { encoding:'utf8', flag:'r' },
  )
  .split('\n');

const LOWER = 'abcdefghijklmnopqrstuvwxyz'.repeat(2);
const UPPER = LOWER.toUpperCase();

function allRotN(message) {
  const chars = [];
  [...message].forEach(c => {
    const lowerIndex = LOWER.indexOf(c);
    if (lowerIndex !== -1) {
      chars.push([...LOWER.slice(lowerIndex).slice(0, 26)]);
      return;
    }
    const upperIndex = UPPER.indexOf(c);
    if (upperIndex !== -1) {
      chars.push([...UPPER.slice(upperIndex).slice(0, 26)]);
      return;
    }
    chars.push(Array(26).fill(c));
  });
  return [...Array(26).keys()].map(i => chars.map(c => c[i]).join(''));
}

const rotSpecificCommands = [...Array(26).keys()].map(i => {
  const n = i + 1;
  return {
    schema: new SlashCommandBuilder()
      .setName(`rot${n}`)
      .setDescription(`Rotates a message just by rot${n}`)
      .addStringOption(option => option
        .setName('message')
        .setDescription(`Message to rotate through rot${n}`)
        .setRequired(true),
      ),
    execute: async (interaction) => {
      const message = interaction.options.getString('message');
      let response = '```\n';
      response += `ORIGINAL: ${message}\n`;
      response += `ROT ${n}: `.padStart(10) + allRotN(message)[n % 26];
      response += '\n```';
      try {
        await interaction.reply(response);
      } catch (_) {
        await interaction.reply(
          'Sorry, response was too long for Discord. Try a shorter string',
        );
      }
    },
  };
});

module.exports = {
  commands: [
    {
      schema: new SlashCommandBuilder()
        .setName('stuck')
        .setDescription('Suggests some tips from the Have You Tried? list'),
      execute: async (interaction) => {
        const tips = shuffle(haveyoutried).slice(0, 5).join('\n');
        await interaction.reply({
          content: `**Have You Tried...**\n${tips}`,
          embeds: [
            new MessageEmbed({
              title: 'Have You Tried?',
              url: 'https://wind-up-birds.org/wiki/index.php/Have_You_Tried',
            }),
          ],
        });
      },
    },
    {
      schema: new SlashCommandBuilder()
        .setName('rot')
        .setDescription(
          'Rotates a message through all rot N and displays the permutations',
        )
        .addStringOption(option => option
          .setName('message')
          .setDescription('Message to rotate through rot N')
          .setRequired(true),
        ),
      execute: async (interaction) => {
        const message = interaction.options.getString('message');
        let response = '```\nROT  -N   N   MESSAGE\n';
        response += allRotN(message)
          .map((rot, n) => {
            const backward = (n - 26).toString().padStart(3);
            const forward = n.toString().padStart(2);
            rot = rot.substr(0, 60);
            return ` ${UPPER[n + 25]}  ${backward}  ${forward}   ${rot}`;
          })
          .join('\n');
        response += '\n```';
        try {
          await interaction.reply(response);
        } catch (_) {
          await interaction.reply(
            'Sorry, response was too long for Discord. Try a shorter string',
          );
        }
      },
    },
    ...rotSpecificCommands,
  ],
};
