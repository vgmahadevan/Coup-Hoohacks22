import discord
import gamerunner

client = discord.Client()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'We have logged in as {client.user}')

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.lower == 'start chicken coop' or message.content.lower == 'c!start':
            await message.channel.send('Hello!')

client = MyClient()
client.run('OTU3MzY5MTcxODc0ODI0MjAy.Yj9xhQ.3lfLWE2SLUgBhWRDJqhRaKSoFKM')
