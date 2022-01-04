import discord
from discord.ext import commands
import os
import logging
from discord.ext.commands.errors import BadArgument
from dotenv import load_dotenv
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
intents = discord.Intents().default()

db_client = MongoClient('localhost',27017)
db = db_client["discord_frog_db"]

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)


### EVENTS
@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has conneced to Discord!')

# @bot.event
# async def on_guild_join(guild):
#     for channel in guild.text_channels:
#         if channel.permissions_for(guild.me).send_messages:
#             await channel.send("Hello!")
#         break

### COMMANDS
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! **{round(bot.latency, 3)}ms**.')

@bot.command()
async def add(ctx, *args):
    if (len(args) < 1):
        await ctx.send("Please enter a name for your image/video.")
        return
    elif (len(ctx.message.attachments) <1):
        await ctx.send("Please attach some photo or video.")
        return
    url = ctx.message.attachments[0].proxy_url
    coll = db[str(ctx.guild.id)]
    coll.update_one({"_id" : args[0]}, {"$set" : {"url" : url}}, upsert=True)
    await ctx.send("Got it.")

@bot.command()
async def m(ctx, *args):
    if (len(args) < 1):
        await ctx.send("Please enter a name for your image/video.")
        return
    coll = db[str(ctx.guild.id)]
    url = coll.find_one({"_id" : args[0]})
    if (url is None):
        await ctx.send("I couldn't find that...")
        return
    await ctx.send(url.get("url"))

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="⭐️ Frog help ⭐️", description="______", color=0x3498db)
    embed.add_field(name="⏺ .add [name]", value="If a photo/video has been attached, will save under the given name.", inline=False)
    embed.add_field(name="⏪ .m [name]", value="Send the photo/video matching the name given.", inline=False)
    embed.add_field(name="🏓 Ping", value="Pong!")
    embed.add_field(name="______", value="https://github.com/wesleynw/frog", inline=False)
    await ctx.send(embed=embed)


load_dotenv()
token = os.environ.get('FROG_DISCORD_TOKEN')
bot.run(token)