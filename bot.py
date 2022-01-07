import discord
from discord.ext import commands
import os, asyncio
from math import ceil
import logging
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
    coll = db[str(ctx.guild.id)]
    if (len(args) < 1):
        if coll.count_documents({}) < 1: 
            await ctx.send("you haven't saved anything yet")
            return
        all_commands = list(coll.find({}))

        embed = discord.Embed(title='🗣 all commands', color=0x3498db)
        embed.set_footer(text='page 1')
        msg = await ctx.send(embed=embed)
        await embed_pagination(ctx.author, msg, embed, all_commands, 1)
    else:
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


### HELPERS
async def embed_pagination(author, msg : discord.Message, embed : discord.Embed, pages : list, page : int):
    embed.clear_fields()
    page_size = 5
    for i in range((page - 1) * page_size, min(len(pages), page - 1 + page_size)):
        embed.add_field(name=pages[i].get('_id'), value='\u200b', inline=False);

    # n_pages = max(1, len(pages) // page_size)
    n_pages = int(ceil(len(pages) / page_size))
    embed.set_footer(text=f'page {page} of {n_pages}')
    await msg.edit(embed=embed)
    if page > 1:
        await msg.add_reaction("⬅️")
    elif len(pages) > page_size:
        await msg.add_reaction("➡️")

    def check(reaction, user):
        r = str(reaction.emoji)
        return user == author and (r == "➡️" or r == "⬅️")

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        return
    else:
        print(reaction)
        r = str(reaction.emoji)
        if r == "⬅️":
            page -= 1
        elif r == "➡️":
            page += 1
        await reaction.clear()
        await embed_pagination(author, msg, embed, pages, page)

load_dotenv()
token = os.environ.get('FROG_DISCORD_TOKEN')
bot.run(token)