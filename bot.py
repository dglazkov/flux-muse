import asyncio
import logging
import os
import traceback

from polymath_client import ask_polymath

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


def format_polymath_embed(answer, sources):
    sources_label = "Here are some inks to explore" if answer == "I don't know." else "Sources"
    links = "\n".join([f" - [{title}]( {url} )" for url, title in sources[:4]])
    return f"{answer}\n\n{sources_label}:\n{links}"


async def make_wdl(ctx, prompt):
    await asyncio.sleep(1.0)
    print(f"make_wdl with prompt: {prompt}")
    embed = discord.Embed()
    embed.color = embed_color
    embed.title = prompt
    try:
        embed.description = format_polymath_embed(
            *ask_polymath(prompt, "https://polymath.glazkov.com"))
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="wdl failed", description=f"{e}\n{traceback.print_exc()}", color=embed_color)
        await ctx.followup.send(embed=embed)


@bot.slash_command(description="Ask What Dimitri Learned")
async def wdl(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to wdl: {prompt}")
    queue.put_nowait(make_wdl(ctx, prompt))


async def make_flux(ctx, prompt):
    await asyncio.sleep(1.0)
    print(f"make_flux with prompt: {prompt}")
    embed = discord.Embed()
    embed.color = embed_color
    embed.title = prompt
    try:
        embed.description = format_polymath_embed(
            *ask_polymath(prompt, "https://polymath.fluxcollective.org"))
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="flux failed", description=f"{e}\n{traceback.print_exc()}", color=embed_color)
        await ctx.followup.send(embed=embed)


@ bot.slash_command(description="Ask FLUX Review issue archives")
async def flux(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to flux: {prompt}")
    queue.put_nowait(make_flux(ctx, prompt))


async def make_alex(ctx, prompt):
    await asyncio.sleep(1.0)
    print(f"make_alex with prompt: {prompt}")
    embed = discord.Embed()
    embed.color = embed_color
    embed.title = prompt
    try:
        embed.description = format_polymath_embed(
            *ask_polymath(prompt, "https://polymath.komoroske.com"))
        await ctx.followup.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="alex failed", description=f"{e}\n{traceback.print_exc()}", color=embed_color)
        await ctx.followup.send(embed=embed)


@ bot.slash_command(description="Ask Alex's collective writings")
async def alex(ctx, prompt: str):
    await ctx.defer()
    print(f"asked to alex: {prompt}")
    queue.put_nowait(make_alex(ctx, prompt))


runner.start()
bot.run(discord_api_token)
