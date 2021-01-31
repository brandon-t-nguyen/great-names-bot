import time
import numpy as np # we want their nice randint for uniform random *integers*

def log(string):
    print('({:.4f}):     '.format(time.time()) + string)
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

def cmd_roll(args):
    n = 1
    if len(args) > 0:
        try:
            n = int(args[0])
        except ValueError:
            return "{num} is not a valid integer".format(num=args[0])
    if n == 0:
        return None

    rolls = []
    rolls = sorted(np.random.randint(1, high=10, size=n))
    msg = ""
    for roll in rolls[0:-1]:
        msg += str(roll) + ', '
    if len(rolls) > 0:
        msg += str(rolls[-1])

    return msg

help_roll =\
"""
Usage: `!roll [number of die: default 1]`
    Rolls the provided number of die, defaulting to 1
    Die values range from 1 to 10

Examples:
    * `!roll`
        * `4`
    * `!roll 5`
        * `1, 2, 4, 6, 10`
"""


help_prove =\
"""
Usage: `!prove <attribute score> [skill value + modifiers: default is 0] [dice count: default is attribute]`
    By default, rolls a number of dice equal to the provided attribute score.
    Optional positional arguments include:
        * skill value + modifiers (bonuses, power) to add to the total number of successes. The default is 0.
        * dice count, to handle additional dice granted by points of power.
          If this argument has a `+` (e.g. `+2`) in front of the number, it will be added to the attribute score.
          Otherwise, the provided number will be the number of die rolled.

    This will perform the "prove" mechanic, where the number of successes is
    determined by how many die values are less than or equal to the attribute score,
    with 10s negating a success.

Examples:
    * `!prove 5`: this will roll 5 die where rolled values &leq;5 are successes
    * `!prove 5 2`: this will roll 5 die where rolled values &leq;5 are successes, with 2 bonus successes
    * `!prove 5 0 7`: this will roll 7 die where rolled values &leq;5 are successes, with 0 bonus successes 
    * `!prove 5 1 +4`: this will roll 9 (5+4) die where rolled values &leq;5 are successes, with 1 bonus success
"""
def cmd_prove(args):
    if len(args) == 0:
        return "Please provide an attribute score to prove with\n" + help_prove

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

Rolled {n} {die} with an attribute score of {attr} and {bonus} bonus successes.
{successes} rolled successes, {bonus} bonus successes, and {negations} negations

**Total successes: {total}**
""".format(n=n, die=('die' if n==1 else 'dice'), attr=attr, bonus=bonus, successes=successes, negations=negations, total=total)

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
                msg = "`{cmd}` is not a valid command"
    return msg

def cmd_about(args):
    return\
"""
**Great Names Bot**

This bot assists in performing die rolls and proves for claims in the
Great Names system by Adam Franti.

Bot maintainer: Brandon Nguyen
"""

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

    return None;

# initialization
commands.add(Command('!help', "Provides help for commands", cmd_help, cmd_help))
commands.add(Command('!about', "Provides info about this bot", None, cmd_about))
commands.add(Command('!roll', "Rolls d10s", help_roll, cmd_roll))
commands.add(Command('!prove', "Rolls to prove a claim", help_prove, cmd_prove))
