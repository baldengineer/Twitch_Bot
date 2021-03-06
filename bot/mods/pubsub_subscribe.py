from os import getenv

from twitchbot import cfg
from twitchbot import get_pubsub
from twitchbot import Mod
from twitchbot import PubSubTopics


class PubSub(Mod):
    """
    This class is used only to subscribe to pubsub topics.
    Handling of the responses should be handled in other Mods
    """

    name = "pubsub_subscribe"

    def __init__(self):
        super().__init__()

    async def loaded(self):
        for channel in cfg.channels:
            await get_pubsub().listen_to_channel(
                channel,
                [
                    PubSubTopics.channel_points,
                    PubSubTopics.moderation_actions,
                    PubSubTopics.bits,
                    PubSubTopics.channel_subscriptions,
                    PubSubTopics.bits_badge_notification,
                ],
                access_token=getenv("PUBSUB_OAUTH"),
            )
            print(f"PubSub active for {channel}")
