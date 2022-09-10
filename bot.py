import logging
import os
import traceback

import discord
import replicate
from dotenv import load_dotenv

logging.basicConfig()
logger = logging.getLogger(__name__)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

embed_color = discord.Colour.from_rgb(200, 200, 100)
bot = discord.Bot()


@bot.slash_command(description="Show a picture that represents the prompt")
async def show(ctx, prompt: str):
    logger.info(f"asked to show: {prompt}")
    await ctx.defer()
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

bot.run(token)
