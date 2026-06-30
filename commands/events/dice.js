import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { EMOJIS, COLORS } from '../../config.js';
import db from '../../database.js';

const dice = {
  data: new SlashCommandBuilder()
    .setName('dice')
    .setDescription('فعالية رولة النرد')
    .addStringOption(option =>
      option.setName('title').setDescription('عنوان الفعالية').setRequired(true)
    )
    .addStringOption(option =>
      option.setName('description').setDescription('وصف الفعالية').setRequired(true)
    ),

  async execute(interaction) {
    const title = interaction.options.getString('title');
    const description = interaction.options.getString('description');

    await interaction.deferReply();

    db.addUserStats(interaction.user.id, interaction.user.username);

    const event = db.createEvent(title, description, 'dice', interaction.user.id, {
      rolls: {},
    });

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.dice} ${title}`)
      .setDescription(description)
      .setColor(COLORS.primary)
      .setAuthor({ name: interaction.user.username, iconURL: interaction.user.avatarURL() })
      .addFields(
        { name: 'المشاركون', value: '0', inline: true },
        { name: 'النتيجة الأعلى', value: 'لم يتم اللعب بعد', inline: true }
      )
      .setFooter({ text: `معرّف الفعالية: ${event.eventId}` });

    const button = new ButtonBuilder()
      .setCustomId(`dice_${event.eventId}_roll`)
      .setLabel('رمي النرد')
      .setEmoji(EMOJIS.dice)
      .setStyle(ButtonStyle.Primary);

    const row = new ActionRowBuilder().addComponents(button);

    const msg = await interaction.followUp({ embeds: [embed], components: [row] });

    await interaction.followUp({
      content: `${EMOJIS.success} تم إنشاء فعالية النرد بنجاح! (${event.eventId})`,
      ephemeral: true,
    });
  },

  async handleButton(interaction) {
    const [, eventId] = interaction.customId.split('_');
    const event = db.getEvent(parseInt(eventId));

    if (!event) {
      await interaction.reply({
        content: `${EMOJIS.error} الفعالية غير موجودة`,
        ephemeral: true,
      });
      return;
    }

    const roll = Math.floor(Math.random() * 6) + 1;
    event.data.rolls[interaction.user.id] = roll;
    db.addParticipant(parseInt(eventId), interaction.user.id, interaction.user.username);

    const maxRoll = Math.max(...Object.values(event.data.rolls));

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.dice} نتيجتك`)
      .setDescription(`حصلت على **${roll}**!`)
      .setColor(COLORS.primary)
      .addFields(
        { name: 'أعلى نتيجة الآن', value: String(maxRoll), inline: false },
        { name: 'عدد اللاعبين', value: String(Object.keys(event.participants).length), inline: false }
      );

    await interaction.reply({ embeds: [embed], ephemeral: true });
  },
};

export default dice;
