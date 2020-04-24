import discord
import random

class Voter():

    """Stores information about a vote on a proposed team.

    Parameters
    ----------
    game : discord.Game
        The current game

    Attributes
    ----------
    voted_accept : List[Players]
        The players who have voted accept
    voted_reject : List[Players]
        The players who have voted reject
    recent_voted_accept : List[Players]
        The most recent copy of voted_accept
    recent_voted_reject : List[Players]
        The most recent copy of voted_reject
    game
    """

    def __init__(self, game):
        self.game = game
        self.voted_accept = []
        self.voted_reject = []
        self.recent_voted_accept = []
        self.recent_voted_reject = []

    async def record_vote(self, player, vote):
        """Records a vote.

        Parameters
        ----------
        player : discord.Player
            The player who voted
        vote : int
            The submitted vote: 0=accept, 1=reject
        """
        if vote == 0:
            self.voted_accept.append(player)
            player.set_done_voting()
            await player.member.dm_channel.send('Thank you for your `>>vote accept`.')
        else:
            self.voted_reject.append(player)
            player.set_done_voting()
            await player.member.dm_channel.send('Thank you for your `>>vote reject`.')
        await self.check_all_voted()

    async def check_all_voted(self):
        if len(self.voted_accept) + len(self.voted_reject) == self.game.player_count:
            random.shuffle(self.voted_accept)
            random.shuffle(self.voted_reject)
            await self.game.do_post_vote_actions() 
            random.shuffle(self.voted_accept)
            random.shuffle(self.voted_reject)
            if len(self.voted_accept) > len(self.voted_reject):
                await self.game.start_mission()
            else:
                await self.game.rejected_team()

    def reset(self):
        self.recent_voted_accept = self.voted_accept
        self.recent_voted_reject = self.voted_reject        
        self.voted_accept = []
        self.voted_reject = []

class Missioner():

    """Stores information about a mission

    Parameters
    ----------
    game : discord.Game
        The current game

    Attributes
    ----------
    conducted_success : List[Player]
        The players who have played a success card
    conducted_fail : List[Player]
        The players who have played a fail card
    conducted_switch : List[Player]
        The players who have played a switch card
    recent_conducted_success : List[Player]
        The most recent copy of conducted_success
    recent_conducted_fail : List[Player]
        The most recent copy of conducted_fail
    recent_conducted_switch : List[Player]
        The most recent copy of conducted_switch
    game
    """

    def __init__(self, game):
        self.game = game
        self.conducted_success = []
        self.conducted_fail = []
        self.conducted_switch = []
        self.recent_conducted_success = []
        self.recent_conducted_fail = []
        self.recent_conducted_switch = []

    async def record_mission_card(self, player, card):
        """Records a mission card.

        Parameters
        ----------
        player : discord.Player
            The player who voted
        vote : int
            The submitted vote: 0=success, 1=fail, 2=switch
        """
        if card == 0:
            self.conducted_success.append(player)
            player.set_done_missioning()
            await player.member.dm_channel.send('Thank you for your `>>mission success`.')
        elif card == 1:
            self.conducted_fail.append(player)
            player.set_done_missioning()
            await player.member.dm_channel.send('Thank you for your `>>mission fail`.')
        else:
            self.conducted_switch.append(player)
            player.set_done_missioning()
            await player.member.dm_channel.send('Thank you for your `>>mission switch`.')
        await self.check_all_conducted_mission() #TODO
        
    async def check_all_conducted_mission(self):
        if len(self.conducted_success) + len(self.conducted_fail) + len(self.conducted_switch) == int(self.game.get_team_size()):
            await self.game.do_post_mission_actions()
            await self.game.end_mission()

    def reset(self):
        self.recent_conducted_success = self.conducted_success
        self.recent_conducted_fail = self.conducted_fail
        self.recent_conducted_switch = self.conducted_switch
        self.conducted_success = []
        self.conducted_fail = []
        self.conducted_switch = []