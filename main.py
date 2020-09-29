import discord
import re
from database import Database
from discord.ext import commands
from discord.ext import tasks
from network import Network


class HelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'help': 'Shows the various commands, their usages, and other specifics',
            'cooldown': commands.Cooldown(1, 5.0, commands.BucketType.member)
        })

    async def send_pages(self):
        destination = self.get_destination()
        title = 'Bulbwatch Discord Bot Commands'
        desc = 'A comprehensive list of all of the Bulbwatch Discord Bot\'s commands (commands tagged with + are only for' \
               ' those who have "Manage Server" permissions)'
        color = 0xFFC67A

        footer = 'Bulbwatch - Centennial Bulb Watchman made by Elereth'
        author_url = 'https://www.github.com/CPLShiv/'

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text=footer).set_author(name='Elereth', url=author_url)
        embed.add_field(name='$currentchannel, $current, $subbed (+)', value='Lists the channel currently set as this'
                                                                             ' server\'s Bulbwatch channel (specifies if'
                                                                             ' there is not one set)', inline=False)
        embed.add_field(name='$help', value='Shows this command!', inline=False)
        embed.add_field(name='$info', value='Shows information about the Bulbwatch Discord Bot, as well as information'
                                            ' about the creator.', inline=False)
        embed.add_field(name='$invite',
                        value='Gives the bot\'s invite URL to share with others so the bot can be in more'
                              ' servers!', inline=False)
        embed.add_field(name='$subscribe, $sub (+)', value='Allows those with appropriate privileges to add either the'
                                                           ' current channel or a specified channel as this server\'s '
                                                           ' Bulbwatch channel. Providing no arguments will specify the'
                                                           ' current channel, otherwise provide a channel tag i.e.'
                                                           ' `$subscribe #channelname` or `$sub #channelname`',
                        inline=False)
        embed.add_field(name='$unsubscribe, $unsub (+)', value='Allows those with appropriate privileges to remove this'
                                                               ' server from the subscription list. Does not take a channel'
                                                               ' tag as $subscribe does, as it automatically removes the'
                                                               ' server itself from the subscription list.',
                        inline=False)

        await destination.send(embed=embed)


bot = commands.Bot(command_prefix='$')
bot.help_command = HelpCommand()


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
@bot.command(aliases=['current', 'subbed'])
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def currentchannel(ctx):
    channel = ctx.channel
    db = Database()

    channel_id = db.get_channel(ctx.guild.id)

    if channel_id is None:
        await channel.send('There is currently no Bulbwatch channel assigned for this server!')
    else:
        await channel.send('The current Bulbwatch channel for this server is <#{}>!'.format(channel_id[0]))


#@bot.command()
#@commands.guild_only()
#async def help(ctx):
#    title = 'Bulbwatch Discord Bot Commands'
#    desc = 'A comprehensive list of all of the Bulbwatch Discord Bot\'s commands (commands tagged with + are only for' \
#           ' those who have "Manage Server" permissions)'
#    color = 0xFFC67A
#
#    footer = 'Bulbwatch - Centennial Bulb Watchman made by Elereth'
#    author_url = 'https://www.github.com/CPLShiv/'
#
#    embed = discord.Embed(title=title, description=desc, color=color)
#    embed.set_footer(text=footer).set_author(name='Elereth', url=author_url)
#    embed.add_field(name='$currentchannel, $current, $subbed (+)', value='Lists the channel currently set as this'
#                                                                         ' server\'s Bulbwatch channel (specifies if'
#                                                                         ' there is not one set)', inline=False)
#    embed.add_field(name='$help', value='Shows this command!', inline=False)
#    embed.add_field(name='$info', value='Shows information about the Bulbwatch Discord Bot, as well as information'
#                                        ' about the creator.', inline=False)
#    embed.add_field(name='$invite', value='Gives the bot\'s invite URL to share with others so the bot can be in more'
#                                          ' servers!', inline=False)
#    embed.add_field(name='$subscribe, $sub (+)', value='Allows those with appropriate privileges to add either the'
#                                                       ' current channel or a specified channel as this server\'s '
#                                                       ' Bulbwatch channel. Providing no arguments will specify the'
#                                                       ' current channel, otherwise provide a channel tag i.e.'
#                                                       ' `$subscribe #channelname` or `$sub $channelname`',
#                                                        inline=False)
#    embed.add_field(name='$unsubscribe, $unsub (+)', value='Allows those with appropriate privileges to remove this'
#                                                           ' server from the subscription list. Does not take a channel'
#                                                           ' tag as $subscribe does, as it automatically removes the'
#                                                           ' server itself from the subscription list.', inline=False)
#    await ctx.channel.send(embed=embed)


@bot.command()
@commands.guild_only()
async def info(ctx):
    title = 'Bulbwatch Discord Bot'
    desc = 'Information about the Bulbwatch Discord Bot and its creator'
    color = 0xFFC67A

    footer = 'Bulbwatch - Centennial Bulb Watchman made by Elereth'
    author_url = 'https://www.github.com/CPLShiv/'

    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text=footer).set_author(name='Elereth', url=author_url)
    embed.add_field(name='Bulbwatch Bot', value='The Bulbwatch Discord bot was created with the intention of spreading'
                                                ' the word of older technology and show what the human race has been'
                                                ' able to accomplish. The ability to invite the bot to other servers'
                                                ' allows this amazing concept to flood between servers with ease, and'
                                                ' continue to provide people with a somewhat-live feed of the'
                                                ' Centennial Bulb.', inline=False)
    embed.add_field(name='Elereth, the Bot\'s Creator', value='Elereth, the creator of the Bulbwatch Discord bot, is an'
                                                ' avid programmer, college student, and volunteer firefighter. He takes'
                                                ' great pride in his programming projects, Bulbwatch being one of the'
                                                ' greatest. Want him to code a Discord bot for you? Check out the'
                                                ' contact information below!', inline=False)
    embed.add_field(name='Elereth Contact Information', value='Discord: Elereth#4300\n'
                                                        'E-Mail: caleb.g2001@gmail.com\n'
                                                        'Fiverr: https://fiverr.com/caleb_garcia\n'
                                                        'LinkedIn: https://www.linkedin.com/in/caleb-garcia-5226717a/',
                                                        inline=False)

    await ctx.channel.send(embed=embed)


@bot.command(aliases=['inv'])
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def invite(ctx):
    await ctx.channel.send('Use this link to invite me to other servers: <{}>'
                           .format(discord.utils.oauth_url("758570848990527499")))


@bot.command(aliases=['sub'])
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def subscribe(ctx, channel=None):
    guild = ctx.guild
    guild_id = guild.id

    if channel is None:
        ch = ctx.channel
        ch_id = ch.id
        db = Database()
        sending = await ch.send('Asssigning channel...')
        rows = db.update_channel(guild_id, ch_id)
        db.close()

        if rows == 0:
            await sending.edit(content='This is already this server\'s Bulbwatch channel!')
        elif rows == 1:
            await sending.edit(content='Added this channel (<#{}>) as this server\'s Bulbwatch channel!'.format(ch_id))
        elif rows == 2:
            await sending.edit(content='<#{}> is the new Bulbwatch channel for this server!'.format(ch_id))
    else:
        channel_id = int(''.join(re.findall("\d*", channel)))
        db = Database()
        sending = await ctx.channel.send('Asssigning channel...')
        rows = db.update_channel(guild_id, channel_id)
        db.close()

        if rows == 0:
            await sending.edit(content='That is already this server\'s Bulbwatch channel!')
        elif rows == 1:
            await sending.edit(content='Added <#{}> as this server\'s Bulbwatch channel!'.format(channel_id))
        elif rows == 2:
            await sending.edit(content='<#{}> is the new Bulbwatch channel for this server!')


@bot.command(aliases=['unsub'])
@commands.guild_only()
@commands.has_guild_permissions(manage_guild=True)
async def unsubscribe(ctx):
    guild_id = ctx.guild.id
    channel = ctx.channel

    db = Database()
    rows = db.unsubscribe(guild_id)
    db.close()

    if rows == 0:
        await channel.send('I couldn\'t unsubscribe this server because it\'s not subscribed!')
    elif rows == 1:
        await channel.send('This server is no longer subscribed to the Bulbwatch!')


# ERRORS
@invite.error
@subscribe.error
@unsubscribe.error
async def forbidden_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, discord.errors.Forbidden):
        dm = await ctx.author.create_dm()
        await dm.send('I cannot send messages in the #{} channel on {}!'.format(ctx.channel.name, ctx.guild.name))


cred = open("cred.txt", "r").readline()
bot.run(cred)
