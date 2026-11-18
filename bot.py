import os
import discord
from discord.ext import commands, tasks
import datetime

# ================= การตั้งค่า =================
TOKEN = os.getenv('DISCORD_TOKEN')  # ดึง Token จากตัวแปรใน Railway เพื่อความปลอดภัย
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

@bot.event
async def on_ready():
    global last_message_time
    print(f'ล็อกอินสำเร็จในชื่อ: {bot.user}')
    last_message_time = datetime.datetime.now(datetime.timezone.utc)
    if not check_inactivity.is_running():
        check_inactivity.start()

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
            mention_text = f"@{TARGET_USERNAME}"
            if TARGET_USER_ID != 0:
                mention_text = f"<@{TARGET_USER_ID}>"
            else:
                member = discord.utils.get(channel.guild.members, name=TARGET_USERNAME)
                if member:
                    mention_text = member.mention

            await channel.send(f"⏰ {mention_text} ไม่มีข้อความในช่องนี้เกิน {TIMEOUT_MINUTES} นาทีแล้ว!")
            has_notified = True

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: ไม่พบ DISCORD_TOKEN ใน Variables")
