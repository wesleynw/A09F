import discord
import os, logging, asyncio
from math import ceil
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
intents = discord.Intents().default()

db_client = MongoClient('localhost',27017)
db = db_client["discord_A09F_db"]
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)


### EVENTS
@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} has conneced to Discord!')


### COMMANDS
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! **{round(bot.latency * 1000)}ms**.')

@bot.command()
async def m(ctx, *args):
    coll = db[str(ctx.guild.id)]
    l = len(args)
    if l == 0:
        if coll.count_documents({}) < 1: 
            await ctx.send("you haven't saved anything yet")
        else:
            all = list(coll.find({}))
            all = [x.get("_id") for x in all]
            all.sort()
            embed = discord.Embed(title='🗣 all commands', color=0x3498db)
            embed.set_footer(text='page 1')
            msg = await ctx.send(embed=embed)
            await embed_pagination(ctx.author, msg, embed, all, 1)
    elif args[0] == 'add':
        if l == 1:
            await ctx.send("you have to enter a name for your photo or video")
        elif len(ctx.message.attachments) < 1:
            await ctx.send("you have to attach some photo or video")
        else:
            prev_url = coll.find_one({'_id' : args[1]})
            if prev_url is not None:
                msg = await ctx.send("there's already something with that name, do you want to overwrite it?")
                await msg.add_reaction('✅')
                await msg.add_reaction('❌')
                def check(reaction, user):
                    r = str(reaction.emoji)
                    return user == ctx.author and (r == '✅' or r == '❌')
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return
                else:
                    r = str(reaction.emoji)
                    if r == '❌':
                        await msg.delete()
                        return
            url = ctx.message.attachments[0].proxy_url
            coll.update_one({'_id' : args[1]}, {'$set' : {'url' : url}}, upsert=True)
            await ctx.send('got it')
    else:
        url = coll.find_one({"_id" : args[0]})
        if (url is None):
            await ctx.send("I couldn't find that...")
            return
        await ctx.send(url.get("url"))

@bot.command()
async def q(ctx, *args):
    coll = db[str(ctx.guild.id)]
    if len(args) == 0:
        quotes = coll.find_one({"_id" : "quotes"}).get("arr")
        quotes = [str((await bot.fetch_user(x[0])).name) + ' said "' + str(x[1]) + '"' for x in quotes]

        embed = discord.Embed(title='quotes', color=0x3498db)
        embed.set_footer(text='page 1')
        msg = await ctx.send(embed=embed)
        await embed_pagination(ctx.author, msg, embed, quotes, 1)


    elif len(args) == 1 and args[0] == "add":
        if ctx.message.reference is not None:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            async for m_hist in ctx.channel.history(before=ctx.message.created_at):
                if m_hist.content is not None:
                    msg = m_hist
                    break; 
        coll.update_one({'_id' : 'quotes'}, {'$push' : {'arr' : [msg.author.id, msg.content]}}, upsert=True)
        await ctx.send("quoted!")

    
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="⭐️ A09F help ⭐️", description="______", color=0x3498db)
    embed.add_field(name="⏺ .m add [name]", value="add the given photo or video to the bot's library", inline=False)
    embed.add_field(name="⏪ .m [name]", value="send the photo or video with the given name", inline=False)
    embed.add_field(name="🔡 .m", value="show a list of all photos and videos")
    embed.add_field(name="✍️ .q add", value="quote the above message, or a message that is replied to", inline=False)
    embed.add_field(name="📝 .q", value="show a list of all quotes", inline=False)
    embed.add_field(name="🏓 ping", value="pong!", inline=False)
    embed.set_footer(text="https://github.com/wesleynw/A09F")
    await ctx.send(embed=embed)


### HELPERS
async def embed_pagination(author, msg : discord.Message, embed : discord.Embed, pages : list, page : int):
    embed.clear_fields()
    page_size = 10
    for i in range((page - 1) * page_size, min(len(pages), page - 1 + page_size)):
        embed.add_field(name=pages[i], value='\u200b', inline=False);

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
        r = str(reaction.emoji)
        if r == "⬅️":
            page -= 1
        elif r == "➡️":
            page += 1
        await reaction.clear()
        await embed_pagination(author, msg, embed, pages, page)


### RUN
load_dotenv()
token = os.environ.get('A09F_DISCORD_TOKEN')
bot.run(token)
