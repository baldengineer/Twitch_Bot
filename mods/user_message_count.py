from datetime import datetime

from twitchbot import Message
from twitchbot import Mod
from twitchbot.database.session import session

from mods.database_models import Users


class UserMessageCount(Mod):
    def __init__(self) -> None:
        super().__init__()
        print("UserMessageCount loaded")

    async def on_raw_message(self, msg: Message) -> None:
        """Increment the user message counter"""

        if not msg.is_user_message:
            return

        user_id = msg.tags.user_id
        server_id = msg.tags.room_id

        rows_affected = (
            session.query(Users)
            .filter(Users.user_id == user_id, Users.channel == server_id)
            .update({"message_count": Users.message_count + 1, "last_message": datetime.now()})
        )

        # If the user doesn't exist, insert them
        if not rows_affected:
            user_object = Users(user_id=user_id, channel=server_id, user=msg.author, message_count=1)
            session.add(user_object)

        session.commit()
