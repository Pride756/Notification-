import os
import discord
from discord.ext import commands, tasks
import datetime

# ================= การตั้งค่า =================
TOKEN = os.getenv('DISCORD_TOKEN')          # ดึง Token จาก Railway
WATCH_CHANNEL_ID = 1556023754449092669      # ช่องที่จับเวลา (หากไม่มีข้อความเข้าเกิน 10 นาที)
ALERT_CHANNEL_ID = 1572222518943686747      # ช่องปลายทางที่จะให้ส่งแจ้งเตือน
TARGET_USER_ID = 000000000000000000         # ใส่ User ID ของ resolute._.p (ถ้ามี)
TARGET_USERNAME = 'resolute._.p'            # ชื่อผู้ใช้สำหรับแท็ก
TIMEOUT_MINUTES = 10                        # ระยะเวลาที่กำหนด (นาที)
# ===========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_message_time = None
has_notified = False

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
    
    try:
        synced = await bot.tree.sync()
        print(f'ซิงค์คำสั่ง Slash Command สำเร็จ {len(synced)} คำสั่ง')
    except Exception as e:
        print(f'ซิงค์คำสั่งไม่สำเร็จ: {e}')

    last_message_time = datetime.datetime.now(datetime.timezone.utc)
    if not check_inactivity.is_running():
        check_inactivity.start()

# คำสั่ง /test สำหรับกดทดสอบส่งไปที่ช่อง 1572222518943686747 ทันที
@bot.tree.command(name="test", description="ทดสอบส่งข้อความแจ้งเตือนไปยังช่องปลายทาง")
async def test_alert(interaction: discord.Interaction):
    alert_channel = bot.get_channel(ALERT_CHANNEL_ID)
    if alert_channel:
        mention_text = get_mention_text(alert_channel.guild)
        await alert_channel.send(
            f"🧪 **[ข้อความทดสอบ]**\n{mention_text} เข้าcloud phoneมาเช็คหน่อยหลุดรึป่าว"
        )
        await interaction.response.send_message(f"✅ ส่งข้อความทดสอบไปที่ช่อง <#{ALERT_CHANNEL_ID}> เรียบร้อยแล้ว!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ ไม่พบช่องแจ้งเตือน (ID: `{ALERT_CHANNEL_ID}`) กรุณาเช็กสิทธิ์ของบอทในช่องนั้น", ephemeral=True)

@bot.event
async def on_message(message):
    global last_message_time, has_notified
    if message.author == bot.user:
        return

    # นับเวลาใหม่ทุกครั้งที่มีข้อความเข้าในช่อง 1556023754449092669
    if message.channel.id == WATCH_CHANNEL_ID:
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

    # หากครบ 10 นาทีและยังไม่เคยแจ้งเตือน ให้ส่งไปที่ช่อง 1572222518943686747
    if elapsed >= datetime.timedelta(minutes=TIMEOUT_MINUTES) and not has_notified:
        alert_channel = bot.get_channel(ALERT_CHANNEL_ID)
        if alert_channel:
            mention_text = get_mention_text(alert_channel.guild)
            await alert_channel.send(
                f"{mention_text} เข้าcloud phoneมาเช็คหน่อยหลุดรึป่าว"
            )
            has_notified = True

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: ไม่พบ DISCORD_TOKEN ใน Variables")
