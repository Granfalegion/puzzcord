""" Utility functions for getting information about discord channels, users, etc. """

import discord
import json

with open("configs/prod.json", "r") as f:
    PROD_CONFIG = json.load(f)

GUILD_ID = int(PROD_CONFIG["guild_id"])

VISITOR_ROLE = int(PROD_CONFIG["roles"]["visitor"])
HUNT_MEMBER_ROLE = int(PROD_CONFIG["roles"]["member"])
PUZZTECH_ROLE = int(PROD_CONFIG["roles"]["puzztech"])
PUZZBOSS_ROLE = int(PROD_CONFIG["roles"]["puzzboss"])
BETABOSS_ROLE = int(PROD_CONFIG["roles"]["betaboss"])

PUZZTECH_CHANNEL = int(PROD_CONFIG["channels"]["puzztech"])
STATUS_CHANNEL = int(PROD_CONFIG["channels"]["status"])
TABLE_REPORT_CHANNEL = int(PROD_CONFIG["channels"]["table_report"])


def get_team_members(guild):
    return guild.get_role(HUNT_MEMBER_ROLE).members


def is_puzzboss(member):
    return PUZZBOSS_ROLE in [role.id for role in member.roles]


def is_puzzle_channel(channel):
    if channel.type != discord.ChannelType.text:
        return False
    category = channel.category
    if not category:
        return False
    return category.name.startswith("🧩") or channel.category.name.startswith("🏁")


def get_table(member):
    voice = member.voice
    if not voice:
        return None
    channel = voice.channel
    if not channel:
        return None
    category = channel.category
    if not category:
        return None
    if "tables" not in category.name.lower():
        return None
    return channel


def get_tables(ctx):
    return [
        channel
        for channel in ctx.guild.voice_channels
        if "tables" in str(channel.category).lower()
    ]
