import asyncio
import logging
import os
import traceback

import discord
import replicate
from discord.ext import commands, tasks
from dotenv import load_dotenv

logging.basicConfig()
logger = logging.getLogger(__name__)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

embed_color = discord.Colour.from_rgb(200, 200, 100)
bot = discord.Bot()

queue = asyncio.Queue()


@tasks.loop(seconds=1.0)
async def runner():
    task = await queue.get()
    await task
    queue.task_done()


@runner.before_loop
async def before():
    await bot.wait_until_ready()


async def make_image(ctx, prompt):
    await asyncio.sleep(1.0)
    print(f"make_image with prompt: {prompt}")
    embed = discord.Embed()
    embed.color = embed_color
    embed.set_footer(text=prompt)
    try:
        model = replicate.models.get("stability-ai/stable-diffusion")
        image_url = model.predict(prompt=prompt)[0]
        embed.set_image(url=image_url)
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title='show failed', description=f'{e}\n{traceback.print_exc()}', color=embed_color)
        await ctx.followup.send(embed=embed)


@bot.slash_command(description="Show a picture that represents the prompt")
async def picture(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to picture: {prompt}")
    queue.put_nowait(make_image(ctx, prompt))

runner.start()
bot.run(token)
