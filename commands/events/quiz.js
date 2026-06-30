import { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } from 'discord.js';
import { EMOJIS, COLORS, EVENT_CONFIG } from '../../config.js';
import db from '../../database.js';

const quiz = {
  data: new SlashCommandBuilder()
    .setName('quiz')
    .setDescription('فعالية أسئلة ثقافية')
    .addStringOption(option =>
      option.setName('title').setDescription('عنوان المسابقة').setRequired(true)
    )
    .addStringOption(option =>
      option.setName('question').setDescription('السؤال').setRequired(true)
    )
    .addStringOption(option =>
      option.setName('answer').setDescription('الإجابة الصحيحة').setRequired(true)
    )
    .addStringOption(option =>
      option.setName('options').setDescription('الخيارات مفصولة بفاصلة').setRequired(true)
    ),

  async execute(interaction) {
    const title = interaction.options.getString('title');
    const question = interaction.options.getString('question');
    const answer = interaction.options.getString('answer');
    const optionsStr = interaction.options.getString('options');

    await interaction.deferReply();

    db.addUserStats(interaction.user.id, interaction.user.username);

    let options = optionsStr.split(',').map(opt => opt.trim());
    if (!options.includes(answer)) {
      options.push(answer);
    }
    options = options.sort(() => Math.random() - 0.5);

    const event = db.createEvent(title, question, 'quiz', interaction.user.id, {
      options,
      answer,
      participants: {},
    });

    const embed = new EmbedBuilder()
      .setTitle(`${EMOJIS.brain} ${title}`)
      .setDescription(question)
      .setColor(COLORS.info);

    options.slice(0, 4).forEach((option, index) => {
      embed.addFields({ name: `الخيار ${index + 1}`, value: option, inline: false });
    });

    embed.setFooter({ text: `معرّف الفعالية: ${event.eventId}` });

    const row = new ActionRowBuilder();
    options.slice(0, 4).forEach((option, index) => {
      row.addComponents(
        new ButtonBuilder()
          .setCustomId(`quiz_${event.eventId}_${index}`)
          .setLabel(option.substring(0, 80))
          .setStyle(ButtonStyle.Secondary)
      );
    });

    await interaction.followUp({ embeds: [embed], components: [row] });

    await interaction.followUp({
      content: `${EMOJIS.success} تم إنشاء السؤال بنجاح! (${event.eventId})`,
      ephemeral: true,
    });
  },

  async handleButton(interaction) {
    const [, eventId, optionIndex] = interaction.customId.split('_');
    const event = db.getEvent(parseInt(eventId));

    if (!event) {
      await interaction.reply({
        content: `${EMOJIS.error} الفعالية غير موجودة`,
        ephemeral: true,
      });
      return;
    }

    const selectedAnswer = event.data.options[parseInt(optionIndex)];
    const isCorrect = selectedAnswer === event.data.answer;

    if (isCorrect) {
      db.addUserStats(interaction.user.id, interaction.user.username);
      db.updateUserPoints(interaction.user.id, EVENT_CONFIG.pointsPerWin);

      const embed = new EmbedBuilder()
        .setTitle(`${EMOJIS.success} إجابة صحيحة!`)
        .setDescription(`حصلت على ${EVENT_CONFIG.pointsPerWin} نقطة!`)
        .setColor(COLORS.success);

      await interaction.reply({ embeds: [embed], ephemeral: true });
    } else {
      const embed = new EmbedBuilder()
        .setTitle(`${EMOJIS.error} إجابة خاطئة`)
        .setDescription(`الإجابة الصحيحة: **${event.data.answer}**`)
        .setColor(COLORS.error);

      await interaction.reply({ embeds: [embed], ephemeral: true });
    }
  },
};

export default quiz;
