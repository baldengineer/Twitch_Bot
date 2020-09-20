from aiofile import AIOFile
from datetime import datetime, date

from data import load_data, save_data

from twitchbot import Message, Mod, Channel, PubSubData


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
        if msg.author not in self.user_data:
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

    async def on_pubsub_received(self, raw: PubSubData):
        # Dump to a log file
        async with AIOFile("pubsub.log", "a") as afp:
            data = f"{datetime.now().isoformat()}:{raw.raw_data}"
            await afp.write(data + "\n")
            await afp.fsync()

    async def on_pubsub_bits(self, raw: PubSubData, data) -> None:
        """Send MQTT push when a us4er redeems bits"""
        """
        print(raw.message_dict)
        {'data':
            {'user_name': 'tisboyo', 'channel_name': 'baldengineer',
            'user_id': '461713054', 'channel_id': '125957551', 'time': '2020-09-20T02:48:34.819702158Z',
            'chat_message': 'cheer1', 'bits_used': 1, 'total_bits_used': 2,
            'is_anonymous': False, 'context': 'cheer', 'badge_entitlement': None},
        'version': '1.0',
        'message_type': 'bits_event',
        'message_id': '5a2da2f4-a6b5-5d23-b7cc-839a3ea5140c'
        }
        """
        bits = await load_data("bits")
        bits[datetime.now().isoformat()] = raw.message_dict
        await save_data("bits", bits)
