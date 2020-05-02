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

@client.event
async def on_message(message):
    if message.content.startswith('>>'):
        await client.process_commands(message)
    if message.author != client.user and message.content.lower().find('lychee') != -1:
        affection = [':blush:', ':smiling_face_with_3_hearts:', ':kissing_heart:', ':star_struck:', ':flushed:', 
                     ':pleading_face:', ':hugging:', ':sneeze:', ':bow:', ':ok_woman:', ':star2:', ':sparkles:', 
                     ':revolving_hearts:', ':sparkling_heart:', ':receipt:', ':eyes:', ':grin:']
        validation = [':+1:', ':grinning:', ':blush:', ':clown:', ':fist:', ':raised_hands:', ':ok_hand:']
        greeting = [':partying_face:', ':wave:', ':star2:', ':sparkles:', ':dancer:', ':clown:', ':raised_hands:']
        confirmation = [':partying_face:', ':unicorn:', ':clown:', ':fist:', ':raised_hands:', ':ok_hand:']
        mischievious = [':zany_face:', ':stuck_out_tongue_winking_eye:', ':clown:', ':snake:', ':full_moon_with_face:',
                        ':star2:', ':sparkles:', ':tropical_drink:', ':fork_knife_plate:', ':joystick:']
        flirting = [':sweat:', ':eggplant:', ':fire:', ':hot_face:', ':triumph:', ':heart_eyes:', ':kissing_heart:', 
                    ':revolving_hearts:', ':sparkling_heart:', ':shushing_face:', ':wink:', ':yum:', ':smiling_imp:', 
                    ':fingers_crossed:', ':pray:', ':takeout_box:', ':peach:', ':beers:', ':clinking_glass:', ':fireworks:', 
                    ':closed_lock_with_key:', ':bangbang:', ':cupid:', ':love_letter:', ':spoon:', ':banana:', ':hot_pepper:']
        disgust = [':face_with_monocle:', ':scream:', ':cold_sweat:', ':receipt:', ':thinking:', ':upside_down:', 
                   ':sick:', ':face_vomiting:', ':ghost:', ':clown:', ':no_good:', ':facepalm:', ':thunder_cloud_rain:'
                   ':sos:', ':no_entry:', ':previous_track:', ':twisted_rightwards_arrows:', ':no_bell:']
        threat = [':receipt:', ':upside_down:', ':syringe:', ':gun:', ':safety_pin:', ':anger:', ':warning:', 
                  ':scissors:', ':broom:', ':knife:', ':dagger:', ':axe:', ':firecracker:', ':hourglass:', 
                  ':timer:', ':oncoming_police_car:', ':ambulance:', ':wrestling:', ':boxing_glove:', ':boom:', ':snake:',
                  ':b:', ':tooth:', ':angry:', ':rage:', ':triumph:', ':face_with_symbols_over_mouth:']
        rrandom = [':blush:', ':smiling_face_with_3_hearts:', ':kissing_heart:', ':star_struck:', ':flushed:', 
                  ':pleading_face:', ':hugging:', ':sneeze:', ':bow:', ':ok_woman:', ':star2:', ':sparkles:', 
                  ':revolving_hearts:', ':sparkling_heart:', ':receipt:', ':eyes:', ':grin:', ':receipt:', 
                  ':upside_down:', ':face_with_monocle:', ':thinking:', ':wink:', ':shushing_face:', ':unicorn:',
                  ':dancer:', ':+1:', ':woozy_face:', ':smiling_imp:', ':clown:', ':fist:', ':raised_hands:',
                  ':haircut:', ':drum:', ':exploding_head:', ':liar:', ':grimacing:', ':sleepy:', ':clap:']
        if (message.content.lower().find('love') != -1 or message.content.lower().find('like') != -1 )and message.content.lower().find('i') != -1:
            await message.channel.send(f'{random.choice(affection)}')
        elif (message.content.lower().find('wanna') != -1 or message.content.lower().find('want') != -1):
            if message.author.name == 'Oreo9238':
                await message.channel.send(f'{random.choice(flirting)}')
            elif message.author.name == 'nutrishous':
                await message.channel.send(f'{random.choice(disgust)}')
            else:
                await message.channel.send(f'{random.choice(validation)}')
        elif message.content.lower().find('hi') != -1 or message.content.lower().find('hello') != -1 or message.content.lower().find('bye') != -1:
            await message.channel.send(f'{random.choice(greeting)}')
        elif message.content.lower().find('live') != -1 or message.content.lower().find('die') != -1 or message.content.lower().find('kill') != -1 or message.content.lower().find('savage') != -1 or message.content.lower().find('fight') != -1 or message.content.lower().find('uck') != -1:
            await message.channel.send(f'{random.choice(threat)}')
        elif message.content.lower().find('are you') != -1 or message.content.lower().find('r you') != -1 or message.content.lower().find('r u') != -1 or message.content.lower().find('are u') != -1:
            if message.author.name == 'Oreo9238':
                await message.channel.send(f'{random.choice(flirting)}')
            elif message.author.name == 'nutrishous':
                await message.channel.send(f'{random.choice(disgust)}')
            else:
                await message.channel.send(f'{random.choice(confirmation)}')
        elif message.content.lower().find('cute') != -1 or message.content.lower().find('sexy') != -1:
            if message.author.name == 'Oreo9238':
                await message.channel.send(f'{random.choice(flirting)}')
            elif message.author.name == 'nutrishous':
                await message.channel.send(f'{random.choice(disgust)}')
            else:
                await message.channel.send(f'{random.choice(affection)}')
        elif message.content.lower().find('why') != -1 or message.content.lower().find('y ') != -1:
            await message.channel.send(f'{random.choice(mischievious)}')
        else:
            await message.channel.send(f'{random.choice(rrandom)}')
        
game = None
general_channel = None

@client.command(help='Starts a game')
@commands.has_role('Admin')
async def vanilla(ctx, *, player_mentions):
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
        game = Game(guild, client, general_channel, player_id_nums, ['Resistance', 'Resistance', 'Resistance', 'Resistance', 'Resistance', 'Resistance'],
                                                                    ['Spy', 'Spy', 'Spy', 'Spy'])
        await game.finish_initialization()
        game.stop_night_actions()
        await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Round 1!'))
    else:
        await ctx.send('Sorry, there is currently an ongoing game.')

@client.command(help='Starts a game')
@commands.has_role('Admin')
async def commander(ctx, *, player_mentions):
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
        # create role lists
        all_resistance_roles = ['Commander', 'Bodyguard', 'Resistance']
        all_spy_roles = ['Assassin', 'False Commander']
        while (len(all_resistance_roles) + len(all_spy_roles)) < len(player_id_nums):
            if (len(all_resistance_roles) + len(all_spy_roles)) % 2 == 1:
                all_resistance_roles.append('Resistance')
            else:
                all_spy_roles.append('Spy')
        game = Game(guild, client, general_channel, player_id_nums, all_resistance_roles, all_spy_roles)
        await game.finish_initialization()
        game.stop_night_actions()
        await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Round 1!'))
    else:
        await ctx.send('Sorry, there is currently an ongoing game.')

@client.command(help='Starts a game')
@commands.has_role('Admin')
async def party(ctx, *, player_mentions):
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
        game = Game(guild, client, general_channel, player_id_nums, ['President', 'Officer', 'Gambler', 'Psychic', 'Witch', 'Freelancer', 'Informant',
                                                                     'Resistance Reverser', 'Professor', 'Resistance Clown', 'Traditionalist', 'Librarian'],
                                                                    ['Organizer', 'Martyr', 'Bomber', 'Angel', 'Spy Reverser', 'Silencer', 'Victimizer',
                                                                     'Spy Clown', 'Timekeeper', 'Mad Scientist'])
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
        for temp_name in temp_player_names:
            temp_player = game.get_player_from_name(temp_name)
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
        for temp_name in temp_player_names:
            temp_player = game.get_player_from_name(temp_name)
            if temp_player.can_be_on_current_mission == False:
                await ctx.send(f'Sorry, a player you have added to your team cannot be on any team this round.')
                return
        await client.change_presence(activity=discord.Game(f'Round {game.round_tracker.get_round()} Voting!'))
        await game.start_vote(temp_player_names)

@client.command(help='Skips a team leader')
@commands.has_role('Admin')
async def next_leader(ctx):
    global game
    global general_channel
    # check that all conditions are met
    if game == None:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 0:
        await ctx.send('Sorry, it is not the team building phase.')
    else:
        game.next_team_leader()
        await ctx.send(f'The new team leader is {game.player_names[game.team_leader_index]}.')
    
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
        await ctx.send('Please use `>>vote` in your private messages with me.')
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
                await game.voter.record_vote(temp_player, 0)
                await general_channel.send(f'{temp_player.name} has voted.')

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

@client.command(help='Assassinates a player', hidden=True)
async def assassinate(ctx, assassinated_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.get_player_from_member(ctx.author).role != 'Assassin':
        await ctx.send('Sorry, you are not the Assassin.')
    elif ctx.channel != general_channel:
        await ctx.send('Please use `>>assassinate` in the main channel.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, it is not the end of game action phase.')
    elif game.is_player(assassinated_player) == False:
        await ctx.send('Please name the player you want to assassinate.')
    else:
        await game.get_player_from_member(ctx.author).do_assassination(game.get_player_from_name(assassinated_player))

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
        await ctx.send('Sorry, the player you picked is an invalid target. Please target someone different.')
    else:
        await game.get_player_from_member(ctx.author).do_see(game.get_player_from_name(seen_player))

@client.command(help='Freelances for spies', hidden=True)
async def freelance(ctx, freelanced_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).role != 'Freelancer':
        await ctx.send('Sorry, you are not the Freelancer.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>freelance` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already seen this round or have not yet been prompted to freelance.')
    elif game.is_player(freelanced_player) == False:
        await ctx.send('Please name the player you want to freelance.')
    elif (game.get_player_from_name(freelanced_player) in game.get_player_from_member(ctx.author).past_targets):
        await ctx.send('Sorry, the player you picked is an invalid target. Please target someone different.')
    else:
        await game.get_player_from_member(ctx.author).do_freelance(game.get_player_from_name(freelanced_player))

@client.command(help='Teaches a player to `>>mission switch`', hidden=True)
async def teach(ctx, taught_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).role != 'Professor':
        await ctx.send('Sorry, you are not the Professor.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>teach` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already seen this round or have not yet been prompted to teach.')
    elif game.is_player(taught_player) == False:
        await ctx.send('Please name the player you want to teach.')
    elif (game.get_player_from_name(taught_player) in game.get_player_from_member(ctx.author).past_targets):
        await ctx.send('Sorry, the player you picked is an invalid target. Please target someone different.')
    else:
        await game.get_player_from_member(ctx.author).do_teach(game.get_player_from_name(taught_player))

@client.command(help='Teaches a player to `>>mission switch` but blocks `>>mission success`', hidden=True)
async def experiment(ctx, experimented_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).role != 'Mad Scientist':
        await ctx.send('Sorry, you are not the Mad Scientist.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>experiment` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already seen this round or have not yet been prompted to experiment.')
    elif game.is_player(experimented_player) == False:
        await ctx.send('Please name the player you want to experiment.')
    else:
        await game.get_player_from_member(ctx.author).do_experiment(game.get_player_from_name(experimented_player))

@client.command(help='Silences a player', hidden=True)
async def silence(ctx, silenced_player):
    global game
    global general_channel
    if game == None or game.completed == True:
        await ctx.send('Sorry, there is no ongoing game.')
    elif game.current_window != 3:
        await ctx.send('Sorry, it is not the end of round action phase.')
    elif game.get_player_from_member(ctx.author).role != 'Librarian' and game.get_player_from_member(ctx.author).role != 'Silencer':
        await ctx.send('Sorry, you are not the Librarian or the Silencer.')
    elif ctx.channel == general_channel:
        await ctx.send('Please use `>>silence` in your private messages with me.')
    elif game.get_player_from_member(ctx.author).has_action == False:
        await ctx.send('Sorry, you have already seen this round or have not yet been prompted to silence.')
    elif game.is_player(silenced_player) == False:
        await ctx.send('Please name the player you want to silence.')
    else:
        await game.get_player_from_member(ctx.author).do_silence(game.get_player_from_name(silenced_player))

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
