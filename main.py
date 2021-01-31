#!/bin/env python3

import time
import requests
import asyncio
import websockets
import json

# Die roller stuff


# command functions will return a string
# provide them the args *after* the command itself (not unix-style!)

commands = sorted(['!help', '!roll', '!claim', '!about'])
commands.sort()
def cmd_help(args):
    if len(args) == 0:
        msg =\
"""
For additional help, run `!help <command name>` e.g. `!help !roll`

Available commands:
"""
        for cmd in commands:
            msg += "`{cmd}`\n".format(cmd=cmd)
    else:
        # TODO
        msg = "TODO"
    return msg

commands_functions = {
    '!help': cmd_help,
    #'!roll': cmd_roll,
    #'!claim': cmd_claim,
}

# parses command, returns message
# precondition: command has > 0 characters
def parse_command(command):
    tokens = command.split()
    cmd = tokens[0];
    args = tokens[1:];

    # run the command
    try:
        return commands_functions[cmd](args)
    except KeyError:
        # nothing to do if command not found
        pass

    return None;

####

def log(string):
    print('({:.4f}): '.format(time.time()) + string)

# https://stackoverflow.com/questions/42883134/how-to-run-a-coroutine-that-does-not-end-without-getting-stuck-awaiting-a-result
class Sequence:
    def __init__(self):
        self.s = 0
    def set(self, s):
        self.s = s

async def heartbeat_routine(ws, period, sequence):
    payload = {'op': 1, 'd': {}, 'd': sequence.s, 't': 'HEARTBEAT'}
    while True:
        log("Sending heartbeat")
        await ws.send(json.dumps(payload))
        await asyncio.sleep(period/1000)

# https://websockets.readthedocs.io/en/stable/intro.html ugh
async def gateway_loop(uri):
    log("Connecting to gateway...")
    async with websockets.connect(uri) as ws:
        log("Connected to gateway")
        gpay = json.loads(await ws.recv())
        if gpay['op'] == 10:
            heartbeat_interval = gpay['d']['heartbeat_interval']
            heratbeat_seq = 0
            log("Received Hello, heartbeat={} ms".format(heartbeat_interval))
        else:
            log("Failed hello, exiting...")
            return

        # identify
        intents = 1 << 9 # server messages
        identify_payload = json.dumps({'op': 2, 'd': {'token': token, 'intents': intents, 'properties': {'$os': 'linux', '$browser': 'test', '$device': 'server'}}})

        await ws.send(identify_payload)
        gpay = json.loads(await ws.recv())

        if gpay['t'] == 'READY':
            log("Identify handshake complete")
        else:
            log("Failed handshake, exiting...")
            return

        sequence = Sequence()
        sequence.set(gpay['s'])

        # starting up heartbeats
        heartbeat_future = asyncio.ensure_future(heartbeat_routine(ws, heartbeat_interval, sequence))
        #gpay = json.loads(await ws.recv())

        # we good now, enter loop
        run = True
        log("Beginning main receive loop")
        while run:
            gpay = json.loads(await ws.recv())
            if gpay['t'] == 'MESSAGE_CREATE':
                # let's get it via REST api
                data = gpay['d']
                #log("MESSAGE_CREATE: \"{}\"".format(data['content']))
                content = data['content']
                if content.find('!') == 0:
                    response = parse_command(content)
                    if response is not None:
                        # good: send it
                        guild_id = data['guild_id']
                        channel_id = data['channel_id']
                        message_id = data['id']
                        payload = {'content': response, 'message_reference': {'message_id': message_id, 'channel_id': channel_id, 'guild_id': guild_id}}
                        url = '{}/channels/{}/messages'.format(api_url, channel_id)
                        r = requests.post(url, headers=headers, json=payload)
                        log("Sent message ({}: {}): \"{}\"".format(url, str(r.status_code), response))
            elif gpay['op'] == 11:
                log("Received heartbeat ACK")
            sequence.set(gpay['s'])


if __name__ == "__main__":
    log("Begin execution")
    token = 'NzM0NDY3ODg1NzI4MjY4Mjg4.XxSIhQ.IGOaJcrGUsAA490RPVoPetzZYpg'
    # let's make a random ass request to post a message
    headers = {'User-Agent': "Great Names Bot",'Authorization': 'Bot ' + token}
    channel_id = '805235577213026316'
    api_url = 'https://discord.com/api'

    # get gateway
    log("Requesting bot gateway...")
    r = requests.get('https://discord.com/api/gateway/bot', headers=headers)
    gateway_r = r.json()
    gateway_url = gateway_r['url'] + '/?v=8&encoding=json'
    log("Gateway received")

    asyncio.get_event_loop().run_until_complete(gateway_loop(gateway_url))
