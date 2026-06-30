import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { EMOJIS, COLORS } from '../../config.js';
import db from '../../database.js';

const giveaway = {
  data: new SlashCommandBuilder()
    .setName('giveaway')
    .setDescription('فعالية توزيع الجوائز')
    .addStringOption(option =>
      option.setName('title').setDescription('اسم الجائزة').setRequired(true)
    )
    .addStringOption(option =>
      option.setName('description').setDescription('وصف الجائزة').setRequired(true)
    )
    .addIntegerOption(option =>
      option.setName('duration').setDescription('المدة بالدقائق').setRequired(false).setMinValue(1)
    )
    .addIntegerOption(option =>
      option.setName('winners').setDescription('عدد الفائزين').setRequired(false).setMinValue(1)
    ),

  async execute(interaction) {
    const title = interaction.options.getString('title');
    const description = interaction.options.getString('description');
    const duration = interaction.options.getInteger('duration') || 5;
    const winnersCount = interaction.options.getInteger('winners') || 1;

    await interaction.deferReply();

    db.addUserStats(interaction.user.id, interaction.user.username);

    const event = db.createEvent(title, description, 'giveaway', interaction.user.id, {
      duration,
      winnersCount,
      participants: [],
      endTime: new Date(Date.now() + duration * 60000).toISOString(),
    });

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.gift} ${title}`)
      .setDescription(description)
      .setColor(COLORS.success)
      .addFields(
        { name: 'الجوائز', value: String(winnersCount), inline: true },
        { name: 'المدة', value: `${duration} دقيقة`, inline: true },
        { name: 'المشاركون', value: '0', inline: true }
      )
      .setFooter({ text: `معرّف الفعالية: ${event.eventId}` });

    const button = new ButtonBuilder()
      .setCustomId(`giveaway_${event.eventId}_join`)
      .setLabel('المشاركة')
      .setEmoji(EMOJIS.gift)
      .setStyle(ButtonStyle.Success);

    const row = new ActionRowBuilder().addComponents(button);

    await interaction.followUp({ embeds: [embed], components: [row] });

    await interaction.followUp({
      content: `${EMOJIS.success} تم إنشاء فعالية الجائزة بنجاح! (${event.eventId})`,
      ephemeral: true,
    });

    // إنهاء الفعالية تلقائياً بعد المدة المحددة
    setTimeout(() => {
      const finalEvent = db.getEvent(event.eventId);
      if (finalEvent && finalEvent.status === 'active') {
        const participantIds = Object.keys(finalEvent.participants).map(id => parseInt(id));
        const winners = [];
        for (let i = 0; i < Math.min(winnersCount, participantIds.length); i++) {
          const winnerIndex = Math.floor(Math.random() * participantIds.length);
          winners.push(participantIds[winnerIndex]);
          participantIds.splice(winnerIndex, 1);
        }
        db.endEvent(event.eventId, winners);
      }
    }, duration * 60000);
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

    if (String(interaction.user.id) in event.participants) {
      await interaction.reply({
        content: `${EMOJIS.error} أنت مشارك بالفعل!`,
        ephemeral: true,
      });
      return;
    }

    db.addParticipant(parseInt(eventId), interaction.user.id, interaction.user.username);

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.success} تم تسجيل اشتراكك`)
      .setDescription(`تمت إضافتك للمسابقة!\nعدد المشاركين: ${Object.keys(event.participants).length + 1}`)
      .setColor(COLORS.success);

    await interaction.reply({ embeds: [embed], ephemeral: true });
  },
};

export default giveaway;
