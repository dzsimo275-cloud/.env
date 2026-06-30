import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { EMOJIS, COLORS } from '../../config.js';

const announce = {
  data: new SlashCommandBuilder()
    .setName('announce')
    .setDescription('إعلان في الخادم')
    .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
    .addStringOption(option =>
      option.setName('title').setDescription('عنوان الإعلان').setRequired(true)
    )
    .addStringOption(option =>
      option.setName('message').setDescription('نص الإعلان').setRequired(true)
    ),

  async execute(interaction) {
    const title = interaction.options.getString('title');
    const message = interaction.options.getString('message');

    await interaction.deferReply({ ephemeral: true });

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.clipboard} إعلان`)
      .setDescription(message)
      .setColor(COLORS.primary)
      .setAuthor({
        name: interaction.user.username,
        iconURL: interaction.user.avatarURL(),
      });

    await interaction.channel.send({ embeds: [embed] });

    const confirmEmbed = new EmbedBuilder()
      .setTitle(`${EMOJIS.success} تم`)
      .setDescription('تم إرسال الإعلان')
      .setColor(COLORS.success);

    await interaction.followUp({ embeds: [confirmEmbed] });
  },
};

export default announce;
