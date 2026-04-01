"""
Matchmaking Manager
- Supports 3v3 (6 players) and Showdown/Столкновение (10 players)
- If waiting > 10 seconds: start immediately with bots, even if only 1 real player.
  Real players are always placed in team 0 (first slots).
  Remaining slots filled with bots — no cancel button shown to client.
- Столкновение: max 10 slots, same bot-fill logic after 10 sec.
"""

import time
import threading
import random
from Utils.Battle import Battle

MATCHMAKING_TIMEOUT = 10  # seconds

# Room types
ROOM_3V3   = 1  # 6 players total (3 per team)
ROOM_SD    = 3  # Showdown/Столкновение 10 players

# Bot name pool
BOT_NAMES = [
    "Bot_Shelly", "Bot_Colt", "Bot_Brock", "Bot_Nita",
    "Bot_Bull", "Bot_Jessie", "Bot_Dynamike", "Bot_Bo",
    "Bot_Tick", "Bot_8-Bit", "Bot_Emz", "Bot_El Primo",
]

# Shared queues: {room_type: [{'player': player_obj, 'client': client, 'joined_at': float}]}
_queues = {
    ROOM_3V3: [],
    ROOM_SD:  [],
}
_lock = threading.Lock()

# Active battles: {battle_id: {'players': [...], 'bots': [...], 'tick': int}}
_battles = {}
_battle_id_counter = [0]


def _next_battle_id():
    _battle_id_counter[0] += 1
    return _battle_id_counter[0]


def get_max_players(room_type):
    if room_type == ROOM_SD:
        return 10
    return 6  # 3v3 default


def join_queue(player, client, room_type=ROOM_3V3):
    """Add a player to the matchmaking queue."""
    with _lock:
        # Prevent duplicate entries
        for entry in _queues.get(room_type, []):
            if entry['player'].low_id == player.low_id:
                return
        if room_type not in _queues:
            _queues[room_type] = []
        _queues[room_type].append({
            'player': player,
            'client': client,
            'joined_at': time.time(),
        })
        player.inmm = True
    _try_start_battle(room_type)


def leave_queue(player, room_type=ROOM_3V3):
    """Remove player from queue."""
    with _lock:
        queue = _queues.get(room_type, [])
        _queues[room_type] = [e for e in queue if e['player'].low_id != player.low_id]
        player.inmm = False


def _make_bot(slot_index, team):
    """Create a lightweight bot dict."""
    return {
        'is_bot': True,
        'low_id': 0,  # bots have 0 high/low id
        'name': BOT_NAMES[slot_index % len(BOT_NAMES)],
        'team': team,
        'brawler_id': random.randint(0, 5),
        'skin_id': 0,
        'trophies': random.randint(100, 5000),
        'power_level': random.randint(1, 9),
    }


def _try_start_battle(room_type):
    """Try to start a battle; may fill bots if timeout exceeded."""
    with _lock:
        queue = _queues.get(room_type, [])
        max_plrs = get_max_players(room_type)
        now = time.time()

        # Check oldest waiting time
        if not queue:
            return

        oldest_wait = now - queue[0]['joined_at']
        enough_players = len(queue) >= max_plrs
        timeout_expired = oldest_wait >= MATCHMAKING_TIMEOUT

        # After 10 sec — start no matter how many real players (even 1)
        can_start_with_bots = timeout_expired and len(queue) >= 1

        if not enough_players and not can_start_with_bots:
            return

        # Take up to max_plrs real players
        selected = queue[:max_plrs]
        _queues[room_type] = queue[max_plrs:]

        # Build player list with team assignment
        participants = []
        bots = []

        if room_type == ROOM_3V3:
            # 3 per team
            for i, entry in enumerate(selected):
                team = 0 if i < 3 else 1
                entry['team'] = team
                participants.append(entry)
            # Fill remaining with bots
            for i in range(len(selected), max_plrs):
                team = 0 if i < 3 else 1
                bots.append(_make_bot(i, team))
        else:
            # Showdown: no teams (team = slot index)
            for i, entry in enumerate(selected):
                entry['team'] = i
                participants.append(entry)
            for i in range(len(selected), max_plrs):
                bots.append(_make_bot(i, i))

        battle_id = _next_battle_id()
        _battles[battle_id] = {
            'id': battle_id,
            'room_type': room_type,
            'players': participants,
            'bots': bots,
            'tick': 0,
            'started_at': now,
        }

    # Launch battle outside lock
    _launch_battle(_battles[battle_id])


def _launch_battle(battle):
    """Send StartLoading to all real players and start battle thread."""
    from Logic.PlayerSession import PlayerSession
    for entry in battle['players']:
        player = entry['player']
        client = entry['client']
        # Mark inmm=False BEFORE sending StartLoadingMessage so any stray
        # CancelMatchmaking packet from the client is silently dropped.
        player.inmm = False
        player.battle_id = battle['id']
        player.team = entry.get('team', 0)
        _attach_bots_to_player(player, battle)
        session = PlayerSession(client, player, battle)
        session.daemon = True
        session.start()


def _attach_bots_to_player(player, battle):
    """Store bot + full player list info on player object for StartLoadingMessage."""
    player.battle_players = battle['players']
    player.battle_bots = battle['bots']
    player.battle_room_type = battle['room_type']


def check_timeouts():
    """Background thread: periodically check if any queue needs bot-fill."""
    while True:
        time.sleep(1)
        for room_type in list(_queues.keys()):
            _try_start_battle(room_type)


def start_timeout_checker():
    t = threading.Thread(target=check_timeouts, daemon=True)
    t.start()
