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
                    msg = "usage: `{cmd}`\n{desc}".format(cmd=cmd.name, desc=cmd.desc)
                else:
                    msg = cmd.help(args[1:])
            else:
                msg = "`{cmd}` is not a valid command"
    return msg

def cmd_about(args):
    return\
"""
**Great Names Bot**

This bot assists in performing die rolls and claims for the Great Names
system by Adam Franti.

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
        return commands.map[cmd].func(args)
    except KeyError:
        # nothing to do if command not found
        pass

    return None;

# initialization
commands.add(Command('!help', "Provides help for commands", cmd_help, cmd_help))
commands.add(Command('!about', "Provides info about this bot", None, cmd_about))
