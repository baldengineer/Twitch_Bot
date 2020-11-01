from main import AddOhmsBot
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Message
from twitchbot import Mod
from twitchbot import PubSubData
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand


class ChannelPoints(Mod):
    name = "channelpoints"

    def __init__(self):
        super().__init__()
        print("ChannelPoints loaded")

        # Create a key as the name of a reward, and a value of the function to call
        self.redemptions = {
            "highlighted-message": self.highlighted_message,
            "Give BaldEngineer a treat.": self.dispense_treat,
            "Get His Attention!": self.attention_attention,
        }

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        await self.points_redeemed(reward)

    async def on_pubsub_received(self, raw: PubSubData):

        if len(raw.message_data) == 0:
            # Happens at startup, and possibly other times.
            return

        elif raw.is_channel_points_redeemed:
            r = raw.message_data["redemption"]["reward"]["title"]
            await self.points_redeemed(r)

    async def points_redeemed(self, reward: str):

        print("Redemption".center(80, "*"))
        try:
            # Call the function for the reward that was redeemed.
            await self.redemptions[reward]()

        except KeyError:
            # Don't have a function for the reward that was redeemed.
            print(f"Unknown reward redeemed - '{reward}'")

    async def dispense_treat(self, channel=cfg.channels[0]):
        if AddOhmsBot.AIO.send("dispense-treat-toggle"):
            await channels[channel].send_message(f"{AddOhmsBot.msg_prefix}Teleporting a treat")
        else:
            await channels[channel].send_message(f"{AddOhmsBot.msg_prefix}I couldn't do that at the moment. Sorry ☹️")

        print("Dispensing a treat!")

    async def attention_attention(self, channel=cfg.channels[0]):
        print("Hey!!!")
        if AddOhmsBot.ATTN_ENABLE:
            if not AddOhmsBot.AIO.send("twitch-attn-indi"):
                await channels[channel].send_message(f"{AddOhmsBot.msg_prefix}Something went wrong getting my attention. ☹️")

        else:
            print("Shhhhh....")

    async def highlighted_message(self):
        print("Highlighted message.")

    @ModCommand(name, "channelpoint_cooldown", permission="admin")
    async def channelpoint_cooldown(self, msg, *args):
        # Nothing really to do here
        pass

    @SubCommand(channelpoint_cooldown, "attention", permission="admin")
    async def attention_cooldown(self, msg, *args):
        aio_key = "twitch-attn-indi"

        try:
            new_cooldown = int(args[0])
            # Update the database
            AddOhmsBot.AIO.set_cooldown(aio_key, new_cooldown)

            await msg.reply(f"Attention cooldown changed to {new_cooldown}")

        except IndexError:
            await msg.reply(f"Current cooldown is {AddOhmsBot.AIO.get_cooldown(aio_key)} seconds.")
            return

        except ValueError:
            await msg.reply("Invalid value.")

        except Exception as e:
            print(type(e), e)
            return

    @SubCommand(channelpoint_cooldown, "treat", permission="admin")
    async def treat_cooldown(self, msg, *args):
        """
        This entire function is a duplicate from `commands/treatme.py`
        and is only here for completeness, or if the command is removed.
        """
        aio_key = "dispense-treat-toggle"

        try:
            new_cooldown = int(args[0])

            # Update the database
            AddOhmsBot.AIO.set_cooldown(aio_key, new_cooldown)

            await msg.reply(f"Treatme cooldown changed to {new_cooldown}")

        except IndexError:
            await msg.reply(f"Current cooldown is {AddOhmsBot.AIO.get_cooldown(aio_key)} seconds.")
            return

        except ValueError:
            await msg.reply("Invalid value.")

        except Exception as e:
            print(type(e), e)
            return