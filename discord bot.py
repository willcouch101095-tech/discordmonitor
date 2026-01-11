import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

MAIN_VOICE_CHANNEL_ID = 1008241694912811090
MUTED_VOICE_CHANNEL_ID = 1044391550811127818
MONITOR_TIME = 10  # seconds

# Tracks users currently in the 10-second window
monitoring_users = set()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Ignore bots
    if member.bot:
        return

    # User joins main voice channel
    if (
        after.channel
        and after.channel.id == MAIN_VOICE_CHANNEL_ID
        and before.channel != after.channel
    ):
        monitoring_users.add(member.id)

        async def stop_monitoring():
            await asyncio.sleep(MONITOR_TIME)
            monitoring_users.discard(member.id)

        bot.loop.create_task(stop_monitoring())
        return

    # If user is being monitored and mutes → move immediately
    if (
        member.id in monitoring_users
        and after.channel
        and after.channel.id == MAIN_VOICE_CHANNEL_ID
        and not before.self_mute
        and after.self_mute
    ):
        muted_channel = member.guild.get_channel(MUTED_VOICE_CHANNEL_ID)
        if muted_channel:
            await member.move_to(muted_channel)

        monitoring_users.discard(member.id)
