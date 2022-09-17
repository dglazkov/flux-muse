import asyncio
import logging
import os
import traceback

import discord
import openai
import replicate
from discord.ext import tasks
from dotenv import load_dotenv

logging.basicConfig()
logger = logging.getLogger(__name__)

load_dotenv()
discord_api_token = os.getenv("DISCORD_API_TOKEN")
openai.api_key = os.getenv("OPENAI_API_TOKEN")

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
            title="show failed", description=f"{e}\n{traceback.print_exc()}", color=embed_color)
        await ctx.followup.send(embed=embed)


@bot.slash_command(description="Show a picture that represents the prompt")
async def picture(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to picture: {prompt}")
    queue.put_nowait(make_image(ctx, prompt))


async def make_story(ctx, prompt):
    await asyncio.sleep(1.0)
    print(f"make_story with prompt: {prompt}")
    embed = discord.Embed()
    embed.color = embed_color
    embed.title = prompt
    try:
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        embed.description = response.choices[0].text
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="show failed", description=f"{e}\n{traceback.print_exc()}", color=embed_color)
        await ctx.followup.send(embed=embed)


@bot.slash_command(description="Tell me a story")
async def story(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to tell a story: {prompt}")
    queue.put_nowait(make_story(ctx, prompt))


async def make_chain(ctx, prompt):
    await asyncio.sleep(1.0)
    print(f"make_chain with prompt: {prompt}")
    embed = discord.Embed()
    embed.color = embed_color
    embed.title = prompt
    try:
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f"describe a picture of a {prompt}",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        embed.description = response.choices[0].text
        model = replicate.models.get("stability-ai/stable-diffusion")
        image_url = model.predict(prompt=prompt)[0]
        embed.set_image(url=image_url)
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="show failed", description=f"{e}\n{traceback.print_exc()}", color=embed_color)
        await ctx.followup.send(embed=embed)


@bot.slash_command(description="Tell me a story")
async def chain(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to chain: {prompt}")
    queue.put_nowait(make_chain(ctx, prompt))


runner.start()
bot.run(discord_api_token)
