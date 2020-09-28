import discord
from database import Database
from discord.ext import commands
from discord.ext import tasks
from network import Network

bot = commands.Bot(command_prefix='$')


# SEND IMAGE FUNCTION
@tasks.loop(minutes=10)
async def send_image():
    image_url = "http://centennialbulb.org/oldbulb/ctbulb.jpg"
    filename = image_url.split("/")[-1]
    db = Database()
    net = Network(image_url)

    if net.r_get.status_code == 200:
        net.download_image(filename)
        channels = db.get_channels()
        for channel_id in channels:
            channel = bot.get_channel(int(channel_id[0]))
            await channel.send(file=discord.File(filename))
            await channel.send('Remember to check out the Centennial Bulb\'s official website here: '
                               '<https://centennialbulb.org>\n'
                               '------------------------------------------------------------------------------------------------------------')

    db.close()


# EVENTS
@bot.event
async def on_ready():
    send_image.start()
    print('Logged in as', bot.user)


@bot.event
async def on_guild_remove(guild):
    db = Database()
    db.remove_server(guild.id)


# COMMANDS
@bot.command()
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def bulbchannel(ctx):
    channel = ctx.channel
    guild = ctx.guild
    channel_id = channel.id
    guild_id = guild.id

    sending = await channel.send('Asssigning channel...')
    db = Database()

    rows = db.update_channel(guild_id, channel_id)
    db.close()
    if rows == 0:
        await sending.edit(content='That is already the assigned Bulbwatch channel for this server!')
    elif rows == 1:
        await sending.edit(content='Added <#{}> as this server\'s Bulbwatch channel!'.format(channel_id))
    elif rows == 2:
        await sending.edit(content='<#{}> is the new Bulbwatch channel for this server!'.format(channel_id))


@bot.command()
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def invite(ctx):
    await ctx.channel.send('Use this link to invite me to other servers: <{}>'
                           .format(discord.utils.oauth_url("758570848990527499")))


@bot.command()
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def removechannel(ctx):
    channel = ctx.channel
    channel_id = channel.id

    db = Database()
    db.remove_channel(channel_id)
    db.close()

    await channel.send('<#{}> removed from the send list!'.format(channel_id))


# ERRORS
@bulbchannel.error
@invite.error
@removechannel.error
async def forbidden_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, discord.errors.Forbidden):
        dm = await ctx.author.create_dm()
        await dm.send('I cannot send messages in the #{} channel on {}!'.format(ctx.channel.name, ctx.guild.name))


cred = open("cred.txt", "r").readline()
bot.run(cred)
