import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
from datetime import datetime, timedelta
from config import EMOJIS, COLORS, EVENT_CONFIG
from database import Database
from typing import Optional

class EventsCog(commands.Cog):
    """كوج الفعاليات الرئيسية"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
        self.event_timers = {}
    
    @app_commands.command(name="dice", description="فعالية رولة النرد")
    @app_commands.describe(
        title="عنوان الفعالية",
        description="وصف الفعالية"
    )
    async def dice_event(self, interaction: discord.Interaction, title: str, description: str):
        """إنشاء فعالية رولة النرد"""
        await interaction.response.defer()
        
        # إضافة منشئ الفعالية كمستخدم
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        # إنشاء الفعالية
        event = self.db.create_event(
            title=title,
            description=description,
            event_type='dice',
            creator_id=interaction.user.id,
            data={'rolls': {}}
        )
        
        # إنشاء Embed
        embed = discord.Embed(
            title=f"{EMOJIS['dice']} {title}",
            description=description,
            color=COLORS['primary'],
            timestamp=datetime.now()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.add_field(name="المشاركون", value="0", inline=True)
        embed.add_field(name="النتيجة الأعلى", value="لم يتم اللعب بعد", inline=True)
        embed.set_footer(text=f"معرّف الفعالية: {event.event_id}")
        
        # إرسال الرسالة مع الأزرار
        view = DiceEventView(self.db, event.event_id)
        msg = await interaction.followup.send(embed=embed, view=view)
        
        # حفظ معرّف الرسالة
        event.data['message_id'] = msg.id
        
        await interaction.followup.send(f"{EMOJIS['success']} تم إنشاء فعالية النرد بنجاح! ({event.event_id})")
    
    @app_commands.command(name="giveaway", description="فعالية توزيع الجوائز")
    @app_commands.describe(
        title="اسم الجائزة",
        description="وصف الجائزة",
        duration="المدة بالدقائق",
        winners="عدد الفائزين"
    )
    async def giveaway_event(self, interaction: discord.Interaction, title: str, description: str, duration: int = 5, winners: int = 1):
        """إنشاء فعالية توزيع جوائز"""
        await interaction.response.defer()
        
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        event = self.db.create_event(
            title=title,
            description=description,
            event_type='giveaway',
            creator_id=interaction.user.id,
            data={'duration': duration, 'winners_count': winners, 'participants': []}
        )
        
        embed = discord.Embed(
            title=f"{EMOJIS['gift']} {title}",
            description=description,
            color=COLORS['success'],
            timestamp=datetime.now()
        )
        embed.add_field(name="الجوائز", value=winners, inline=True)
        embed.add_field(name="المدة", value=f"{duration} دقيقة", inline=True)
        embed.add_field(name="المشاركون", value="0", inline=True)
        embed.set_footer(text=f"معرّف الفعالية: {event.event_id}")
        
        view = GiveawayEventView(self.db, event.event_id, duration)
        msg = await interaction.followup.send(embed=embed, view=view)
        
        event.data['message_id'] = msg.id
        event.data['end_time'] = (datetime.now() + timedelta(minutes=duration)).isoformat()
        
        await interaction.followup.send(f"{EMOJIS['success']} تم إنشاء فعالية الجوائز! ({event.event_id})")
    
    @app_commands.command(name="quiz", description="أسئلة ثقافية")
    @app_commands.describe(
        title="عنوان المسابقة",
        question="السؤال",
        answer="الإجابة الصحيحة",
        options="الخيارات مفصولة بفاصلة"
    )
    async def quiz_event(self, interaction: discord.Interaction, title: str, question: str, answer: str, options: str):
        """إنشاء فعالية أسئلة ثقافية"""
        await interaction.response.defer()
        
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        options_list = [opt.strip() for opt in options.split(',')]
        if answer not in options_list:
            options_list.append(answer)
        
        random.shuffle(options_list)
        
        event = self.db.create_event(
            title=title,
            description=question,
            event_type='quiz',
            creator_id=interaction.user.id,
            data={'options': options_list, 'answer': answer, 'participants': {}}
        )
        
        embed = discord.Embed(
            title=f"{EMOJIS['brain']} {title}",
            description=question,
            color=COLORS['info'],
            timestamp=datetime.now()
        )
        
        for i, option in enumerate(options_list, 1):
            embed.add_field(name=f"الخيار {i}", value=option, inline=False)
        
        embed.set_footer(text=f"معرّف الفعالية: {event.event_id}")
        
        view = QuizEventView(self.db, event.event_id, options_list)
        await interaction.followup.send(embed=embed, view=view)
        
        await interaction.followup.send(f"{EMOJIS['success']} تم إنشاء فعالية الأسئلة! ({event.event_id})")


class DiceEventView(discord.ui.View):
    """عرض أزرار فعالية النرد"""
    
    def __init__(self, db: Database, event_id: int):
        super().__init__(timeout=None)
        self.db = db
        self.event_id = event_id
    
    @discord.ui.button(label="رمي النرد", emoji=EMOJIS['dice'], style=discord.ButtonStyle.primary)
    async def roll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر رمي النرد"""
        await interaction.response.defer()
        
        event = self.db.get_event(self.event_id)
        if not event:
            await interaction.followup.send("❌ الفعالية غير موجودة", ephemeral=True)
            return
        
        roll = random.randint(1, 6)
        user_id = interaction.user.id
        
        event.data['rolls'][str(user_id)] = roll
        self.db.add_participant(self.event_id, user_id, interaction.user.name)
        
        max_roll = max(event.data['rolls'].values())
        
        embed = discord.Embed(
            title=f"{EMOJIS['dice']} نتيجتك",
            description=f"حصلت على **{roll}**!",
            color=COLORS['primary']
        )
        embed.add_field(name="أعلى نتيجة الآن", value=str(max_roll), inline=False)
        embed.add_field(name="عدد اللاعبين", value=str(len(event.participants)), inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class GiveawayEventView(discord.ui.View):
    """عرض أزرار فعالية الجوائز"""
    
    def __init__(self, db: Database, event_id: int, duration: int):
        super().__init__(timeout=None)
        self.db = db
        self.event_id = event_id
        self.duration = duration
    
    @discord.ui.button(label="المشاركة", emoji=EMOJIS['gift'], style=discord.ButtonStyle.success)
    async def participate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر المشاركة"""
        await interaction.response.defer()
        
        event = self.db.get_event(self.event_id)
        if not event:
            await interaction.followup.send("❌ الفعالية غير موجودة", ephemeral=True)
            return
        
        if str(interaction.user.id) in event.participants:
            await interaction.followup.send(f"{EMOJIS['error']} أنت مشارك بالفعل!", ephemeral=True)
            return
        
        self.db.add_participant(self.event_id, interaction.user.id, interaction.user.name)
        
        embed = discord.Embed(
            title=f"{EMOJIS['success']} تم تسجيل اشتراكك",
            description=f"تم إضافتك للمسابقة!\nعدد المشاركين: {len(event.participants)}",
            color=COLORS['success']
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class QuizEventView(discord.ui.View):
    """عرض أزرار فعالية الأسئلة"""
    
    def __init__(self, db: Database, event_id: int, options: list):
        super().__init__(timeout=None)
        self.db = db
        self.event_id = event_id
        self.options = options
        
        for i, option in enumerate(options[:4]):
            self.add_item(discord.ui.Button(
                label=option[:80],
                custom_id=f"quiz_{event_id}_{i}",
                style=discord.ButtonStyle.secondary
            ))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.custom_id.startswith(f"quiz_{self.event_id}_"):
            return False
        
        event = self.db.get_event(self.event_id)
        if not event:
            await interaction.response.send_message("❌ الفعالية غير موجودة", ephemeral=True)
            return False
        
        option_index = int(interaction.custom_id.split('_')[-1])
        selected_answer = self.options[option_index]
        is_correct = selected_answer == event.data['answer']
        
        if is_correct:
            self.db.add_user_stats(interaction.user.id, interaction.user.name)
            self.db.update_user_points(interaction.user.id, EVENT_CONFIG['points_per_win'])
            
            embed = discord.Embed(
                title=f"{EMOJIS['success']} إجابة صحيحة!",
                description=f"حصلت على {EVENT_CONFIG['points_per_win']} نقطة!",
                color=COLORS['success']
            )
        else:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} إجابة خاطئة",
                description=f"الإجابة الصحيحة: **{event.data['answer']}**",
                color=COLORS['error']
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return True


async def setup(bot: commands.Bot):
    await bot.add_cog(EventsCog(bot))
