import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';
import { EMOJIS, COLORS } from '../../config.js';
import db from '../../database.js';

const myStats = {
  data: new SlashCommandBuilder()
    .setName('my_stats')
    .setDescription('إحصائياتي الشخصية'),

  async execute(interaction) {
    await interaction.deferReply();

    let stats = db.getUserStats(interaction.user.id);

    if (!stats) {
      stats = db.addUserStats(interaction.user.id, interaction.user.username);
    }

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.chart} إحصائياتي`)
      .setColor(COLORS.primary)
      .setAuthor({
        name: interaction.user.username,
        iconURL: interaction.user.avatarURL(),
      })
      .addFields(
        { name: 'النقاط', value: `⭐ ${stats.points}`, inline: true },
        {
          name: 'الفعاليات المشاركة',
          value: `📊 ${stats.eventsParticipated}`,
          inline: true,
        },
        { name: 'الفعاليات المربحة', value: `🏆 ${stats.eventsWon}`, inline: true }
      );

    if (stats.achievements.length > 0) {
      const achievementsText = stats.achievements.join(' ');
      embed.addFields({ name: 'الإنجازات', value: achievementsText, inline: false });
    } else {
      embed.addFields({
        name: 'الإنجازات',
        value: 'لم تحصل على إنجازات بعد',
        inline: false,
      });
    }

    await interaction.followUp({ embeds: [embed] });
  },
};

export default myStats;
