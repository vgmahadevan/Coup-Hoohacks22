from pydoc import describe
from turtle import pos
import discord
import json
from CoupGame import CoupGame
import asyncio

auth = json.load(open('auth.json'))
token = auth['discord-token']['token']

NUMREACTS = ['0️⃣','1️⃣','2️⃣','3️⃣', '4', '5️⃣','6️⃣','7️⃣']
ALLACTIONS = ['0: Tax', '1: Assassinate', '2: Exchange', '3: Steal', '4: blank', '5: Income', '6: Foreign Aid', '7: Coup']
CHICKENCOLOR = 0xF4E8A4

class GameClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_running = False
        self.game_inst = None
        self.in_q = False
        self.cur_q = None
        self.player_count = 0
        self.players = []
        self.game_channel = None

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
                await message.channel.send(embed=discord.Embed(title="smh", description="there is alr a game running dumbass", color=CHICKENCOLOR))
            else:
                self.game_running = True
                self.game_inst = CoupGame()
                q_emb = discord.Embed(title="new game :D", description="react 🥚 to join game!\nreact 🐣 to start!", color=CHICKENCOLOR)
                embm = await message.channel.send(embed=q_emb)
                await embm.add_reaction("🥚")
                await embm.add_reaction("🐣")
                self.cur_q = embm.id

                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u == message.author and str(r.emoji) in "🐣", timeout=20)
                except asyncio.TimeoutError:
                    q_emb = discord.Embed(title="D:", description="game start timed out D:", color=CHICKENCOLOR)
                    await embm.edit(embed=q_emb)
                    self.game_running = False
                    self.inq = False
                    self.cur_q = None
                    self.player_count = 0
                    return
                
                if str(reaction.emoji) == "🐣":
                    self.cur_q = None
                    self.in_q = False
                    q_emb = discord.Embed(title=":D", description="game start", color=CHICKENCOLOR)
                    self.game_channel = message.channel
                    await embm.edit(embed=q_emb)
                
                cards = ["duke", "assassin", "ambassador", "captain", "contessa"]
                self.game_inst.deal()
                for i, plyr in enumerate(self.players):
                    await plyr.send(f"your cards are {cards[self.game_inst.alive[i].cards[0]]} and {cards[self.game_inst.alive[i].cards[1]]}")
                self.bg_game = self.loop.create_task(self.run_game())

    async def run_game(self):
        await self.wait_until_ready()
        if self.game_running:
            while not self.is_closed():
                await self.game_channel.send(f"it is now your turn, {self.game_inst.alive[self.game_inst.currentPlayer].name}")
                posActs = self.game_inst.alive[self.game_inst.currentPlayer].getActions()
                toDisplay = "\n".join([act for i, act in enumerate(ALLACTIONS) if i in posActs])
                choice_emb = discord.Embed(title=f"{self.game_inst.alive[self.game_inst.currentPlayer].name}'s turn",
                                            description=f"here are your possible moves...\n{toDisplay}",
                                            color=CHICKENCOLOR)
                choice_msg = await self.game_channel.send(embed=choice_emb)
                for i, num in enumerate(NUMREACTS):
                    if i in posActs:
                        await choice_msg.add_reaction(num)
                
                player_choice = 7 if len(posActs) == 1 else 5
                print(player_choice)
                print([num for i, num in enumerate(NUMREACTS) if i in posActs])
                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[self.game_inst.currentPlayer].id and str(r.emoji) in [num for i, num in enumerate(NUMREACTS) if i in posActs], timeout=15)
                except asyncio.TimeoutError:
                    choice_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                    await choice_msg.edit(embed=choice_emb)
                
                if str(reaction.emoji) in [num for i, num in enumerate(NUMREACTS) if i in posActs]:
                    player_choice = NUMREACTS.index(str(reaction.emoji))
                
                self.game_inst.takeTurn(player_choice)
                print(player_choice)
                
client = GameClient()
client.run(token)
