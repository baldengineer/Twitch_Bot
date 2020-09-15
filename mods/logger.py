import asyncio
from aiofile import AIOFile
import json
from datetime import datetime, date

from data import load_data, save_data

from twitchbot import Event, Message, Mod, cfg, Channel


class TwitchLog(Mod):
    def __init__(self):
        super().__init__()
        print("TwitchLog loaded")
        self.user_data = dict()

    async def on_raw_message(self, msg: Message):

        if True:
            async with AIOFile(f"irc_logs/{date.today().isoformat()}-{msg.channel_name}.log", "a") as afp:
                await afp.write(f"{datetime.now().isoformat()}:{msg} \n")
                await afp.fsync()

        # If the message is a system message, we're done here
        if not msg.author:
            return

        # Create an empty object if the user is new
        if not msg.author in self.user_data:
            self.user_data[msg.author] = {"last_message": None, "message_count": 0}

        author = self.user_data[msg.author]

        # Track users last message time
        author["last_message"] = datetime.now()

        # Track the number of messages total from the user
        author["message_count"] += 1

        await save_data("user", self.user_data)

    async def on_connected(self):
        """Load user data from file when connected"""
        print("Loading user data from json file...", end="")
        self.user_data = await load_data("user")
        print("done")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        """Log channel raid"""

        raid_data = await load_data("raided")

        raid_data[datetime.now().isoformat()] = (raider, viewer_count)

        await save_data("raided", raid_data)

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        """Log channel points redemptions"""
        channel_point_data = await load_data("channel_points")
        channel_point_data[datetime.now().isoformat()] = (msg.author, msg.msg_id, msg.raw_msg, msg.normalized_content)
        await save_data("channel_points", channel_point_data)
