import os
import discord
from discord.ext import commands, tasks
import datetime

# ================= การตั้งค่า =================
TOKEN = os.getenv('DISCORD_TOKEN')  # ดึง Token จาก Railway
CHANNEL_ID = 1556023754449092669    # ID ของช่องแชต
TARGET_USER_ID = 000000000000000000 # ใส่ User ID ของ resolute._.p (แนะนำ)
TARGET_USERNAME = 'resolute._.p'    # สำรองกรณีไม่ได้ใส่ User ID
TIMEOUT_MINUTES = 10                # ระยะเวลา (นาที)
# ===========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_message_time = None
has_notified = False

# ฟังก์ชันช่วยหาข้อความสำหรับแท็ก (ใช้ร่วมกันทั้งระบบจริงและคำสั่ง /test)
def get_mention_text(guild):
    if TARGET_USER_ID != 0:
        return f"<@{TARGET_USER_ID}>"
    if guild:
        member = discord.utils.get(guild.members, name=TARGET_USERNAME)
        if member:
            return member.mention
    return f"@{TARGET_USERNAME}"

@bot.event
async def on_ready():
    global last_message_time
    print(f'ล็อกอินสำเร็จในชื่อ: {bot.user}')
    
    # ซิงค์คำสั่ง Slash Command (/test) ให้ขึ้นใน Discord
    try:
        synced = await bot.tree.sync()
        print(f'ซิงค์คำสั่ง Slash Command สำเร็จ {len(synced)} คำสั่ง')
    except Exception as e:
        print(f'ซิงค์คำสั่งไม่สำเร็จ: {e}')

    last_message_time = datetime.datetime.now(datetime.timezone.utc)
    if not check_inactivity.is_running():
        check_inactivity.start()

# สร้างคำสั่ง /test
@bot.tree.command(name="test", description="ทดสอบข้อความแจ้งเตือนเมื่อไม่มีคนพิมพ์เกินเวลาที่กำหนด")
async def test_alert(interaction: discord.Interaction):
    mention_text = get_mention_text(interaction.guild)
    await interaction.response.send_message(
        f"🧪 **[ข้อความทดสอบ]**\n⏰ {mention_text} ไม่มีข้อความในช่องนี้เกิน {TIMEOUT_MINUTES} นาทีแล้ว!"
    )

@bot.event
async def on_message(message):
    global last_message_time, has_notified
    if message.author == bot.user:
        return

    if message.channel.id == CHANNEL_ID:
        last_message_time = datetime.datetime.now(datetime.timezone.utc)
        has_notified = False

    await bot.process_commands(message)

@tasks.loop(seconds=30)
async def check_inactivity():
    global last_message_time, has_notified
    if last_message_time is None:
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    elapsed = now - last_message_time

    if elapsed >= datetime.timedelta(minutes=TIMEOUT_MINUTES) and not has_notified:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            mention_text = get_mention_text(channel.guild)
            await channel.send(f"⏰ {mention_text} ไม่มีข้อความในช่องนี้เกิน {TIMEOUT_MINUTES} นาทีแล้ว!")
            has_notified = True

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: ไม่พบ DISCORD_TOKEN ใน Variables")
