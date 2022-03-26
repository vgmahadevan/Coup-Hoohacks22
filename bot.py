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

    async def on_ready(self):
        print(f'We have logged in as {client.user}')

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.lower() == 'start chicken coop' or message.content.lower() == 'c!start':
            if self.game_running:
                await message.channel.send(embed=discord.Embed(title="smh", description="there is alr a game running dumbass", color=0xF4E8A4))
            else:
                self.game_running = True
                self.game_inst = CoupGame()
                q_emb = discord.Embed(title="new game :D", description="react 🥚 to join game!\nreact 🐣 to start!", color=0xF4E8A4)
                self.cur_q = q_emb.id
                await message.channel.send(embed=q_emb)
                await q_emb.add_reaction("🐔")

                player_num = 1

                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u == ctx.author and str(r.emoji) in "🐣", timeout=30)
                except asyncio.TimeoutError:
                    await q_emb.edit(content="game start timed out D:")
                    return
                
                if str(reaction.emoji) == "🐣":
                    self.cur_q = None
                    self.in_q = False
                    await q_emb.edit(content="game start!")

    async def on_reaction_add(self, reaction, user):
        if reaction.me:
            return
        if reaction.message.id == self.cur_q and reaction.emoji == "🥚":
            self.player_count += 1
            await reaction.message.channel.send(f"welcome player {self.player_count}: {user}!")

client = GameClient()
client.run(token)
