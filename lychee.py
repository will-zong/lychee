import discord
import os
import random

from discord.ext import commands, tasks
from dotenv import load_dotenv

from game import Game

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_LYCHEE')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix='>>')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('No ongoing game!'))
    print('Bot is ready')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Sorry, that does not seem to be a command. Check `>>help` for every command that I recognize!')
    elif isinstance(error, commands.MissingRole):
        await ctx.send('Sorry, it seems that you do not have permission to use that command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Sorry, it seems that you have forgotting to include a required argument. Please try again!')
    else:
        await ctx.send(f'An unhandled error has occurred.\n{error}')
        print(error)

game = None
general_channel = None

@client.command(help='Starts a game')
@commands.has_role('Admin')
async def start(ctx, *, player_mentions):
    """Starts a game.

    Parameters
    ----------
    player_mentions : str
        A list of each person's mention that you want in the game
    """
    global game
    global general_channel
    # check for ongoing game
    if game == None or game.completed == True:
        # check that the string actually contains individual mentions then convert to ID numbers
        temp_player_mentions = player_mentions.split()
        player_id_nums = []
        for temp_mention in temp_player_mentions:
            if temp_mention.startswith('<@') == False or temp_mention[-1:] != '>':
                await ctx.send('Please mention the players you want in this game. Be sure to seperate each mention with a space!')
                return
            else:
                temp_id_num = temp_mention[:-1]
                if temp_id_num.startswith('<@!'):
                    temp_id_num = temp_id_num[3:]
                else:
                    temp_id_num = temp_id_num[2:]
                player_id_nums.append(int(temp_id_num))
        # get current guild
        for temp_guild in client.guilds:
            if temp_guild.name == GUILD:
                guild = temp_guild
                break
        general_channel = ctx.channel
        game = Game(guild, client, general_channel, player_id_nums)
        await game.finish_initialization()
        await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Round 1!'))
    else:
        await ctx.send('Sorry, there is currently an ongoing game.')

@client.command(help='Proposes a team')
async def team(ctx, *, team_player_names):
    """Proposes a team.

    Parameters
    ----------
    team_player_names : str
        A list of each person's name that you want on the team
    """
    global game
    global general_channel
    # check that all conditions are met
    if game == None:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 0:
        await ctx.send('Sorry, it is not the team building phase.')
    elif not game.is_team_leader(ctx.author):
        await ctx.send('Sorry, you are not the current team leader.')
    elif ctx.channel != general_channel:
        await ctx.send('Please use `>>team` in the main channel.')
    else:
        # check that the string actually contains player names
        temp_player_names = team_player_names.split()
        for temp_name in temp_player_names:
            if game.is_player(temp_name) == False:
                await ctx.send('Please name the players you want on this team. Be sure to separate each name with a space!')
                return
        if len(temp_player_names) != int(game.round_tracker.get_team_size()):
            await ctx.send(f'Sorry, this team requires {int(game.round_tracker.get_team_size())} players!')
            return
        for temp_player in game.get_current_team():
            if temp_player.can_be_on_current_mission == False:
                await ctx.send(f'Sorry, a player you have added to your team cannot be on any team this round.')
                return
        await client.change_presence(activity=discord.Game(f'Round {game.round_tracker.get_round()} Voting!'))
        await game.start_vote(temp_player_names)

@client.command(help='Proposes a team')
@commands.has_role('Admin')
async def team_override(ctx, *, team_player_names):
    """Proposes a team but circumvents the team leader condition.

    Parameters
    ----------
    team_player_names : str
        A list of each person's name that you want on the team
    """
    global game
    global general_channel
    # check that all conditions are met
    if game == None:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 0:
        await ctx.send('Sorry, it is not the team building phase.')
    elif ctx.channel != general_channel:
        await ctx.send('Please use `>>team_overrid` in the main channel.')
    else:
        # check that the string actually contains player names
        temp_player_names = team_player_names.split()
        for temp_name in temp_player_names:
            if game.is_player(temp_name) == False:
                await ctx.send('Please name the players you want on this team. Be sure to separate each name with a space!')
                return
        if len(temp_player_names) != int(game.round_tracker.get_team_size()):
            await ctx.send(f'Sorry, this team requires {int(game.round_tracker.get_team_size())} players!')
            return
        for temp_player in game.get_current_team():
            if temp_player.can_be_on_current_mission == False:
                await ctx.send(f'Sorry, a player you have added to your team cannot be on any team this round.')
                return
        await client.change_presence(activity=discord.Game(f'Round {game.round_tracker.get_round()} Voting!'))
        await game.start_vote(temp_player_names)

@client.command(help='Submits a vote: accept or reject')
async def vote(ctx, vote):
    global game
    global general_channel
    # check that all conditions are met
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 1:
        await ctx.send('Sorry, it is not the voting phase.')
    elif game.get_player_from_member(ctx.author).voted:
        await ctx.send('Sorry, you have already voted.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>vote` in you private messages with me.')
    elif 'accept'.startswith(vote.lower()) or vote.lower().startswith('accept'):
        await general_channel.send(f'{game.get_player_from_member(ctx.author).name} has voted.')
        await game.voter.record_vote(game.get_player_from_member(ctx.author), 0)
    elif 'reject'.startswith(vote.lower()) or vote.lower().startswith('reject'):
        await general_channel.send(f'{game.get_player_from_member(ctx.author).name} has voted.')
        await game.voter.record_vote(game.get_player_from_member(ctx.author), 1)
    else:
        await ctx.send('Please either `>>vote accept` or `>>vote reject`.')

@client.command(help='Ends the current vote')
@commands.has_role('Admin')
async def end_vote(ctx):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 1:
        await ctx.send('Sorry, it is not the voting phase.')
    else:
        for temp_player in game.players:
            if temp_player.voted == False:
                await general_channel.send(f'{temp_player.name} has voted.')
                await game.voter.record_vote(temp_player, 0)

@client.command(help='Conducts a mission: success, fail, or switch')
async def mission(ctx, card):
    global game
    global general_channel
    # check that all condiitons are met
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 2:
        await ctx.send('Sorry, it is not the mission conducting phase.')
    elif not game.get_player_from_member(ctx.author).on_current_team:
        await ctx.send('Sorry, you are not on the current team.')
    elif game.get_player_from_member(ctx.author).completed_mission:
        await ctx.send('Sorry, you have already submitted.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>mission` in you private messages with me.')
    elif 'success'.startswith(card.lower()) or card.lower().startswith('success'):
        if game.get_player_from_member(ctx.author).possible_mission_cards[0]:
            await general_channel.send(f'{game.get_player_from_member(ctx.author).name} has submitted for the mission.')
            await game.missioner.record_mission_card(game.get_player_from_member(ctx.author), 0) 
        else:
            await ctx.send('Sorry, you currently cannot `>>mission success`.')
    elif 'fail'.startswith(card.lower()) or card.lower().startswith('fail'):
        if game.get_player_from_member(ctx.author).possible_mission_cards[1]:
            await general_channel.send(f'{game.get_player_from_member(ctx.author).name} has submitted for the mission.')
            await game.missioner.record_mission_card(game.get_player_from_member(ctx.author), 1)
        else:
            await ctx.send('Sorry, you currently cannot `>>mission fail`.')
    elif 'switch'.startswith(card.lower()) or card.lower().startswith('switch'):
        if game.get_player_from_member(ctx.author).possible_mission_cards[2]:
            await general_channel.send(f'{game.get_player_from_member(ctx.author).name} has submitted for the mission.')
            await game.missioner.record_mission_card(game.get_player_from_member(ctx.author), 2)
        else:
            await ctx.send('Sorry, you currently cannot `>>mission switch`.')
    else:
        await ctx.send('Please `>>mission success`, `>>mission fail`, or `>>mission switch`.')

@client.command(help='Ends the current mission')
@commands.has_role('Admin')
async def end_mission(ctx):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 2:
        await ctx.send('Sorry, it is not the mission conducting phase.')
    else:
        for temp_player in game.players:
            if temp_player.on_current_team == True and temp_player.completed_mission == False:
                if temp_player.alignment == 'Resistance':
                    if temp_player.possible_mission_cards[0]:
                        await general_channel.send(f'{temp_player.name} has submitted for the mission.')
                        await game.missioner.record_mission_card(temp_player, 0)
                    elif temp_player.possible_mission_cards[2]:
                        await general_channel.send(f'{temp_player.name} has submitted for the mission.')
                        await game.missioner.record_mission_card(temp_player, 2)
                    else:
                        await general_channel.send(f'{temp_player.name} has submitted for the mission.')
                        await game.missioner.record_mission_card(temp_player, 1)
                else:
                    if temp_player.possible_mission_cards[1]:
                        await general_channel.send(f'{temp_player.name} has submitted for the mission.')
                        await game.missioner.record_mission_card(temp_player, 1)
                    elif temp_player.possible_mission_cards[2]:
                        await general_channel.send(f'{temp_player.name} has submitted for the mission.')
                        await game.missioner.record_mission_card(temp_player, 2)
                    else:
                        await general_channel.send(f'{temp_player.name} has submitted for the mission.')
                        await game.missioner.record_mission_card(temp_player, 0)

@client.command(help='Gambles two players are not both Spies', hidden=True)
async def gamble(ctx, *, gambled_player_names):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).role != 'Gambler':
        await ctx.send('Sorry, you are not the Gambler.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>gamble` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already gambled this round or have not yet been prompted to gamble.')
    else:
        # check that the string actually contains player names
        temp_player_names = gambled_player_names.split()
        for temp_name in temp_player_names:
            if game.is_player(temp_name) == False:
                await ctx.send('Please name the players you want to gamble on. Be sure to separate the names with a space!')
                return
        if len(temp_player_names) != 2:
            await ctx.send('Sorry, you must gamble on 2 players!')
        elif (game.get_player_from_member(ctx.author).name in temp_player_names):
            await ctx.send('Sorry, you cannot gamble on yourself.')
        elif temp_player_names[0] == temp_player_names[1]:
            await ctx.send('Please pick two different people.')
        else: 
            gambled_players = []
            gambled_players.append(game.get_player_from_name(temp_player_names[0]))
            gambled_players.append(game.get_player_from_name(temp_player_names[1]))
            await game.get_player_from_member(ctx.author).do_gamble(gambled_players)

@client.command(help='Arrests a player', hidden=True)
async def arrest(ctx, arrested_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).role != 'Officer':
        await ctx.send('Sorry, you are not the Officer.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>arrest` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already arrested this round or have not yet been prompted to arrest.')
    elif game.is_player(arrested_player) == False:
        await ctx.send('Please name the player you want to arrest.')
    elif (game.get_player_from_name(arrested_player) in game.get_player_from_member(ctx.author).past_targets):
        await ctx.send('Sorry, you have already targeted that player before. Please target someone new.')
    else: 
        await game.get_player_from_member(ctx.author).do_arrest(game.get_player_from_name(arrested_player))
        
@client.command(help='Sees a player\'s alignment', hidden=True)
async def see(ctx, seen_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).believed_role != 'Psychic':
        await ctx.send('Sorry, you are not the Psychic.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>see` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already seen this round or have not yet been prompted to see.')
    elif game.is_player(seen_player) == False:
        await ctx.send('Please name the player you want to see.')
    elif (game.get_player_from_name(seen_player) in game.get_player_from_member(ctx.author).past_targets):
        await ctx.send('Sorry, you have already targeted that player before. Please target someone new.')
    else:
        await game.get_player_from_member(ctx.author).do_see(game.get_player_from_name(seen_player))

@client.command(help='Skips the current action')
@commands.has_role('Admin')
async def skip_action(ctx):
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the action phase.')
    else:
        game.skip_night_action = True
        await ctx.send('Action skipped!')

@client.command(help='Ends the game')
@commands.has_role('Admin')
async def end_game(ctx):
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    else:
        game.success_count = 3
        await game.check_end_game()

@client.command(help='Clears all pins')
@commands.has_role('Admin')
async def clear_pins(ctx):
    await ctx.send('Please wait.')
    messages = await ctx.pins()
    for message in messages:
        if message.author.bot == True:
            await message.unpin()
    await ctx.send('All pins have been cleared!')

client.run(TOKEN)