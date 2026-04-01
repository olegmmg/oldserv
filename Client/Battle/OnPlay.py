from database.DataBase import DataBase
from Server.Battle.MatchmakeCancelledMessage import MatchmakeCancelledMessage
from Server.Battle.MatchmakingInfoMessage import MatchmakingInfoMessage
from Utils.Reader import BSMessageReader
from Utils.Matchmaking import join_queue, ROOM_3V3, ROOM_SD
import threading


class OnPlay(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        pass

    def process(self):
        if self.player.inmm:
            # Already in queue, just send current status
            MatchmakingInfoMessage(self.client, self.player).send()
            return

        # Determine room type from player's current mode selection
        # Default: 3v3. Can be extended when player selects a mode.
        room_type = getattr(self.player, 'selected_room_type', ROOM_3V3)

        DataBase.replaceValue(self, 'roomID', 0)
        self.player.inmm = True

        # Join online matchmaking queue
        join_queue(self.player, self.client, room_type)

        # Send initial matchmaking info to client
        MatchmakingInfoMessage(self.client, self.player).send()
