import discord
from discord.ext import commands
import sqlite3, random
from datetime import datetime
from cryptography.fernet import Fernet
import config

PLATFORMS = [
    "fortnite", "amongus", "totalbattle", "steam", "epicgames",
    "microsoft", "ubisoft", "eaplay", "origin", "genshin", "apex"
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

db = sqlite3.connect("cuentas.db", check_same_thread=False)
cursor = db.cursor()
fernet = Fernet(config.CLAVE_CIFRADO)

def es_admin(ctx):
    return any(r.name == config.ROL_PERMITIDO for r in ctx.author.roles)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Slash commands listos")
    
# ================= ADMIN =================

@bot.command()
async def add(ctx, platform, username, password):
    if not es_admin(ctx):
        return await ctx.send("No tienes permisos.")

    platform = platform.lower()
    if platform not in PLATFORMS:
        return await ctx.send("Plataforma no permitida.")

    pwd = fernet.encrypt(password.encode()).decode()
    cursor.execute(
        "INSERT INTO accounts (platform, username, password) VALUES (?, ?, ?)",
        (platform, username, pwd)
    )
    db.commit()
    await ctx.send(f"Cuenta agregada a **{platform}**.")

@bot.command()
async def limpiar(ctx):
    if not es_admin(ctx):
        return
    cursor.execute("DELETE FROM accounts WHERE used = 1")
    db.commit()
    await ctx.send("Cuentas usadas eliminadas.")

# ================= USUARIOS =================

@bot.command()
async def stock(ctx):
    cursor.execute("""
    SELECT platform, COUNT(*) FROM accounts
    WHERE used = 0 GROUP BY platform
    """)
    rows = cursor.fetchall()

    if not rows:
        return await ctx.send("No hay stock.")

    msg = "📦 **STOCK DISPONIBLE**\n"
    for p, c in rows:
        msg += f"• {p}: {c}\n"

    await ctx.send(msg)

@bot.command()
async def cuenta(ctx, platform):
    platform = platform.lower()
    if platform not in PLATFORMS:
        return await ctx.send("Plataforma inválida.")

    cursor.execute("""
    SELECT id, username, password FROM accounts
    WHERE platform = ? AND used = 0 LIMIT 1
    """, (platform,))
    acc = cursor.fetchone()

    if not acc:
        return await ctx.send("No hay cuentas disponibles.")

    acc_id, user, pwd = acc
    pwd = fernet.decrypt(pwd.encode()).decode()

    cursor.execute("UPDATE accounts SET used = 1 WHERE id = ?", (acc_id,))
    cursor.execute(
        "INSERT INTO logs (user_id, platform, date) VALUES (?, ?, ?)",
        (ctx.author.id, platform, datetime.now().isoformat())
    )
    db.commit()

    try:
        await ctx.author.send(
            f"🎮 **Cuenta {platform.upper()}**\n"
            f"Usuario: `{user}`\n"
            f"Contraseña: `{pwd}`"
        )
        await ctx.send("Cuenta enviada por DM.")
    except:
        await ctx.send("Tienes los DMs cerrados.")

# ================= JUEGOS =================

@bot.command()
async def coin(ctx):
    await ctx.send(random.choice(["Cara", "Cruz"]))

@bot.command()
async def dice(ctx):
    await ctx.send(f"🎲 Salió: {random.randint(1,6)}")

@bot.command()
async def ball(ctx):
    respuestas = [
        "Sí", "No", "Tal vez", "Definitivamente",
        "No lo creo", "Pregunta luego"
    ]
    await ctx.send(random.choice(respuestas))

@bot.command()
async def rps(ctx, choice):
    opciones = ["piedra", "papel", "tijera"]
    bot_choice = random.choice(opciones)
    await ctx.send(f"Tú: {choice} | Bot: {bot_choice}")

@bot.command()
async def love(ctx, member: discord.Member):
    porcentaje = random.randint(0,100)
    await ctx.send(f"💖 Compatibilidad: {porcentaje}%")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong: {round(bot.latency*1000)}ms")

bot.run(config.TOKEN)
