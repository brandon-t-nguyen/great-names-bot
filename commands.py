import time
import numpy as np # we want their nice randint for uniform random *integers*

MAXIMUM_DICE = 1000
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
            if len(msg) > 0: return msg

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

    return msg


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

    rolls = sorted(np.random.randint(1, high=11, size=n))

    successes = 0
    negations = 0
    for roll in rolls:
        if roll == 10:
            negations += 1
        elif roll <= attr:
            successes += 1

    total = max(0, successes + bonus - negations)

    # print rolls
    msg = ""
    for roll in rolls[0:-1]:
        if roll <= attr: fmt = '**'
        elif roll == 10: fmt = '~~'
        else:            fmt = ''
        msg += "{fmt}{val}{fmt}, ".format(fmt=fmt, val=str(roll))
    if len(rolls) > 0:
        roll = rolls[-1]
        if roll <= attr: fmt = '**'
        elif roll == 10: fmt = '~~'
        else:            fmt = ''
        msg += "{fmt}{val}{fmt}".format(fmt=fmt, val=str(roll))

    # print explanation
    msg +=\
"""

Rolled {n} {n_noun} with an attribute score of {attr} and {bonus} bonus successes.
{successes} rolled {rs_noun}, {bonus} bonus {bs_noun}, and {negations} {neg_noun}

**Total successes: {total}**
""".format(n=n, n_noun=('die' if n==1 else 'dice'), attr=attr, bonus=bonus, successes=successes, negations=negations, total=total,
           rs_noun='success' if successes == 1 else 'successes', bs_noun='success' if bonus == 1 else 'successes',
           neg_noun='negation' if negations == 1 else 'negations')

    return msg


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
        for name in args:
            if name in commands.map.keys():
                cmd = commands.map[name]
                if type(cmd.help) is str:
                    msg = cmd.help
                elif cmd.help is None:
                    msg = "Usage: `{cmd}`\n{desc}".format(cmd=cmd.name, desc=cmd.desc)
                else:
                    msg = cmd.help(args[1:])
            else:
                msg = "`{cmd}` is not a valid command".format(cmd=cmd.name)
    return msg

def cmd_about(args):
    return\
"""
**Great Names Bot** v{ver}

This bot assists in performing die rolls and success calculation in the
Great Names system by Adam Franti.

Bot maintainer: Brandon Nguyen
""".format(ver=VERSION_STRING)

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
    except:
        return "I ran into an error on my end, sorry :cry:"

    return None;

# initialization
commands.add(Command('!help', "Provides help for commands", cmd_help, cmd_help))
commands.add(Command('!about', "Provides info about this bot", None, cmd_about))
commands.add(Command('!dice', "Rolls dice, default being d10", help_dice, cmd_dice))
commands.add(Command('!roll', "Rolls to calculate successes", help_roll, cmd_roll))
