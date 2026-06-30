import { EmbedBuilder } from 'discord.js';
import { COLORS, EMOJIS } from '../config.js';

export function createEmbed(title, description, color = COLORS.primary, fields = []) {
  const embed = new EmbedBuilder()
    .setTitle(title)
    .setDescription(description)
    .setColor(color)
    .setTimestamp();

  fields.forEach(field => {
    embed.addFields(field);
  });

  return embed;
}

export function formatLeaderboard(stats) {
  const medals = ['🥇', '🥈', '🥉'];
  let description = '';

  stats.forEach((stat, index) => {
    const medal = medals[index] || `${index + 1}️⃣`;
    description += `${medal} **${stat.username}** - ${stat.points} نقطة\n`;
  });

  return description;
}

export function getRandomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
