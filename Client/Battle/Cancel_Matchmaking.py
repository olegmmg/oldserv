from Server.Battle.MatchmakeCancelledMessage import MatchmakeCancelledMessage
from Utils.Reader import BSMessageReader
from Utils.Matchmaking import leave_queue, ROOM_3V3, ROOM_SD


class CancelMatchMaking(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        pass

    def process(self):
        # If battle already started (inmm=False after launch), ignore cancel attempt
        if not self.player.inmm:
            return

        # Remove from queue and confirm cancellation to client
        room_type = getattr(self.player, 'selected_room_type', ROOM_3V3)
        leave_queue(self.player, room_type)
        MatchmakeCancelledMessage(self.client, self.player).send()