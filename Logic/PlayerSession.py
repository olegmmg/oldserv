from Server.Battle.VisionUpdate import VisionUpdate
from Server.Battle.StartLoadingMessage import StartLoadingMessage
from Server.Battle.UDPConnectionInfo import UDPConnectionInfo
import time
from threading import Thread
from Utils.Battle import Battle


class PlayerSession(Thread):
    def __init__(self, client, player, battle=None):
        Thread.__init__(self)
        self.client = client
        self.player = player
        self.battle = battle  # battle dict from Matchmaking
        self.subTick = 0
        self.tick = 0
        self.started = 0
        self.daemon = True

    def run(self):
        self.startBattle()

    def startBattle(self):
        self.player.inmm = False
        self.started = 1
        try:
            StartLoadingMessage(self.client, self.player).send()
            UDPConnectionInfo(self.client, self.player).send()
        except Exception as e:
            print(f"[PlayerSession] Error starting battle for {self.player.low_id}: {e}")
            self.started = 0
            return

        while self.started:
            self.tick += 1
            self.subTick = 0
            self.player.battleTick = self.tick
            try:
                self.process()
            except Exception:
                self.started = 0
                break
            time.sleep(0.045)

    def process(self):
        try:
            VisionUpdate(self.client, self.player).send()
        except Exception:
            self.started = 0
