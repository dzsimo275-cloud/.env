import { Client, GatewayIntentBits, Collection } from 'discord.js';
import { config } from 'dotenv';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { EMOJIS, COLORS } from './config.js';

config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TOKEN = process.env.DISCORD_TOKEN;

if (!TOKEN) {
  console.error(`${EMOJIS.error} خطأ: لم يتم العثور على DISCORD_TOKEN في ملف .env`);
  process.exit(1);
}

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessageReactions,
  ],
});

client.commands = new Collection();
client.commandArray = [];

// تحميل الأوامر من المجلدات الفرعية
async function loadCommands() {
  const commandsPath = path.join(__dirname, 'commands');

  if (!fs.existsSync(commandsPath)) {
    console.log(`${EMOJIS.warning} مجلد الأوامر غير موجود`);
    return;
  }

  // الحصول على كل المجلدات الفرعية (events, games, stats, admin)
  const folders = fs.readdirSync(commandsPath).filter(file => {
    return fs.statSync(path.join(commandsPath, file)).isDirectory();
  });

  console.log(`${EMOJIS.success} تم العثور على ${folders.length} مجلدات أوامر\n`);

  // تحميل الأوامر من كل مجلد فرعي
  for (const folder of folders) {
    const folderPath = path.join(commandsPath, folder);
    const commandFiles = fs.readdirSync(folderPath).filter(file => file.endsWith('.js'));

    console.log(`${EMOJIS.success} تحميل أوامر من مجلد: ${folder}`);

    for (const file of commandFiles) {
      const filePath = path.join(folderPath, file);
      try {
        const command = await import(`file://${filePath}`);
        const commandModule = command.default;

        if (commandModule.data && commandModule.execute) {
          client.commands.set(commandModule.data.name, commandModule);
          client.commandArray.push(commandModule.data.toJSON());
          console.log(`  ✅ تم تحميل: ${commandModule.data.name}`);
        }
      } catch (error) {
        console.error(`  ${EMOJIS.error} خطأ في تحميل ${file}:`, error.message);
      }
    }
  }

  console.log(`\n${EMOJIS.success} تم تحميل إجمالي ${client.commands.size} أمر\n`);
}

client.once('ready', async () => {
  console.log(`\n${EMOJIS.success} تم تشغيل البوت بنجاح!`);
  console.log(`اسم البوت: ${client.user.tag}`);
  console.log(`معرّف البوت: ${client.user.id}`);
  console.log(`عدد السيرفرات: ${client.guilds.cache.size}`);
  console.log(`عدد المستخدمين: ${client.users.cache.size}`);

  // تحديث الحالة
  await client.user.setActivity('🎉 الفعاليات المثيرة | /', { type: 'WATCHING' });
  console.log(`${EMOJIS.success} تم تحديث حالة البوت\n`);

  // تسجيل الأوامر
  try {
    await client.application.commands.set(client.commandArray);
    console.log(`${EMOJIS.success} تم تسجيل ${client.commandArray.length} أمر في Discord\n`);
  } catch (error) {
    console.error(`${EMOJIS.error} خطأ في تسجيل الأوامر:`, error);
  }
});

client.on('guildCreate', async guild => {
  console.log(`${EMOJIS.success} تم إضافة البوت إلى السيرفر: ${guild.name} (ID: ${guild.id})`);

  // إرسال رسالة ترحيب
  for (const channel of guild.channels.cache.values()) {
    if (channel.isTextBased() && channel.permissionsFor(guild.members.me).has('SendMessages')) {
      const { EmbedBuilder } = await import('discord.js');
      const embed = new EmbedBuilder()
        .setTitle(`${EMOJIS.gift} شكراً لإضافتك البوت!`)
        .setDescription('مرحباً بك في بوت الفعاليات الشامل!\n\nاستخدم `/` لرؤية جميع الأوامر المتاحة')
        .setColor(COLORS.success)
        .addFields(
          {
            name: '⚡ المميزات',
            value: `${EMOJIS.dice} رولة النرد\n${EMOJIS.gift} توزيع الجوائز\n${EMOJIS.brain} أسئلة ثقافية\n${EMOJIS.image} خمن الصورة\n${EMOJIS.lightning} سباق الكتابة\n${EMOJIS.game} تحديات الأزرار\n${EMOJIS.trophy} نظام النقاط\n${EMOJIS.chart} إحصائيات`,
            inline: false,
          }
        );

      await channel.send({ embeds: [embed] });
      break;
    }
  }
});

client.on('interactionCreate', async interaction => {
  if (interaction.isCommand() || interaction.isSubcommand()) {
    const command = client.commands.get(interaction.commandName);

    if (!command) {
      console.log(`${EMOJIS.warning} الأمر ${interaction.commandName} غير موجود`);
      return;
    }

    try {
      await command.execute(interaction);
    } catch (error) {
      console.error(`${EMOJIS.error} خطأ في تنفيذ الأمر:`, error);
      await interaction.reply({
        content: `${EMOJIS.error} حدث خطأ في تنفيذ الأمر`,
        ephemeral: true,
      });
    }
  } else if (interaction.isButton()) {
    // معالجة الأزرار
    try {
      const command = client.commands.get(interaction.customId.split('_')[0]);
      if (command && command.handleButton) {
        await command.handleButton(interaction);
      }
    } catch (error) {
      console.error(`${EMOJIS.error} خطأ في معالجة الزر:`, error);
    }
  } else if (interaction.isModalSubmit()) {
    // معالجة النوافذ
    try {
      const command = client.commands.get(interaction.customId.split('_')[0]);
      if (command && command.handleModal) {
        await command.handleModal(interaction);
      }
    } catch (error) {
      console.error(`${EMOJIS.error} خطأ في معالجة النافذة:`, error);
    }
  }
});

// تحميل الأوامر وتشغيل البوت
await loadCommands();

client.login(TOKEN).catch(err => {
  console.error(`${EMOJIS.error} خطأ في تسجيل الدخول:`, err);
  process.exit(1);
});

// معالجة الأخطاء
process.on('unhandledRejection', error => {
  console.error(`${EMOJIS.error} خطأ غير معالج:`, error);
});

process.on('uncaughtException', error => {
  console.error(`${EMOJIS.error} استثناء غير معالج:`, error);
  process.exit(1);
});
