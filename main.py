import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from config import DISCORD_TOKEN, EMOJIS, COLORS
import asyncio

load_dotenv()

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True
intents.dm_messages = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f'\n{EMOJIS["success"]} تم تشغيل البوت بنجاح!')
    print(f'اسم البوت: {bot.user}')
    print(f'معرّف البوت: {bot.user.id}')
    print(f'عدد السيرفرات: {len(bot.guilds)}')
    print(f'عدد المستخدمين: {sum(g.member_count for g in bot.guilds)}')
    
    # تحديث الحالة
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="🎉 الفعاليات المثيرة | /help"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)
    print(f'{EMOJIS["success"]} تم تحديث حالة البوت\n')

@bot.event
async def on_guild_join(guild):
    print(f'{EMOJIS["success"]} تم إضافة البوت إلى السيرفر: {guild.name} (ID: {guild.id})')
    
    # إرسال رسالة ترحيب
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title=f"{EMOJIS['gift']} شكراً لإضافتك البوت!",
                description="مرحباً بك في بوت الفعاليات الشامل!\n\nاستخدم `/` لرؤية جميع الأوامر المتاحة",
                color=COLORS['success']
            )
            embed.add_field(name="الميزات", value=f"""
{EMOJIS['dice']} رولة النرد
{EMOJIS['gift']} توزيع الجوائز
{EMOJIS['brain']} أسئلة ثقافية
{EMOJIS['image']} خمن الصورة
{EMOJIS['lightning']} سباق الكتابة
{EMOJIS['game']} تحديات الأزرار
{EMOJIS['trophy']} نظام النقاط
{EMOJIS['chart']} إحصائيات كاملة
            """, inline=False)
            
            try:
                await channel.send(embed=embed)
                break
            except:
                pass

@bot.command(name='help', hidden=True)
async def help_command(ctx):
    """عرض قائمة المساعدة"""
    embed = discord.Embed(
        title=f"{EMOJIS['clipboard']} قائمة المساعدة",
        description="استخدم أوامر Slash للوصول إلى جميع الميزات",
        color=COLORS['primary']
    )
    
    embed.add_field(
        name="🎉 الفعاليات",
        value="`/dice` - رولة النرد\n`/giveaway` - توزيع الجوائز\n`/quiz` - أسئلة ثقافية",
        inline=False
    )
    
    embed.add_field(
        name="🎮 الألعاب",
        value="`/image_guess` - خمن الصورة\n`/typing_race` - سباق الكتابة\n`/button_challenge` - تحدي الأزرار",
        inline=False
    )
    
    embed.add_field(
        name="📊 الإحصائيات",
        value="`/leaderboard` - لوحة الترتيب\n`/my_stats` - إحصائياتي\n`/events_stats` - إحصائيات الفعاليات",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ الإدارة",
        value="`/end_event` - إنهاء فعالية\n`/cancel_event` - إلغاء فعالية\n`/announce` - إعلان",
        inline=False
    )
    
    await ctx.send(embed=embed)

async def load_cogs():
    """تحميل جميع ملحقات البوت"""
    cogs_dir = 'cogs'
    if not os.path.exists(cogs_dir):
        os.makedirs(cogs_dir)
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'{cogs_dir}.{cog_name}')
                print(f'{EMOJIS["success"]} تم تحميل الكوج: {cog_name}')
            except Exception as e:
                print(f'{EMOJIS["error"]} خطأ في تحميل {cog_name}: {str(e)}')

async def main():
    async with bot:
        print(f'{EMOJIS["success"]} جاري تحميل الملحقات...')
        await load_cogs()
        
        if not DISCORD_TOKEN:
            print(f'{EMOJIS["error"]} خطأ: لم يتم العثور على DISCORD_TOKEN')
            return
        
        print(f'{EMOJIS["success"]} جاري توصيل البوت...\n')
        await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f'\n{EMOJIS["success"]} تم إيقاف البوت بنجاح')
    except Exception as e:
        print(f'{EMOJIS["error"]} خطأ: {str(e)}')
