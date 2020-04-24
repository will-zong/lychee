import discord
import random

from player import *
from voter import *

class Game():

    """Stores information about the overall game.

    Parameters
    ----------
    guild : discord.Guild
        The current guild
    client : discord.Client
        Lychee (The current bot)
    general_channel : discord.Channel
        The public channel of the game
    player_id_nums : List[int]
        A list of each player's id number

    Attributes
    ----------
    player_count : int
        How many players are in the game
    round_tracker : Round_Tracker
        The Round Tracker initialized with the correct number of players
    player_members : List[discord.Member]
        Each player's member
    player_names : List[str]
        Each player's name
    player_resistance_roles : List[str]
        The resistance roles in the current game
    player_spy_roles : List[str]
        The spy roles in the current game
    all_resistance_roles : List[str]
        The resistance roles not in the game            ### Update when changing script
    all_spy_roles : List[str]
        The spy roles not in the game                   ### Update when changing script
    spy_indices : List[int] — len()=self.num_spies
        The indicies of the spy players in any "player" List
    players : List[Players]
        The players in the current game
    team_leader_index : int
        The index of the current team leader
    voter : Voter
        Handles all votes
    rejected_team_count: int
        The number of rejected teams
    missioner : Missioner
        Handles all missions
    success_count : int
        The number of successful missions
    fail_count : int
        The number of failed missions
    current_window : int
        Which window it currently is: 0=team_building, 1=voting, 2=mission, 3=night_actions
    skip_night_action : bool
        Whether or not to skip the current night action
    completed : bool
        If the game is done
    guild
    client
    general_channel
    player_id_nums
    """

    def __init__(self, guild, client, general_channel, player_id_nums):
        self.guild = guild
        self.client = client
        self.general_channel = general_channel
        self.player_id_nums = player_id_nums
    
    async def finish_initialization(self):
        # initialize Round Tracker
        self.player_count = len(self.player_id_nums) # int
        if self.player_count < 5:
            self.round_tracker = Round_Tracker(4) 
        else:
            self.round_tracker = Round_Tracker(self.player_count)
        self.player_members = [] # List[discord.Member]
        self.player_names = [] # List[str]
        self.player_resistance_roles = [] # List[str]
        self.player_spy_roles = [] # List[str]
        # randomize roles and spies
        self.all_resistance_roles = ['President', 'Dueler', 'Officer', 'Contrarian',
                                    'Informant', 'Psychic', 'Witch', 'Insider', 'Resistance Reverser', 'Gambler']
        self.all_spy_roles = ['Organizer', 'Bomber', 'Martyr', 'Usurper', 'Muckraker',
                             'Drunken Spy', 'Angel', 'Spy Reverser']
        # random.shuffle(self.all_resistance_roles)
        random.shuffle(self.all_spy_roles)
        if self.player_count == 5 or self.player_count == 6:
            self.num_spies = 2 
        elif self.player_count == 7 or self.player_count == 8:
            self.num_spies = 3
        elif self.player_count == 9 or self.player_count == 10:
            self.num_spies = 4
        else:
            self.num_spies = 0 # int
        self.spy_indices = random.sample(range(0, self.player_count-1), self.num_spies) # List[int] — len()=self.num_spies
        # initialize Players
        self.players = [] # List[Players]
        for x in range(len(self.player_id_nums)):
            temp_member = self.guild.get_member(self.player_id_nums[x])
            self.player_members.append(temp_member)
            self.player_names.append(temp_member.display_name)
            if (x in self.spy_indices):
                temp_role = self.all_spy_roles.pop()
                self.player_spy_roles.append(temp_role)
            else:
                temp_role = self.all_resistance_roles.pop()
                self.player_resistance_roles.append(temp_role)
            self.players.append(create_player(temp_role, self, self.player_members[x], self.player_names[x], self.player_id_nums[x]))
        for temp_player in self.players: 
            await temp_player.get_starting_info()
        # give @Player role to all players
        for role in self.guild.roles:
            if role.name == 'Player':
                for temp_member in self.player_members:
                    await temp_member.add_roles(role)
                break
        self.team_leader_index = 0
        # initialize Voter and Missioner
        self.voter = Voter(self)
        self.rejected_team_count = 0
        self.missioner = Missioner(self)
        self.success_count = 0
        self.fail_count = 0
        self.current_window = 0
        self.skip_night_actions = False
        self.completed = False
        await self.general_channel.send(f'A game has been started! There are {self.player_count - self.num_spies} Resistance members and {self.num_spies} Spy members.')
        # pin message
        messages = await self.general_channel.history(limit=5).flatten()
        for message in reversed(messages):
            if message.content == (f'A game has been started! There are {self.player_count - self.num_spies} Resistance members and {self.num_spies} Spy members.'):
                await message.pin()
        await self.start_team_building()

    def is_player(self, name):
        for temp_name in self.player_names:
            if temp_name == name:
                return True
        return False

    def get_spy_names(self):
        spy_names = []
        for index in self.spy_indices:
            spy_names.append(self.player_names[index])
        return spy_names
    
    def get_round(self):
        return self.round_tracker.get_round()

    def next_round(self):
        self.round_tracker.next_round()

    def get_team_size(self):
        return self.round_tracker.get_team_size()

    def next_team_leader(self):
        self.team_leader_index += 1
        if self.team_leader_index == self.player_count:
            self.team_leader_index = 0

    def is_team_leader(self, member):
        if self.player_members[self.team_leader_index] == member:
            return True
        return False

    def set_window(self, window):
        self.current_window = window

    def get_current_team(self):
        current_team = []
        for temp_player in self.players:
            if temp_player.on_current_team:
                current_team.append(temp_player)
        return current_team

    def get_player_from_member(self, member):
        if member in self.player_members:
            return self.players[self.player_members.index(member)]
        return None

    def get_player_from_name(self, name):
        if name in self.player_names:
            return self.players[self.player_names.index(name)]
        return None

    async def start_team_building(self):
        # open and announce team building window
        self.set_window(0)
        self.next_team_leader()
        await self.general_channel.send(f'Players, prepare to conduct Mission {self.get_round()}.\n{int(self.get_team_size())} players will be on this team.\n'
                                      + f'Your team leader is {self.player_names[self.team_leader_index]}.')
        if self.get_team_size() == 4.5 or self.get_team_size() == 5.5:
            await self.general_channel.send('This mission requires 2 `>>mission fail`s to fail.')
        # pin message
        messages = await self.general_channel.history(limit=5).flatten()
        for message in reversed(messages):
            if message.content == (f'Players, prepare to conduct Mission {self.get_round()}.\n{int(self.get_team_size())} players will be on this team.\n'
                                 + f'Your team leader is {self.player_names[self.team_leader_index]}.'):
                await message.pin()
                return

    async def start_vote(self, team_player_names):
        """Starts a vote.

        Parameters
        ----------
        team_player_names : List[str]
            A List of each person's name that you want on the team
        """
        # add players to the team
        for temp_name in team_player_names:
            self.get_player_from_name(temp_name).add_to_team()
        # convert Players to names to display
        current_team_names = []
        for temp_player in self.get_current_team():
            current_team_names.append(temp_player.name)
        # open and announce voting window
        self.set_window(1)
        for temp_member in self.player_members:
            await temp_member.dm_channel.send(f'Please `>>vote accept` or `>>vote reject` on the proposed team: {current_team_names}')
        await self.general_channel.send(f'{self.player_names[self.team_leader_index]} has proposed the following team: {current_team_names}\n'
                                       + 'Please private message Lychee your vote using the `>>vote` command.')
        # pin message
        messages = await self.general_channel.history(limit=5).flatten()
        for message in reversed(messages):
            if message.content == (f'{self.player_names[self.team_leader_index]} has proposed the following team: {current_team_names}\n'
                                  + 'Please private message Lychee your vote using the `>>vote` command.'):
                await message.pin()

    async def rejected_team(self):
        self.rejected_team_count += 1
        # convert Players to names to display
        voted_accept_names = []
        for temp_player in self.voter.voted_accept:
            voted_accept_names.append(temp_player.name)
        voted_reject_names = []
        for temp_player in self.voter.voted_reject:
            voted_reject_names.append(temp_player.name)
        await self.general_channel.send(f'The team was rejected.\nAccepted: {voted_accept_names}\nRejected: {voted_reject_names}\n' +
                                        f'There have been {self.rejected_team_count} rejected teams.')
        # reset
        for temp_player in self.players:
            temp_player.soft_reset()
        self.voter.reset()
        await self.check_end_game()
        if self.completed == False:
            await self.start_team_building()

    async def start_mission(self):
        """Starts conducting a mission."""
        # convert Players to names to display
        voted_accept_names = []
        for temp_player in self.voter.voted_accept:
            voted_accept_names.append(temp_player.name)
        voted_reject_names = []
        for temp_player in self.voter.voted_reject:
            voted_reject_names.append(temp_player.name)
        await self.general_channel.send(f'The team was accepted.\nAccepted: {voted_accept_names}\nRejected: {voted_reject_names}')
        await self.do_pre_mission_actions()
        # reset and open mission window
        self.voter.reset()
        self.set_window(2)
        for temp_player in self.get_current_team():
            await temp_player.member.dm_channel.send(f'You are on the Mission {self.get_round()} team. Please `>>mission success`, `>>mission fail`, or `>>mission switch`')
        await self.general_channel.send(f'Team members, prepare to conduct Mission {self.get_round()}.\nPlease message me privately using the `>>mission` command.')
        await self.client.change_presence(activity=discord.Game(f'Conducting Mission {self.get_round()}!'))

    async def end_mission(self):
        """Ends a mission and determines the result out of 12 possiblities.
        determine number of switches (0/2, 1)
            determine if it is a double-fail round (yes, no)
                determine number of fails to determine result (2+, 1, 0)"""
        if len(self.missioner.conducted_switch) == 0 or len(self.missioner.conducted_switch) == 2:
            if self.get_team_size() == 4.5 or self.get_team_size() == 5.5:
                if len(self.missioner.conducted_fail) >= 2:
                    # mission fail with 2+ fails and 0/2 switches
                    await self.general_channel.send(f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.'):
                            await message.pin()
                    self.fail_count += 1
                elif len(self.missioner.conducted_fail) == 1:
                    # mission success with 1 fail and 0/2 switches
                    await self.general_channel.send(f'The mission has succeeded with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switches.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has succeeded with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switches.'):
                            await message.pin()
                    self.success_count += 1
                else:
                    # mission success with 0 fails and 0/2 switches
                    await self.general_channel.send(f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.'):
                            await message.pin()
                    self.success_count += 1
            else:
                if len(self.missioner.conducted_fail) >= 2:
                    # mission fail with 2+ fails and 0/2 switch
                    await self.general_channel.send(f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.'):
                            await message.pin()
                    self.fail_count += 1
                elif len(self.missioner.conducted_fail) == 1:
                    # mission fail with 1 fail and 0/2 switch
                    await self.general_channel.send(f'The mission has failed with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switches.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has failed with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switches.'):
                            await message.pin()
                    self.fail_count += 1
                else:
                    # mission success with 0 fails and 0/2 switch
                    await self.general_channel.send(f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switches.'):
                            await message.pin()
                    self.success_count += 1
        else:
            if self.get_team_size() == 4.5 or self.get_team_size() == 5.5:
                if len(self.missioner.conducted_fail) >= 2:
                    # mission success with 2+ fails and 1 switch
                    await self.general_channel.send(f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.'):
                            await message.pin()
                    self.success_count += 1
                elif len(self.missioner.conducted_fail) == 1:
                    # mission fail with 1 fail and 1 switch
                    await self.general_channel.send(f'The mission has failed with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switch.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has failed with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switch.'):
                            await message.pin()
                    self.fail_count += 1
                else:
                    # mission fail with 0 fails and 1 switch
                    await self.general_channel.send(f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.'):
                            await message.pin()
                    self.fail_count += 1
            else:
                if len(self.missioner.conducted_fail) >= 2:
                    # mission success with 2+ fails and 1 switch
                    await self.general_channel.send(f'The mission has succeeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has suceeded with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.'):
                            await message.pin()
                    self.success_count += 1
                elif len(self.missioner.conducted_fail) == 1:
                    # mission success with 1 fail and 1 switch
                    await self.general_channel.send(f'The mission has suceeded with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switch.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has suceeded with {len(self.missioner.conducted_fail)} fail and {len(self.missioner.conducted_switch)} switch.'):
                            await message.pin()
                    self.success_count += 1
                else:
                    # mission fail with 0 fails and 1 switch
                    await self.general_channel.send(f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.')
                    # pin message
                    messages = await self.general_channel.history(limit=5).flatten()
                    for message in reversed(messages):
                        if message.content == (f'The mission has failed with {len(self.missioner.conducted_fail)} fails and {len(self.missioner.conducted_switch)} switch.'):
                            await message.pin()
                    self.fail_count += 1
        # reset
        for temp_player in self.players:
            temp_player.hard_reset()
        self.missioner.reset()
        await self.check_end_game()
        if self.completed == False:
            await self.do_night_actions()

    async def do_post_vote_actions(self):
        # if Usurper exists, do action
        # if Contrarian exists, do_action
        # if Muckraker exists, do action
        usurper_player = None
        contrarian_player = None
        muckraker_player = None
        for temp_player in self.players:
            if temp_player.role == 'Usurper':
                usurper_player = temp_player
            elif temp_player.role == 'Contrarian':
                contrarian_player = temp_player
            elif temp_player.role == 'Muckraker':
                muckraker_player = temp_player
        if usurper_player != None:
            await usurper_player.do_action()
        if contrarian_player != None:
            await contrarian_player.do_action()
        if muckraker_player != None:
            await muckraker_player.do_action()

    async def do_pre_mission_actions(self):
        # if Dueler is on the team, do action
        # Bomber do action
        dueler_player = None
        bomber_player = None
        for temp_player in self.players:
            if temp_player.role == 'Dueler':
                dueler_player = temp_player
            elif temp_player.role == 'Bomber':
                dueler_player = temp_player
        if dueler_player != None and (dueler_player in self.get_current_team()):
            await dueler_player.do_action()
        if bomber_player != None:
            await bomber_player.do_action()

    async def do_post_mission_actions(self):
        # if Martyr is on the team, do action
        # if Angel is on the team, do action
        martyr_player = None
        angel_player = None
        for temp_player in self.players:
            if temp_player.role == 'Martyr':
                martyr_player = temp_player
            elif temp_player.role == 'Angel':
                angel_player = temp_player
        if martyr_player != None and (martyr_player in self.get_current_team()):
            await martyr_player.do_action()
        if angel_player != None and (angel_player in self.get_current_team()):
            await angel_player.do_action()

    async def do_night_actions(self):
        # open and announce night action window
        self.set_window(3)
        await self.general_channel.send('Players, if appropriate, please wait until queued to do your action in your private messages with me.')
        await self.client.change_presence(activity=discord.Game(f'End of Round {self.get_round()} actions!'))
        # do actions
        action_count = 0
        for temp_player in self.players:
            self.skip_night_action = False
            if temp_player.action_windows[self.get_round()-1]:
                action_count += 1
                await temp_player.do_action()
        await asyncio.sleep(15*(4-action_count))
        await self.general_channel.send('All night actions have been performed!')
        # end round
        self.set_window(0)
        self.next_round()
        await self.start_team_building()

    async def check_end_game(self):
        """Checks if the game is over. If it is over, cleans everything up."""
        if self.success_count >= 3:
            self.completed = True
            await self.general_channel.send('The game has ended—the Resistance has won!\nThere have been 3 successful missions.')
        elif self.fail_count >= 3:
            self.completed = True
            await self.general_channel.send('The game has ended—the Spies has won!\nThere have been 3 failed missions.')
        elif self.rejected_team_count >= 5:
            self.completed = True
            await self.general_channel.send('The game has ended—the Spies has won!\nThere have been 5 rejected teams.')
        if self.completed == True:
            # reveal all player roles and alignments
            tell_all_roles = ''
            for temp_player in self.players:
                tell_all_roles += f'{temp_player.name} was the {temp_player.role} on the {temp_player.alignment} side.\n'
            await self.general_channel.send(tell_all_roles[:-1])
            await asyncio.sleep(45)
            # remove @Player role
            for role in self.guild.roles:
                if role.name == 'Player':
                    player_role = role
            for temp_player in self.players:
                await temp_player.member.remove_roles(player_role)
            # unpin all messages
            messages = await self.general_channel.pins()
            for message in messages:
                if message.author.bot == True:
                    await message.unpin()
            await self.client.change_presence(status=discord.Status.idle, activity=discord.Game('No ongoing game!'))

class Round_Tracker():

    """Stores information about the team size for every round

    Parameters
    ----------
    player_count : int
        The number of players in the game
    Attributes
    ----------
    current_round : int
        Which round it currently is
    team_sizes : List[List[float, float, float, float]]
        Stores the team size for each round (1-5) at each player count (4, 5-10)
        4.5/5.5 represent that two mission fail cards are required for the mission to fail
        player_count = 4 is used for testing purposes only
    player_count
    """

    def __init__(self, player_count):
        self.player_count = player_count
        self.current_round = 1 # int
        self.team_sizes =  [[1.0, 1.0, 1.0, 1.0, 1.0], 
                            [2.0, 3.0, 2.0, 3.0, 3.0], 
                            [2.0, 3.0, 4.0, 3.0, 3.0], 
                            [2.0, 3.0, 3.0, 4.5, 4.0], 
                            [3.0, 4.0, 4.0, 5.5, 5.0], 
                            [3.0, 4.0, 4.0, 5.5, 5.0], 
                            [3.0, 4.0, 4.0, 5.5, 5.0]] # List[List[float, float, float, float, float]]

    def get_round(self):
        return self.current_round

    def next_round(self):
            self.current_round += 1

    def get_team_size(self):
        return self.team_sizes[(self.player_count-4)][(self.current_round-1)]

def create_player(role, game, member, name, id_num):
    if role == 'President':
        return President(game, member, name, id_num)
    elif role == 'Gambler':
        return Gambler(game, member, name, id_num)
    elif role == 'Dueler':
        return Dueler(game, member, name, id_num)
    elif role == 'Officer':
        return Officer(game, member, name, id_num)
    elif role == 'Contrarian':
        return Contrarian(game, member, name, id_num)
    elif role == 'Informant':
        return Informant(game, member, name, id_num)
    elif role == 'Psychic':
        return Psychic(game, member, name, id_num)
    elif role == 'Witch':
        return Witch(game, member, name, id_num)
    elif role == 'Insider':
        return Insider(game, member, name, id_num)
    elif role == 'Resistance Reverser':
        return Resistance_Reverser(game, member, name, id_num)
    elif role == 'Organizer':
        return Organizer(game, member, name, id_num)
    elif role == 'Bomber':
        return Bomber(game, member, name, id_num)
    elif role == 'Martyr':
        return Martyr(game, member, name, id_num)
    elif role == 'Usurper':
        return Usurper(game, member, name, id_num)
    elif role == 'Muckraker':
        return Muckraker(game, member, name, id_num)
    elif role == 'Drunken Spy':
        return Drunken_Spy(game, member, name, id_num)
    elif role == 'Angel':
        return Angel(game, member, name, id_num)
    elif role == 'Spy Reverser':
        return Spy_Reverser(game, member, name, id_num)
    return None