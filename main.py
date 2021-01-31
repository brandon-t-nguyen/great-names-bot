#!/bin/env python3

import sys
import os
import time
import requests
import asyncio
import websockets
import json

import commands

def log(string):
    print('({:.4f}): commands: '.format(time.time()) + string)

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
                    msg = commands.parse(content)
                    if msg is not None:
                        # good: send it
                        guild_id = data['guild_id']
                        channel_id = data['channel_id']
                        message_id = data['id']
                        payload = {'content': msg, 'message_reference': {'message_id': message_id, 'channel_id': channel_id, 'guild_id': guild_id}}
                        url = '{}/channels/{}/messages'.format(api_url, channel_id)
                        r = requests.post(url, headers=headers, json=payload)
                        log("Sent message ({}: {}): \"{}\"".format(url, str(r.status_code), msg))
            elif gpay['op'] == 11:
                log("Received heartbeat ACK")
            sequence.set(gpay['s'])


if __name__ == "__main__":
    log("Begin execution")

    # load token
    token_path = './token'

    if len(sys.argv) > 2 and sys.argv[1] == '--token-path':
        token_path = sys.argv[2]

    if 'GNB_TOKEN_PATH' in os.environ:
        token_path = os.environ['GNB_TOKEN_PATH']

    log("Loading token at " + token_path)
    try:
        with open(token_path, 'r') as token_file:
            token = token_file.read().strip()
    except FileNotFoundError:
        log("Unable to find token file " + token_path + ", exiting...")
        exit(1)

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
