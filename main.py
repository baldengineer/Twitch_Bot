# Twitch bot written for the BaldEngineer channel
import os
import logging

from twitchio.ext import commands

# Set logging level and format
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self):
        irc_token = os.environ.get("twitch_oauth")
        nick = os.environ.get("twitch_nickname")
        prefix = os.environ.get("twitch_prefix")
        channel = os.environ.get("twitch_channel")

        super().__init__(
            irc_token=irc_token,
            api_token="test",
            nick=nick,
            prefix="!",
            initial_channels=[channel],
        )

        self.active_users = dict()
        self.max_users = 0

    # Events don't need decorators when subclassed
    async def event_ready(self):
        logger.warning(f"Ready | {self.nick}")

    async def event_message(self, message):
        logger.debug(f"{message.author.display_name}: {message.content}")

        try:  # Count how many messages a user has sent.
            self.active_users[message.author.display_name] += 1
        except KeyError:
            self.active_users[message.author.display_name] = 1
        except Exception as e:
            logger.warning(e)

        # Check if more members are in the channel, and keep track of maximum
        if len(message.channel.chatters) > self.max_users:
            self.max_users = len(message.channel.chatters)

        # Handle any commands issued
        await self.handle_commands(message)

    @commands.command(name="active")
    async def active_users(self, ctx):
        await ctx.send(
            f"I have seen {len(self.active_users)} user{'s' if len(self.active_users) > 1 else ''} since starting."
        )

    @commands.command(name="max")
    async def send_max_users(self, ctx):
        await ctx.send(
            f"There have been a maximum of {self.max_users} users with us today."
        )


bot = Bot()
bot.run()
