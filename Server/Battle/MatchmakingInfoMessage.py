from Utils.Writer import Writer
from Server.Battle.UDPConnectionInfo import UDPConnectionInfo


class MatchmakingInfoMessage(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 20405
        self.player = player

    def encode(self):
        # Count real players found so far in same queue
        # Use player's queued_count if available (set by matchmaking), else default 1
        found = getattr(self.player, 'mm_found_count', 1)
        max_plrs = getattr(self.player, 'mm_max_players', 6)
        self.writeInt(30)       # Timer shown to client
        self.writeInt(found)    # Players found
        self.writeInt(max_plrs) # Max players for this mode
