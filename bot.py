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
GAMECARDS = ["duke", "assassin", "ambassador", "captain", "contessa"]
cardnums = ['🅰', '🅱']

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
        self.challenger = None
        self.challenged = None

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
        if payload.message_id == self.cur_q and payload.emoji.name == "⁉" and payload.member in self.players:
                challenge_emb = discord.Embed(title=f"{self.challenged.name} has been challenged!",
                                            description=f"{payload.member.name} has challenged {self.challenged.name}",
                                            color=CHICKENCOLOR)
                await self.game_channel.send(embed=challenge_emb)
                self.cur_q = None
                self.challenger = self.game_inst.alive[self.players.index(payload.member)]
        

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
                
                self.game_inst.deal()
                for i, plyr in enumerate(self.players):
                    await plyr.send(f"your cards are a. {GAMECARDS[self.game_inst.alive[i].cards[0]]} and b. {GAMECARDS[self.game_inst.alive[i].cards[1]]}")
                self.bg_game = self.loop.create_task(self.run_game())

    async def run_game(self):
        await self.wait_until_ready()
        if self.game_running:
            while not self.is_closed():
                await self.show_status()

                if len(self.players) <= 1:
                    finish_emb = discord.Embed(title=f'WINNER WINNER VEGAN DINNER!', description=f'{self.players[0].name} has won!', color=CHICKENCOLOR)
                    await self.game_channel.send(embed=finish_emb)
                    self.game_running = False
                    self.game_inst = None
                    self.in_q = False
                    self.cur_q = None
                    self.player_count = 0
                    self.players = []
                    self.game_channel = None
                    self.challenger = None
                    self.challenged = None
                    return

                await self.game_channel.send(f"it is now your turn, {self.game_inst.alive[self.game_inst.currentPlayer].name}")
                posActs = self.game_inst.alive[self.game_inst.currentPlayer].getActions()
                if 3 in posActs and self.game_inst.noSteal():
                    posActs.remove(3)
                toDisplay = "\n".join([act for i, act in enumerate(ALLACTIONS) if i in posActs])
                choice_emb = discord.Embed(title=f"{self.game_inst.alive[self.game_inst.currentPlayer].name}'s turn",
                                            description=f"here are your possible moves...\n{toDisplay}",
                                            color=CHICKENCOLOR)
                choice_msg = await self.game_channel.send(embed=choice_emb)
                for i, num in enumerate(NUMREACTS):
                    if i in posActs:
                        await choice_msg.add_reaction(num)
                
                player_choice = 7 if len(posActs) == 1 else 5
                reaction = None
                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[self.game_inst.currentPlayer].id and str(r.emoji) in [num for i, num in enumerate(NUMREACTS) if i in posActs], timeout=15)
                except asyncio.TimeoutError:
                    choice_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                    await choice_msg.edit(embed=choice_emb)
                
                if reaction and str(reaction.emoji) in [num for i, num in enumerate(NUMREACTS) if i in posActs]:
                    player_choice = NUMREACTS.index(str(reaction.emoji))
                    choice_emb = discord.Embed(title=f"{ALLACTIONS[player_choice][3:]}", description=f"you have chosen (to) {ALLACTIONS[player_choice]}!", color=CHICKENCOLOR)
                    await choice_msg.edit(embed=choice_emb)
                
                posTargs = []
                if player_choice == 1 or player_choice == 7:
                    posTargs = []
                    for i in range(self.game_inst.playerCount):
                        if (i != self.game_inst.currentPlayer):
                            posTargs.append(i)
                if player_choice == 3:
                    posTargs = []
                    for i in range(self.game_inst.playerCount):
                        if (i != self.game_inst.currentPlayer) and (self.game_inst.alive[i].coins > 0):
                            posTargs.append(i)
                targ_choice = None
                if len(posTargs) > 0:
                    tcStr = ""
                    for targ, plyr in enumerate(self.players):
                        if targ in posTargs:
                            tcStr += f'\n{targ}: {plyr.name}'
                    target_emb = discord.Embed(title=f"select a target to influence", description=f"here are all ur possible targets!\n{tcStr}", color=CHICKENCOLOR)
                    target_msg = await self.game_channel.send(embed=target_emb)
                    for i, num in enumerate(NUMREACTS):
                        if i in posTargs:
                            await target_msg.add_reaction(num)

                    targ_choice = posTargs[0]
                    try:
                        reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[self.game_inst.currentPlayer].id and str(r.emoji) in [num for i, num in enumerate(NUMREACTS) if i in posTargs], timeout=15)
                    except asyncio.TimeoutError:
                        target_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                        await target_msg.edit(embed=target_emb)

                    if str(reaction.emoji) in [num for i, num in enumerate(NUMREACTS) if i in posTargs]:
                        targ_choice = NUMREACTS.index(str(reaction.emoji))
                        target_emb = discord.Embed(title=f"{ALLACTIONS[player_choice][3:]} {self.players[targ_choice].name}", description=f"you have chosen to target {self.players[targ_choice].name}!", color=CHICKENCOLOR)
                        await target_msg.edit(embed=target_emb)

                    self.game_inst.takeTurn(player_choice)
                
                passed = True

                if targ_choice is not None:
                    target = self.game_inst.alive[targ_choice]

                if player_choice < 4:
                    self.challenged = self.game_inst.alive[self.game_inst.currentPlayer]
                    passed = await self.challenge(self.challenged, player_choice)

                # print(passed)

                def inc():
                    self.game_inst.currentPlayer += 1
                    self.game_inst.currentPlayer %= self.game_inst.playerCount

                if not passed:
                    inc()
                    continue

                passed = True

                if player_choice == 0:
                    self.game_inst.alive[self.game_inst.currentPlayer].coins += 3
                    inc()
                    continue

                if player_choice == 1:
                    block_emb = discord.Embed(title=f"block {self.game_inst.alive[self.game_inst.currentPlayer].name}?",
                                                description=f"{target.name} react 🛑 to block with contessa",
                                                color=CHICKENCOLOR)
                    block_msg = await self.game_channel.send(embed=block_emb)
                    await block_msg.add_reaction('🛑')

                    try:
                        reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[targ_choice].id and str(r.emoji) in '🛑', timeout=5)
                    except asyncio.TimeoutError:
                        pass

                    if str(reaction.emoji) in '🛑':
                        self.challenged = self.game_inst.alive[targ_choice]
                        passed = await self.challenge(self.challenged, 4)
                    
                    if passed:
                        inc()
                        continue
                    
                    succ_emb = discord.Embed(title=f"you have been assassinated!",
                                    description=f"{target.name} please select which card to lose",
                                    color=CHICKENCOLOR)

                    succ_msg = await self.game_channel.send(embed=succ_emb)
                    for card in range(len(target.cards) - 1):
                        await succ_msg.add_reaction(cardnums[card])
                    
                    try:
                        reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[[plyr.name for plyr in self.players].index(target.name)].id and str(r.emoji) in cardnums[:target.numCards], timeout=15)
                    except asyncio.TimeoutError:
                        succ_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                        await succ_msg.edit(embed=succ_emb)


                    if str(reaction.emoji) in [card for num, card in enumerate(cardnums) if num in range(len(target.cards) - 1)]:
                        lose_choice = 0 if str(reaction.emoji) == "🅰" else 1

                    lost_emb = discord.Embed(title=f"{self.players[targ_choice].name} lost a card",
                                        description=f"you lost {GAMECARDS[target.cards[lose_choice]]}",
                                        color=CHICKENCOLOR)
                    passed = await self.game_channel.send(embed=lost_emb)
                    
                    if not passed:
                        inc()
                        continue

                    self.game_inst.loseCard(target, lose_choice)

                    if target not in self.game_inst.alive:
                        dead_emb = discord.Embed(title=f"you dead",
                                            description=f"{self.players[targ_choice].name} is now ghosty 👻",
                                            color=CHICKENCOLOR)
                        await self.game_channel.send(embed=dead_emb)
                        del self.players[[plyr.name for plyr in self.players].index(self.players[targ_choice].name)]
                        inc()
                        continue
                    inc()
                elif player_choice == 2:
                    to_swap = self.game_inst.alive[self.game_inst.currentPlayer].numCards
                    self.game_inst.deck.add(self.game_inst.alive[self.game_inst.currentPlayer].cards[0], self.game_inst.alive[self.game_inst.currentPlayer].cards[1])
                    self.game_inst.deck.shuffle()
                    for n in range(to_swap):
                        to_add = self.game_inst.deck.draw()
                        self.game_inst.alive[self.game_inst.currentPlayer].cards[n] = to_add

                    card_show = f"a. {GAMECARDS[self.game_inst.alive[self.game_inst.currentPlayer].cards[0]]}"
                    if to_swap == 2:
                        card_show += f" and b. {GAMECARDS[self.game_inst.alive[self.game_inst.currentPlayer].cards[1]]}"
                    await self.players[self.game_inst.currentPlayer].send(f"your cards are now {card_show}")
                    inc()
                elif player_choice == 3:
                    block_emb = discord.Embed(title=f"block {self.game_inst.alive[self.game_inst.currentPlayer].name}?",
                                                description=f"anyone react 🧢 to block with captain or 🍑 to block with ambassador",
                                                color=CHICKENCOLOR)
                    block_msg = await self.game_channel.send(embed=block_emb)
                    await block_msg.add_reaction('🧢')
                    await block_msg.add_reaction('🍑')

                    try:
                        reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id in [plyr.id for plyr in self.players] and str(r.emoji) in '🧢🍑', timeout=5)
                    except asyncio.TimeoutError:
                        pass

                    if str(reaction.emoji) in '🧢':
                        self.challenged = self.game_inst.alive[[plyr.name for plyr in self.players].index(user.name)]
                        passed = await self.challenge(self.challenged, 3)
                    elif str(reaction.emoji) in '🍑':
                        self.challenged = self.game_inst.alive[[plyr.name for plyr in self.players].index(user.name)]
                        passed = await self.challenge(self.challenged, 2)

                    self.game_inst.alive[self.game_inst.currentPlayer].coins += min(2, target.coins)
                    target.coins -= min(2, target.coins)

                    if not passed:
                        inc()
                        continue
                    passed = True
                elif player_choice == 5:
                    self.game_inst.alive[self.game_inst.currentPlayer].coins += 1
                    inc()
                elif player_choice == 6:
                    block_emb = discord.Embed(title=f"block {self.game_inst.alive[self.game_inst.currentPlayer].name}?",
                                                description=f"anyone react 🛑 to block with duke",
                                                color=CHICKENCOLOR)
                    block_msg = await self.game_channel.send(embed=block_emb)
                    await block_msg.add_reaction('🛑')

                    try:
                        reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id in [plyr.id for plyr in self.players] and str(r.emoji) in '🛑', timeout=5)
                    except asyncio.TimeoutError:
                        pass

                    if str(reaction.emoji) in '🛑':
                        self.challenged = self.game_inst.alive[[plyr.name for plyr in self.players].index(user.name)]
                        passed = await self.challenge(self.challenged, 6)

                        if passed:
                            inc()
                            continue
                    
                    self.game_inst.alive[self.game_inst.currentPlayer].coins += 2
                    inc()
                    
                    passed = True
                elif player_choice == 7:
                    target = self.game_inst.alive[targ_choice]

                    lose_choice = 0

                    succ_emb = discord.Embed(title=f"you have been chicken cooped!",
                                        description=f"{target.name} please select which card to lose",
                                        color=CHICKENCOLOR)
                    succ_msg = await self.game_channel.send(embed=succ_emb)
                    for card in range(len(target.cards) - 1):
                        await succ_msg.add_reaction(cardnums[card])

                    try:
                        reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[targ_choice].id and str(r.emoji) in cardnums[:target.numCards], timeout=15)
                    except asyncio.TimeoutError:
                        succ_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                        await succ_msg.edit(embed=succ_emb)

                    if str(reaction.emoji) in [card for num, card in enumerate(cardnums) if num in range(len(target.cards) - 1)]:
                        lose_choice = 0 if str(reaction.emoji) == "🅰" else 1

                    lost_emb = discord.Embed(title=f"{target.name} lost a card!",
                                        description=f"you lost {GAMECARDS[target.cards[lose_choice]]}",
                                        color=CHICKENCOLOR)
                    await self.game_channel.send(embed=lost_emb)

                    self.game_inst.loseCard(target, lose_choice)
                    inc()
                    if target not in self.game_inst.alive:
                        dead_emb = discord.Embed(title=f"you dead",
                                            description=f"{target.name} is now ghosty 👻",
                                            color=CHICKENCOLOR)
                        await self.game_channel.send(embed=dead_emb)
                        del self.players[[plyr.name for plyr in self.players].index(target.name)]
                        continue
                

    async def challenge(self, challenged, player_choice):
        challenge_emb = discord.Embed(title=f"challenge {challenged.name}?",
                                                description=f"react ⁉ to challenge {challenged.name}",
                                                color=CHICKENCOLOR)
        challenge_msg = await self.game_channel.send(embed=challenge_emb)
        self.cur_q = challenge_msg.id
        await challenge_msg.add_reaction('⁉')

        await asyncio.sleep(5)
        self.cur_q = None
    
        crplyr = challenged
        lose_choice = 0
        if self.challenger:
            test_challenge = self.game_inst.resolveChallenge(self.challenger, challenged, player_choice) 
            if test_challenge:
                succ_emb = discord.Embed(title=f"your challenge has failed!",
                                    description=f"{self.challenger.name} please select which card to lose",
                                    color=CHICKENCOLOR)
                succ_msg = await self.game_channel.send(embed=succ_emb)
                for card in range(len(self.challenger.cards)):
                    await succ_msg.add_reaction(cardnums[card])
                
                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[[plyr.name for plyr in self.players].index(self.challenger.name)].id and str(r.emoji) in cardnums[:self.challenger.numCards], timeout=15)
                except asyncio.TimeoutError:
                    succ_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                    await succ_msg.edit(embed=succ_emb)


                if str(reaction.emoji) in [card for num, card in enumerate(cardnums) if num in range(len(self.challenger.cards))]:
                    lose_choice = 0 if str(reaction.emoji) == "🅰" else 1

                lost_emb = discord.Embed(title=f"{self.challenger.name} lost a card",
                                    description=f"you lost {GAMECARDS[self.challenger.cards[lose_choice]]}",
                                    color=CHICKENCOLOR)
                await self.game_channel.send(embed=lost_emb)

                self.game_inst.loseCard(self.challenger, lose_choice)

                if self.challenger not in self.game_inst.alive:
                    dead_emb = discord.Embed(title=f"you dead",
                                        description=f"{self.challenger.name} is now ghosty 👻",
                                        color=CHICKENCOLOR)
                    await self.game_channel.send(embed=dead_emb)
                    del self.players[[plyr.name for plyr in self.players].index(self.challenger.name)]
                    self.challenger = None
                    self.challenged = None
            else:
                succ_emb = discord.Embed(title=f"your challenge has been successful!",
                                    description=f"{challenged.name} please select which card to lose",
                                    color=CHICKENCOLOR)
                succ_msg = await self.game_channel.send(embed=succ_emb)
                for card in range(len(challenged.cards)):
                    await succ_msg.add_reaction(cardnums[card])

                try:
                    reaction, user = await self.wait_for("reaction_add", check=lambda r, u: u.id == self.players[[plyr.name for plyr in self.players].index(self.challenged.name)].id and str(r.emoji) in cardnums[:challenged.numCards], timeout=15)
                except asyncio.TimeoutError:
                    succ_emb = discord.Embed(title="D:", description="time's up! default choice is chosen for you", color=CHICKENCOLOR)
                    await succ_msg.edit(embed=succ_emb)

                if str(reaction.emoji) in [card for num, card in enumerate(cardnums) if num in range(len(challenged.cards))]:
                    lose_choice = 0 if str(reaction.emoji) == "🅰" else 1

                lost_emb = discord.Embed(title=f"{challenged.name} lost a card",
                                    description=f"you lost {GAMECARDS[challenged.cards[lose_choice]]}",
                                    color=CHICKENCOLOR)
                await self.game_channel.send(embed=lost_emb)

                self.game_inst.loseCard(challenged, lose_choice)

                if crplyr not in self.game_inst.alive:
                    dead_emb = discord.Embed(title=f"you dead",
                                        description=f"{crplyr.name} is now ghosty 👻",
                                        color=CHICKENCOLOR)
                    await self.game_channel.send(embed=dead_emb)
                    del self.players[[plyr.name for plyr in self.players].index(crplyr.name)]

                self.challenger = None
                self.challenged = None
                return False

        self.challenger = None
        self.challenged = None
        return True
    
    async def show_status(self):
        stat_str = ''
        for plyr in self.game_inst.alive:
            stat_str += f'\n{plyr.name} has {plyr.numCards} card(s) and {plyr.coins} coin(s)\n'
        status_emb = discord.Embed(title='current status', description=stat_str, color=CHICKENCOLOR)
        await self.game_channel.send(embed=status_emb)

client = GameClient()
client.run(token)
