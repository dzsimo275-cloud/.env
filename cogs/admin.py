import discord
from discord.ext import commands
from discord import app_commands
from config import EMOJIS, COLORS
from database import Database

class AdminCog(commands.Cog):
    """كوج إدارة الفعاليات"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="end_event", description="إنهاء فعالية")
    @app_commands.describe(event_id="معرّف الفعالية")
    async def end_event(self, interaction: discord.Interaction, event_id: int):
        """إنهاء فعالية"""
        await interaction.response.defer()
        
        event = self.db.get_event(event_id)
        
        if not event:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="الفعالية غير موجودة",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if event.creator_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} ممنوع",
                description="ليس لديك صلاحيات لإنهاء هذه الفعالية",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        self.db.end_event(event_id)
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} تم الإنهاء",
            description=f"تم إنهاء الفعالية: **{event.title}**",
            color=COLORS['success']
        )
        embed.add_field(name="المشاركون", value=len(event.participants), inline=True)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="cancel_event", description="إلغاء فعالية")
    @app_commands.describe(event_id="معرّف الفعالية")
    async def cancel_event(self, interaction: discord.Interaction, event_id: int):
        """إلغاء فعالية"""
        await interaction.response.defer()
        
        event = self.db.get_event(event_id)
        
        if not event:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خطأ",
                description="الفعالية غير موجودة",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if event.creator_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} ممنوع",
                description="ليس لديك صلاحيات لإلغاء هذه الفعالية",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # حذف الفعالية (تعيين الحالة إلى cancelled)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE events SET status = ? WHERE event_id = ?', ('cancelled', event_id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} تم الإلغاء",
            description=f"تم إلغاء الفعالية: **{event.title}**",
            color=COLORS['warning']
        )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="announce", description="الإعلان عن فعالية في الخادم")
    @app_commands.describe(
        title="عنوان الإعلان",
        message="نص الإعلان"
    )
    async def announce(self, interaction: discord.Interaction, title: str, message: str):
        """إصدار إعلان عام"""
        await interaction.response.defer()
        
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} ممنوع",
                description="ليس لديك صلاحيات لإصدار إعلانات",
                color=COLORS['error']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"{EMOJIS['clipboard']} إعلان",
            description=message,
            color=COLORS['primary']
        )
        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        
        await interaction.channel.send(embed=embed)
        
        confirm = discord.Embed(
            title=f"{EMOJIS['success']} تم",
            description="تم إرسال الإعلان",
            color=COLORS['success']
        )
        await interaction.followup.send(embed=confirm, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
