import discord
import json
import gamerunner

client = discord.Client()
auth = json.load(open('auth.json'))
token = auth['discord-token']['token']

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'We have logged in as {client.user}')

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.lower() == 'start chicken coop' or message.content.lower() == 'c!start':
            print('hi')
            await message.channel.send('Hello!')

client = MyClient()
client.run(token)
