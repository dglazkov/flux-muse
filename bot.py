import os
from dotenv import load_dotenv
from torch import autocast
from diffusers import StableDiffusionPipeline
from io import BytesIO
import sys
import traceback
import discord
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = discord.Bot()

embed_color = discord.Colour.from_rgb(215, 195, 134)


def txt2img(prompt):
    # make sure you're logged in with `huggingface-cli login`

    pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4", use_auth_token=True)
    pipe = pipe.to("mps")

    # First-time "warmup" pass (see explanation above)
    _ = pipe(prompt, num_inference_steps=1)

    # Results match those from the CPU device after the warmup pass.
    image = pipe(prompt).images[0]

    return image


@bot.slash_command()
async def show(ctx, prompt: str):
    logger.info(f"asked to show: {prompt}")
    await ctx.defer()
    embed = discord.Embed()
    embed.color = embed_color
    embed.set_footer(text=prompt)
    try:
        image = txt2img(prompt)

        with BytesIO() as buffer:
            image.save(buffer, 'PNG')
            buffer.seek(0)
            await ctx.followup.send(embed=embed, file=discord.File(fp=buffer, filename=f'picture.png'))
    except Exception as e:
        embed = discord.Embed(
            title='show failed', description=f'{e}\n{traceback.print_exc()}', color=embed_color)
        await ctx.followup.send(embed=embed)

bot.run(token)
