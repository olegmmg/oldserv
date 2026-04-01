from Utils.Writer import Writer
from Utils.Matchmaking import ROOM_3V3, ROOM_SD


class StartLoadingMessage(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 20559
        self.player = player

    def encode(self):
        # Get battle participants from player object (set by Matchmaking._attach_bots_to_player)
        battle_players = getattr(self.player, 'battle_players', [])
        battle_bots    = getattr(self.player, 'battle_bots', [])
        room_type      = getattr(self.player, 'battle_room_type', ROOM_3V3)

        # Build full slot list: real players + bots
        all_slots = []
        for entry in battle_players:
            p = entry['player']
            all_slots.append({
                'high_id': 0,
                'low_id': p.low_id,
                'team': entry.get('team', 0),
                'name': p.name,
                'brawler_id': p.brawler_id,
                'skin_id': p.skin_id,
                'trophies': getattr(p, 'trophies', 0),
                'power_level': 1,
                'is_bot': False,
            })
        for bot in battle_bots:
            all_slots.append({
                'high_id': 0,
                'low_id': 0,
                'team': bot.get('team', 0),
                'name': bot['name'],
                'brawler_id': bot.get('brawler_id', 0),
                'skin_id': bot.get('skin_id', 0),
                'trophies': bot.get('trophies', 0),
                'power_level': bot.get('power_level', 1),
                'is_bot': True,
            })

        # Fallback: if no battle info (offline/solo), create single-player slot
        if not all_slots:
            all_slots = [{
                'high_id': 0,
                'low_id': self.player.low_id,
                'team': 0,
                'name': self.player.name,
                'brawler_id': self.player.brawler_id,
                'skin_id': self.player.skin_id,
                'trophies': getattr(self.player, 'trophies', 0),
                'power_level': 1,
                'is_bot': False,
            }]

        total = len(all_slots)
        max_plrs = 10 if room_type == ROOM_SD else 6

        # Pad to max if needed (shouldn't happen normally)
        while len(all_slots) < max_plrs:
            all_slots.append({
                'high_id': 0, 'low_id': 0,
                'team': 1, 'name': 'Bot',
                'brawler_id': 0, 'skin_id': 0,
                'trophies': 0, 'power_level': 1, 'is_bot': True,
            })
            total = len(all_slots)

        self.writeInt(6)   # version/unk
        self.writeInt(0)
        self.writeInt(0)

        self.writeInt(total)  # players count

        for i, slot in enumerate(all_slots):
            self.writeInt(slot['high_id'])
            self.writeInt(slot['low_id'])
            self.writeVint(i)                  # slot index
            self.writeVint(slot['team'])        # team (0 or 1)
            self.writeVint(0)

            self.writeInt(0)  # unk

            self.writeScId(16, slot['brawler_id'])
            self.writeVint(0)
            self.writeBoolean(False)
            self.writeString(slot['name'])
            self.writeVint(slot['power_level'] * 10 + 90)  # ~100
            self.writeVint(28000000)
            self.writeVint(43000000)
            self.writeVint(43000000)
            self.writeBoolean(slot['is_bot'])   # True = bot flag

        self.writeInt(0)  # count
        self.writeInt(0)  # count
        self.writeInt(0)  # unknown

        self.writeVint(0)
        self.writeVint(1)   # DrawMap
        self.writeVint(1)

        self.writeBoolean(True)
        self.writeVint(0)   # is Spectating
        self.writeVint(0)

        # Map selection: 15 = map category, 7 = map id
        map_id = getattr(self.player, 'map_id', 7)
        self.writeScId(15, map_id)
        self.writeBoolean(False)
