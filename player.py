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
    has_action : bool
        Whether the player still has an action to perform
    silenced : bool
        Whether the player is silenced
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
        self.silenced = False # bool
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

    def block_switch(self):
        self.possible_mission_cards[2] = False

    def teach_switch(self):
        self.possible_mission_cards[2] = True

    def silence(self):
        self.silenced = True

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

"""Resistance Roles"""

class Resistance(Player):
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Resistance', 'Resistance')

class Commander(Player):
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Commander', 'Resistance')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')

class Bodyguard(Player):
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Bodyguard', 'Resistance')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Commanders in this game are: {self.game.get_commander_names()}')

class President(Player):
    
    """President — At the end of round 3, you learn 1 Resistance player."""          # complete

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'President', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, False, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        all_other_resistance_player_names = []
        for temp_player in self.game.players:
            if not (self.game.players.index(temp_player) in self.game.spy_indices) and temp_player != self:
                all_other_resistance_player_names.append(temp_player.name)
        random.shuffle(all_other_resistance_player_names)
        await self.member.dm_channel.send(f'{all_other_resistance_player_names[0]} is on the Resistance side.') 

class Gambler(Player):
        
    """Gambler — At the end of round 4, you must privately choose 2 other players. 
                 If they are opposite alignments, you cannot >>mission success during the next round."""            # completed
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Gambler', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, False, False, True]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose 2 other players using the `>>gamble` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False
            
    async def do_gamble(self, gambled_players):
        if gambled_players[0].alignment != gambled_players[1].alignment:
            self.block_success()
            await self.member.dm_channel.send('Those 2 players are opposite alignments. You cannot `>>mission success` during the next round.')
        else:
            await self.member.dm_channel.send('Those 2 players are not opposite alignments.')
        self.has_action = False
        
class Officer(Player):

    """Officer — At the end of 2 random rounds, you must privately choose a player. 
                 It is publicly revealed that that player cannot be on any team during the next round. You cannot choose the same player twice."""           # complete
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Officer', 'Resistance')

    def set_actions(self):
        self.action_windows = [True, True, False, False]
        random.shuffle(self.action_windows)
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>arrest` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_arrest(self, arrested_player):
        arrested_player.block_mission()
        await self.member.dm_channel.send(f'You have arrested {arrested_player.name}.')
        await self.game.general_channel.send(f'{arrested_player.name} has been arrested by the Officer. They cannot be on any team during the next round.')
        self.past_targets.append(arrested_player)
        self.has_action = False

class Informant(Player):

    """Informant — You know two Spy roles that aren't in the game."""           # complete
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Informant', 'Resistance')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The following Spy roles are not in this game: {random.sample(self.game.all_spy_roles, 2)}')

class Psychic(Player):

    """Psychic — At the end of rounds 3 and 4, you must privately choose another player to learn their alignment."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Psychic', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, False, True, True]
        self.past_targets = [self]
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>see` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_see(self, seen_player):
        await self.member.dm_channel.send(f'{seen_player.name} is on the {seen_player.alignment} side.')
        self.past_targets.append(seen_player)
        self.has_action = False

class Witch(Player):

    """Witch — You think you're the Psychic but you always learn the opposite alignment."""         # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Witch', 'Resistance')

    def set_believed_role(self):
        self.believed_role = 'Psychic'

    def set_actions(self):
        self.action_windows = [False, False, True, True]
        self.past_targets = [self]
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>see` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_see(self, seen_player):
        if seen_player.alignment == 'Resistance':
            await self.member.dm_channel.send(f'{seen_player.name} is on the Spy side.')
        else: 
            await self.member.dm_channel.send(f'{seen_player.name} is on the Resistance side.')
        self.past_targets.append(seen_player)
        self.has_action = False

class Resistance_Reverser(Player):

    """Resistance Reverser — You can >>mission switch to swap the outcome of the mission."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Resistance Reverser', 'Resistance')

    def set_possible_mission_cards(self):
        self.possible_mission_cards = [True, True, True]

class Traditionalist(Player):

    """Traditionalist — No one can `>>mission switch` while you are on a mission."""            # completed

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Traditionalist', 'Resistance')

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        for temp_player in self.game.get_current_team():
            temp_player.block_switch()

class Freelancer(Player):

    """Freelancer — At the end of round 3, you must privately choose another player.
                    If they are a spy, during the next round, a random Resistance player on the mission team cannot >>mission success."""         # completed

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Freelancer', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, False, True, False]
        self.past_targets = [self]
        self.has_action = False
        self.set_bomb = False

    async def do_action(self):
        if self.set_bomb:
            temp_team = self.game.get_current_team()
            random.shuffle(temp_team)
            for temp_player in temp_team:
                if temp_player.alignment == 'Resistance' and (temp_player.possible_mission_cards[0] == True):
                    temp_player.block_success()
            self.set_bomb = False
            await self.member.dm_channel.send('Your set bomb has gone off!')
        elif self.silenced == True and self.has_action:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
        elif self.game.current_window == 3:
            self.has_action = True
            await self.member.dm_channel.send('Please choose another player using the `>>freelance` command.')
            while (self.has_action == True) and (self.game.skip_night_action == False):
                await asyncio.sleep(1)
            self.has_action = False

    async def do_freelance(self, freelanced_player):
        if freelanced_player.alignment == 'Spy':
            self.set_bomb = True
            await self.member.dm_channel.send('You have chosen a Spy and have set a bomb!')
        else:
            await self.member.dm_channel.send('You have not chosen a Spy.')
        self.has_action = False
        
class Professor(Player):

    """Professor — At the end of rounds 2, 3, and 4, you must privately choose a player.
                   During the next round, they can >>mission switch. You may not choose the same player twice."""         # completed

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Professor', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, True, True, True]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>teach` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_teach(self, taught_player):
        taught_player.teach_switch()
        self.past_targets.append(taught_player)
        await self.member.dm_channel.send(f'You have taught {taught_player.name} `>>mission switch`.')
        self.has_action = False

class Resistance_Clown(Player):

    """Clown — You do not learn your alignment until the end of round 3."""         # completed

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Resistance Clown', 'Resistance')

    def set_believed_role(self):
        self.believed_role = 'Clown'

    async def get_starting_info(self):
        await self.member.create_dm()
        await self.member.dm_channel.send('—————— New Game ——————')
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role}.')

    def set_actions(self):
        self.action_windows = [False, False, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role} on the {self.alignment} side.')

class Dueler(Player):

    """Dueler — If there is exactly one spy with you on a team, they cannot >>mission fail. 
                If there are two or more spies with you on a team, you cannot >>mission success."""         # complete

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Dueler', 'Resistance')

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
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

class Insider(Player):

    """Insider — At the end of rounds 1, 2, and 3, you learn whether or not all of the Resistance voted together during the passing vote."""            # completed
         
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Insider', 'Resistance')

    def set_actions(self):
        self.action_windows = [True, True, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        # check if all of the Resistance voted together and tell answer
        resistance_voted_accept_count = 0
        for temp_player in self.game.voter.recent_voted_accept:
            if temp_player.alignment == 'Resistance':
                resistance_voted_accept_count += 1
        if resistance_voted_accept_count == len(self.game.player_resistance_roles) or resistance_voted_accept_count == 0:
            await self.member.dm_channel.send('The Resistance voted all together during the passing vote this round.')
        else:
            await self.member.dm_channel.send('The Resistance did not vote all together during the passing vote this round.')

class Contrarian(Player):

    """Contrarian — The first time you vote with the minority, everyone's vote is swapped."""           # complete
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Contrarian', 'Resistance')

    async def do_action(self):
        if self.has_action == False: return
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
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

class Librarian(Player):

    """Librarian — At the end of rounds 2 and 3, you must choose another player. During their next action window, that player does not perform their action."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Librarian', 'Resistance')

    def set_actions(self):
        self.action_windows = [False, True, True, False]
        self.past_targets = [self]
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>silence` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_silence(self, silenced_player):
        silenced_player.silence()
        await self.member.dm_channel.send(f'You have silenced {silenced_player.name}.')
        self.has_action = False

"""Spy Roles"""

class Spy(Player):

    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Spy', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')

class Assassin(Player):
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Assassin', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')

    async def do_action(self):
        self.has_action = True
        await self.game.general_channel.send('There have been 3 successful missions. Assassin, please choose another player using the `>>assassinate` command.')
        while (self.has_action == True) and (self.game.skip_night_actions == False):
            await asyncio.sleep(1)

    async def do_assassination(self, assassinated_player):
        if assassinated_player.role == 'Commander':
            self.game.completed = True
            await self.game.general_channel.send('The game has ended—the Spies have won!\nThe Assassin has killed the Commander.')
        self.has_action = False

class False_Commander(Player):
    
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'False Commander', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')

class Organizer(Player):

    """Organizer — You know every player's role."""           # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Organizer', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}\nTheir respective roles are: {self.game.player_spy_roles}')
        await self.member.dm_channel.send(f'The Resistance in this game are: {self.game.get_resistance_names()}\nTheir respective roles are: {self.game.player_resistance_roles}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

class Bomber(Player):

    """Bomber — The first time you >>mission success, during the next mission, a random Resistance player on the mission team cannot >>mission success."""          # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Bomber', 'Spy')
 
    def set_actions(self):
        self.action_windows = [True, True, True, True]
        self.past_targets = []
        self.has_action = True
        self.set_bomb = False

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    async def do_action(self):
        # check if bomb set or bomb triggered
        if self.set_bomb:
            temp_team = self.game.get_current_team()
            random.shuffle(temp_team)
            for temp_player in temp_team:
                if temp_player.alignment == 'Resistance' and (temp_player.possible_mission_cards[0] == True):
                    temp_player.block_success()
                    break
            self.set_bomb = False
            await self.member.dm_channel.send('Your set bomb has gone off!')
        elif self.silenced == True and self.has_action:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
        elif self.has_action and (self in self.game.missioner.recent_conducted_success):
            self.set_bomb = True
            self.has_action = False
            await self.member.dm_channel.send('Your bomb has been set!')

class Martyr(Player):

    """Martyr — The first time you >>mission fail, everyone also >>mission fail even if they cannot, except for the Angel."""           # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Martyr', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    async def do_action(self):
        if self.has_action == False: return
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        if (self in self.game.missioner.conducted_fail):
            for x in range(len(self.game.missioner.conducted_success)):
                self.game.missioner.conducted_fail.append(self.game.missioner.conducted_success.pop())
            for x in range(len(self.game.missioner.conducted_switch)):
                self.game.missioner.conducted_fail.append(self.game.missioner.conducted_switch.pop())
            self.has_action = False
            await self.member.dm_channel.send('Your ability has been triggered!')

class Angel(Player):

    """Angel — As long as there is at least one >>mission fail, you always >>mission success."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Angel', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')
        
    async def do_action(self):
        if self in self.game.missioner.conducted_success: return
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        elif len(self.game.missioner.conducted_fail) >= 2:
            self.game.missioner.conducted_fail.remove(self)
            self.game.missioner.conducted_success.append(self)
            await self.member.dm_channel.send('Your ability has been triggered! Your `>>mission fail` has been swapped to `>>mission success`.')

class Spy_Reverser(Player):

    """Spy Reverser — You can >>mission switch to swap the outcome of the mission. You cannot >>mission fail."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Spy Reverser', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')
        
    def set_possible_mission_cards(self):
        self.possible_mission_cards = [True, False, True]

class Timekeeper(Player):

    """Timekeeper — If you >>vote reject during the 5th vote of a round, everyone >>vote reject."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Timekeeper', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        if self.game.rejected_team_count == 4 and (self in self.game.voter.voted_reject):
            for temp_player in self.game.voter.voted_accept:
                self.game.voter.voted_reject.append(self.game.voter.voted_accept.pop())
            await self.member.dm_channel.send(f'Your ability has been triggered!')

class Mad_Scientist(Player):

    """Mad Scientist — At the end of rounds 2 and 3, you must privately choose a player.
                       During the next round, they can >>mission switch but cannot >>mission success."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Mad Scientist', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    def set_actions(self):
        self.action_windows = [False, True, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>experiment` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_experiment(self, taught_player):
        taught_player.teach_switch()
        taught_player.block_success()
        await self.member.dm_channel.send(f'You have taught {taught_player.name} `>>mission switch` and blocked `>>mission success`.')
        self.has_action = False

class Silencer(Player):

    """Silencer — At the end of rounds 1, 2, and 3, you must pick another player. During their next action window, that player does not perform their action."""            # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Silencer', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    def set_actions(self):
        self.action_windows = [True, True, True, False]
        self.past_targets = [self]
        self.has_action = False

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
        self.has_action = True
        await self.member.dm_channel.send('Please choose another player using the `>>silence` command.')
        while (self.has_action == True) and (self.game.skip_night_action == False):
            await asyncio.sleep(1)
        self.has_action = False

    async def do_silence(self, silenced_player):
        silenced_player.silence()
        await self.member.dm_channel.send(f'You have silenced {silenced_player.name}.')
        self.has_action = False

class Victimizer(Player):

    """Victimizer — The first time, you >>mission success, during their next action window, every player on your team does not perform their action."""          # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Victimizer', 'Spy')
 
    def set_actions(self):
        self.action_windows = [True, True, True, True]
        self.past_targets = []
        self.has_action = True

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    async def do_action(self):
        if self.silenced == True and self.has_action:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
        elif self.has_action and (self in self.game.missioner.recent_conducted_success):
            for temp_player in self.game.missioner.recent_conducted_success:
                temp_player.silence()
            for temp_player in self.game.missioner.recent_conducted_fail:
                temp_player.silence()
            for tmep_player in self.game.missioner.recent_conducted_switch:
                temp_player.silence()
            self.has_action = False
            await self.member.dm_channel.send('Your ability has been triggered!')

class Spy_Clown(Player):

    """Clown — You do not learn your alignment until the end of round 3."""         # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Spy Clown', 'Spy')

    def set_believed_role(self):
        self.believed_role = 'Clown'

    async def get_starting_info(self):
        await self.member.create_dm()
        await self.member.dm_channel.send('—————— New Game ——————')
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role}.')

    def set_actions(self):
        self.action_windows = [False, False, True, False]
        self.past_targets = []
        self.has_action = False

    async def do_action(self):
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role} on the {self.alignment} side.')
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

class Usurper(Player):

    """Usurper — The first time you vote with all of the Resistance, everyone's vote is swapped."""         # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Usurper', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    async def do_action(self):
        if self.has_action == False: return
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
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

    """Muckraker — Whenever you vote with all of the spies, you and a random Resistance player swap votes."""           # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Muckraker', 'Spy')

    async def get_starting_info(self):
        await super().get_starting_info()
        await self.member.dm_channel.send(f'The Spies in this game are: {self.game.get_spy_names()}')
        await self.member.dm_channel.send(f'A safe role is {self.game.all_resistance_roles[self.game.spy_indices.index(self.game.players.index(self))]}')

    async def do_action(self):
        if self.silenced == True:
            self.silenced = False
            await self.member.dm_channel.send('You were silenced this round.')
            return
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

    """Drunken Spy — You think you are the Informant but the two roles are actually in the game."""         # completed
        
    def __init__(self, game, member, name, id_num):
        super().__init__(game, member, name, id_num, 'Drunken Spy', 'Spy')

    def set_believed_role(self):
        self.believed_role = 'Informant'

    async def get_starting_info(self):
        await self.member.create_dm()
        await self.member.dm_channel.send('—————— New Game ——————')
        await self.member.dm_channel.send(f'{self.name}: you are the {self.believed_role} on the Resistance side.')
        await self.member.dm_channel.send(f'The following Spy roles are not in this game: {random.sample(self.game.player_spy_roles, 2)}')
