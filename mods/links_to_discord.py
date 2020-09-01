from twitchbot import (
    cfg,
    Mod,
    task_exist,
    stop_task,
    add_task,
    channels,
    ModCommand,
    Message,
)
from asyncio import sleep
from aiofile import AIOFile
import json
from datetime import datetime
import re
import aiohttp


class LinksToDiscord(Mod):
    name = "linkstodiscord"

    def __init__(self):
        pass

    def find_url(self, string):
        # findall() has been used
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        return [x[0] for x in url]

    async def on_privmsg_received(self, msg: Message):
        # Make sure the webhook url is set
        if cfg.webhookurl == None:
            return

        webhook = cfg.webhookurl

        urls = self.find_url(msg.content)

        if len(urls):
            for each in urls:
                async with aiohttp.ClientSession() as session:
                    response = await session.post(
                        webhook, json={"content": each, "username": "TwitchBot"}
                    )
                    if response.status == 204:
                        message = "Thanks for the link, I posted it to discord."
                        await channels[cfg.channels[0]].send_message("🤖" + message)
