import discord
from database import Database
from discord.ext import tasks
from network import Network


class Client(discord.Client):
    async def on_ready(self):
        self.send_image.start()

        print('Logged in as', self.user)

    async def on_message(self, message):
        if message.content == '$bulbchannel':
            channel_id = message.channel.id
            try:
                sending = await message.channel.send('Assigning channel...')
                server = message.channel.guild
                db = Database()

                rows = db.update_channel(server, channel_id)
                db.close()
                if rows == 0:
                    await sending.edit(content='That is already the assigned Bulbwatch channel!')
                elif rows == 1:
                    await sending.edit(content='Added <#{}> as the Bulbwatch channel!'.format(channel_id))
                elif rows == 2:
                    await sending.edit(content='<#{}> is the new Bulbwatch channel!'.format(channel_id))
            except discord.errors.Forbidden:
                dm = await message.author.create_dm()
                await dm.send('Could not assign #{} in {} as the Bulbwatch channel: missing \'Send Messages\' '
                              'permission!'.format(message.channel.name, message.guild.name))

    @tasks.loop(minutes=10)
    async def send_image(self):
        image_url = "http://centennialbulb.org/oldbulb/ctbulb.jpg"
        filename = image_url.split("/")[-1]
        db = Database()
        net = Network(image_url)

        if net.r_get.status_code == 200:
            net.download_image(filename)
            channels = db.get_channels()
            for channel_id in channels:
                await self.get_channel(int(channel_id[0])).send(file=discord.File(filename))

        db.close()


client = Client()
cred = open("cred.txt", "r").readline()
client.run(cred)
