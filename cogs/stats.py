import discord
from discord.ext import commands
from discord import app_commands
from config import EMOJIS, COLORS, EVENT_CONFIG
from database import Database
from datetime import datetime

class StatsCog(commands.Cog):
    """كوج الإحصائيات والترتيبات"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="leaderboard", description="لوحة الترتيب العامة")
    async def leaderboard(self, interaction: discord.Interaction):
        """عرض لوحة الترتيب"""
        await interaction.response.defer()
        
        leaderboard = self.db.get_leaderboard(10)
        
        if not leaderboard:
            embed = discord.Embed(
                title=f"{EMOJIS['trophy']} لوحة الترتيب",
                description="لا توجد بيانات حتى الآن",
                color=COLORS['info']
            )
            await interaction.followup.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"{EMOJIS['trophy']} لوحة الترتيب العامة",
            color=COLORS['primary'],
            timestamp=datetime.now()
        )
        
        medals = ['🥇', '🥈', '🥉']
        description = ""
        
        for idx, stats in enumerate(leaderboard, 1):
            medal = medals[idx-1] if idx <= 3 else f"{idx}️⃣"
            description += f"{medal} **{stats.username}** - {stats.points} نقطة\n"
        
        embed.description = description
        embed.set_footer(text="تم التحديث الآن")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="my_stats", description="إحصائياتي الشخصية")
    async def my_stats(self, interaction: discord.Interaction):
        """عرض إحصائيات المستخدم"""
        await interaction.response.defer()
        
        stats = self.db.get_user_stats(interaction.user.id)
        
        if not stats:
            stats = self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        embed = discord.Embed(
            title=f"{EMOJIS['chart']} إحصائياتي",
            color=COLORS['primary'],
            timestamp=datetime.now()
        )
        
        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        
        embed.add_field(name="النقاط", value=f"⭐ {stats.points}", inline=True)
        embed.add_field(name="الفعاليات المشاركة", value=f"📊 {stats.events_participated}", inline=True)
        embed.add_field(name="الفعاليات المربحة", value=f"🏆 {stats.events_won}", inline=True)
        
        if stats.achievements:
            achievements_text = ' '.join(stats.achievements)
            embed.add_field(name="الإنجازات", value=achievements_text, inline=False)
        else:
            embed.add_field(name="الإنجازات", value="لم تحصل على إنجازات بعد", inline=False)
        
        if stats.last_event:
            embed.add_field(name="آخر مشاركة", value=stats.last_event.strftime('%Y-%m-%d %H:%M'), inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="events_stats", description="إحصائيات الفعاليات")
    async def events_stats(self, interaction: discord.Interaction):
        """عرض إحصائيات الفعاليات النشطة"""
        await interaction.response.defer()
        
        active_events = self.db.get_active_events()
        
        if not active_events:
            embed = discord.Embed(
                title=f"{EMOJIS['chart']} إحصائيات الفعاليات",
                description="لا توجد فعاليات نشطة",
                color=COLORS['info']
            )
            await interaction.followup.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"{EMOJIS['chart']} إحصائيات الفعاليات",
            color=COLORS['primary'],
            timestamp=datetime.now()
        )
        
        for event in active_events[:5]:
            participants_count = len(event.participants)
            embed.add_field(
                name=f"{event.title}",
                value=f"المشاركون: {participants_count} | النوع: {event.event_type}",
                inline=False
            )
        
        embed.set_footer(text=f"إجمالي الفعاليات النشطة: {len(active_events)}")
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))
