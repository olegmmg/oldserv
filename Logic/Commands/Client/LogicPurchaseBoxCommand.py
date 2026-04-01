from database.DataBase import DataBase
from Logic.Commands.Client.LogicBoxDataCommand import LogicBoxDataCommand
from Logic.MCbyLkPrtctrd.MilestonesClaimSupplyByLkPrtctrd import MilestonesClaimSupplyByLkPrtctrd as Supply
from Utils.Reader import BSMessageReader

class LogicPurchaseBoxCommand(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.a = self.read_Vint()
        self.b = self.read_Vint()
        self.c = self.read_Vint()
        self.d = self.read_Vint()
        self.boxid = self.read_Vint()


    def process(self):
        if self.boxid==3:
            self.boxid=11
            DataBase.replaceValue(self, 'gems', self.player.gems-80)
        elif self.boxid==1:
            self.boxid=12
            DataBase.replaceValue(self, 'gems', self.player.gems-30)
        Supply(self.client, self.player, "BOXLkPrtctrd", {"BoxDID": self.boxid}).send()