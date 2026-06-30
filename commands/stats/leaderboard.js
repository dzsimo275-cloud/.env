import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { EMOJIS, COLORS } from '../../config.js';
import db from '../../database.js';

const leaderboard = {
  data: new SlashCommandBuilder()
    .setName('leaderboard')
    .setDescription('لوحة الترتيب العامة'),

  async execute(interaction) {
    await interaction.deferReply();

    const stats = db.getLeaderboard(10);

    if (stats.length === 0) {
      const embed = new EmbedBuilder()
        .setTitle(`${EMOJIS.trophy} لوحة الترتيب`)
        .setDescription('لا توجد بيانات حتى الآن')
        .setColor(COLORS.info);

      await interaction.followUp({ embeds: [embed] });
      return;
    }

    const medals = ['🥇', '🥈', '🥉'];
    let description = '';

    stats.forEach((stat, index) => {
      const medal = medals[index] || `${index + 1}️⃣`;
      description += `${medal} **${stat.username}** - ${stat.points} نقطة\n`;
    });

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.trophy} لوحة الترتيب العامة`)
      .setDescription(description)
      .setColor(COLORS.primary)
      .setFooter({ text: 'تم التحديث الآن' });

    await interaction.followUp({ embeds: [embed] });
  },
};

export default leaderboard;
