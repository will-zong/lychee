import discord
import asyncio
import random 
import time

class Player():

    """Stores information about a specific player

    Parameters
    ----------
    game
        The game this player is in.
    member : discord.Member
        The player's member
    name : str
        The player's name/nickname
    id_num : int
        The player's ID number
    role : str
        The player's role
    alignment : str
        The player's alignment, either 'Resistance' or 'Spy'

    Attributes
    ----------
    believed_role : str
        The role the player thinks they are
    believed_alignment : str
        The alignment the player thinks they are
    action_windows : List[bool, bool, bool, bool]
        Whether the player as an action window at end of rounds 1, 2, 3, and 4
    past_targets : List[Players]
        The players who have been targeted already
    possible_mission_cards : List[bool, bool, bool]
        Which mission cards the player can play out of the three possible: [success, fail, switch]
    voted : bool
        Whether the player has voted to accept/reject the current team
    can_be_on_current_mission : bool
        Whether the player can or cannot be in the current mission
    on_current_team : bool
        Whether or not the player is on the current team
    completed_mission : bool
        Whether or not the player has submitted a mission card
    game
    member
    name
    id_num
    role
    alignment
    """

    # All roles are subclasses of Player, overriding the appropriate functions and creating new appropriate attributes

    def __init__(self, game, member, name, id_num, role, alignment):
        self.game = game
        self.member = member
        self.name = name
        self.id_num = id_num
        self.role = role
        self.alignment = alignment
        self.set_believed_role() # self.believed_role : str
        self.set_believed_alignment() # self.believed_alignment : str
        self.set_actions() # self.action_windows : List[bool, bool, bool, bool]
                           # self.past_targets : List[Players]
                           # self.has_action : bool
        self.set_possible_mission_cards() # self.possible_mission_cards : List[bool, bool, bool]
        self.voted = False # bool
        self.can_be_on_current_mission = True # bool
        self.on_current_team = False # bool
        self.completed_mission = False # bool

    def swap_alignment(self):
        if self.alignment == 'Resistance':
            self.alignment = 'Spy'
        else:
            self.alignment = 'Resistance'

    def set_believed_role(self):
        self.believed_role = self.role

    def set_believed_alignment(self):
        self.believed_alignment = self.alignment

    def set_actions(self):
        self.action_windows = [False, False, False, False]
        self.past_targets = []
        self.has_action = True

    def set_possible_mission_cards(self):
        self.possible_mission_cards = [True, True, False]

    def block_success(self):
        self.possible_mission_cards[0] = False

    def block_fail(self):
        self.possible_mission_cards[1] = False

    def has_already_targeted(self, player):
        return (player in self.past_targets)

    def soft_reset(self):
        """Resets players to default values after a rejected team."""
        self.voted = False
        self.on_current_team = False

    def hard_reset(self):
        """Resets players to default values after a completed mission."""
        self.set_possible_mission_cards()
        self.voted = False
        self.can_be_on_current_mission = True
        self.on_current_team = False
        self.completed_mission = False

    def set_done_voting(self):
        self.voted = True

    def block_mission(self):
        self.can_be_on_current_mission = False
    
    def add_to_team(self):
        self.on_current_team = True

    def set_done_missioning(self):
        self.completed_mission = True

    async def get_starting_info(self):
        """Tells the player their starting info."""
        await self.member.create_dm()
        await self.member.dm_channel.send('—————— New Game ——————')
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role} on the {self.alignment} side.')

    async def do_action(self):
        pass

"""
__Resistance Roles__
:necktie: **President** — You know 1 other Resistance player (5-7 players) or 2 other Resistance players (8-10 players).
:game_die: **Gambler** — At the end of rounds 1 and 2, you must privately choose 2 other players. If they are both Spies, you will not be able to `>>mission success` during the next round.
:crossed_swords: **Dueler** — If there is exactly one spy with you on a team, they cannot `>>mission fail`. If there are two or more spies with you on a team, you cannot `>>mission success`.
:police_officer: **Officer** — At the end of rounds 2 and 3, you must privately choose one player. You cannot choose the same player twice. It is publicly revealed that that player cannot be on teams during the next round.
:rage: **Contrarian** — The first time you vote with the minority, everyone's vote is swapped.
:detective: **Informant** — You know two Spy roles that aren't in the game.
:crystal_ball: **Psychic** — At the end of rounds 2, 3, and 4, you must privately choose one player to learn their alignment. However, you learn the opposite alignment during a random round.
:womans_hat: **Witch** — You think you're the Psychic but you always learn the opposite alignment.
:mag: **Insider** — At the end of rounds 1, 2, and 3, you learn whether or not all of the Resistance voted together during the passing vote.
:woman_gesturing_no: **Resistance Reverser** — You can `>>mission switch` to swap the outcome of the mission.

__Spy Roles__
:speaking_head: **Organizer** — You know the role of every Spy.
:bomb: **Bomber** — The first time you `>>mission success`, during the next mission, a random Resistance player on the mission team cannot `>>mission success`.
:exploding_head: **Martyr** — The first time you `>>mission fail`, everyone also `>>mission fail` even if they cannot, except for the Angel.
:boxing_glove: **Usurper** — The first time you vote with all of the Resistance, everyone's vote is swapped.
:japanese_goblin: **Muckraker** — Whenever you vote with all of the spies, you and a random Resistance player swap votes.
:beer: **Drunken Spy** — You think you are the Informant but the two roles are actually in the game.
:angel: **Angel** — As long as there is at least one `>>mission fail`, you always `>>mission success`.
:man_gesturing_no: **Spy Reverser** — You can `>>mission switch` to swap the outcome of the mission. You cannot `>>mission fail`.
"""

class President(Player):
    
    """President — You know which Resistance roles are in the game."""

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'President', 'Resistance')

    async def get_starting_info(self):
        await super().get_starting_info()
        all_other_resistance_player_names = []
        for temp_player in self.game.players:
            if not (self.game.players.index(temp_player) in self.game.spy_indices) and temp_player != self:
                all_other_resistance_player_names.append(temp_player.name)
        random.shuffle(all_other_resistance_player_names)
        if self.game.player_count <= 7:
            await self.member.dm_channel.send(f'{all_other_resistance_player_names[0]} is on the Resistance side.') 
        else:
            await self.member.dm_channel.send(f'{all_other_resistance_player_names[0]} and {all_other_resistance_player_names[1]} are on the Resistance side.') 

class Gambler(Player):
        
    """Gambler — At the end of rounds 1 and 2, you must privately choose 2 other players. 
                 If they are both Spies, you will not be able to >>mission success during the next round."""
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Gambler', 'Resistance')

    def set_actions(self):
        self.action_windows = [True, True, False, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        self.has_action = True
        start_time = time.perf_counter()
        await self.member.send('Please choose 2 other players using the `>>gamble` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False) and (time.perf_counter() - start_time < 45):
            await asyncio.sleep(1)

    async def do_gamble(self, gambled_players):
        if gambled_players[0].alignment == 'Spy' and gambled_players[1].alignment == 'Spy':
            self.block_success()
            await self.member.dm_channel.send('Those 2 players are both on the Spy side. You cannot `>>mission success` during the next round.')
        else:
            await self.member.dm_channel.send('Those 2 players are not both on the Spy side.')
        self.has_action = False

class Dueler(Player):

    """Dueler — If there is exactly one spy with you on a team, they cannot >>mission fail. 
                If there are two or more spies with you on a team, you cannot >>mission success."""

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Dueler', 'Resistance')

    async def do_action(self):
        # get spies on the current team
        temp_spy_players = []
        for temp_player in self.game.get_current_team():
            if temp_player.alignment == 'Spy':
                temp_spy_players.append(temp_player)
        # do appropriate action based on number of spies
        if len(temp_spy_players) == 1:
            temp_spy_players[0].block_fail()
        elif len(temp_spy_players) >= 2:
            self.block_success()
        
class Officer(Player):

    """Officer — At the end of rounds 2 and 3, you must privately choose one player. You cannot choose the same player twice. 
                 It is publicly revealed that that player cannot be on any team during the next round."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Officer', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, True, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        self.has_action = True
        start_time = time.perf_counter()
        await self.member.send('Please choose another player using the `>>arrest` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False) and (time.perf_counter() - start_time < 45):
            await asyncio.sleep(1)

    async def do_arrest(self, arrested_player):
        arrested_player.block_mission()
        await self.member.dm_channel.send(f'You have arrested {arrested_player.name}.')
        await self.game.general_channel.send(f'{arrested_player.name} has been arrested by the Officer. They cannot be on any team during the next round.')
        self.past_targets.append(arrested_player)
        self.has_action = False

class Contrarian(Player):

    """Contrarian — The first time you vote with the minority, everyone's vote is swapped."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Contrarian', 'Resistance')

    async def do_action(self):
        if self.has_action == False: return
        # check and switch if minority
        if (self in self.game.voter.voted_accept) and (len(self.game.voter.voted_accept) < len(self.game.voter.voted_reject)):
            temp_voted_accept = self.game.voter.voted_accept
            self.game.voter.voted_accept = self.game.voter.voted_reject
            self.game.voter.voted_reject = temp_voted_accept
            self.has_action = False
            await self.member.dm_channel.send('Your ability has been triggered.')
        elif (self in self.game.voter.voted_reject) and (len(self.game.voter.voted_reject) < len(self.game.voter.voted_accept)):
            temp_voted_accept = self.game.voter.voted_accept
            self.game.voter.voted_accept = self.game.voter.voted_reject
            self.game.voter.voted_reject = temp_voted_accept
            self.has_action = False
            await self.member.dm_channel.send('Your ability has been triggered.')

class Informant(Player):

    """Informant — You know two Spy roles that aren't in the game."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Informant', 'Resistance')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The following Spy roles are not in this game: {random.sample(self.game.all_spy_roles, 2)}')

class Psychic(Player):

    """Psychic — At the end of rounds 2, 3, and 4, you must privately choose one player to learn their alignment.
                 However, you learn the opposite alignment during a random round."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Psychic', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, True, True, True]
        self.past_targets = []
        self.opposite_round = [2, 3, 4]
        random.shuffle(self.opposite_round)
        self.has_action = False

    async def do_action(self):
        self.has_action = True
        start_time = time.perf_counter()
        await self.member.send('Please choose another player using the `>>see` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False) and (time.perf_counter() - start_time < 45):
            await asyncio.sleep(1)

    async def do_see(self, seen_player):
        if self.opposite_round[0] == self.game.get_round():
            if seen_player.alignment == 'Resistance':
                await self.member.dm_channel.send(f'{seen_player.name} is on the Spy side.')
            else: 
                await self.member.dm_channel.send(f'{seen_player.name} is on the Resistance side.')
        else: 
            await self.member.dm_channel.send(f'{seen_player.name} is on the {seen_player.alignment} side.')
        self.past_targets.append(seen_player)
        self.has_action = False

class Witch(Player):

    """Witch — You think you're the Psychic but you always learn the opposite alignment."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Witch', 'Resistance')

    def set_believed_role(self):
        self.believed_role = 'Psychic'

    def set_actions(self):
        self.action_windows = [False, True, True, True]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        self.has_action = True
        start_time = time.perf_counter()
        await self.member.send('Please choose another player using the `>>see` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False) and (time.perf_counter() - start_time < 45):
            await asyncio.sleep(1)

    async def do_see(self, seen_player):
        if seen_player.alignment == 'Resistance':
            await self.member.dm_channel.send(f'{seen_player.name} is on the Spy side.')
        else: 
            await self.member.dm_channel.send(f'{seen_player.name} is on the Resistance side.')
        self.past_targets.append(seen_player)
        self.has_action = False

class Insider(Player):

    """Insider — At the end of rounds 1, 2, and 3, you learn whether or not all of the Resistance voted together during the passing vote."""
         
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Insider', 'Resistance')

    def set_actions(self):
        self.action_windows = [True, True, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        # check if all of the Resistance voted together and tell answer
        resistance_voted_accept_count = 0
        for temp_player in self.game.voter.recent_voted_accept:
            if temp_player.alignment == 'Resistance':
                resistance_voted_accept_count += 1
        if resistance_voted_accept_count == len(self.game.player_resistance_roles) or resistance_voted_accept_count == 0:
            await self.member.dm_channel.send('The Resistance voted all together during the passing vote this round.')
        else:
            await self.member.dm_channel.send('The Resistance did not vote all together during the passing vote this round.')

class Resistance_Reverser(Player):

    """Resistance Reverser — You can >>mission switch to swap the outcome of the mission."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Resistance Reverser', 'Resistance')

    def set_possible_mission_cards(self):
        self.possible_mission_cards = [True, True, True]

class Organizer(Player):

    """Organizer — You know the role of every Spy."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Organizer', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}\nTheir respective roles are: {self.game.player_spy_roles}')

class Bomber(Player):

    """Bomber — The first time you >>mission success, during the next mission, a random Resistance player on the mission team cannot >>mission success."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Bomber', 'Spy')
 
    def set_actions(self):
        self.action_windows = [False, False, False, False]
        self.past_targets = []
        self.has_action = True
        self.set_bomb = False

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')

    async def do_action(self):
        # check if bomb set or bomb triggered
        if self.set_bomb:
            temp_team = self.game.get_current_team()
            random.shuffle(temp_team)
            for temp_player in temp_team:
                if temp_player.alignment == 'Resistance' and temp_player.possible_mission_cards[1]:
                    temp_player.block_success()
                    await self.member.dm_channel.send('Your set bomb has gone off!')
                    return
        elif self.has_action and (self in self.game.missioner.recent_conducted_success):
            self.set_bomb = True
            self.has_action = False
            await self.member.dm_channel.send('Your bomb has been set!')

class Martyr(Player):

    """Martyr — The first time you >>mission fail, everyone also >>mission fail even if they cannot, except for the Angel."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Martyr', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')

    async def do_action(self):
        if self.has_action == False: return
        if (self in self.game.missioner.conducted_fail):
            for x in range(len(self.game.missioner.conducted_success)):
                self.game.missioner.conducted_fail.append(self.game.missioner.conducted_success.pop())
            for x in range(len(self.game.missioner.conducted_switch)):
                self.game.missioner.conducted_fail.append(self.game.missioner.conducted_switch.pop())
            self.has_action == False
            await self.member.dm_channel.send('Your ability has been triggered.')

class Usurper(Player):

    """Usurper — The first time you vote with all of the Resistance, everyone's vote is swapped."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Usurper', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        
    async def do_action(self):
        if self.has_action == False: return
        temp_resistance_count = 0
        if (self in self.game.voter.voted_accept):
            for temp_player in self.game.voter.voted_accept:
                if temp_player.alignment == 'Resistance':
                    temp_resistance_count += 1
            if temp_resistance_count == len(self.game.player_resistance_roles):
                temp_voted_accept = self.game.voter.voted_accept
                self.game.voter.voted_accept = self.game.voter.voted_reject
                self.game.voter.voted_reject = temp_voted_accept
                self.has_action = False
                await self.member.dm_channel.send('Your ability has been triggered. Everyone\'s vote has been swapped.')
        else:
            for temp_player in self.game.voter.voted_reject:
                if temp_player.alignment == 'Resistance':
                    temp_resistance_count += 1
            if temp_resistance_count == len(self.game.player_resistance_roles):
                temp_voted_accept = self.game.voter.voted_accept
                self.game.voter.voted_accept = self.game.voter.voted_reject
                self.game.voter.voted_reject = temp_voted_accept
                self.has_action = False
                await self.member.dm_channel.send('Your ability has been triggered. Everyone\'s vote has been swapped.')

class Muckraker(Player):

    """Muckraker — Whenever you vote with all of the spies, you and a random Resistance player swap votes."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Muckraker', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        
    async def do_action(self):
        temp_spy_count = 0
        if (self in self.game.voter.voted_accept) and len(self.game.voter.voted_reject) != 0: 
            for temp_player in self.game.voter.voted_accept:
                if temp_player.alignment == 'Spy':
                    temp_spy_count += 1
            if temp_spy_count == len(self.game.player_spy_roles):
                self.game.voter.voted_accept.append(self.game.voter.voted_reject.pop())
                self.game.voter.voted_accept.remove(self)
                self.game.voter.voted_reject.append(self)
                await self.member.dm_channel.send('Your ability has been triggered. Your `>>vote accept` has been swapped to `>>vote reject`.')
        elif (self in self.game.voter.voted_reject) and len(self.game.voter.voted_accept) != 0:
            for temp_player in self.game.voter.voted_reject:
                if temp_player.alignment == 'Spy':
                    temp_spy_count += 1
            if temp_spy_count == len(self.game.player_spy_roles):
                self.game.voter.voted_reject.append(self.game.voter.voted_accept.pop())
                self.game.voter.voted_reject.remove(self)
                self.game.voter.voted_accept.append(self)
                await self.member.dm_channel.send('Your ability has been triggered. Your `>>vote reject` has been swapped to `>>vote accept`.')

class Drunken_Spy(Player):

    """Drunken Spy — You think you are the Informant but the two roles are actually in the game."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Drunken Spy', 'Spy')

    def set_believed_role(self):
        self.believed_role = 'Informant'

    def set_believed_alignment(self):
        self.believed_alignment = 'Resistance'

    async def get_starting_info(self):
        await self.member.create_dm()
        await self.member.dm_channel.send('—————— New Game ——————')
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role} on the Resistance side.')
        await self.member.dm_channel.send(f'The following Spy roles are not in this game: {random.sample(self.game.player_spy_roles, 2)}')

class Angel(Player):

    """Angel — As long as there is at least one >>mission fail, you always >>mission success."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Angel', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        
    async def do_action(self):
        if self in self.game.missioner.conducted_success: return
        elif len(self.game.missioner.conducted_fail) >= 2:
            self.game.missioner.conducted_fail.remove(self)
            self.game.missioner.conducted_success.append(self)
            await self.member.dm_channel.send('Your ability has been triggered. Your `>>mission fail` has been swapped to `>>mission success`.')

class Spy_Reverser(Player):

    """Spy Reverser — You can >>mission switch to swap the outcome of the mission. You cannot >>mission fail."""
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Spy Reverser', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        
    def set_possible_mission_cards(self):
        self.possible_mission_cards = [True, False, True]