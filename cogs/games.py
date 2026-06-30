import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from config import EMOJIS, COLORS, EVENT_CONFIG
from database import Database

class GamesCog(commands.Cog):
    """كوج الألعاب والتحديات"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()
    
    @app_commands.command(name="image_guess", description="لعبة خمن الصورة")
    @app_commands.describe(
        image_url="رابط الصورة",
        correct_answer="الإجابة الصحيحة"
    )
    async def image_guess(self, interaction: discord.Interaction, image_url: str, correct_answer: str):
        """إنشاء لعبة خمن الصورة"""
        await interaction.response.defer()
        
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        event = self.db.create_event(
            title="خمن الصورة",
            description=correct_answer,
            event_type='image_guess',
            creator_id=interaction.user.id,
            data={'image_url': image_url, 'answer': correct_answer, 'guesses': {}}
        )
        
        embed = discord.Embed(
            title=f"{EMOJIS['image']} خمن الصورة",
            description="ما الشيء في هذه الصورة؟",
            color=COLORS['primary']
        )
        embed.set_image(url=image_url)
        embed.add_field(name="الوقت", value="غير محدود", inline=True)
        embed.set_footer(text=f"معرّف الفعالية: {event.event_id}")
        
        msg = await interaction.followup.send(embed=embed)
        
        # إضافة تفاعلات
        await msg.add_reaction('✍️')  # للرد
        
        await interaction.followup.send(
            f"{EMOJIS['success']} تم إنشاء اللعبة! اضغط ✍️ ثم رد بالإجابة",
            ephemeral=True
        )
    
    @app_commands.command(name="typing_race", description="سباق الكتابة السريعة")
    @app_commands.describe(
        text="النص المطلوب كتابته",
        time_limit="حد زمني بالثواني"
    )
    async def typing_race(self, interaction: discord.Interaction, text: str, time_limit: int = 30):
        """إنشاء سباق كتابة"""
        await interaction.response.defer()
        
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        event = self.db.create_event(
            title="سباق الكتابة",
            description=text,
            event_type='typing_race',
            creator_id=interaction.user.id,
            data={'text': text, 'time_limit': time_limit, 'results': {}}
        )
        
        embed = discord.Embed(
            title=f"{EMOJIS['lightning']} سباق الكتابة السريعة",
            description=f"``{text}``",
            color=COLORS['warning'],
            timestamp=None
        )
        embed.add_field(name="الحد الزمني", value=f"{time_limit} ثانية", inline=True)
        embed.add_field(name="المشاركون", value="0", inline=True)
        embed.set_footer(text=f"معرّف الفعالية: {event.event_id}")
        
        view = TypingRaceView(self.db, event.event_id, text, time_limit)
        await interaction.followup.send(embed=embed, view=view)
        
        await interaction.followup.send(
            f"{EMOJIS['success']} تم إنشاء سباق الكتابة!",
            ephemeral=True
        )
    
    @app_commands.command(name="button_challenge", description="تحدي الأزرار")
    @app_commands.describe(
        title="عنوان التحدي",
        instruction="التعليمات"
    )
    async def button_challenge(self, interaction: discord.Interaction, title: str, instruction: str):
        """إنشاء تحدي بالأزرار"""
        await interaction.response.defer()
        
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        event = self.db.create_event(
            title=title,
            description=instruction,
            event_type='button_challenge',
            creator_id=interaction.user.id,
            data={'sequence': [], 'participants': {}}
        )
        
        # إنشاء تسلسل عشوائي
        sequence = [random.randint(0, 3) for _ in range(5)]
        event.data['sequence'] = sequence
        
        embed = discord.Embed(
            title=f"{EMOJIS['game']} {title}",
            description=instruction,
            color=COLORS['primary']
        )
        embed.add_field(name="الصعوبة", value="🟢 سهلة", inline=True)
        embed.set_footer(text=f"معرّف الفعالية: {event.event_id}")
        
        view = ButtonChallengeView(self.db, event.event_id, sequence)
        await interaction.followup.send(embed=embed, view=view)
        
        await interaction.followup.send(
            f"{EMOJIS['success']} تم إنشاء تحدي الأزرار!",
            ephemeral=True
        )


class TypingRaceView(discord.ui.View):
    """عرض سباق الكتابة"""
    
    def __init__(self, db: Database, event_id: int, text: str, time_limit: int):
        super().__init__(timeout=time_limit)
        self.db = db
        self.event_id = event_id
        self.text = text
        self.time_limit = time_limit
        self.results = {}
    
    @discord.ui.button(label="ابدأ!", emoji=EMOJIS['lightning'], style=discord.ButtonStyle.success)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """زر البداية"""
        await interaction.response.send_modal(TypingRaceModal(self.db, self.event_id, self.text))


class TypingRaceModal(discord.ui.Modal):
    """نافذة لعبة الكتابة"""
    
    def __init__(self, db: Database, event_id: int, correct_text: str):
        super().__init__(title="اكتب النص")
        self.db = db
        self.event_id = event_id
        self.correct_text = correct_text
        
        self.text_input = discord.ui.TextInput(
            label="النص",
            placeholder="اكتب النص هنا",
            required=True
        )
        self.add_item(self.text_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """معالجة الإجابة"""
        user_text = self.text_input.value
        is_correct = user_text.lower().strip() == self.correct_text.lower().strip()
        
        self.db.add_user_stats(interaction.user.id, interaction.user.name)
        
        if is_correct:
            self.db.update_user_points(interaction.user.id, EVENT_CONFIG['points_per_win'])
            embed = discord.Embed(
                title=f"{EMOJIS['success']} صحيح!",
                description=f"حصلت على {EVENT_CONFIG['points_per_win']} نقطة!",
                color=COLORS['success']
            )
        else:
            embed = discord.Embed(
                title=f"{EMOJIS['error']} خاطئ",
                description=f"النص الصحيح: `{self.correct_text}`",
                color=COLORS['error']
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ButtonChallengeView(discord.ui.View):
    """عرض تحدي الأزرار"""
    
    def __init__(self, db: Database, event_id: int, sequence: list):
        super().__init__(timeout=None)
        self.db = db
        self.event_id = event_id
        self.sequence = sequence
        self.user_sequence = {}
        
        # إضافة 4 أزرار
        colors = [discord.ButtonStyle.red, discord.ButtonStyle.green, discord.ButtonStyle.blue, discord.ButtonStyle.primary]
        for i in range(4):
            self.add_item(discord.ui.Button(
                label=str(i+1),
                custom_id=f"btn_{event_id}_{i}",
                style=colors[i]
            ))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.custom_id.startswith(f"btn_{self.event_id}_"):
            return False
        
        button_index = int(interaction.custom_id.split('_')[-1])
        user_id = interaction.user.id
        
        if user_id not in self.user_sequence:
            self.user_sequence[user_id] = []
        
        self.user_sequence[user_id].append(button_index)
        
        if len(self.user_sequence[user_id]) <= len(self.sequence):
            if self.user_sequence[user_id][-1] == self.sequence[len(self.user_sequence[user_id]) - 1]:
                if len(self.user_sequence[user_id]) == len(self.sequence):
                    self.db.add_user_stats(user_id, interaction.user.name)
                    self.db.update_user_points(user_id, EVENT_CONFIG['points_per_win'])
                    await interaction.response.send_message(
                        f"{EMOJIS['success']} أكملت التسلسل بنجاح! حصلت على {EVENT_CONFIG['points_per_win']} نقطة!",
                        ephemeral=True
                    )
                else:
                    await interaction.response.defer()
            else:
                await interaction.response.send_message(
                    f"{EMOJIS['error']} خطأ! الزر الصحيح كان رقم {self.sequence[len(self.user_sequence[user_id]) - 1] + 1}",
                    ephemeral=True
                )
                self.user_sequence[user_id] = []
        
        return True


async def setup(bot: commands.Bot):
    await bot.add_cog(GamesCog(bot))
