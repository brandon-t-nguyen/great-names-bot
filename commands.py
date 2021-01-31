import time
import numpy as np # we want their nice randint for uniform random *integers*

import roller
from classes import Message as Message
import stats

MAXIMUM_DICE = 1000
MAXIMUM_SAMPLE_SIZE = 1000000
VERSION_STRING = '1.0.0'

def log(string):
    print('({:.4f}): commands: '.format(time.time()) + string)
# command functions will return a string
# provide them the args *after* the command itself (not unix-style!)

class Command:
    # help_data can be a function (with args passed in), or a string
    def __init__(self, name, desc, help_data, func):
        self.name = name;
        self.desc = desc;
        self.help = help_data;
        self.func = func;

class Commands:
    def __init__(self):
        self.list = []
        self.map = {}

    def add(self, command):
        self.list.append(command)
        self.map[command.name] = command

    def help_commands(self, args, nest=0):
        indent = ""
        while nest > 0: indent = indent + ' '
        msg = ""
        for cmd in self.list:
            msg += "{indent}* `{name}`: {desc}\n".format(indent=indent, name=cmd.name, desc=cmd.desc)
        return msg

    def execute(self, args):
        if len(args) == 0:
            return Message(content="Please provide a subcommand\nSubcommands:\n{}".format(self.help_commands(args)))

        subcommand = args[0]
        try:
            if len(args) > 1 and args[1] == 'help':
                help_data = self.map[subcommand].help
                if type(help_data) is str: return Message(help_data)
                elif help_data is None:    return Message("Usage: `{name}`".format(name=subcommand))
                else:                      return self.map[subcommand].help(args[1:])
            else:
                return self.map[subcommand].func(args[1:])
        except KeyError:
            return Message(content="{name} is not a valid subcommand".format(subcommand))


commands = Commands()


help_dice =\
"""
Usage: `!dice [number of dice: default 1] [sides: default 10]`
    Rolls the provided number of dice, defaulting to 1 with 10 sides
    Die values range from 1 to the number of sides.
    The number of sides may also use "*N*d*M*" notation e.g. `5d20`.

    The maximum number of dice that can be rolled is {max_dice}.

Examples:
    * `!dice`
        * `4`
    * `!dice 5`
        * `1, 2, 4, 6, 10`
    * `!dice 5 20`
        * `1, 3, 8, 14, 20`
    * `!dice 5d20`
        * `1, 3, 8, 14, 20`
""".format(max_dice=MAXIMUM_DICE)
def cmd_dice(args):
    n = 1
    sides = 10

    if len(args) > 0:
        if 'd' in args[0]:
            # NdM notation
            tokens = args[0].split('d')

            if len(tokens) > 2:
                return "Invalid notation"

            msg = ""

            try:
                n = int(tokens[0])
            except ValueError:
                msg += "`{num}` is not a valid integer\n".format(num=args[0])

            try:
                sides = int(tokens[1])
                if sides < 1: msg +=  "`{num}` is not a valid number of sides".format(num=sides)
            except ValueError:
                msg += "`{num}` is not a valid integer\n".format(num=args[0])
            msg = msg.strip()

            # oops, bad string
            if len(msg) > 0: return Message(msg)

            # ignore rest of args: we've got everything
            args = []
        else:
            try:
                # boring count
                n = int(args[0])
                args = args[1:]
            except ValueError:
                return "`{num}` is not a valid integer".format(num=args[0])
    if n == 0:
        return None

    if n > MAXIMUM_DICE:
        return "`{num}` exceeds the number of dice that can be rolled ({max_dice})".format(num=n, max_dice=MAXIMUM_DICE)

    if len(args) > 0:
        try:
            sides = int(args[0])
            args = args[1:]
            if sides < 1:
                return "`{num}` is not a valid number of sides".format(num=sides)
        except ValueError:
            return "`{num}` is not a valid integer".format(num=args[0])

    rolls = []
    rolls = sorted(np.random.randint(1, high=sides+1, size=n))
    msg = ""
    for roll in rolls[0:-1]:
        msg += str(roll) + ', '
    if len(rolls) > 0:
        msg += str(rolls[-1])

    return Message(msg)

def emoji_scale_absolute(s):
    if   s >=  9: return ':sunglasses:'
    elif s >=  8: return ':laughing:'
    elif s >=  7: return ':grin:'
    elif s >=  6: return ':grinning:'
    elif s >=  5: return ':slight_smile:'
    elif s >=  4: return ':neutral_face:'
    elif s >=  3: return ':slight_frown:'
    elif s >=  2: return ':worried:'
    elif s >=  1: return ':fearful:'
    else:         return ':scream:'
help_roll =\
"""
Usage: `!roll <attribute score> [skill value + modifiers: default is 0] [number of dice: default is attribute]`
    By default, rolls a number of dice equal to the provided attribute score.
    Optional positional arguments include:
        * skill value + modifiers (bonuses, power) to add to the total number of successes. The default is 0.
        * number of dice, to handle additional dice granted by points of stamina.
          If this argument has a `+` (e.g. `+2`) in front of the number, it will be added to the attribute score.
          Otherwise, the provided number will be the number of die rolled.

    This will calculate the number of successes, where the number of successes is
    determined by how many die values are less than or equal to the attribute score,
    with 10s negating a success.

    The maximum number of dice that can be rolled is {max_dice}.

Examples:
    * `!roll 5`: this will roll 5 dice where rolled values ≤5 are successes
    * `!roll 5 2`: this will roll 5 dice where rolled values ≤5 are successes, with 2 bonus successes
    * `!roll 5 0 7`: this will roll 7 dice where rolled values ≤5 are successes, with 0 bonus successes
    * `!roll 5 1 +4`: this will roll 9 (5+4) dice where rolled values ≤5 are successes, with 1 bonus success
""".format(max_dice=MAXIMUM_DICE)
def cmd_roll(args):
    if len(args) == 0:
        return "Please provide an attribute score\n" + help_roll

    try:
        attr = int(args[0])
        args = args[1:]
    except ValueError:
        return "`{num}` is not a valid integer".format(num=args[0])

    bonus = 0
    if len(args) > 0:
        try:
            bonus = int(args[0])
            args = args[1:]
        except ValueError:
            return "`{num}` is not a valid integer".format(num=args[0])

    n = attr
    if len(args) > 0:
        try:
            if args[0][0] == '+':
                # relative add
                n = attr + int(args[0][1:])
            else:
                # absolute count
                n = int(args[0])
            args = args[1:]
        except ValueError:
            return "`{num}` is not a valid integer".format(num=args[0])

    if n > MAXIMUM_DICE:
        return "`{num}` exceeds the number of dice that can be rolled ({max_dice})".format(num=n, max_dice=MAXIMUM_DICE)

    result = roller.roll(attr, bonus, n)

    # print rolls
    msg = ""
    for roll in result.rolls[0:-1]:
        if roll <= attr: fmt = '**'
        elif roll == 10: fmt = '~~'
        else:            fmt = ''
        msg += "{fmt}{val}{fmt}, ".format(fmt=fmt, val=str(roll))
    if len(result.rolls) > 0:
        roll = result.rolls[-1]
        if roll <= attr: fmt = '**'
        elif roll == 10: fmt = '~~'
        else:            fmt = ''
        msg += "{fmt}{val}{fmt}".format(fmt=fmt, val=str(roll))

    # print explanation
    msg +=\
"""

Rolled {n} {n_noun} with an attribute score of {attr} and {bonus} bonus successes.
{successes} rolled {rs_noun}, {bonus} bonus {bs_noun}, and {negations} {neg_noun}

**Total successes: {total}  {emoji}**
""".format(n=n, n_noun=('die' if n==1 else 'dice'), attr=attr, bonus=result.bonus,
           successes=result.successes, negations=result.negations, total=result.total,
           rs_noun='success' if result.successes == 1 else 'successes',
           bs_noun='success' if result.bonus == 1 else 'successes',
           neg_noun='negation' if result.negations == 1 else 'negations',
           emoji=emoji_scale_absolute(result.total))

    return Message(content=msg)


def cmd_stats_sim_success_histogram(args):
    if len(args) < 2:
        return Message("Expected at least 2 arguments, found {}".format(len(args)))

    msg_parse = ""
    try:               sample_size = int(args[0])
    except ValueError: msg_parse += "`{}` is not a valid integer for sample size".format(args[0])

    if sample_size > MAXIMUM_SAMPLE_SIZE:
        return Message("`{num}` exceeds the number of maximum sample size (`{max}`)".format(num=sample_size,
                                                                                           max=MAXIMUM_SAMPLE_SIZE))
    attr = 0
    try:               attr = int(args[1])
    except ValueError: msg_parse += "`{}` is not a valid integer for sample size".format(args[1])

    n = attr
    if len(args) > 2:
        try:
            if args[2][0] == '+': n = attr + int(args[2][1:])
            else:                 n = int(args[2])
        except ValueError: msg_parse += "`{}` is not a valid integer for sample size".format(args[1])

    if n <= 0: return Message("Number of dice to be rolled must be greater than 0")

    if len(msg_parse) > 0: return Message(msg_parse)

    path = stats.success_histogram(sample_size, attr, n)
    return Message("Simulation results", file_path=path)

commands_stats_sim = Commands()
commands_stats_sim.add(Command('success-histogram', "Provides a histogram of successes given attribute score and dice count", "Usage: `success-histogram <sample size> <attribute score> [dice count: default attr, use '+' for relative]`", cmd_stats_sim_success_histogram))


def cmd_stats_simulate(args): return(commands_stats_sim.execute(args))
commands_stats = Commands()
commands_stats.add(Command('simulate', "Perform simulations and generate statistics", "Usage: `simulate <subcommand>`", cmd_stats_simulate))

def help_stats(args):
    msg =\
"""
Usage: `!stats <subcommand>`

Subcommands:
"""
    msg += commands_stats.help_commands(args)
    return Message(msg)
    # for cmd in commands_stats.list:
    #     if type(cmd.help) is str:
    #         msg = cmd.help
    #     elif cmd.help is None:
    #         msg = "Usage: `{cmd}`\n{desc}".format(cmd=cmd.name, desc=cmd.desc)
    #     else:
    #         msg = cmd.help(args[1:])

def cmd_stats(args): return(commands_stats.execute(args))

def cmd_help(args):
    if len(args) == 0:
        msg =\
"""
For additional help, run `!help <command name>` e.g. `!help !roll`

Available commands:
"""
        for cmd in commands.list:
            msg += "`{cmd}`: {desc}\n".format(cmd=cmd.name, desc=cmd.desc)
    else:
        msg = ""
        for name in args:
            if name in commands.map.keys():
                cmd = commands.map[name]
                if type(cmd.help) is str:
                    msg += cmd.help
                elif cmd.help is None:
                    msg += "Usage: `{cmd}`\n{desc}".format(cmd=cmd.name, desc=cmd.desc)
                else:
                    msg += cmd.help(args[1:]).content
            else:
                msg += "`{name}` is not a valid command".format(name=name)
            msg += '\n'
    return Message(content=msg)

def cmd_about(args):
    msg = \
"""
**Great Names Bot** v{ver}

This bot assists in performing die rolls and success calculation in the
Great Names system by Adam Franti.

Bot maintainer: Brandon Nguyen
""".format(ver=VERSION_STRING)
    return Message(msg)

# parses command, returns message
# precondition: command has > 0 characters
def parse(command):
    tokens = command.split()
    cmd = tokens[0];
    args = tokens[1:];

    # run the command
    try:
        func = commands.map[cmd].func
        log('Running command \'{cmd}\' with args {args}'.format(cmd=cmd, args=args))
        return func(args)
    except KeyError:
        # nothing to do if command not found
        pass
    except Exception as e:
        log('Ran into exception!')
        log(str(e))
        return Message("I ran into an error on my end, sorry :cry:")

    return None;

# initialization
commands.add(Command('!help', "Provides help for commands", cmd_help, cmd_help))
commands.add(Command('!about', "Provides info about this bot", None, cmd_about))
commands.add(Command('!dice', "Rolls dice, default being d10", help_dice, cmd_dice))
commands.add(Command('!roll', "Rolls to calculate successes", help_roll, cmd_roll))
commands.add(Command('!stats', "Provides various statistics", help_stats, cmd_stats))
