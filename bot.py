import argparse
import os
import sys
import discord
from discord.ext import commands
import logging

logging.basicConfig()

logger = logging.getLogger(__name__)
token = sys.argv[1]

bot = discord.Bot()


@bot.slash_command()
async def show(ctx):
    await ctx.respond(f"I don't know how yet!")

bot.run(token)
