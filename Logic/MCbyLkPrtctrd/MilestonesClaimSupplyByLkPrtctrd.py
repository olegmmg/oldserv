from Utils.Writer import Writer
from random import randint as r
from database.DataBase import DataBase
from Logic.MCbyLkPrtctrd.MilestonesClaimHelpByLkPrtctrd import MilestonesClaimHelpByLkPrtctrd as Lyney 
import random as rnd
from Logic.Commands.Client.LogicBoxDataCommand import LogicBoxDataCommand as BOXES
class MilestonesClaimSupplyByLkPrtctrd(Writer):

    def __init__(self, client, player, what,data):
        super().__init__(client)
        self.id = 24111
        self.player = player

        self.id1 = what

        
        self.mult1 = data


    def encode(self):
        self.writeVInt=self.writeVint
        if self.id1 == "BOXLkPrtctrd":
            """boxtype = self.mult1["BoxDID"]
            boxtype = Lyney().GetAmountOfLevel(boxtype, [10,12,11], [6,7,8])
            lkprtctrd = {"V": True, "R": self.mult1["Road"], "L": self.mult1["Level"]+2, "S": self.mult1["Season"]}
            BOXES(self.client, self.player, boxtype, lkprtctrd).send()
            self.writeBoolean(False)
            self.writeVint(self.mult1["Road"])
            self.writeVint(self.mult1["Level"]+2)
            self.writeVint(self.mult1["Season"])
            for x in range(5):
                self.writeVInt(0)
            return"""
            self.writeBool = self.writeBoolean
            self.writeVInt = self.writeVint
            boxtype = self.mult1["BoxDID"]
            money = Lyney().GetAmountOfBox(boxtype)
            moneygive=[money]
            try:
                del self.player.UnlockedBrawlers["48"]
            except:
                pass
            ownedbrs = [int(LkPrtctrd) for LkPrtctrd,x in self.player.UnlockedBrawlers.items() if int(x)==1 and int(LkPrtctrd)<39 and self.player.brawlerPoints[str(LkPrtctrd)]<1410]
            ownedbrsforall = [int(LkPrtctrd) for LkPrtctrd,x in self.player.UnlockedBrawlers.items() if int(x)==1 and int(LkPrtctrd)<39]
            allbrswithoutown = [int(LkPrtctrd) for LkPrtctrd in range(39) if LkPrtctrd not in ownedbrsforall and LkPrtctrd!=33 and LkPrtctrd!=48]
            if boxtype == 11:
                ppcount = 5 if len(ownedbrs)>=5 else len(ownedbrs)
            elif boxtype==10:
                ppcount = 2 if len(ownedbrs)>=2 else len(ownedbrs)
            else:
                ppcount = 3 if len(ownedbrs)>=3 else len(ownedbrs)
            powerpointsgive = []
            pointsgivetable = {
                "10": {"1": 10, "2": 25},
                "11": {"1": 80, "2": 200},
                "12": {"1": 30, "2": 75}
            }
            #print('mmmm')
            for LkPrtctrd in range(ppcount):
                brawler = rnd.choice(ownedbrs)
                pointsnow = self.player.brawlerPoints[str(brawler)]
                pointsgive = rnd.randint(pointsgivetable[str(boxtype)]["1"], pointsgivetable[str(boxtype)]["2"])
                pointsgivefinish = pointsgive if pointsgive+pointsnow<=1410 else 1410-pointsnow
                ownedbrs.remove(brawler)
                powerpointsgive.append({"Brawler": brawler, "Points": pointsgivefinish})
            brsgive = []
            brsgivetable = {
                "10": [95,30,0,0],
                "11": [95,50,30,15],
                "12": [95,45,20,0]
            }
            for LkPrtctrd in [0,1,2,3,7,8,9,14,22,27,30,45]:
                try:
                    allbrswithoutown.remove(LkPrtctrd)
                except:
                    pass
            brsgivecount = rnd.choices([0,1,2,3], brsgivetable[str(boxtype)])[0]
            if len(allbrswithoutown)<brsgivecount:
                brsgivecount = len(allbrswithoutown)
            for LkPrtctrd in range(brsgivecount):
                brawler = rnd.choice(allbrswithoutown)
                allbrswithoutown.remove(brawler)
                brsgive.append(brawler)

            
            if boxtype==10 and brsgive!=[]:
                powerpointsgive=[]
                moneygive=[]


            self.writeVint(203)
            self.writeVint(0)
            self.writeVint(1)
            self.writeVint(boxtype)

            #1410
            rewardcount = len(moneygive)+len(powerpointsgive)+len(brsgive)
            self.writeVint(rewardcount) # Reward count
            for x in moneygive:
                self.writeVint(x) # Reward ammount
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(7)
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(0)
            for x in powerpointsgive:
                self.writeVint(x["Points"]) # Reward ammount
                self.writeBPScId(16, x["Brawler"]) # RewardID
                self.writeVint(6)
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(0)
            for x in brsgive:
                self.writeVint(1) # Reward ammount
                self.writeBPScId(16, x) # RewardID
                self.writeVint(1)
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(0)
            
            self.writeBool(False)
            try:
                self.writeVint(self.mult1["Road"])
                self.writeVint(self.mult1["Level"]+2)
                self.writeVint(self.mult1["Season"])
            except:
                self.writeVint(0)
                self.writeVint(0)
                self.writeVint(0)

            for x in range(11):
                self.writeVInt(0)
            
            for x in moneygive:
                self.player.gold += x
                dbupd = 'gold'
                DataBase.replaceValue(self, dbupd, self.player.gold)
            for x in powerpointsgive:
                self.player.brawlerPoints[str(x["Brawler"])]+=x["Points"]
            for x in brsgive:
                self.player.UnlockedBrawlers[str(x)] = 1
                DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
            return
        
        if self.id1 == "BPLkPrtctrd":
            self.writeVint(203)
            self.writeVint(0)
            self.writeVint(1)
            try:
                self.writeVint(self.mult1["Box"])
            except:
                self.writeVint(100)

            if self.mult1["Type"]==6:
                brawler = self.mult1["Character"][1]
                resbeen = self.player.brawlerPoints[str(brawler)]
                if resbeen + self.mult1["Amount"]>1410:
                    resnewplus = 1410 - resbeen
                    resnewmoney = self.mult1["Amount"]-resnewplus
                else:
                    resnewplus = self.mult1["Amount"]
                    resnewmoney = 0
                resnewpp = [resnewplus,resnewmoney*2]
            
            rewardcount = 1
            if self.mult1["Type"]==6:
                rewardcount = 2 if resnewpp[1]>0 else 1               

            if self.mult1["Type"]==9:
                rewardcount = 2 if self.player.UnlockedBrawlers[str(self.mult1['Character'][1])]==0 else 1

            self.writeVint(rewardcount) # Reward count
            if self.mult1["Type"] not in [1,6,9]:
                self.writeVint(self.mult1["Amount"]) # Reward ammount
                self.writeBPScId(0,0) # RewardID
                self.writeVint(self.mult1["Type"])
                self.writeBPScId(0,0) # RewardID
                self.writeBPScId(0,0) # RewardID
                self.writeBPScId(0,0) # RewardID
                self.writeVint(0)
            elif self.mult1["Type"]==1:
                self.writeVint(self.mult1["Amount"]) # Reward ammount
                self.writeBPScId(16, self.mult1["Character"][1]) # RewardID
                self.writeVint(self.mult1["Type"])
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(0)
            elif self.mult1["Type"]==9:
                if rewardcount==2:
                    self.writeVint(1) # Reward ammount
                    self.writeBPScId(16, self.mult1["Character"][1]) # RewardID
                    self.writeVint(1)
                    self.writeBPScId(0, 0) # RewardID
                    self.writeBPScId(0, 0) # RewardID
                    self.writeBPScId(0, 0) # RewardID
                    self.writeVint(0)
                    self.player.UnlockedBrawlers[str(self.mult1["Character"][1])] = 1
                    DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
                self.writeVint(1) # Reward ammount
                self.writeBPScId(16, self.mult1["Character"][1]) # RewardID
                self.writeVint(9)
                self.writeBPScId(29, self.mult1["Skin"][1]) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(0)
            elif self.mult1["Type"]==6:
                self.writeVint(resnewpp[0]) # Reward ammount
                self.writeBPScId(16, self.mult1["Character"][1]) # RewardID
                self.writeVint(6)
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeBPScId(0, 0) # RewardID
                self.writeVint(0)
                if resnewpp[1]>0:
                    self.writeVint(resnewpp[1]) # Reward ammount
                    self.writeBPScId(0, 0) # RewardID
                    self.writeVint(7)
                    self.writeBPScId(0, 0) # RewardID
                    self.writeBPScId(0, 0) # RewardID
                    self.writeBPScId(0, 0) # RewardID
                    self.writeVint(0)
            self.writeBoolean(False)
            self.writeVint(self.mult1["Road"])
            self.writeVint(self.mult1["Level"]+2)
            self.writeVint(self.mult1["Season"])
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)
            
            if self.mult1["Type"]==7:
                self.player.gold += self.mult1['Amount']
                dbupd = 'gold'
                DataBase.replaceValue(self, dbupd, self.player.gold)
            elif self.mult1["Type"]==8:
                self.player.gems += self.mult1['Amount']
                dbupd = 'gems'
                DataBase.replaceValue(self, dbupd, self.player.gems)
            elif self.mult1["Type"]==6:
                self.player.gold += resnewpp[1]
                DataBase.replaceValue(self, 'gold', self.player.gold)
                self.player.brawlerPoints[f"{self.mult1['Character'][1]}"]+=resnewpp[0]
                DataBase.replaceValue(self, 'brawlerPoints', self.player.brawlerPoints)
            elif self.mult1["Type"]==1:
                self.player.UnlockedBrawlers[str(self.mult1["Character"][1])] = 1
                DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
            elif self.mult1["Type"]==9:
                self.player.UnlockedSkins[str(self.mult1["Skin"][1])] = 1
                DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)
            return
        
        