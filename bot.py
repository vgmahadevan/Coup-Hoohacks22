from pydoc import describe
import discord
import json
from CoupGame import CoupGame
import asyncio

auth = json.load(open('auth.json'))
token = auth['discord-token']['token']

class GameClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_running = False
        self.game_inst = None
        self.in_q = False
        self.cur_q = None
        self.player_count = 0
        self.players = []

    async def on_ready(self):
        print(f'We have logged in as {client.user}')

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == client.user.id:
            return
        if payload.message_id == self.cur_q and payload.emoji.name == "🥚":
            self.player_count += 1
            msg = await self.fetch_message(payload)
            await msg.channel.send(f"welcome player {self.player_count}: {payload.member.name}!")
            self.game_inst.addPlayer(payload.member.name)
            self.players.append(payload.member)

    async def fetch_message(self, payload):
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        return message

    async def on_message(self, message):
        if message.author == client.user:
            return

        if "yargo" in message.content.lower():
            await message.channel.send("yargo!")

        if message.content.lower() == 'start chicken coop' or message.content.lower() == 'c!start':
            if self.game_running:
                await message.channel.send(embed=discord.Embed(title="smh", description="there is alr a game running dumbass", color=0xF4E8A4))
            else:
                self.game_running = True
                self.game_inst = CoupGame()
                q_emb = discord.Embed(title="new game :D", description="react 🥚 to join game!\nreact 🐣 to start!", color=0xF4E8A4)
                embm = await message.channel.send(embed=q_emb)
                await embm.add_reaction("🥚")
                await embm.add_reaction("🐣")
                self.cur_q = embm.id

                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u == message.author and str(r.emoji) in "🐣", timeout=20)
                except asyncio.TimeoutError:
                    q_emb = discord.Embed(title="D:", description="game start timed out D:", color=0xF4E8A4)
                    await embm.edit(embed=q_emb)
                    self.game_running = False
                    self.inq = False
                    self.cur_q = None
                    self.player_count = 0
                    return
                
                if str(reaction.emoji) == "🐣":
                    self.cur_q = None
                    self.in_q = False
                    q_emb = discord.Embed(title=":D", description="game start", color=0xF4E8A4)
                    await embm.edit(embed=q_emb)
                
                cards = ["duke", "assassin", "ambassador", "captain", "contessa"]
                self.game_inst.deal()
                for i, plyr in enumerate(self.players):
                    await plyr.send(f"your cards are {cards[self.game_inst.alive[i].cards[0]]} and {cards[self.game_inst.alive[i].cards[1]]}")

client = GameClient()
client.run(token)
