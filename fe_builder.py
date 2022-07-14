import random as rand
import time
import os
import datetime
import traceback
def init_battle(char1,char2,dist,*weaponX):
    expGain=0
    dmgMod=0
    hitMod=0
    cont=False
    active_art=None
    z='End'
    if weaponX:
        weapon1=weaponX[0]
        startHP=char1.hp
        cont=True
    else:
        startHP=char2.hp
        viable_arts=[]
        art_types={}
        viable_weapons=[]
        for j in char1.weapon_arts:
            if dist in j.range:
                for i in char1.inventory:
                    if isinstance(i,weapon):
                        if i.weapontype==j.weapontype and i.curUses>=j.cost:
                            if j.weapontype not in art_types:
                                art_types[j.weapontype]=j.cost
                            elif j.weapontype in art_types:
                                if j.cost<art_types[j.weapontype]:
                                   art_types[j.weapontype]=j.cost
                            if j not in viable_arts:
                                viable_arts.append(j)                                         
        for i in range(0,len(char1.inventory)):
            if isinstance(char1.inventory[i],weapon):
                if dist in char1.inventory[i].rng or (char1.inventory[i].weapontype in art_types and char1.inventory[i].curUses>=art_types[char1.inventory[i].weapontype]):
                    if char1.inventory[i].weapontype in char1.weaponType:
                        if char1.weaponType[char1.inventory[i].weapontype]>=char1.inventory[i].weaponlevel:
                            print(str(i)+ " "+char1.inventory[i].name + " " + str(char1.inventory[i].curUses) +
                                  " " + str(char1.inventory[i].dmg) + " "+ char1.inventory[i].dmgtype + " " + str(char1.inventory[i].rng) +
                                  " " + str(char1.inventory[i].crit))
                            viable_weapons.append(char1.inventory[i])
    while cont==False:
        selection=input('Choose a weapon to use \n')
        try:
            if char1.inventory[int(selection)] in viable_weapons:                
                weapon1=char1.inventory[int(selection)]
                char1.active_item=weapon1
            possible_arts=[]
            for i in viable_arts:
                if i.weapontype==weapon1.weapontype and i.cost<=weapon1.curUses:
                    possible_arts.append(i)
            if len(possible_arts)>0:
                art=input('Input Y to use a weapon art \n')
                if art.lower()=='y':
                    for i in range(0,len(possible_arts)):
                        print(f'{i} {possible_arts[i].name}')
                    choice=input('Choose the weapon art to use \n')
                    try:
                        active_art=possible_arts[int(choice)]
                    except Exception as e:
                        print(traceback.format_exc())
                        print('Bad choice, try again')
            cont=True
        except Exception as e:
            print(traceback.format_exc())        
    if char2.active_item==None:
        weapon2=empty
    else:
        weapon2=char2.active_item
    if not nosupport:
        if isinstance(char1,player_char):
            hitMod+=char1.check_support_bonus()
        elif isinstance(char2,player_char):
            hitMod-=char2.check_support_bonus()
    if (weapon1.weapontype=='Sword' and weapon2.weapontype=='Lance') or (weapon1.weapontype=='Axe' and weapon2.weapontype=='Sword') or (weapon1.weapontype=='Lance' and weapon2.weapontype=='Axe'):
        dmgMod+=-1
        hitMod+=-10
    elif (weapon1.weapontype=='Sword' and weapon2.weapontype=='Axe') or (weapon1.weapontype=='Axe' and weapon2.weapontype=='Lance') or (weapon1.weapontype=='Lance' and weapon2.weapontype=='Sword'):
        dmgMod+=1
        hitMod+=10
    if battle(char1,weapon1,char2,dmgMod,hitMod,active_art)=='Continue':
        if weapon2!=None and dist in weapon2.rng:
            z=battle(char2,weapon2,char1,-dmgMod,-hitMod)
        else:
            z='Continue'
            input(f"{char2.name} was unable to counter \n")
    if z=='Continue' and char1.spd-5>=char2.spd and weapon1 in char1.inventory:
        input(f"{char1.name} made a follow up attack \n")
        battle(char1,weapon1,char2,dmgMod,hitMod,active_art)
    if z=='Continue' and char2.spd-5>=char1.spd and weapon2 in char2.inventory:
        input(f"{char2.name} made a follow up attack \n")
        battle(char2,weapon2,char1,-dmgMod,-hitMod)
    print(char1.name + " HP: "+str(char1.curhp)+'\n')
    input(char2.name+ " HP: "+str(char2.curhp))
    char1.battles+=1
    char2.battles+=1
    if weaponX:
        player_unit=char2
        player_weapon=weapon2
        enemy_unit=char1
    else:
        player_unit=char1
        enemy_unit=char2
        player_weapon=weapon1
    if enemy_unit.status=='Dead':
        player_unit.weaponType[player_weapon.weapontype]+=10
        expGain=30+enemy_unit.hp
    else:
        player_unit.weaponType[player_weapon.weapontype]+=1
        expGain=startHP-enemy_unit.curhp
    if paragon in player_unit.skill_list:
        expGain*=2
    if char1.status!='Dead':
        if galeforce not in char1.skills:
            char1.moved=True
    if player_unit.status!='Dead':
        if player_unit.level<20:
            player_unit.exp+=expGain
        if player_unit.exp>=100:
            player_unit.level_up()
            
def battle(char1,weapon1,char2,dmgMod,hitMod,*active_art):
    input(f'{char1.name} attacked {char2.name} with a {weapon1.name} \n')
    try:
        hitMod-=curMap.objectList[char2.location[0],char2.location[1]].avoidBonus
    except Exception as e:
        pass
    if active_art:
        if active_art[0]!=None:
            hitMod+=active_art[0].accuracy
            dmgMod=dmgMod+eval(f'{active_art[0].effect_change}')
    hit=1.5*char1.skill+.5*char1.luck+weapon1.hit+hitMod
    avoid=1.5*char2.spd+.5*char2.luck
    crit=.5*char1.skill+weapon1.crit
    dodge=char2.luck
    randohit=rand.randrange(0,100)
    randocrit=rand.randrange(0,100)
    truehit=hit-avoid
    truecrit=crit-dodge
    crit=False
    if char2.classType.name in weapon1.super_effective:
        dmgMod+=weapon1.dmg*weapon1.super_effective[char2.classType.name]
    if truehit>100:
        truehit=100
    elif truehit<0:
        truehit=0
    if truecrit>100:
        truecrit=100
    elif truecrit<0:
        truecrit=0 
    print(f"Hit chance of {truehit}")
    print(f"Crit chance of {truecrit}")
    if randohit <= truehit:
        pass
    else:
        input(f"{char1.name}'s attack missed")
        return("Continue")
    if randocrit <= truecrit:
        crit=True
    player_dict,enemy_dict,weapon_dict=char1.skill_roll(char2)
    if weapon1.dmgtype=='Phys':
        for i in char2.inventory:
            if isinstance(i,armor):
                if i.stat=='def':
                    dmgMod-=i.effect
        try:
            dmgMod-=curMap.objectList[char2.location[0],char2.location[1]].defBonus
        except Exception as e:
            pass
        damage=char1.atk+weapon1.dmg+dmgMod-char2.defense
    elif weapon1.dmgtype=='Magic':
        for i in char2.inventory:
            if isinstance(i,armor):
                if i.stat=='res':
                    dmgMod-=i.effect
        damage=char1.mag+weapon1.dmg+dmgMod-char2.res
    if damage<0:
        damage=0
    if crit==True:
        damage*=3
        input("Critical hit!")
    weapon1.curUses-=1
    if weapon1.curUses<=0:
        weapon1.breakX(char1)
    for i in player_dict:
        setattr(char1,i,player_dict[i])
    for j in enemy_dict:
        setattr(char2,j,enemy_dict[j])
    for k in weapon_dict:
        setattr(weapon1,k,weapon_dict[k])
    if char2.curhp-damage>0:
        char2.curhp=char2.curhp-damage
        input(f"{char1.name} attacked {char2.name} and did {damage} damage \n")
        return("Continue")
    else:
        char2.die(char1)
        return("End")

def menu(self):
    atkRange=[0]
    targetRange=[]
    end=False
    while end==False:
        tradeRange=[]
        supportRange=[]
        charTriggerRange=[]
        doors=[]
        triggerRange=False
        openable=False
        openableDoor=False
        for i in self.inventory:
            if isinstance(i,weapon):
                if i.weapontype in self.weaponType:
                    for j in i.rng:
                        if j not in atkRange:
                            atkRange.append(j)
                    for k in self.weapon_arts:
                        if k.weapontype==i.weapontype and k.cost<=i.curUses:
                            for m in k.range:
                                if m not in atkRange:
                                    atkRange.append(m)
        for i in curMap.spaces:
            if abs(i[0]-self.location[0])+abs(i[1]-self.location[1])==1:
                if (i[0],i[1]) in curMap.objectList:
                    if isinstance(curMap.objectList[i[0],i[1]],door):
                        if curMap.objectList[i[0],i[1]].opened==False:
                            doors.append([i,curMap.objectList[i[0],i[1]]])
            if curMap.spaces[i][0]==True:
                if abs(i[0]-self.location[0])+abs(i[1]-self.location[1]) in atkRange:
                    if curMap.spaces[i][1].alignment!=self.alignment and [i,curMap.spaces[i][1]] not in targetRange:
                        targetRange.append([i,curMap.spaces[i][1]])
                if abs(i[0]-self.location[0])+abs(i[1]-self.location[1])==1:
                    if curMap.spaces[i][1].alignment==self.alignment:
                        if [i,curMap.spaces[i][1]] not in tradeRange:
                            tradeRange.append([i,curMap.spaces[i][1]])
                        if curMap.spaces[i][1].name in self.support_list:
                            if (self.name, curMap.spaces[i][1].name) in self.alignment.support_master:
                                if int(self.support_list[curMap.spaces[i][1].name]/10)>self.alignment.support_master[self.name, curMap.spaces[i][1].name][0] and self.alignment.support_master[self.name, curMap.spaces[i][1].name][0]<len(self.alignment.support_master[self.name, curMap.spaces[i][1].name])-1 and[self.name, curMap.spaces[i][1].name] not in supportRange:
                                    supportRange.append([self.name, curMap.spaces[i][1].name])
                            elif (curMap.spaces[i][1].name,self.name) in self.alignment.support_master:
                                if int(self.support_list[curMap.spaces[i][1].name]/10)>self.alignment.support_master[curMap.spaces[i][1].name,self.name][0] and self.alignment.support_master[curMap.spaces[i][1].name,self.name][0]<len(self.alignment.support_master[curMap.spaces[i][1].name,self.name])-1 and[curMap.spaces[i][1].name,self.name] not in supportRange:
                                    supportRange.append([curMap.spaces[i][1].name,self.name])
                        if (self.name, curMap.spaces[i][1].name) in curMap.char_trigger_list:
                            charTriggerRange.append([self.name, curMap.spaces[i][1].name])
                        elif (curMap.spaces[i][1].name,self.name) in curMap.char_trigger_list:
                            charTriggerRange.append([curMap.spaces[i][1].name,self.name])
        if (self.location[0],self.location[1]) in curMap.triggerList:
            if curMap.triggerList[self.location[0],self.location[1]].triggered==False and (self.name in curMap.triggerList[self.location[0],self.location[1]].character or 'All' in curMap.triggerList[self.location[0],self.location[1]].character):
                print('E : Event')
                triggerRange=True
        if len(targetRange)>0:
            print("0 : Battle")
        if len(tradeRange)>0:
            print("T : Trade")
        if len(supportRange)>0 and not nosupport:
            print("B : Support")
        if len(charTriggerRange)>0:
            print("C : Character Event")
        print("1 : Inventory")
        print("2 : Equip")
        print("3 : Consume")
        print("4 : Check Stats")
        print("5 : End Turn")
        print("6 : Exit Menu")
        try:
            if isinstance(curMap.objectList[self.location[0],self.location[1]],throne):
                print("7 : Sieze Throne")
            elif isinstance(curMap.objectList[self.location[0],self.location[1]],shop):
                print("S : Shop")
            elif isinstance(curMap.objectList[self.location[0],self.location[1]],treasure_chest):
                for i in self.inventory:
                    if isinstance(i,key):
                        keyX=i
                        openable==True
                if curMap.objectList[self.location[0],self.location[1]].opened==True:
                    openable==False
                if openable==True:
                    print("Z : Open Chest")
        except Exception as e:
            pass
        if len(doors)>0:
            for i in self.inventory:
                if isinstance(i,key):
                    keyY=i
                    openableDoor==True
            if openableDoor:
                print('D : Open Door')
        v=input("Press the key of the action you wish to take \n")
        if v.lower()=='b' and len(supportRange)>0 and not nosupport:
            for i in range(0,len(supportRange)):
                print(f"{i} : {supportRange[i]}")
            choiceSupport=input("Press the number of the support you wish to view or x to cancel \n")
            if choiceSupport=='x':
                print('Returning to menu')
            else:
                try:
                    print(self.alignment.support_master[supportRange[int(choiceSupport)][0],
                                                        supportRange[int(choiceSupport)][1]][self.alignment.support_master[supportRange[int(choiceSupport)][0],
                                                                                                                           supportRange[int(choiceSupport)][1]][0]+1])
                    self.alignment.support_master[supportRange[int(choiceSupport)][0],supportRange[int(choiceSupport)][1]][0]+=1
                    self.moved=True
                    end=True
                except Exception as e:
                    print(traceback.format_exc())
                    print('Invalid input, returning to menu')
        elif v.lower()=='e' and triggerRange==True:
            print(curMap.triggerList[self.location[0],self.location[1]].event)
            curMap.triggerList[self.location[0],self.location[1]].triggered=True
        elif v.lower()=='z' and openable==True:
            self.add_item(curMap.objectList[self.location[0],self.location[1]].contents)
            curMap.objectList[self.location[0],self.location[1]].opened=True
            keyX.use(self)
            self.moved=True
            end=True
        elif v.lower()=='d' and openableDoor==True:
            for i in range(0,len(doors)):
                print(f'{i} : {doors[i][0]}')
            doorChoice=input('Input the door you would like to open or X to cancel \n')
            try:
                if choiceChar=='x':
                    pass
                elif doors[int(doorChoice)]:
                    doors[int(doorChoice)].opened=True
                    keyY.use(self)
                    self.moved=True
                    end=True
            except Exception as e:
                print(traceback.format_exc())
                print('Invalid input, returning to menu')
        elif v.lower()=='c' and len(charTriggerRange)>0:
            contChar=True
            while contChar==True:
                for j in range(0,len(charTriggerRange)):
                    print(f'{j} : {curMap.char_trigger_list[charTriggerRange[j][0],charTriggerRange[j][1]].name}')
                choiceChar=input("Input the event you wish to view or x to cancel \n")
                try:
                    if choiceChar=='x':
                        contChar=False
                    elif charTriggerRange[int(choiceChar)]:
                        print(f'{curMap.char_trigger_list[charTriggerRange[int(choiceChar)][0],charTriggerRange[int(choiceChar)][1]].event}')
                        contChar=False
                except Exception as e:
                    print(traceback.format_exc())
                    print('Bad selection, try again')            
        elif v=='0' and len(targetRange)>0:
            contBattle=True
            while contBattle==True:
                for j in range(0,len(targetRange)):
                    print(str(j)+": "+targetRange[j][1].name+" at "+str(targetRange[j][0]))
                choiceBattle=input("Input the enemy you wish to fight or x to cancel \n")
                try:
                    if choiceBattle=='x':
                        contBattle=False
                    elif targetRange[int(choiceBattle)][1]:
                        dis=abs(self.location[0]-targetRange[int(choiceBattle)][1].location[0])+abs(self.location[1]-targetRange[int(choiceBattle)][1].location[1])
                        init_battle(self,targetRange[int(choiceBattle)][1],dis)
                        end=True
                        contBattle=False
                except Exception as e:
                    print(traceback.format_exc())
                    print('Bad selection, try again')
        elif v.lower()=='t' and len(tradeRange)>0:
            for i in range(0,len(tradeRange)):
                print(i,' ',tradeRange[i][1].name)
            choiceTrade=input("Input the unit you wish to trade with or x to cancel \n")
            if choiceTrade.lower=='x':
                break
            else:
                try:
                    self.trade_items(tradeRange[int(choiceTrade)][1])
                except Exception as e:
                    print(traceback.format_exc())
                    print('Invalid input, returning to menu')
        elif v.lower()=='s':
            try:
                if isinstance(curMap.objectList[self.location[0],self.location[1]],shop):
                    self.enter_shop(curMap.objectList[self.location[0],self.location[1]])
                    self.moved=True
                    end=True
                    return
            except Exception as e:
                print(traceback.format_exc())
                print('Bad selection, try again')
        elif v=='1':
            self.show_inventory()
        elif v=='2':
            self.equip_weapon()
        elif v=='3':
            self.use_consumable()
            end=True
            return
        elif v=='5':
            self.moved=True
            end=True
            return
        elif v=='6':
            end=True
            return
        elif v=='4':
            self.check_stats()
        elif v=='7':
            try:
                if isinstance(curMap.objectList[self.location[0],self.location[1]],throne):
                    global levelComplete
                    levelComplete=True
                    end=True
                    return
            except Exception as e:
                print(traceback.format_exc())
                print('Bad selection, try again')
        else:
            print(traceback.format_exc())
            print("Bad selection, try again")
                                           
            
class character:
    character_list=[]    
    stats=['hp','atk','mag','skill','luck','defense','res','spd','movModifier']
    growths={'hpG':'hp','atkG':'atk','magG':'mag','skillG':'skill','luckG':'luck','defG':'defense','resG':'res','spdG':'spd'}
    def __init__(self,name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,alignment,classtype,weaponType,joinMap,inventory,level):
        self.name=name
        self.curhp=curhp
        self.hp=hp
        self.hpG=hpG
        self.atk=atk
        self.atkG=atkG
        self.mag=mag
        self.magG=magG
        self.skill=skill
        self.skillG=skillG
        self.luck=luck
        self.luckG=luckG
        self.defense=defense
        self.defG=defG
        self.res=res
        self.resG=resG
        self.spd=spd
        self.spdG=spdG
        self.movModifier=mov
        self.level=level
        self.exp=0
        self.kills=0
        self.battles=0
        self.status='Alive'
        self.joinMap=joinMap
        if isinstance(alignment,str):
            self.alignment=eval(alignment.lower())
        else:
            self.alignment=alignment
        self.inventory=inventory
        self.classType=None
        for i in classType.class_list:
            if i.name==classtype or i==classtype:
                self.classType=i
        if self.classType.skill_list[0]!=placeholder:
            self.skills=[self.classType.skill_list[0]]
            self.skills_all=[self.classType.skill_list[0]]
            if self.level>=10:
                self.skills.append(self.classType.skill_list[1])
                self.skills_all.append(self.classType.skill_list[1])
            if self.level==20:
                self.skills.append(self.classType.skill_list[2])
                self.skills_all.append(self.classType.skill_list[2])
        else:
            self.skills=[]
            self.skills_all=[]        
        self.mov=self.classType.moveRange+mov
        self.weaponType=weaponType
        for i in self.classType.weaponType:
            if i not in self.weaponType:
                self.weaponType[i]=self.classType.weaponType[i]
        self.active_item=None
        if len(inventory)>0:
            if isinstance(inventory[0],weapon):
                if inventory[0].weapontype in self.weaponType:
                    if inventory[0].weaponlevel>=self.weaponType[inventory[0].weapontype]:
                        self.active_item=inventory[0]
        self.location=[-1,-1]
        self.moved=False
        self.placed=False
        self.deployed=False
        for i in mapLevel.map_list:
            if i.mapNum==joinMap:
                if alignment==player:
                    i.player_roster.append(self)
                else:
                    i.enemy_roster.append(self)
        self.character_list.append(self)        
    def add_item(self,item):
        if len(self.inventory)<5:
            self.inventory.append(item)
            if self.active_item==None and type(item)==weapon:
                if item.weapontype in self.weaponType:
                    self.active_item=item
        else:
            print('0 '+ item.name)
            for i in range(0,len(self.inventory)):
                print(str(i+1)+' '+self.inventory[i].name)            
            drop=input('Choose an item to send to the convoy with the number key \n')
            if int(drop)==0:
                self.alignment.convoy.append(item)
                return
            else:
                self.alignment.convoy.append(self.inventory[int(drop)-1])
                self.inventory.pop(int(drop)-1)
                self.inventory.append(item)
                if self.active_item==None and type(item)==weapon:
                    if item.weapontype in self.weaponType:
                        self.active_item=item
    def store_item(self):
        end=False
        while end==False:
            if len(self.inventory)==0:
                end=True
                return
            for i in range(0,len(self.inventory)):
                print(f'{i+1}')
                self.inventory[i].info()
            dropY=input('Choose an item to send to the convoy with the number key, or exit by inputing x \n')
            if dropY.lower()=='x':
                end=True
                return
            else:
                try:
                    item=self.drop_item(self.inventory[int(dropY)-1])
                    self.alignment.convoy.append(item)
                except Exception as e:
                    print('Invalid input, try again')
        return
    def enter_shop(self,shop):
        end=False
        while end==False:
            buysell=input('Input 0 to buy, 1 to sell, or x to exit \n')
            if buysell=='0':
                self.buy_item(shop)
            elif buysell=='1':
                self.sell_item()
            elif buysell.lower()=='x':
                return
    def sell_item(self):
        end=False
        while end==False:
            if len(self.inventory)==0:
                print(f"{self.name}'s inventory is empty, exiting the shop")
                return
            print(f"{self.alignment.gold} gold")
            for i in range(0,len(self.inventory)):
                print(f"{i}: {self.inventory[i].name} {(self.inventory[i].cost/2)*(self.inventory[i].curUses/self.inventory[i].maxUses)}")
            sell=input('Input the number of the item you would like to sell or x to exit \n')
            if sell.lower()=='x':
                return
            try:
                confirm=input(f"Would you like to sell the {self.inventory[int(sell)].name} for {(self.inventory[int(sell)].cost/2)*(self.inventory[int(sell)].curUses/self.inventory[int(sell)].maxUses)} gold? Input Y to confirm, anything else to cancel \n")
                if confirm.lower()=='y':
                    print(f"Sold {self.inventory[int(sell)].name} for {(self.inventory[int(sell)].cost/2)*(self.inventory[int(sell)].curUses/self.inventory[int(sell)].maxUses)} gold")
                    item=self.drop_item(self.inventory[int(sell)])
                    self.alignment.gold+=(item.cost/2)*(item.curUses/item.maxUses)
            except Exception as e:
                print(traceback.format_exc())
                print('Invalid input, please try again')
    def buy_item(self,shop):
        end=False
        while end==False:
            if len(shop.contents)==0:
                print("We're fresh out of items, sorry chum")
                return
            print(f"{self.alignment.gold} gold")
            for i in range(0,len(shop.contents)):
                print(f"{i} : {shop.contents[i][0].name}, {shop.contents[i][0].cost} gold x{shop.contents[i][1]}")
            buy=input('Input the number of the item you would like to buy or x to exit \n')
            if buy.lower()=='x':
                return
            try:
                if shop.contents[int(buy)][0].cost<=self.alignment.gold:
                    confirm=input(f"Would you like to buy the {shop.contents[int(buy)][0].name} for {shop.contents[int(buy)][0].cost} gold? Input Y to confirm, anything else to cancel \n")
                    if confirm.lower()=='y':
                        print(f"{shop.contents[int(buy)][0].name} bought!")
                        z=shop.contents[int(buy)][0].name
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](False)
                        except:
                            p=shop.contents[int(buy)][0]
                        self.add_item(p)
                        shop.contents[int(buy)][1]-=1
                        if shop.contents[int(buy)][1]<=0:
                            shop.contents.pop(int(buy))
                        self.alignment.gold-=p.cost
                else:
                    print("That item is too expensive for you! Buy something else, will ya?")
            except Exception as e:
                print(traceback.format_exc())
                print('Invalid input, try again')
    def trade_items(self,trade_partner):
        cont=False
        while cont==False:
            if len(self.inventory)==0 and len(trade_partner.inventory)==0:
                cont=True
                return
            self.show_inventory()
            trade_partner.show_inventory()
            route=input(f"Input 0 to trade from {self.name}'s inventory, 1 to trade from {trade_partner.name}'s inventory, or x to exit \n")
            if route.lower()=='x':
                cont=True
                return
            elif route=='0':
                for i in range(0,len(self.inventory)):
                    print(f"{i} {self.inventory[i].name}")
                route2=input(f"Input the item to trade or x to cancel \n")
                if route2.lower()=='x':
                    break
                else:
                    try:
                        item=self.drop_item(self.inventory[int(route2)])
                        trade_partner.inventory.append(item)
                        while len(trade_partner.inventory)>5:
                            routeFix=input(f"{trade_partner.name} has too many items, input 0 to send one to the convoy or 1 to trade an item to {self.name} \n")
                            if routeFix=='0':
                                for i in range(0,len(trade_partner.inventory)):
                                    print(f"{i} {trade_partner.inventory.name}")
                                routeConvoyFix=input(f"Input the item to store \n")
                                try:
                                    itemX=trade_partner.drop_item(trade_partner.inventory[int(routeConvoyFix)])
                                    trade_partner.alignment.convoy.append(itemX)
                                except Exception as e:
                                    print('Invalid input, try again')
                            elif routeFix=='1':
                                for i in range(0,len(trade_partner.inventory)):
                                    print(f"{i} {trade_partner.inventory.name}")
                                routeTradeFix=input(f"Input the item to trade \n")
                                try:
                                    itemX=trade_partner.drop_item(trade_partner.inventory[int(routeTradeFix)])
                                    self.inventory.append(itemX)
                                except Exception as e:
                                    print('Invalid input, try again')
                            else:
                                print('Invalid input, try again')
                    except Exception as e:
                        print(traceback.format_exc())
            elif route=='1':
                for i in range(0,len(trade_partner.inventory)):
                    print(f"{i} {trade_partner.inventory[i].name}")
                route2=input(f"Input the item to trade or x to cancel \n")
                if route2.lower()=='x':
                    break
                else:
                    try:
                        item=trade_partner.inventory.pop(int(route2))
                        if trade_partner.active_item==item:
                            trade_partner.active_item=None
                        self.inventory.append(item)
                        while len(self.inventory)>5:
                            routeFix=input(f"{self.name} has too many items, input 0 to send one to the convoy or 1 to trade an item to {trade_partner.name} \n")
                            if routeFix=='0':
                                for i in range(0,len(self.inventory)):
                                    print(f"{i} {self.inventory.name}")
                                routeConvoyFix=input(f"Input the item to store \n")
                                try:
                                    itemX=self.drop_item(self.inventory[int(routeConvoyFix)])
                                    self.alignment.convoy.append(itemX)
                                except Exception as e:
                                    print('Invalid input, try again')
                            elif routeFix=='1':
                                for i in range(0,len(self.inventory)):
                                    print(f"{i} {self.inventory.name}")
                                routeTradeFix=input(f"Input the item to trade \n")
                                try:
                                    itemX=self.drop_item(self.inventory[int(routeTradeFix)])
                                    trade_partner.inventory.append(itemX)
                                except Exception as e:
                                    print('Invalid input, try again')
                            else:
                                print('Invalid input, try again')
                    except Exception as e:
                        print(traceback.format_exc())
                pass
            else:
                print(route)
                print('Invalid input, please try again')
    def withdraw_items(self):
        end=False
        if len(self.alignment.convoy)==0:
            end=True
        while end==False:
            if len(self.alignment.convoy)==0:
                end=True
                return
            if len(self.inventory)<5:
                for i in range(0,len(self.alignment.convoy)):
                    print(f'{i} {self.alignment.convoy[i].name}')
                item=input('Enter the number of the item you want to add or input x to exit \n')
                if item.lower()=='x':
                    end=True
                    return
                else:
                    try:
                        self.alignment.convoy[int(item)].info()
                        confirm=input(f"Input Y to confirm that you want to add this item to {self.name}'s inventory \n")
                        if confirm.lower()=='y':
                            addition=self.alignment.convoy.pop(int(item))
                            self.inventory.append(addition)
                            print(f"{addition.name} added to {self.name}'s inventory")
                        else:
                            pass
                    except Exception as e:
                        print('Invalid input, try again')
            else:
                print(f"{self.name}'s inventory is full, returning to menu")
                end=True
                return
    def drop_item(self,item):
        itemX=self.inventory.pop(item)
        if self.active_item==item:
            self.active_item=None
            print(f'{self.name} has no active item equipped')
        return itemX
    def add_skill(self,skill):
        if skill not in self.skills_all:
            self.skills_all.append(skill)
        if skill not in self.skills:
            if len(self.skills)<5:
                self.skills.append(skill)
            else:
                print('0 '+ skill.name)
                for i in range(0,len(self.skills)):
                    print(str(i+1)+' '+self.skills[i].name)            
                drop=input('Choose a skill to forget with the number key \n')
                if drop==0:
                    return
                else:
                    self.skills.pop(int(drop)-1)
                    self.skills.append(skill)
    def swap_skills(self):
        end=False
        while end==False:
            for i in range(0,len(self.skills_all)):
                if self.skills_all[i] not in self.skills:
                    print(f"{i} : {self.skills_all[i].name}")
            add=input(f"Input the number of the skill you want to add or x to cancel")
            if add.lower()=='x':
                return
            else:
                try:
                    self.add_skill(self.skills_all[int(add)])
                except Exception as e:
                    print(traceback.format_exc())
                    print('Invalid input, try again')
    def level_up(self,*silent):
        self.exp-=100
        self.level+=1
        if self.level>20:
            self.level=20
            self.exp=0
            return
        if not silent:
            print('Level up!')
        if self.level==10 or self.level==20:
            if self.level==10:
                skillX=self.classType.skill_list[1]
            else:
                skillX=self.classType.skill_list[2]
            if not silent:
                print(f'You have unlocked the skill {skillX.name}')
            self.add_skill(skillX)
        if not silent:
            print('Current level: '+str(self.level))
        for i in self.growths:
            if getattr(self,i)>=1 or getattr(self,i)<=-1:
                if getattr(self,self.growths[i])+int(getattr(self,i))>=0:
                    setattr(self,i,getattr(self,self.growths[i])+int(getattr(self,i)))
                    if not silent:
                        print(f'+{int(i)} {self.growths[i]} {getattr(self,i)}')
            if rand.random()<=getattr(self,i) and getattr(self,i)>=0:
                setattr(self,i,getattr(self,self.growths[i])+1)
                if not silent:
                    print(f'+1 {self.growths[i]} {getattr(self,i)}')
            elif getattr(self,i)<0:
                if -rand.random()>=getattr(self,i):
                    if getattr(self,self.growths[i])>1:
                        setattr(self,i,getattr(self,self.growths[i])-1)
                        if not silent:
                            print(f'-1 {self.growths[i]} {getattr(self,i)}')                
    def skill_roll(self,enemy):
        changed_stats_player={}
        changed_stats_enemy={}
        changed_stats_weapon={}
        for i in self.skills:
            roll=rand.randrange(0,100)
            stat=getattr(self,i.trigger_stat)
            if roll<=stat*i.trigger_chance:
                print(f'{i.name} has procced!')
                time.sleep(1)
                if i.effect_target=='self':
                    cur=getattr(self,i.effect_stat)
                    if i.effect_temp==True:
                        changed_stats_player[i.effect_stat]=cur
                    final_num=round(eval(f'{cur}{i.effect_operator}{i.effect_change}'))
                    setattr(self,i.effect_stat,final_num)
                elif i.effect_target=='enemy':
                    cur=getattr(enemy,i.effect_stat)
                    if i.effect_temp==True:
                        changed_stats_enemy[i.effect_stat]=cur
                    final_num=round(eval(f'{cur}{i.effect_operator}{i.effect_change}'))
                    setattr(enemy,i.effect_stat,final_num)
                elif i.effect_target=='weapon':
                    weap=self.active_item
                    cur=getattr(weap,i.effect_stat)
                    if i.effect_temp==True:
                        changed_stats_weapon[i.effect_stat]=cur
                    final_num=round(eval(f'{cur}{i.effect_operator}{i.effect_change}'))
                    setattr(weap,i.effect_stat,final_num)                    
        return changed_stats_player,changed_stats_enemy,changed_stats_weapon
    def show_inventory(self):
        print(self.name + "'s inventory: ")
        for i in self.inventory:
            i.info()
    def move(self,location):
        if (location[0],location[1]) not in curMap.spaces:
            print("That location is out of bounds")
            dest=input('Type where you want to move the character to in X,Y form \n')
            dest=dest.split(',')
            self.move([int(dest[0]),int(dest[1])])
            return 
        if curMap.spaces[location[0],location[1]][0]==True and curMap.spaces[location[0],location[1]][1]!=self:
            print("Theres already something there, try again")
            dest=input('Type where you want to move the character to in X,Y form \n')
            dest=dest.split(',')
            self.move([int(dest[0]),int(dest[1])])
            return       
        if location[0]==self.location[0] and location[1]==self.location[1]:
            input(f"Opening menu for {self.name}")
            menu(self)
        elif abs(location[0]-self.location[0])+abs(location[1]-self.location[1])<=self.mov:
            self.update_location(location)
            input(f'{self.name} moved')
            self.moved=True
            menu(self)
        else:
            print("Bad move, try again")
            dest=input('Type where you want to move the character to in X,Y form \n')
            dest=dest.split(',')
            self.move([int(dest[0]),int(dest[1])])
    def update_location(self,location):
        try:
            if curMap.spaces[self.location[0],self.location[1]][1]==self:
                curMap.spaces[self.location[0],self.location[1]]=[False]
        except Exception as e:
            pass
        if (location[0],location[1]) in curMap.spaces:
            self.location=location
            curMap.spaces[location[0],location[1]]=[True,self]
        else:
            cont=False
            while cont==False:
                try:
                    loc=input(f'{self.name} has been wrongly placed, please enter a new location for them to be in x,y form\n')
                    loc=loc.split(',')
                    loc[0]=int(loc[0])
                    loc[1]=int(loc[1])
                    self.update_location(loc)
                    return
                except:
                   print(traceback.format_exc())
                   print('Invalid input, please try again')
    def use_consumable(self):
        for i in range(0,len(self.inventory)):
            if isinstance(self.inventory[i],consumable):
                print(i)
                self.inventory[i].info()
            elif isinstance(self.inventory[i],promotion_item):
                if self.level>=10 and len(self.classType.promotions) >0 and ('All' in self.inventory[i].classType or self.classType.name in self.inventory[i].classType):
                    print(i)
                    self.inventory[i].info()
        path=input('Choose a item to use with their number, or input X to cancel \n')
        if path.lower()=='x':
            return
        else:
            if isinstance(self.inventory[int(path)],consumable):
                self.inventory[int(path)].active=True
                self.inventory[int(path)].curUses-=1
                if self.inventory[int(path)].stat=='curhp':
                   if self.curhp+self.inventory[int(path)].effect>self.hp:
                       self.curhp=self.hp
                       if self.inventory[int(path)].curUses<=0:
                           self.inventory[int(path)].breakX(self)
                       return
                setattr(self,self.inventory[int(path)].stat,getattr(self,self.inventory[int(path)].stat)+self.inventory[int(path)].effect)
                print(getattr(self,self.inventory[int(path)].stat))
                if self.inventory[int(path)].curUses<=0:
                   self.inventory[int(path)].breakX(self)
            elif isinstance(self.inventory[i],promotion_item):
                if self.level>=10 and len(self.classType.promotions) >0 and ('All' in self.inventory[i].classType or self.classType.name in self.inventory[i].classType):
                    self.promote()
    def consumable_turn(self,consumable):
        if consumable.active==False or consumable.dur<0:
            return
        elif consumable.active==True and consumable.curdur>1:
            consumable.curdur-=1
            return
        elif consumable.active==True and consumable.curdur==1:
            setattr(self,consumable.stat,getattr(self,consumable.stat)-consumable.effect)
            consumable.curdur=consumable.dur
            consumable.active=False
    def equip_weapon(self):
        for i in range(0,len(self.inventory)):
            if isinstance(self.inventory[i],weapon):
                print(i)
                self.inventory[i].info()
        path=input('Choose a item to use with their number, or input X to cancel \n')
        if path.lower()=='x':
            return
        else:
           if isinstance(self.inventory[int(path)],weapon):
               self.active_item=self.inventory[int(path)]
    def die(self,killer):
        self.status='Dead'
        self.alignment.roster.remove(self)
        print(f"{killer.name} attacked {self.name} and did over {self.curhp} damage, defeating the foe")
        self.curhp=0
        curMap.spaces[self.location[0],self.location[1]]=[False]
        killer.kills+=1
        for i in self.inventory:
            if i.droppable==True:
                print(f"{self.name} dropped {i.name}")
                killer.add_item(i)
        if self.classType==lord:
            global lordDied
            lordDied=True
    def check_stats(self):
        print('\n')
        print("Name: " + self.name)
        for i in self.stats:
            print(f'{i.capitalize()}: {getattr(self,i)}')
        print("Move: "+str(self.mov))
        print("Moved: "+str(self.moved))
        print("Class: "+self.classType.name)
        print("Level: "+str(self.level)+" Exp: "+str(self.exp))
        print("Skills:")
        for i in self.skills:
            print(i.name)
        print("Weapon Levels")
        for i in self.weaponType:
            print(f'{i}: {self.weaponType[i]}')
    def promote(self):
        cont=False
        while cont==False:
            try:
                for i in range(0,len(self.classType.promotions)):
                    print(f'{i}: {self.classType.promotions[i]}')
                choice=input('Choose the class to promote to\n')
                for i in classType.class_list:
                    if i.name==self.classType.promotions[int(choice)]:
                        newClass=i
                self.reclass(newClass)
                self.level=1
                self.exp=0
                return
            except Exception as e:
                print(traceback.format_exc())
    def reclass(self,newClass):
        allow=False
        if neggrowth:
            allow=True
        mov_change=newClass.moveRange-self.classType.moveRange
        self.mov+=mov_change
        if self.mov<1:
            self.mov=1
        print(f'MOV +{mov_change}')
        for i in self.stats:
            stat_change=getattr(newClass,i)-getattr(self.classType,i)
            setattr(self,i,getattr(self,i)+stat_change)
            print(f'{i} +{stat_change}')
            if i=='hp':
                if self.hp==0:
                    self.hp=1
                if self.curhp>self.hp:
                    self.curhp=self.hp
            else:
                if getattr(self,i)<0:
                    setattr(self,i,0)
        for j in self.growths:
            if getattr(self,j)<0:
                allow=True
            growth_change=getattr(newClass,j)-getattr(self.classType,j)
            setattr(self,j,getattr(self,j)+growth_change)
            print(f'{j} +{growth_change}')
            if getattr(self,j)<0 and allow==False:
                setattr(self,j,0)
        self.add_skill(newClass.skill_list[0])
        print(f'Learned {newClass.skill_list[0].name}')
        for i in newClass.weaponType:
            if i not in self.weaponType:
                self.weaponType[i]=newClass.weaponType[i]
        self.classType=newClass
        
class enemy_char(character):
    enemy_char_list=[]
    nameClass='enemy_char'
    def __init__(self,name,classX,joinMap,inventory,level,spawn):
        self.name=name
        self.spawn=spawn
        for i in classType.class_list:
            if i.name==classX:
                classtype=i
        super().__init__(name,classtype.hp,classtype.hp,classtype.hpG,classtype.atk,classtype.atkG,classtype.mag,classtype.magG,
                         classtype.skill,classtype.skillG,classtype.luck,classtype.luckG,classtype.defense,classtype.defG,classtype.res,classtype.resG,classtype.spd,classtype.spdG,0,enemy,classX,{},joinMap,inventory,1)
        while self.level<level:
            self.level_up(1)
        if self not in self.enemy_char_list:
            self.enemy_char_list.append(self)
class boss(character):
    boss_list=[]
    nameClass='boss'
    def __init__(self,name,curhp,hp,atk,mag,skill,luck,defense,res,spd,mov,classType,weaponType,joinMap,inventory,level,spawn):
        self.name=name
        self.spawn=spawn
        super().__init__(name,curhp,hp,0,atk,0,mag,0,skill,0,luck,0,defense,0,res,0,spd,0,mov,enemy,classType,weaponType,joinMap,inventory,level)
        if self not in self.boss_list:
            self.boss_list.append(self)
class recruitable(character):
    recruitable_list=[]
    nameClass='recruitable'
    def __init__(self,name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,spawn,support_list,weapon_arts,recruit_convo):
        self.name=name
        self.support_list=support_list
        self.weapon_arts=weapon_arts
        self.spawn=spawn
        self.recruit_convo=recruit_convo
        super().__init__(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,enemy,classType,weaponType,joinMap,inventory,level)
        if self not in self.recruitable_list:
            self.recruitable_list.append(self)
class player_char(character):
    player_char_list=[]
    nameClass='player_char'
    def __init__(self,name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,support_list,weaponarts):
        self.name=name
        self.support_list=support_list
        self.weapon_arts=[]
        for i in weapon_art.weapon_art_list:
            for j in weaponarts:
                if i.name==j:
                    self.weapon_arts.append(i)
        super().__init__(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,player,classType,weaponType,joinMap,inventory,level)
        if self not in self.player_char_list:
            self.player_char_list.append(self)
    def check_support_bonus(self):
        support_bonus=0
        for i in range(-1,2):
            for j in range(-1,2):
                if abs(i+j)==1:
                    try:
                        if curMap.spaces[self.location[0]+i,self.location[1]+j][0]==True:
                            if curMap.spaces[self.location[0]+i,self.location[1]+j][1].name in self.support_list:
                                support_bonus+=self.support_list[curMap.spaces[self.location[0]+i,self.location[1]+j][1].name]
                    except Exception as e:
                        pass
        return support_bonus
    
class classType:
    class_list=[]
    def __init__(self,name,moveType,hp,hpG,atk,atkG,mag,magG,skillX,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,moveRange,weaponType,promotions,skill_list):
        self.name=name
        self.moveType=moveType
        self.hp=hp
        self.hpG=hpG
        self.atk=atk
        self.atkG=atkG
        self.mag=mag
        self.magG=magG
        self.skill=skillX
        self.skillG=skillG
        self.luck=luck
        self.luckG=luckG
        self.defense=defense
        self.defG=defG
        self.res=res
        self.resG=resG
        self.spd=spd
        self.spdG=spdG
        self.moveRange=moveRange
        self.weaponType=weaponType
        self.promotions=promotions
        self.skill_list=[]
        for i in skill_list:
            for j in skill.skill_list:
                if j.name==i or j==i:
                    self.skill_list.append(j)
        self.class_list.append(self)
    def info(self):
        print(f'Name: {self.name}')
        print(f'Movement Type: {self.moveType}')
        print(f'Weapon Types: {self.weaponType}')
        print('Promotions:')
        for i in self.promotions:
            print(i.name)
        print('Skills:')
        for i in self.skill_list:
            print(i.name)
   
class weapon:
    weapon_list=[]
    def __init__(self,name,maxUses,dmg,dmgtype,rng,crit,hit,weapontype,droppable,cost,rank,super_effective):
        self.name=name
        self.curUses=maxUses
        self.maxUses=maxUses
        self.dmg=dmg
        self.dmgtype=dmgtype
        self.rng=rng
        self.crit=crit
        self.hit=hit
        self.weapontype=weapontype
        self.super_effective=super_effective
        self.droppable=droppable
        self.cost=cost
        self.weaponlevel=rank
        self.weapon_list.append(self)
    def info(self):
        print("Name: " +self.name)
        print("Weapon Type: "+self.weapontype)
        print("Current durability: "+str(self.curUses))
        print("Max durability: " +str(self.maxUses))
        print(f"Weapon level: {self.weaponlevel}")
        print("Power: "+str(self.dmg))
        print("Hit: "+str(self.hit))
        print("Crit: "+str(self.crit))
        print("Range: "+str(self.rng))
        print('\n')
    def breakX(self,char):        
        input(self.name + " Broke!")
        char.inventory.pop(self)
        char.active_item=None
empty=weapon('Empty',0,0,'Empty',[0],0,0,'Empty',False,0,0,{})
unique_weapons=[empty]
base_misc=[]
class sword(weapon):
    def __init__(self,name,maxUses,dmg,dmgtype,rng,crit,hit,droppable,cost,rank,super_effective):
        super().__init__(name,maxUses,dmg,dmgtype,rng,crit,hit,'Sword',droppable,cost,rank,super_effective)
base_sword=[]
class lance(weapon):
    def __init__(self,name,maxUses,dmg,dmgtype,rng,crit,hit,droppable,cost,rank,super_effective):
        super().__init__(name,maxUses,dmg,dmgtype,rng,crit,hit,'Lance',droppable,cost,rank,super_effective)
base_lance=[]
class axe(weapon):
    def __init__(self,name,maxUses,dmg,dmgtype,rng,crit,hit,droppable,cost,rank,super_effective):
        super().__init__(name,maxUses,dmg,dmgtype,rng,crit,hit,'Axe',droppable,cost,rank,super_effective)
base_axe=[]
class bow(weapon):
    def __init__(self,name,maxUses,dmg,dmgtype,rng,crit,hit,droppable,cost,rank,super_effect):
        super_effective={'Wyvern':2}
        for i in super_effect:
            super_effective[i]=super_effect[i]
        super().__init__(name,maxUses,dmg,dmgtype,rng,crit,hit,'Bow',droppable,cost,rank,super_effective)
base_bow=[]
class fist(weapon):
    def __init__(self,name,maxUses,dmg,crit,hit,droppable,cost,rank,super_effective):
        super().__init__(name,maxUses,dmg,'Phys',[1],crit,hit,'Fist',droppable,cost,rank,super_effective)
base_fist=[]
class tome(weapon):
    def __init__(self,name,maxUses,dmg,rng,crit,hit,droppable,cost,rank,super_effective):
        super().__init__(name,maxUses,dmg,'Magic',rng,crit,hit,'Tome',droppable,cost,rank,super_effective)
base_tome=[]
class iron_sword(sword):
    def __init__(self,droppable):
        super().__init__('Iron Sword',30,4,'Phys',[1],10,85,droppable,500,0,{})
base_iron_sword=iron_sword(False)
base_sword.append(base_iron_sword)
class silver_sword(sword):
    def __init__(self,droppable):
        super().__init__('Silver Sword',20,10,'Phys',[1],25,105,droppable,1500,25,{})
base_silver_sword=silver_sword(False)
base_sword.append(base_silver_sword)
class levin_sword(sword):
    def __init__(self,droppable):
        super().__init__('Levin Sword',25,10,'Magic',[1,2],0,100,droppable,750,0,{})
base_levin_sword=levin_sword(False)
base_sword.append(base_levin_sword)
class iron_lance(lance):
    def __init__(self,droppable):
        super().__init__('Iron Lance',30,6,'Phys',[1],0,70,droppable,500,0,{})
base_iron_lance=iron_lance(False)
base_lance.append(base_iron_lance)
class javelin(lance):
    def __init__(self,droppable):
        super().__init__('Javelin',30,5,'Phys',[1,2],0,65,droppable,750,10,{})
base_javelin=javelin(False)
base_lance.append(base_javelin)
class silver_lance(lance):
    def __init__(self,droppable):
        super().__init__('Silver Lance',20,14,'Phys',[1],0,90,droppable,1500,25,{})
base_silver_lance=silver_lance(False)
base_lance.append(base_silver_lance)
class iron_axe(axe):
    def __init__(self,droppable):
        super().__init__('Iron Axe',30,8,'Phys',[1],0,60,droppable,400,0,{})
base_iron_axe=iron_axe(False)
base_axe.append(base_iron_axe)
class silver_axe(axe):
    def __init__(self,droppable):
        super().__init__('Silver Axe',20,16,'Phys',[1],0,80,droppable,1500,25,{})
base_silver_axe=silver_axe(False)
base_axe.append(base_silver_axe)
class hand_axe(axe):
    def __init__(self,droppable):
        super().__init__('Hand Axe',25,6,'Phys',[1,2],0,55,droppable,750,10,{})
base_hand_axe=hand_axe(False)
base_axe.append(base_hand_axe)
class iron_bow(bow):
    def __init__(self,droppable):
        super().__init__('Iron Bow',40,4,'Phys',[2],0,100,droppable,250,0,{})
base_iron_bow=iron_bow(False)
base_bow.append(base_iron_bow)
class silver_bow(bow):
    def __init__(self,droppable):
        super().__init__('Silver Bow',20,12,'Phys',[2],0,110,droppable,1000,25,{})
base_silver_bow=silver_bow(False)
base_bow.append(base_silver_bow)
class fire(tome):
    def __init__(self,droppable):
        super().__init__('Fire',30,5,[1,2],0,90,droppable,600,0,{"Laguz":2})
base_fire=fire(False)
base_tome.append(base_fire)
class forsetti(tome):
    def __init__(self,droppable):
        super().__init__('Forsetti',25,25,[1,2],25,100,droppable,10000,50,{"Wyvern":2})
base_forsetti=forsetti(False)
base_tome.append(base_forsetti)
class gauntlet(fist):
    def __init__(self,droppable):
        super().__init__('Gauntlet',100,2,20,100,droppable,250,0,{})
base_gauntlet=gauntlet(False)
base_fist.append(base_gauntlet)
base_weapon_dict={'sword':base_sword,'lance':base_lance,'axe':base_axe,'tome':base_tome,'fist':base_fist}

class key:
    key_list=[]
    def __init__(self,droppable):
        self.name='Key'
        self.curUses=5
        self.maxUses=5
        self.droppable=droppable
    def info(self):
        print("Name: "+self.name)
        print("Current durability: "+str(self.curUses))
        print("Max durability: " +str(self.maxUses))
    def use(self,char):
        self.curUses-=1
        if curUses<=0:
            self.breakX(char)
    def breakX(self,char):        
        print(self.name + " Broke!")
        char.inventory.remove(self)
base_key=key(False)
base_misc.append(base_key)
       
class consumable:
    consumable_list=[]
    def __init__(self,name,maxUses,itemType,effect,stat,droppable,cost,*dur):
        self.name=name
        self.curUses=maxUses
        self.maxUses=maxUses
        self.itemType=itemType
        self.effect=effect
        self.stat=stat
        self.droppable=droppable
        self.cost=cost
        self.active=False
        if dur:
            self.dur=dur
            self.curdur=dur
        else:
            self.dur=-1
            self.curdur=-1
        self.consumable_list.append(self)
    def info(self):
        print("Name: "+self.name)
        print("Current durability: "+str(self.curUses))
        print("Max durability: " +str(self.maxUses))
        print("Item type: "+self.itemType)
        print("Amount of change: "+str(self.effect))
        print("Stat to change: "+self.stat)
        print('\n')
    def breakX(self,char):        
        print(self.name + " Broke!")
        char.inventory.remove(self)
class vulnary(consumable):
    def __init__(self,droppable):
        super().__init__('Vulnary',3,'Healing',10,'curhp',droppable,100)
base_vulnary=vulnary(False)
base_misc.append(base_vulnary)
class mystic_water(consumable):
    def __init__(self,droppable):
        super().__init__('Mystic Water',5,'Buff',7,'res',5,droppable,250)
base_mystic_water=mystic_water(False)
base_misc.append(base_mystic_water)

class promotion_item:
    promotion_item_list=[]
    def __init__(self,name,classType,droppable,cost):
        self.name=name
        self.classType=classType
        self.droppable=droppable
        self.curUses=0
        self.cost=cost
        self.promotion_item_list.append(self)
    def info(self):
        print('Name: ',self.name)
        print('Classes this item promotes: /n')
        for i in self.classType:
            print(i.name)
class master_seal(promotion_item):
    def __init__(self,droppable):
        super().__init__('Master Seal',['All'],droppable,10000)
base_master_seal=master_seal(False)
base_misc.append(base_master_seal)

class armor:
    armor_list=[]
    def __init__(self,name,effect,stat,droppable,cost):
        self.name=name
        self.effect=effect
        self.stat=stat
        self.droppable=droppable
        self.cost=cost
        self.armor_list.append(self)
        self.curUses=0
    def info(self):
        print("Name: "+self.name)
        print("Stat bonus of "+str(self.effect)+" in "+self.stat)
        print('\n')
base_armor=[]
class shield(armor):
    def __init__(self,droppable):
        super().__init__('Shield',3,'def',droppable,1000)
base_shield=shield(False)
base_armor.append(base_shield)
        
class skill:
    skill_list=[]
    def __init__(self,name,trigger_chance,trigger_stat,effect_stat,effect_change,effect_operator,effect_temp,effect_target,*relative_stat):
        self.name=name
        self.trigger_chance=trigger_chance
        self.trigger_stat=trigger_stat
        self.effect_stat=effect_stat
        self.effect_change=effect_change
        self.effect_operator=effect_operator
        self.effect_target=effect_target
        self.effect_temp=effect_temp
        self.skill_list.append(self)
        
class weapon_art:
    weapon_art_list=[]
    def __init__(self,name,cost,accuracy,effect_stat,effect_change,effect_operator,weapontype,super_effective,rng):
        self.name=name
        self.cost=cost
        self.accuracy=accuracy
        self.effect_stat=effect_stat
        self.effect_change=effect_change
        self.effect_operator=effect_operator
        self.weapontype=weapontype
        self.super_effective=super_effective
        self.range=rng
        self.weapon_art_list.append(self)
                                    
class alignment:
    alignment_list=[]
    def __init__(self,name):
        self.name=name
        self.roster=[]
        self.convoy=[]
        self.gold=0
        self.alignment_list.append(self)
        self.support_master={}
    def show_convoy(self):
        if len(self.convoy)==0:
            print('The convoy is empty')
            return
        for i in self.convoy:
            i.info()
    def buy_item(self,shop):
        end=False
        while end==False:
            print(f"{self.gold} gold")
            for i in range(0,len(shop.contents)):
                print(f"{i} : {shop.contents[i][0].name}, {shop.contents[i][0].cost} gold x{shop.contents[i][1]}")
            buy=input('Input the number of the item you would like to buy or x to exit \n')
            if buy.lower()=='x':
                return
            try:
                if shop.contents[int(buy)][0].cost<=self.gold:
                    confirm=input(f"Would you like to buy the {shop.contents[int(buy)][0].name} for {shop.contents[int(buy)][0].cost} gold? Input Y to confirm, anything else to cancel \n")
                    if confirm.lower()=='y':
                        print(f"{shop.contents[int(buy)][0].name} bought!")
                        z=shop.contents[int(buy)][0].name
                        z=z.replace(' ','_')
                        z=z.lower()
                        p=globals()[z](False)
                        self.convoy.append(p)
                        shop.contents[int(buy)][1]-=1
                        if shop.contents[int(buy)][1]<=0:
                            shop.contents.pop(int(buy))
                        self.gold-=p.cost
                else:
                    print("That item is too expensive for you! Buy something else, will ya?")
            except Exception as e:
                print(traceback.format_exc())
                print('Invalid input, try again')
    def sell_item(self):
        end=False
        while end==False:
            print(f"{self.gold} gold")
            for i in range(0,len(self.convoy)):
                print(f"{i}: {self.convoy[i].name} {(self.convoy[i].cost/2)*(self.convoy[i].curUses/self.convoy[i].maxUses)}")
            sell=input('Input the number of the item you would like to sell or x to exit \n')
            if sell.lower()=='x':
                return
            try:
                confirm=input(f"Would you like to sell the {self.convoy[int(sell)].name} for {(self.convoy[int(sell)].cost/2)*(self.convoy[int(sell)].curUses/self.convoy[int(sell)].maxUses)} gold? Input Y to confirm, anything else to cancel \n")
                if confirm.lower()=='y':
                    print(f"Sold {self.convoy[int(sell)].name} for {(self.convoy[int(sell)].cost/2)*(self.convoy[int(sell)].curUses/self.convoy[int(sell)].maxUses)} gold")
                    item=self.convoy.pop(int(sell))
                    self.gold+=(item.cost/2)*(item.curUses/item.maxUses)
            except Exception as e:
                print(traceback.format_exc())
                print('Invalid input, please try again')
    def show_roster(self):
        for i in self.roster:
            if i.deployed==True:
                i.check_stats()
    def turn_end(self):
        for i in self.roster:
            try:
                if i.curhp+curMap.objectList[i.location[0],i.location[1]].hpBonus<i.hp:
                    i.curhp+=curMap.objectList[i.location[0],i.location[1]].hpBonus
                else:
                    i.curhp=i.hp
            except Exception as e:
                print(traceback.format_exc())
                pass
            for j in i.inventory:
                if isinstance(j,consumable):
                    i.consumable_turn(j)
            i.moved=False
            if self==player:
                for j in curMap.spaces:
                    if curMap.spaces[j][0]==True:
                        if abs(j[0]-i.location[0])+abs(j[1]-i.location[1])==1 and curMap.spaces[j][1].alignment==i.alignment and curMap.spaces[j][1].name in i.support_list:
                            i.support_list[curMap.spaces[j][1].name]+=1
                print(i.name,i.support_list)
            
class mapLevel:
    map_list=[]
    def __init__(self,name,y_size,x_size,mapNum,spawns,player_roster,enemy_roster):
        self.name=name
        self.objectList={}
        self.spaces={}
        self.triggerList={}
        self.char_trigger_list={}
        self.spawns=spawns
        self.mapNum=mapNum
        self.turn_count=1
        self.battle_saves=0
        self.y_size=y_size
        self.x_size=x_size
        for i in range(0,y_size):
            for j in range(0,x_size):
                self.spaces[j,i]=[False]
        self.completion_turns=0
        self.player_roster=[]
        self.enemy_roster=[]
        self.map_list.append(self)
    def start_map(self):
        global levelComplete
        levelComplete=False
        for i in self.player_roster:
            if i not in player.roster:
                player.roster.append(i)
        enemy.roster=self.enemy_roster
        for i in enemy.roster:
            i.update_location(i.spawn)
        for i in player.roster:
            i.deployed=False
            i.curhp=i.hp
        inventory=True
        while inventory==True:
            print('0 Trade Items')
            print('1 Store Items')
            print('2 Withdraw Items')
            print('3 Buy Items')
            print('4 Sell Items')
            print('5 Use Items')
            print('6 Swap Skills')
            if not nosupport:
                print('7 Support')
            if saveallowed:
                print('8 Save')
            print('9 Place Units And Start Map')
            inventory_input=input('Input the number key of the path you want to take or input x to exit \n')
            if inventory_input=='0':
                for j in range(0,len(player.roster)):
                    if player.roster[j].status=='Alive':
                        print(str(j)+" "+player.roster[j].name)
                p1=input('Enter the number of the first unit you want to participate in the trade or x to cancel \n')
                p2=input('Enter the number of the second unit you want to participate in the trade or x to cancel \n')
                if p1.lower()=='x' or p2.lower=='x':
                    pass
                else:
                    try:
                      player.roster[int(p1)].trade_items(player.roster[int(p2)])
                    except:
                        print('Invalid input, returning to menu')
            elif inventory_input=='5':
                for j in range(0,len(player.roster)):
                    if player.roster[j].status=='Alive':
                        print(str(j)+" "+player.roster[j].name)
                choice=input(f"Enter the number of the unit you want to store items or x to cancel \n")
                if choice.lower()=='x':
                    pass
                else:
                    try:
                        player.roster[int(choice)].use_consumable()
                    except Exception as e:
                        print('Invalid input, returning to menu')
            elif inventory_input=='1':
                for j in range(0,len(player.roster)):
                    if player.roster[j].status=='Alive':
                        print(str(j)+" "+player.roster[j].name)
                choice=input(f"Enter the number of the unit you want to store items or x to cancel \n")
                if choice.lower()=='x':
                    pass
                else:
                    try:
                        player.roster[int(choice)].store_item()
                    except Exception as e:
                        print('Invalid input, returning to menu')                
            elif inventory_input=='2':
                if len(player.convoy)==0:
                    print('The convoy is empty, returning to menu')
                else:
                    for j in range(0,len(player.roster)):
                        if player.roster[j].status=='Alive':
                            print(str(j)+" "+player.roster[j].name)
                    choice=input(f"Enter the number of the unit you want to withdraw items or x to cancel \n")
                    if choice.lower()=='x':
                        pass
                    else:
                        try:
                            player.roster[int(choice)].withdraw_items()
                        except Exception as e:
                            print('Invalid input, returning to menu')                 
            elif inventory_input=='3':
                #Buy items
                print('0 Convoy')
                for j in range(0,len(player.roster)):
                    if player.roster[j].status=='Alive':
                        print(str(j+1)+" "+player.roster[j].name)    
                choice=input(f"Enter who you want to buy items or x to cancel \n")
                if choice=='0':
                    player.buy_item(baseShop)
                elif choice.lower()=='x':
                    pass
                else:
                    try:
                        player.roster[int(choice)-1].buy_item(baseShop)
                    except Exception as e:
                        print(traceback.format_exc())
                        print('Invalid input, returning to menu')
                pass
            elif inventory_input=='4':
                #Sell Items
                print('0 Convoy')
                for j in range(0,len(player.roster)):
                    if player.roster[j].status=='Alive':
                        print(str(j+1)+" "+player.roster[j].name)    
                choice=input(f"Enter who you want to sell items or x to cancel \n")
                if choice=='0':
                    player.sell_item()
                elif choice.lower()=='x':
                    pass
                else:
                    try:
                        player.roster[int(choice)-1].sell_item()
                    except Exception as e:
                        print(traceback.format_exc())
                        print('Invalid input, returning to menu')
            elif inventory_input=='6':
                #Swap skills
                skill_count=0
                for j in range(0,len(player.roster)):
                    if player.roster[j].status=='Alive' and len(player.roster[j].skills)!=len(player.roster[j].skills_all):
                        print(str(j)+" "+player.roster[j].name)
                        skill_count+=1
                if skill_count==0:
                    print('Noone has any skills to swap. Returning to menu')
                else:
                    choice=input(f"Enter the number of the unit you want to swap skills or x to cancel \n")
                    try:
                        player.roster[int(choice)].swap_skills()
                    except Exception as e:
                        print(traceback.format_exc())
                        print('Invalid input, returning to menu')
            elif inventory_input=='7' and not nosupport:
                supportRange=[]
                for unit in player.roster:
                    for support_partner in unit.support_list:
                        if (unit.name, support_partner) in player.support_master:
                            if int(unit.support_list[support_partner]/10)>player.support_master[unit.name, support_partner][0] and player.support_master[unit.name, support_partner][0]<len(player.support_master[unit.name, support_partner])-1 and[unit.name, support_partner] not in supportRange:
                                supportRange.append([unit.name, support_partner])
                        elif (support_partner,unit.name) in player.support_master:
                            if int(unit.support_list[support_partner]/10)>player.support_master[support_partner,unit.name][0] and player.support_master[support_partner,unit.name][0]<len(player.support_master[support_partner,unit.name])-1 and[support_partner,unit.name] not in supportRange:
                                supportRange.append([support_partner,unit.name])
                if len(supportRange)==0:
                    print('There are no supports available at this time')
                else:
                    for i in range(0,len(supportRange)):
                        print(f'{i} {supportRange[i]}')
                    choiceSupport=input('Enter the number of the support you would like to view or x to cancel \n')
                    if choiceSupport.lower()=='x':
                        pass
                    else:
                        try:
                            print(player.support_master[supportRange[int(choiceSupport)][0],
                                                        supportRange[int(choiceSupport)][1]][player.support_master[supportRange[int(choiceSupport)][0],
                                                                                                                   supportRange[int(choiceSupport)][1]][0]+1])
                            player.support_master[supportRange[int(choiceSupport)][0],supportRange[int(choiceSupport)][1]][0]+=1
                        except Exception as e:
                            print(traceback.format_exc())
            elif inventory_input=='8' and saveallowed:
                save()
            elif inventory_input.lower()=='x' or inventory_input=='9':
                inventory=False
            else:
                print('Invalid input, please try again')   
        self.display('cur')
        for i in self.spawns:
            cont=False
            count=0
            while cont==False:
                for j in range(0,len(player.roster)):
                    if player.roster[j].placed==False and player.roster[j].status=='Alive':
                        print(str(j)+" "+player.roster[j].name)
                        count+=1
                    else:
                        print(player.roster[j].placed)
                if count==0:
                    cont=True
                    break
                choice=input(f"Enter the number of the unit you want at {i} \n")
                try:
                    if player.roster[int(choice)].placed==False:
                       player.roster[int(choice)].update_location(i)
                       player.roster[int(choice)].placed=True
                       player.roster[int(choice)].deployed=True
                       cont=True
                    else:
                       print("Improper choice, try again") 
                except:
                    print("Improper choice, try again")
        for i in player.roster:
            i.placed=False
            i.moved=False
    def display(self,mode,*dj):
        prev=-1
        rows=[]
        cur=[]
        cont=False
        while cont==False:
            for i in self.spaces:
                if i[1]==0:
                    if i[0]==0:
                        cur=[0]           
                    cur.append(str(i[0]))
                    prev=i[1]
            cont=True
        rows.append(cur)
        prev=-1
        for i in self.spaces:
            char=None
            try:
                char=self.objectList[i].display
            except Exception as e:
                pass
            if dj:
                if i in dj[0]:
                    char='#'
            if(i[1]!=prev):
                if prev!=-1:
                    rows.append(cur)
                cur=[i[1]]
            if char==None:                    
                char=" "
            if self.spaces[i][0]==True:
                if mode.lower()=='cur' or mode.lower()=='djik':
                    if self.spaces[i][1].alignment==enemy:
                        char="E"
                    elif self.spaces[i][1].alignment==player:
                        char="P"
            if mode.lower()=='base':
                for j in self.enemy_roster:
                    if [i[0],i[1]]==j.spawn:
                        char='E'
                if [i[0],i[1]] in self.spawns:
                    char='P'
            if i[0]>=10:
                char+=' '
            cur.append(char)
            prev=i[1]
        rows.append(cur)
        for j in rows:
            print(j)            
    def add_map_objects(self):
        cont=False
        while cont==False:
            obj_list=[]
            for i in display_list:
                if isinstance(i,mapObject):
                    print(f'{i.display}: {i.name}')
                    obj_list.append(i)
            self.display('base')
            object_place=input('Input the display character for the map object you wish to place, 1 to view details of an object, or 0 to finish\n')
            if object_place=='0':
                confirm=input('Input Y to confirm that you are done editing this map and quit, anything else to cancel\n')
                if confirm.lower()=='y':
                    return
            elif object_place=='1':
                for i in obj_list:
                    print(f'{i.display}: {i.name}')
                object_info=input('Input the display character for the map object you wish to view details on')
                for i in obj_list:
                    if object_info==i.display:
                        i.info()
            else:
                cont=True
                while cont==True:
                    possibility=None
                    for i in obj_list:
                        if object_place==i.display:
                            possibility=i
                    if possibility==None:
                        print('Invalid input, try again')
                    else:
                        print(f'Input the coordinates where you would like the {possibility.name} to be placed on the map in x,y integer form, with 0,0 being the top left and 1,1 being down and to the right of that')
                        print('Any x,y pair will work as long as its on the map and not currently occupied, not just 0,0 or 1,1')
                        print('Input x to cancel')
                        location=input('Enter the coordinates now\n')
                        if location.lower()!='x':
                            try:
                                location=location.split(',')
                                location[0]=int(location[0])
                                location[1]=int(location[1])
                                print(self.x_size)
                                print(self.y_size)
                                moveOn=True
                                if (location[0],location[1]) in self.objectList:
                                    print(f'There is already a {self.objectList[location[0],location[1]].name} at {location[0]},{location[1]}.')
                                    confirm=input(f'Input Y to confirm that you want to overwrite this object or anything else to cancel\n')
                                    if confirm.lower()=='y':
                                        pass
                                    else:
                                        moveOn=False
                                for i in self.spawns:
                                    if [location[0],location[1]]==i and possibility.name=='Void' or possibility.name=='Water' or possibility.name=='Door':
                                        print('There is a spawn at this location, you cant add this object there')
                                        moveOn=False
                                for i in self.enemy_roster:
                                    if [location[0],location[1]]==i.spawn:
                                        if i.classType.moveType!='Pirate' and i.classType.moveType!='Flying' and possibility.name=='Water':
                                            print('There is a enemy spawn at this location, you cant add this object there')
                                            moveOn=False
                                        elif i.classType.moveType!='Flying' and possibility.name=='Void':
                                            print('There is a enemy spawn at this location, you cant add this object there')
                                            moveOn=False
                                        elif possibility.name=='Door':
                                            print('There is a enemy spawn at this location, you cant add this object there')
                                            moveOn=False
                                if location[0]<self.x_size and location[1]<self.y_size and location[0]>=0 and location[1]>=0 and moveOn==True:
                                    contI=False
                                    if possibility.name=='Chest' or possibility.name=='Shop':
                                        contI=True
                                        inventory=[]
                                    while contI==True:                                
                                        if possibility.name=='Chest':
                                            inventory=stock_inventory('chest')
                                            if inventory==[]:
                                                cont=False
                                                contI=False
                                        elif possibility.name=='Shop':
                                            inventory=edit_shop()
                                    z=possibility.name.replace(' ','_')
                                    z=z.lower()
                                    if possibility.name=='Shop':
                                        globals()[z](self,[location[0],location[1]],inventory)
                                    elif possibility.name=='Treasure Chest':
                                        globals()[z](self,[location[0],location[1]],inventory[0])
                                    else:
                                        globals()[z](self,[location[0],location[1]])
                                else:
                                    print('Invalid input, try again')
                            except:
                                    print(traceback.format_exc())
    def delete_map_objects(self):
        cont=True
        while cont==True:
            self.display('base')
            for i in self.objectList:
                print(f'{i}: {self.objectList[i].name}')
            path=input(f'Input the x,y coordinates of the object you want to delete or x to finish\n')
            if path.lower()=='x':
                cont=False
            else:
                try:
                    path=path.split(',')
                    path[0]=int(path[0])
                    path[1]=int(path[1])
                    if (path[0],path[1]) in self.objectList:
                        confirm=input(f'Input Y to confirm that you want to delete the {self.objectList[path[0],path[1]].name} at {path[0]},{path[1]} or anything else to cancel\n')
                        if confirm.lower()=='y':
                            del self.objectList[path[0],path[1]]
                            print('Object deleted')
                        else:
                            print('Deletion canceled, returning to menu')
                except:
                    print(traceback.format_exc())
                    print('Invalid input, try again')
        


class tempMap:
    def __init__(self,name,mapLevel):
        self.name=name
        self.mapLevel=mapLevel
        
class mapObject:
    objectList=[]
    def __init__(self,name,mapLevel,location,defBonus,avoidBonus,hpBonus,moveCost,display):
        self.name=name
        self.mapLevel=mapLevel
        self.location=location
        self.defBonus=defBonus
        self.avoidBonus=avoidBonus
        self.hpBonus=hpBonus
        self.moveCost=moveCost
        self.display=display
        self.objectList.append(self)
        if mapLevel!=None:
            self.mapLevel.objectList[self.location[0],self.location[1]]=self
    def info(self):
        print(f'Name: {self.name}')
        print(f'Defense Bonus: {self.defBonus}')
        print(f'Avoid Bonus: {self.avoidBonus}')
        print(f'Healing: {self.hpBonus} per turn')
        print(f'Move Cost: {self.moveCost}')
display_list=[]
###WHEN ADDING NEW OBJECTS
###IF THEY ARE IMPASSIBLE ADD THEM TO THE add_map_objects EXCEPTION LIST
###AND ADD IN BASE FORMS AND APPEND THOSE BASE FORMS TO THE DISPLAY LIST
class fort(mapObject):
    def __init__(self,mapLevel,location):
        super().__init__('Fort',mapLevel,location,1,10,10,1,'F')
base_fort=fort(None,None)
display_list.append(base_fort)
class forest(mapObject):
    def __init__(self,mapLevel,location):
        super().__init__('Forest',mapLevel,location,1,15,0,2,'^')
base_forest=forest(None,None)
display_list.append(base_forest)
class throne(mapObject):
    def __init__(self,mapLevel,location):
        super().__init__('Throne',mapLevel,location,3,5,0,1,'h')
    def info(self):
        super().info()
        print('Sieze this with your Lord to complete a level')
base_throne=throne(None,None)
display_list.append(base_throne)
class void(mapObject):
    def __init__(self,mapLevel,location):
        super().__init__('Void',mapLevel,location,0,0,0,9999,'X')
    def info(self):
        super().info()
        print('Only crossable by flyers')
base_void=void(None,None)
display_list.append(base_void)
class water(mapObject):
    def __init__(self,mapLevel,location):
        super().__init__('Water',mapLevel,location,0,0,0,998,'~')
    def info(self):
        super().info()
        print('Pirates can walk on this and flyers can fly over it')
base_water=water(None,None)
display_list.append(base_water)
class desert(mapObject):
    def __init__(self,mapLevel,location):
        super().__init__('Desert',mapLevel,location,0,0,0,2,'.')
base_desert=desert(None,None)
display_list.append(base_desert)
class treasure_chest(mapObject):
    def __init__(self,mapLevel,location,contents):
        self.contents=contents
        self.opened=False
        super().__init__('Treasure Chest',mapLevel,location,0,0,0,1,'H')
    def info(self):
        super().info()
        print('Can be opened by a key to gain the treasure inside')
    def edit_contents(self):
        print(f'The current item in this chest is {self.contents.name}')
        print('Choose the new item for this chest')
        new_item=stock_inventory('chest')
        if len(new_item)>0:
            self.contents=new_item[0]
            print(f'{self.contents.name} is now in the chest')
        else:
            print('No new item added to chest')
base_treasure_chest=treasure_chest(None,None,None)
display_list.append(base_treasure_chest)
class shop(mapObject):
    def __init__(self,mapLevel,location,contents):
        self.contents=contents
        super().__init__('Shop',mapLevel,location,0,0,0,1,'S')
    def info(self):
        super().info()
        print('Can enter these to buy and sell items with gold')
    def edit_contents(self):
        self.contents=edit_shop(self)
base_shop=shop(None,None,None)
display_list.append(base_shop)
class door(mapObject):
    def __init__(self,mapLevel,location):
        self.opened=False
        super().__init__('Door',mapLevel,location,0,0,0,999,'D')
    def info(self):
        super().info()
        print('Can open these with a key while standing by them to open up a path')
base_door=door(None,None)
display_list.append(base_door)

class map_fake:
    def __init__(self,name,display):
        self.name=name
        self.display=display
        global display_list
        display_list.append(self)
map_fake('Player','P')
map_fake('Enemy','E')

class trigger:
    triggerList=[]
    def __init__(self,name,mapLevel,location,event,*character):
        self.name=name
        self.mapLevel=mapLevel
        self.location=location
        self.event=event
        self.triggered=False
        if character:
            self.character=character
        else:
            self.character=['All']
        self.triggerList.append(self)
        if mapLevel!=None:
            self.mapLevel.triggerList[location[0],location[1]]=self           
class char_trigger:
    char_trigger_list=[]
    def __init__(self,name,mapLevel,event,characters,*location):
        self.name=name
        self.mapLevel=mapLevel
        self.event=event
        self.triggered=False
        self.characters=characters
        if location:
            self.location=location
        else:
            self.location=[-1,-1]
        self.char_trigger_list.append(self)
        if mapLevel!=None:
            self.mapLevel.char_trigger_list[characters[0],characters[1]]=self
        
def gameplay(align):
    count=0
    board=[]
    if curMap.turn_count%5==0:
        checkpoint=True
    else:
        checkpoint=False
    global levelComplete
    if levelComplete==True:
        return
    for i in range(0,len(align.roster)):
        if align.roster[i].moved==False and align.roster[i].status=='Alive' and align.roster[i].deployed==True:
            count+=1
        elif align.roster[i].moved==True and align.roster[i].status=='Alive' and align.roster[i].deployed==True and checkpoint==True:
            checkpoint=False
    if curMap.mapNum==1 and curMap.turn_count==5 and checkpoint==True:
        print('You can save the game once every 5 turns for free, but only if you havent moved any units. Use this wisely!')
    while checkpoint==True:
        saveQue=input('Would you like to save? Input Y to save or X to pass\n')
        if saveQue.lower()=='y':
            save('_battle')
            checkpoint=False
        elif saveQue.lower()=='x':
            checkpoint=False
        else:
            print('Invalid input, try again')
    if count==0:
        align.turn_end()
        return
    for i in player.roster:
        if i.deployed==True and i.status=='Alive':
            print(f'Player unit {i.name} at {i.location}')
    for i in enemy.roster:
        if i.status=='Alive':
            print(f'Enemy unit {i.name}, level {i.level} {i.classType.name} at {i.location}')
    cont2=False
    while cont2==False:
        curMap.display('cur')
        print(f'There are {count} units that can still move')
        print('0: View Character Key')
        print("1: Move unit")
        print("2: View an enemies range")
        print("3: View roster")
        print("4: View convoy")
        print("5: View map features")
        print("6: End Turn")
        if curMap.battle_saves<1 and saveallowed:
            print("7: Save (you get 1 battle save per map)")
        path=input('Enter the number of the path you want to take \n')
        if path=='3':
            align.show_roster()
        elif path=='0':
            for i in display_list:
                print(f'{i.name} : {i.display}')
        elif path=='7' and curMap.battle_saves<1 and saveallowed:
            curMap.battle_saves+=1
            save('_battle')
        elif path=='4':
            align.show_convoy()
        elif path=='5':
            curMap.display('map')
        elif path=='6':
            align.turn_end()
            return
        elif path=='2':
            for i in range(0,len(enemy.roster)):
                print(f'{i} : {enemy.roster[i].name} {enemy.roster[i].location}')
            enemy_checked=input('Enter the number of the enemy whose range you want to check \n')
            ec_r=djikstra(enemy.roster[int(enemy_checked)])
            curMap.display('djik',ec_r)
            listX=[]
            for i in ec_r:
                listX.append(i)
            print(listX)
        elif path=='1':
            for i in range(0,len(align.roster)):
                if align.roster[i].moved==False and align.roster[i].status=='Alive' and align.roster[i].deployed==True:
                    print(str(i)+" "+align.roster[i].name+' '+str(align.roster[i].location))
            cont1=False
            while cont1==False:
                try:
                    choice=input("Enter the number of the unit you want to move \n")
                    print(f"The current location of {align.roster[int(choice)].name} is {align.roster[int(choice)].location} and they can move {align.roster[int(choice)].mov} spaces")
                    cont1=True
                except Exception as e:
                    print('Bad selection')
            dj=djikstra(align.roster[int(choice)])
            curMap.display('djik',dj)
            listY=[]
            for i in dj:
                listY.append(i)
            print(listY)
            cont=False
            while cont==False:
                dest=input('Type where you want to move the character to in X,Y form \n')
                try:
                    dest=dest.split(',')
                    if (int(dest[0]),int(dest[1])) in dj:
                        align.roster[int(choice)].move([int(dest[0]),int(dest[1])])
                        cont=True
                        cont2=True
                    else:
                       print('Bad move, try again') 
                except Exception as e:
                    print(traceback.format_exc())
                    print('Bad move, try again')
    if count!=0 and levelComplete==False and lordDied==False:
        gameplay(align)

def ai(align):
    #The goal here is to make an ai that, if it can attack a player character, it will attack the one that it does the most hp percentage damage to
    #If it cant, it will move towards the nearest player character
    count=0
    board=[]
    global levelComplete
    if levelComplete==True or lordDied==True:
        return
    print('\n')
    for i in range(0,len(align.roster)):
        if align.roster[i].moved==False and align.roster[i].status=='Alive':
            j=i
            count+=1
    if count==0:
        align.turn_end()
        return
    for q in curMap.spaces:
        if curMap.spaces[q][0]==False:
            pass
        elif curMap.spaces[q][0]==True:
            if curMap.spaces[q][1].alignment==player:
                print(f"Player unit {curMap.spaces[q][1].name} at {q}")
            elif curMap.spaces[q][1].alignment==enemy:
                print(f"Enemy unit {curMap.spaces[q][1].name} at {q}")
        else:
            print("Error")
    #We just choose the last item in the list cuz its easiest this way
    curMap.display('cur')
    choice=j
    self=align.roster[j]
    #dist, weapon
    atkRange=[]
    #So here we want to find the attack range of a character
    for i in self.inventory:
        if isinstance(i,weapon):
            if i.weapontype in self.weaponType:
                if i.weaponLevel<=self.weaponType[i.weapontype]:
                    for j in i.rng:
                        atkRange.append([j,i])
    #closest= dist, location
    closest=[9999,[0,0]]
    #maxDamage has character to attack, damage done, location,weapon being used, and distance
    maxDamage=[None,0,[0,0],None,0]
    #We check every map tile
    potential_spaces=djikstra(self)
    for i in potential_spaces:
        for j in curMap.spaces:
            #We find all the spaces with enemies on them
            if curMap.spaces[j][0]==True:
                destToPlayer=abs(j[0]-i[0])+abs(j[1]-i[1])
                for k in atkRange:
                    if k[0]==destToPlayer:
                        bonus=0
                        if k[1].weapontype in self.weaponType and k[1].dmgtype=='Magic' and curMap.spaces[j][1].alignment!=self.alignment:
                            if curMap.spaces[j][1].classType.name in k[1].super_effective:
                                bonus+=k[1].dmg*k[1].super_effective[curMap.spaces[j][1].classType.name]
                            if self.mag+k[1].dmg+bonus-curMap.spaces[j][0][1].res>=maxDamage[1]:
                                maxDamage=[curMap.spaces[j][1],self.mag+k[1].dmg+bonus-curMap.spaces[j][1].res,i,k[1],k[0]]
                        elif k[1].weapontype in self.weaponType and k[1].dmgtype=='Phys' and curMap.spaces[j][1].alignment!=self.alignment:
                            if curMap.spaces[j][1].classType.name in k[1].super_effective:
                                bonus+=k[1].dmg*k[1].super_effective[curMap.spaces[j][1].classType.name]
                            if self.atk+k[1].dmg+bonus-curMap.spaces[j][1].defense>=maxDamage[1]:
                                maxDamage=[curMap.spaces[j][1],self.atk+bonus+k[1].dmg-curMap.spaces[j][1].defense,i,k[1],k[0]]
                #We then calculate the distance from this point to every player, and if its lower than the previous closest to a player we make it the new destination
                if curMap.spaces[j][1].alignment!=self.alignment and destToPlayer<=closest[0]:
                    closest=[destToPlayer,i]
    print('\n')
    if maxDamage[0]==None:
        self.update_location(closest[1])
        print(f'{self.name} moved to {closest[1]}')
        self.moved=True
        time.sleep(1)
    else:
        self.update_location(maxDamage[2])
        print(f'{self.name} moved to {maxDamage[2]}')
        init_battle(self,maxDamage[0],maxDamage[4],maxDamage[3])
    if count!=0 and levelComplete==False and lordDied==False:
        ai(align)

def djikstra(self):
    viable_spaces=[]
    shortest_path={}
    previous_nodes={}
    for i in curMap.spaces:
        distFromAI=abs(i[0]-self.location[0])+abs(i[1]-self.location[1])
        if distFromAI<=self.mov:
            viable_spaces.append([i[0],i[1]])
            if distFromAI==1:
                moveCost=1
                try:
                    moveCost=curMap.objectList[i[0],i[1]].moveCost
                except Exception as e:
                    pass
                try:
                    if curMap.spaces[i[0],i[1]][1].alignment!=self.alignment:
                        moveCost=999
                except Exception as e:
                    pass
                shortest_path[i[0],i[1]]=moveCost
            else:
                shortest_path[i[0],i[1]]=999 
    shortest_path[self.location[0],self.location[1]]=0
    while viable_spaces:
        cur_min=None
        for node in viable_spaces:
            if cur_min== None:
                cur_min= node
            elif shortest_path[node[0],node[1]] < shortest_path[cur_min[0],cur_min[1]]:
                cur_min=node
        neighbors=[]
        for i in range(-1,2):
            for j in range(-1,2):
                if abs(i+j)==1:
                    try:
                        curMap.spaces[cur_min[0]+i,cur_min[1]+j]
                        neighbors.append([cur_min[0]+i,cur_min[1]]+j)
                    except Exception as e:
                        pass
        for neighbor in neighbors:
            tenative_value = shortest_path[cur_min[0],cur_min[1]]
            moveCost=1
            try:
                moveCost=curMap.objectList[neighbor[0],neighbor[1]].moveCost
            except Exception as e:
                pass
            try:
                if curMap.spaces[neighbor[0],neighbor[1]][1].alignment!=self.alignment:
                    moveCost=999
            except Exception as e:
                pass
            if moveCost!=999 and moveCost!=1:
                if self.classType.moveType=='Flying':
                    moveCost=1
                elif self.classType.moveType=='Horse':
                    moveCost*=2
                elif self.classType.moveType=='Mage' and curMap.objectList[neighbor[0],neighbor[1]].name=='Desert':
                    moveCost=1
                elif self.classType.moveType=='Pirate' and curMap.objectList[neighbor[0],neighbor[1]].name=='Water':
                    moveCost=2
            tenative_value+=moveCost
            try:
                if tenative_value < shortest_path[neighbor[0],neighbor[1]]:
                    shortest_path[neighbor[0],neighbor[1]]=tenative_value
                    try:
                        previous_nodes[neighbor[0],neighbor[1]].append(cur_min)
                    except Exception as e:
                        previous_nodes[neighbor[0],neighbor[1]]=[cur_min]
            except Exception as e:
                pass
            try:
                viable_spaces.remove([cur_min[0],cur_min[1]])
            except Exception as e:
                pass
    for i in list(shortest_path):
        if shortest_path[i]>self.mov:
            shortest_path.pop(i)
        elif curMap.spaces[i][0]==True:
            if curMap.spaces[i][1]!=self:
                shortest_path.pop(i)
    return shortest_path

def append_shop(base_class,*weapon):
    if base_class==base_weapon_dict:
        for i in range(0,len(base_class[weapon[0]])):
            print(f'{i} {base_class[weapon[0]][i].name}')
            i.info()
        inventoryX=input(f'Input the number of the {weapon} you wish to add.\n')
        count=input('Input how many of this item you want this shop to have\n')
        if int(count)>0:
            try:
                return [base_class[weapon[0]][int(inventoryX)],int(count)]
            except:
                print(traceback.format_exc())
    else:
        for i in range(0,len(base_class)):
            print(f'{i} {base_class[i].name}')
            i.info()
        inventoryX=input('Input the number of the item you wish to add.\n')
        count=input('Input how many of this item you want this shop to have\n')
        if int(count)>0:
            try:
                return [base_class[int(inventoryX)],int(count)]
            except:
                print(traceback.format_exc())
                   
def edit_shop(*shop):
    if shop:
        inventory=shop[0].contents
    else:
        inventory=[]
    contI=True
    while contI==True:
        if len(inventory)>0:
            print('Current inventory:')
            for i in range(0,len(inventory)):
                print(f'{i}: {inventory[i][0].name}')
        item_inventory=input(f'Press 1 to add a weapon to this shop, 2 to add armor, 3 to add misc, 4 to remove items, or x to finish.\n')
        if item_inventory.lower()=='x':
            return(inventory)
        elif item_inventory=='4' and len(inventory)>0:
            for i in range(0,len(inventory)):
                print(f'{i}: {inventory[i][0].name}')
            path=input(f'Input the item number that you would like to drop or X to cancel\n')
            if path.lower()=='x':
                pass
            else:
                try:
                    confirm=input(f'Input Y to confirm that you would like to remove {inventory[int(path)][0].name} or anything else to cancel\n')
                    if confirm.lower()=='y':
                        inventory.pop(int(path))
                        print('Item removed')
                    else:
                        print("Removal canceled")
                except:
                    print(traceback.format_exc())
                    print('Invalid input, returning to menu')
        elif item_inventory=='1':
            for i in base_weapon_dict:
                print(f'Category {i}: {base_weapon_dict[i].name}')
            weapon_inventory=input('Input the name of the weapon category that you want to add or Unique to add a unique weapon\n')
            if weapon_inventory.lower()=='unique':
                for i in range(0,len(unique_weapons)):
                    print(f'{i}: {unique_weapons[i].name}')
                unique_inventory=input('Input the number of the unique item you wish to add to this shop or X to cancel\n')
                if unique_inventory.lower()=='x':
                    pass
                else:
                    if unique_inventory.isdigit():
                        if int(unique_inventory) in range(0,len(unique_weapons)):
                            confirm=input(f'Input Y to confirm that you wish to add {unique_weapons[int(unique_inventory)]} to the shop or anything else to cancel\n')
                            if confirm.lower()=='y':
                                inventory.append([unique_weapons.pop(int(unique_inventory)),1])
                        else:
                            print('That number doesnt exist')
                    else:
                        print('Invalid input, returning to menu')
            else:
                try:
                    inventory.append(append_shop(base_weapon_dict,weapon_inventory.lower()))
                except:
                    print(traceback.format_exc())
        elif item_inventory=='2':
            inventory.append(append_shop(base_armor))
        elif item_inventory=='3':
            inventory.append(append_shop(base_misc))

def append_stock_inventory(base_class,*weapon):
    if base_class==base_weapon_dict:
        for i in range(0,len(base_class[weapon[0]])):
            print(f'{i} {base_class[weapon[0]][i].name}')
            i.info()
        inventoryX=input(f'Input the number of the {weapon[0]} you wish to add.\n')
        droppable=input('Input Y to make this item droppable when the unit holding it dies or anything else to have it not be droppable\n')
        try:
            x=base_class[weapon[0]][int(inventoryX)].name
        except:
            print(traceback.format_exc())
    else:
        for i in range(0,len(base_class)):
            print(f'{i}: {base_class[i].name}')
        inventoryX=input('Input the number of the item you wish to add\n')
        droppable=input('Input Y to make this item droppable when the unit holding it dies or anything else to have it not be droppable\n')
        try:
            consumable_inventory=int(consumable_inventory)
            x=base_class[int(inventoryX)].name
        except:
            print(traceback.format_exc())
    z=x.replace(' ','_')
    z=z.lower()
    if droppable.lower()=='y':
        return globals()[z](True)
    else:
        return globals()[z](False)

def stock_inventory(name,*inventory):
    contI=True
    if not inventory:
        inventory=[]
    else:
        inventory=inventory[0]
    while contI==True:                                
        if name.lower()=='chest':
            if len(inventory)==1:
                contI=False
        elif name.lower()=='inventory':
            if len(inventory)==5:
                print(f"The {name} is full")
                contI=False
        print('Current inventory:')
        for i in inventory:
            print(i.name)
        item_inventory=input(f'Press 1 to add a weapon to this {name}, 2 to add armor, 3 to add misc, or x to finish.\n')
        if item_inventory.lower()=='x':
            contI=False
        elif item_inventory=='1':
            weapon_inventory=input('Press 1 to view the swords, 2 to view the lances, 3 to view the axes, 4 to view the bows, 5 to view the tomes, 6 to view the fists, 7 to view the unique weapons, or anything else to cancel\n')
            if weapon_inventory=='1':
                inventory.append(append_stock_inventory(base_weapon_dict,'sword'))
            elif weapon_inventory=='2':
                inventory.append(append_stock_inventory(base_weapon_dict,'lance'))
            elif weapon_inventory=='3':
                inventory.append(append_stock_inventory(base_weapon_dict,'axe'))
            elif weapon_inventory=='4':
                inventory.append(append_stock_inventory(base_weapon_dict,'bow'))
            elif weapon_inventory=='5':
                inventory.append(append_stock_inventory(base_weapon_dict,'tome'))
            elif weapon_inventory=='6':
                inventory.append(append_stock_inventory(base_weapon_dict,'fist'))
            elif weapon_inventory=='7':
                for i in range(0,len(unique_weapons)):
                    print(f'{i}:{unique_weapons[i].name}')
                    unique_weapons[i].info()
                unique_inventory=input('Input the number of the item you wish to add or x to cancel.\n')
                if unique_inventory.lower()=='x':
                    pass
                else:
                    try:
                        inventory.append(unique_weapons.pop(int(unique_inventory)))
                        print('Item added')
                    except:
                       print(traceback.format_exc())
                       print('Invalid input, try again')
        elif item_inventory=='2':
            inventory.append(append_stock_inventory(base_armor))
        elif item_inventory=='3':
            inventory.append(append_stock_inventory(base_misc))
    return inventory

        
def map_ordering(name,map_num,*map_lev):
    delete=None
    for i in mapLevel.map_list:
        if i.mapNum==map_num:
            cont=False
            while cont==False:
                new=input(f'Map {i.name} has the same map number as {name}. Input X to delete {i.name}, Y to renumber {i.name}, or Z to renumber {name}\n')
                if new.lower()=='x':
                    confirm=input(f'You are about to delete {i.name}, input Y to confirm or anything else to cancel\n')
                    if confirm.lower()=='y':
                        mapLevel.map_list.pop(i)
                elif new.lower()=='y':
                    taken_nums=[]
                    if not map_lev:
                        taken_nums.append(tempMap(name,map_num))
                    for j in mapLevel.map_list:
                        if j!=i:
                            taken_nums.append(j.mapNum)
                    print(f'The currently taken map numbers are {taken_nums}')
                    new_num=input(f'Input the new number that you want {i.name} to be\n')
                    new_num=int(new_num)
                    if new_num>0:
                        if new_num not in taken_nums:
                            i.map_num=new_num
                            return map_num
                        else:
                            i.map_num=map_ordering(i.name,new_num,i)
                    else:
                        print('Invalid input, try again')
                elif new.lower()=='z':
                    taken_nums=[]
                    for j in mapLevel.map_list:
                        if j.name!=name:
                            taken_nums.append(j.mapNum)
                    print(f'The currently taken map numbers are {taken_nums}')
                    new_num=input('Input the new number that you want {name} to be\n')
                    new_num=int(new_num)
                    if new_num>0:
                        if new_num not in taken_nums:
                            return new_num
                        else:
                            if map_lev:
                                map_lev[0].mapNum=map_ordering(name,new_num,map_lev[0])
                            else:
                                return map_ordering(name,new_num)
                    else:
                        print('Invalid input, try again')

def save(kind=''):
    #weapon arts, unique weapons, skills, classes, units, player roster, maps, supports list
    if saveallowed:
        print("Saving data, please don't turn off the power")
        if not os.path.exists(f'save_data{kind}.txt'):
            open(f'save_data{kind}.txt', 'w')
        with open(f'save_data{kind}.txt', 'r+') as f:
            f.truncate(0)
            toc = time.perf_counter()
            playtime=int(toc-tic)
            playtime+=timemodifier
            f.write(f'time\n{playtime}\nmap\n{mapNum}\n')
            f.write('roster\n')
            for i in player.roster:
                f.write(i.name)
                f.write('\n')
            f.write(f'support\n{player.support_master}')
        f.close()
        with open(f'save_data_maps{kind}.txt', 'w') as f:
            for i in mapLevel.map_list:
                count=0
                for attr, value in i.__dict__.items():
                    if attr=='objectList':
                        for j in value:
                            if value[j].name=='Door':
                                f.write(f'{attr}XYZCYX{value[j].name}/{value[j].location}/{value[j].opened}\n')
                            elif value[j].name=='Treasure Chest':
                                f.write(f'{attr}XYZCYX{value[j].name}/{value[j].location}/{value[j].contents.name}\n')
                            elif value[j].name=='Shop':
                                f.write(f'{attr}XYZCYX{value[j].name}/{value[j].location}')
                                for k in value[j].contents:
                                    f.write(f'/{k[0].name}/{k[1]}')
                                f.write('\n')
                            else:
                                f.write(f'{attr}XYZCYX{value[j].name}/{value[j].location}\n')
                    elif attr=='spaces' or attr=='triggerList' or attr=='char_trigger_list' or attr=='player_roster' or attr=='enemy_roster':
                        pass
                    else:
                        try:
                            f.write(f'{attr}XYZCYX{value.name}\n')
                        except:
                            f.write(f'{attr}XYZCYX{str(value)}\n')
                f.write('BREAK\n')
        #Here we write the type of the character, then the name of the character, then we go through and write all their stuff
        #Weapon arts, inventory, skills, and skills_all are broken up into multiple parts that will need to be combined later
        with open(f'save_data_other{kind}.txt', 'w') as f:
            f.truncate(0)
            f.write('CHARACTERS\n')
            f.write('BREAKX\n')
            for i in character.character_list:
                count=0
                for attr, value in i.__dict__.items():
                    if count==1:
                        f.write(f'{i.nameClass}\n')
                    if attr=='inventory':
                        for j in value:
                            if j in unique_weapons:
                                f.write(f'{attr}XYZCYXUNIQUE{j.name}/{str(j.curUses)}/{str(j.droppable)}\n')
                            else:
                                f.write(f'{attr}XYZCYX{j.name}/{str(j.curUses)}/{str(j.droppable)}\n')
                    elif attr=='weapon_arts' or attr=='skills' or attr=='skills_all':
                        for j in value:
                            f.write(f'{attr}XYZCYX{j.name}\n')
                    else:
                        try:
                            if attr=='active_item':
                                f.write(f'{attr}XYZCYX{value.name}/{str(value.curUses)}/{str(value.droppable)}\n')
                            else:
                                f.write(f'{attr}XYZCYX{value.name}\n')
                        except Exception as e:
                            f.write(f'{attr}XYZCYX{str(value)}\n')
                    count+=1
                f.write('BREAK\n')
            f.write('BREAKX\n')
            f.write('WEAPONS\n')
            f.write('BREAKX\n')
            for i in unique_weapons:
                for attr, value in i.__dict__.items():
                    f.write(f'{attr}XYZCYX{str(value)}\n')
                f.write('BREAK\n')
            f.write('BREAKX\n')
            f.write('SKILLS\n')
            f.write('BREAKX\n')
            for i in skill.skill_list:
                for attr, value in i.__dict__.items():
                    try:
                        f.write(f'{attr}XYZCYX{value.name}\n')
                    except:
                        f.write(f'{attr}XYZCYX{str(value)}\n')
                f.write('BREAK\n')
            f.write('BREAKX\n')
            f.write('WEAPONARTS\n')
            f.write('BREAKX\n')
            for i in weapon_art.weapon_art_list:
                for attr, value in i.__dict__.items():
                    try:
                        f.write(f'{attr}XYZCYX{value.name}\n')
                    except:
                        f.write(f'{attr}XYZCYX{str(value)}\n')
                f.write('BREAK\n')
            f.write('BREAKX\n')
            f.write('CLASSES\n')
            f.write('BREAKX\n')
            for i in classType.class_list:
                for attr, value in i.__dict__.items():
                    if attr=='skill_list':
                        for j in value:
                            f.write(f'{attr}XYZCYX{j.name}\n')
                    else:
                        try:
                            f.write(f'{attr}XYZCYX{value.name}\n')
                        except:
                            f.write(f'{attr}XYZCYX{str(value)}\n')
                f.write('BREAK\n')
        f.close()
        print('Save complete!')

def load(kind=''):
    global curMap
    j = open(f"save_data{kind}.txt", "r")
    saveData=j.read().splitlines()
    j.close()
    mapChoice=False
    for i in saveData:
        if i=='map':
            path='map'
        elif i=='time':
            path='time'
        elif i=='roster':
            path='roster'
        elif i=='support':
            path='support'
        elif i=='battlesaves':
            path='battlesaves'
        elif i=='turncount':
            path='turncount'
        else:
            if path=='map':
                if mapChoice==False:
                    global mapNum
                    mapNum=int(i)
                    mapChoice=True
    weapon.weapon_list=[]
    consumable.consumable_list=[]
    player.roster=[]
    j = open(f"save_data_other{kind}.txt", "r")
    listX=j.read().split('BREAKX\n')
    j.close()
    char_dict={}
    weapon_art_dict={}
    class_dict={}
    weapon_dict={}
    skill_dict={}
    dicts_dict=[char_dict,weapon_art_dict,class_dict,weapon_dict,skill_dict]
    cur=None
    for i in listX:
        if i=='CHARACTERS\n':
            cur_dict=char_dict
        elif i=='WEAPONS\n':
            cur_dict=weapon_dict
        elif i=='WEAPONARTS\n':
            cur_dict=weapon_art_dict
        elif i=='CLASSES\n':
            cur_dict=class_dict
        elif i=='SKILLS\n':
            cur_dict=skill_dict
        else:
            i=i.split('BREAK\n')
            for k in i:
                k=k.split('\n')
                for j in k:
                    j=j.split('XYZCYX')
                    if j[0]=='name':
                        cur=j[1]
                        cur_dict[cur]=[]
                    else:
                        try:
                            if j[0]!='':
                                cur_dict[cur].append(j)
                        except Exception as e:
                            print(traceback.format_exc()) 
                            print(j)
    for i in weapon_dict:
        j=weapon(i,eval(weapon_dict[i][0][1]),eval(weapon_dict[i][2][1]),weapon_dict[i][3][1],
               eval(weapon_dict[i][4][1]),eval(weapon_dict[i][5][1]),eval(weapon_dict[i][6][1]),weapon_dict[i][7][1],
               eval(weapon_dict[i][8][1]),eval(weapon_dict[i][9][1]),eval(weapon_dict[i][10][1]),eval(weapon_dict[i][11][1]))
        unique_weapons.append(j)
        j.curUses=eval(weapon_dict[i][1][1])
    j=open(f"save_data_maps{kind}.txt", "r")
    listZ=j.read().split('BREAK\n')
    j.close()
    map_dict={}
    for i in listZ:
        i=i.split('\n')
        for j in i:
            j=j.split('XYZCYX')
            if j[0]=='name':
                cur=j[1]
                map_dict[cur]={}
            else:
                try:
                    if j[0]=='objectList':
                        if 'objectList' in map_dict[cur]:
                            map_dict[cur]['objectList'].append(j[1])
                        else:
                            map_dict[cur]['objectList']=[j[1]]
                    elif j[0]!='':
                        map_dict[cur][j[0]]=eval(j[1])
                except Exception as e:
                    print(j)
    mapLevel.map_list=[]
    mapObject.objectList=[]
    for k in map_dict:
        newMap=mapLevel(k,map_dict[k]['y_size'],map_dict[k]['x_size'],map_dict[k]['mapNum'],map_dict[k]['spawns'],None,None)
        if map_dict[k]['mapNum']==mapNum:
            curMap=newMap
        newMap.turn_count=map_dict[k]['turn_count']
        newMap.battle_saves=map_dict[k]['battle_saves']
        for j in map_dict[k]['objectList']:
            j=j.split('/')
            j[0]=j[0].lower()
            j[0]=j[0].replace(' ','_')
            if j[0]!='door' and j[0]!='shop' and j[0]!='treasure_chest':
                p=globals()[j[0]](newMap,eval(j[1]))
            elif j[0]=='door':
                p=globals()[j[0]](newMap,eval(j[1]))
                p.opened==eval(j[2])
                if p.opened:
                    p.moveCost=1
            elif j[0]=='treasure_chest':
                j[2]=j[2].lower()
                j[2]=j[2].replace(' ','_')
                try:
                    p=globals()[j[0]](newMap,eval(j[1]),globals()[j[2]](False))
                except:
                    for i in unique_weapons:
                        if i.name.lower.replace(' ',',')==j[2]:
                            itemX=i
                    p=globals()[j[0]](newMap,eval(j[1]),itemX)
            elif j[0]=='shop':
                contents=[]
                for k in range(2,len(j)):
                    if k%2==0:
                        try:
                            contents.append([eval(f'base_{j[k].lower().replace(" ","_")}'),eval(j[k+1])])
                        except:
                            for L in unique_weapons:
                                if L.name==j[k]:
                                    item=L
                            contents.append([item,1])
                p=globals()[j[0]](newMap,eval(j[1]),contents)
        #newMap.display('map')
    for i in weapon_art_dict:
        new=True
        for j in weapon_art.weapon_art_list:
            if j.name==i:
                new=False
                exist=j
        if new==False:
            exist.cost=eval(weapon_art_dict[i][0][1])
            exist.accuracy=eval(weapon_art_dict[i][1][1])
            exist.effect_stat=weapon_art_dict[i][2][1]
            exist.effect_change=eval(weapon_art_dict[i][3][1])
            exist.effect_operator=weapon_art_dict[i][4][1]
            exist.weapontype=weapon_art_dict[i][5][1]
            exist.super_effective=eval(weapon_art_dict[i][6][1])
            exist.range=eval(weapon_art_dict[i][7][1])
        else:
            weapon_art(i,eval(weapon_art_dict[i][0][1]),eval(weapon_art_dict[i][1][1]),weapon_art_dict[i][2][1],eval(weapon_art_dict[i][3][1]),
                       weapon_art_dict[i][4][1],weapon_art_dict[i][5][1],eval(weapon_art_dict[i][6][1]),eval(weapon_art_dict[i][7][1]))
    for i in skill_dict:
        new=True
        for j in skill.skill_list:
            if j.name==i:
                new=False
                exist=j
        if new==False:
            for k in skill_dict[i]:
                try:
                    setattr(exist,k[0],eval(k[1]))
                except:
                    setattr(exist,k[0],k[1])
        else:
            ###Skills (name,trigger_chance,trigger_stat,effect_stat,effect_change,effect_operator,effect_temp,effect_target,*relative_stat):
            if len(skill_dict[i])==7:
                skill(i,eval(skill_dict[i][0]),skill_dict[i][1],skill_dict[i][2],eval(skill_dict[i][3]),skill_dict[i][4],eval(skill_dict[i][6]),skill_dict[i][5])
            else:
                skill(i,eval(skill_dict[i][0]),skill_dict[i][1],skill_dict[i][2],eval(skill_dict[i][3]),skill_dict[i][4],eval(skill_dict[i][6]),skill_dict[i][5],skill_dict[i][7])
    for i in class_dict:
        new=True
        for j in classType.class_list:
            if j.name==i:
                new=False
                exist=j
        #print(class_dict[i])
        if new==False:
            exist.skill_list=[]
            for k in class_dict[i]:
                if k[0]!='skill_list':
                    try:
                        setattr(exist,k[0],eval(k[1]))
                    except:
                        setattr(exist,k[0],k[1])
                else:
                    for L in skill.skill_list:
                        if L.name==k[1]:
                            skillX=L
                    exist.skill_list.append(skillX)
        else:
            #(name,moveType,hp,hpG,atk,atkG,mag,magG,skillX,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,moveRange,weaponType,promotions,skill_list)
            skill_list=[]
            for k in class_dict[i]:
                if k[0]=='skill_list':
                    skill_list.append(k[1])
            p=classType(i,class_dict[i][0],eval(class_dict[i][1]),eval(class_dict[i][2]),eval(class_dict[i][3]),eval(class_dict[i][4]),
                        eval(class_dict[i][5]),eval(class_dict[i][6]),eval(class_dict[i][7]),eval(class_dict[i][8]),eval(class_dict[i][9]),
                        eval(class_dict[i][10]),eval(class_dict[i][11]),eval(class_dict[i][12]),eval(class_dict[i][13]),eval(class_dict[i][14]),
                        eval(class_dict[i][15]),eval(class_dict[i][16]),eval(class_dict[i][17]),eval(class_dict[i][18]),eval(class_dict[i][19]),skill_list)
    for i in char_dict:
        new=True
        for j in character.character_list:
            if j.name==i:
                new=False
                exist=j
        if new==False:
            equipped_count=0
            exist.skills=[]
            skills_placed=[]
            exist.skills_all=[]
            exist.inventory=[]
            exist.weapon_arts=[]
            for j in char_dict[i]:
                if len(j)>1:
                    if j[0]!='alignment' and j[0]!='active_item' and j[0]!='inventory' and j[0]!='skills' and j[0]!='skills_all' and j[0]!='classType' and j[0]!='weapon_arts':
                        try:
                            setattr(exist,j[0],eval(j[1]))
                        except Exception as e:
                            setattr(exist,j[0],j[1])
                    elif j[0]=='weapon_arts':
                        for k in weapon_art.weapon_art_list:
                            if k.name==j[1]:
                                exist.weapon_arts.append(k)
                    elif j[0]=='classType':
                        for k in classType.class_list:
                            if k.name==j[1]:
                                exist.classType=k
                    elif j[0]=='alignment':
                        z=j[1]
                        z=z.replace(' ','_')
                        z=z.lower()
                        setattr(exist,j[0],eval(z))
                    elif j[0]=='active_item' and j[1]!='None':
                        x=j[1]
                        x=x.split('/')
                        uses=x[1]
                        z=x[0]
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](eval(x[2]))
                        except:
                            for k in unique_weapons:
                                if k.name==x[0]:
                                    p=k
                        p.curUses=int(uses)
                        setattr(exist,j[0],p)
                        exist.add_item(p)
                    elif j[0]=='inventory':
                        x=j[1]
                        x=x.split('/')
                        uses=x[1]
                        z=x[0]
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](eval(x[2]))
                        except:
                            for k in unique_weapons:
                                if k.name==x[0]:
                                    p=k
                        p.curUses=int(uses)
                        if eval(z)==type(exist.active_item) and equipped_count==0 and p.curUses==exist.active_item.curUses:
                            equipped_count+=1
                        else:
                            exist.add_item(p)
                    elif j[0]=='active_item' and j[1]=='None':
                        setattr(exist,j[0],None)
                    elif j[0]=='skills':
                        for k in skill.skill_list:
                            if k.name==j[1]:
                                exist.add_skill(k)
                                skills_placed.append(j[1])
                    elif j[0]=='skills_all':
                        if j[1] not in skills_placed:
                            for k in skill.skill_list:
                                if k.name==j[1]:
                                  exist.skills_all.append(k)
                else:
                    unitType=j[0]
        elif new==True:
            ###player_char(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,{weaponType},joinMap,[inventory],level,{supports},[weapon_arts])
###enemy_char(name,classType,joinMap,[inventory],level,[spawn])
###recruitable(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,spawn,support_list,weapon_arts,recruit_convo)
###boss(name,curhp,hp,atk,mag,skill,luck,defense,res,spd,mov,classType,weaponType,joinMap,inventory,level,spawn):
            boss_needed_fields_reg=['name','hp','atk','mag','skill','luck','defense','res','spd','movModifier','classType','weaponType','joinMap','level','spawn']
            recruitable_needed_fields_reg=['name','curhp','hp','hpG','atk','atkG','mag','magG','skill','skillG','luck','luckG','defense','defG','res',
                                       'resG','spd','spdG','movModifier','classType','weaponType','joinMap','level','spawn','supports','recruit_convo']
            enemy_char_needed_fields_reg=['name','classType','joinMap','level','spawn']
            player_char_needed_fields_reg=['name','hp','hpG','atk','atkG','mag','magG','skill','skillG','luck','luckG','defense','defG','res',
                                       'resG','spd','spdG','movModifier','classType','weaponType','joinMap','level','supports']
            i_dict_reg={'supports':{}}
            i_dict_mult={'inventory':[],'weapon_arts':[]}
            i_dict_upd={}
            i_dict_upd_mult={'skills':[],'skills_all':[]}
            if char_dict[i][0][0]=='enemy_char':
                for k in char_dict[i]:
                    if k[0] in enemy_char_needed_fields_reg:
                        try:
                            i_dict_reg[k[0]]=eval(k[1])
                        except:
                            i_dict_reg[k[0]]=k[1]
                    elif k[0] in i_dict_mult:
                        i_dict_mult[k[0]].append(k[1])
                    elif k[0]!='alignment':
                        if k[0] in i_dict_upd_mult:
                            i_dict_upd_mult[k[0]].append(k[1])
                        elif k[0]!='alignment' and len(k)>1:
                            try:
                                i_dict_upd[k[0]]=eval(k[1])
                            except:
                                i_dict_upd[k[0]]=k[1]
                inventory=[]
                for L in i_dict_mult['inventory']:
                        x=L.split('/')
                        uses=x[1]
                        z=x[0]
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](eval(x[2]))
                        except:
                            for k in unique_weapons:
                                if k.name==x[0]:
                                    p=k
                        p.curUses=int(uses)
                        if eval(z)==type(exist.active_item) and equipped_count==0 and p.curUses==exist.active_item.curUses:
                            equipped_count+=1
                        else:
                            inventory.append(p)                        
                char=enemy_char(i,i_dict_reg['classType'],i_dict_reg['joinMap'],inventory,i_dict_reg['level'],i_dict_reg['spawn'])
                                
            ###player_char(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,{weaponType},joinMap,[inventory],level,{supports},[weapon_arts])                    
            elif char_dict[i][0][0]=='player_char':
                for k in char_dict[i]:
                    if k[0] in player_char_needed_fields_reg:
                        try:
                            i_dict_reg[k[0]]=eval(k[1])
                        except:
                            i_dict_reg[k[0]]=k[1]
                    elif k[0] in i_dict_mult:
                        i_dict_mult[k[0]].append(k[1])
                    else:
                        if k[0] in i_dict_upd_mult:
                            i_dict_upd_mult[k[0]].append(k[1])
                        elif k[0]!='alignment' and len(k)>1:
                            try:
                                i_dict_upd[k[0]]=eval(k[1])
                            except:
                                i_dict_upd[k[0]]=k[1]
                                pass
                inventory=[]
                for L in i_dict_mult['inventory']:
                        x=L.split('/')
                        uses=x[1]
                        z=x[0]
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](eval(x[2]))
                        except:
                            for k in unique_weapons:
                                if k.name==x[0]:
                                    p=k
                        p.curUses=int(uses)
                        if eval(z)==type(exist.active_item) and equipped_count==0 and p.curUses==exist.active_item.curUses:
                            equipped_count+=1
                        else:
                            inventory.append(p)                        
                char=player_char(i,i_dict_reg['hp'],i_dict_reg['hp'],i_dict_reg['hpG'],i_dict_reg['atk'],i_dict_reg['atkG'],
                                      i_dict_reg['mag'],i_dict_reg['magG'],i_dict_reg['skill'],i_dict_reg['skillG'],i_dict_reg['luck'],i_dict_reg['luckG'],
                                      i_dict_reg['defense'],i_dict_reg['defG'],i_dict_reg['res'],i_dict_reg['resG'],i_dict_reg['spd'],i_dict_reg['spdG'],
                                      i_dict_reg['movModifier'],i_dict_reg['classType'],i_dict_reg['weaponType'],i_dict_reg['joinMap'],inventory,
                                      i_dict_reg['level'],i_dict_reg['supports'],i_dict_mult['weapon_arts'])

###boss(name,curhp,hp,atk,mag,skill,luck,defense,res,spd,mov,classType,weaponType,joinMap,inventory,level,spawn):                            
            elif char_dict[i][0][0]=='boss':
                for k in char_dict[i]:
                    if k[0] in boss_needed_fields_reg:
                        try:
                            i_dict_reg[k[0]]=eval(k[1])
                        except:
                            i_dict_reg[k[0]]=k[1]                            
                    elif k[0] in i_dict_mult:
                        i_dict_mult[k[0]].append(k[1])
                    else:
                        if k[0] in i_dict_upd_mult:
                            i_dict_upd_mult[k[0]].append(k[1])
                        elif k[0]!='alignment' and len(k)>1:
                            try:
                                i_dict_upd[k[0]]=eval(k[1])
                            except:
                                i_dict_upd[k[0]]=k[1]
                inventory=[]
                for L in i_dict_mult['inventory']:
                        x=L.split('/')
                        uses=x[1]
                        z=x[0]
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](eval(x[2]))
                        except:
                            for k in unique_weapons:
                                if k.name==x[0]:
                                    p=k
                        p.curUses=int(uses)
                        if eval(z)==type(exist.active_item) and equipped_count==0 and p.curUses==exist.active_item.curUses:
                            equipped_count+=1
                        else:
                            inventory.append(p)                        
                char=boss(i,i_dict_reg['hp'],i_dict_reg['hp'],i_dict_reg['atk'],i_dict_reg['mag'],i_dict_reg['skill'],
                               i_dict_reg['luck'],i_dict_reg['defense'],i_dict_reg['res'],i_dict_reg['spd'],i_dict_reg['movModifier'],
                               i_dict_reg['classType'],i_dict_reg['weaponType'],i_dict_reg['joinMap'],inventory,i_dict_reg['level'],i_dict_reg['spawn'])
                
###recruitable(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,spawn,support_list,weapon_arts,recruit_convo)                            
            elif char_dict[i][0][0]=='recruitable':
                for k in char_dict[i]:
                    if k[0] in recruitable_needed_fields_reg:
                        try:
                            i_dict_reg[k[0]]=eval(k[1])
                        except:
                            i_dict_reg[k[0]]=k[1]
                    elif k[0] in i_dict_mult:
                        i_dict_mult[k[0]].append(k[1])
                    else:
                        if k[0] in i_dict_upd_mult:
                            i_dict_upd_mult[k[0]].append(k[1])
                        elif k[0]!='alignment' and len(k)>1:
                            try:
                                i_dict_upd[k[0]]=eval(k[1])
                            except:
                                i_dict_upd[k[0]]=k[1]
                inventory=[]
                for L in i_dict_mult['inventory']:
                        x=L.split('/')
                        uses=x[1]
                        z=x[0]
                        z=z.replace(' ','_')
                        z=z.lower()
                        try:
                            p=globals()[z](eval(x[2]))
                        except:
                            for k in unique_weapons:
                                if k.name==x[0]:
                                    p=k
                        p.curUses=int(uses)
                        if eval(z)==type(exist.active_item) and equipped_count==0 and p.curUses==exist.active_item.curUses:
                            equipped_count+=1
                        else:
                            inventory.append(p)                        
                char=recruitable(i,i_dict_reg['hp'],i_dict_reg['hp'],i_dict_reg['hpG'],i_dict_reg['atk'],i_dict_reg['atkG'],
                      i_dict_reg['mag'],i_dict_reg['magG'],i_dict_reg['skill'],i_dict_reg['skillG'],i_dict_reg['luck'],i_dict_reg['luckG'],
                      i_dict_reg['defense'],i_dict_reg['defG'],i_dict_reg['res'],i_dict_reg['resG'],i_dict_reg['spd'],i_dict_reg['spdG'],
                      i_dict_reg['movModifier'],i_dict_reg['classType'],i_dict_reg['weaponType'],i_dict_reg['joinMap'],inventory,
                      i_dict_reg['level'],i_dict_reg['spawn'],i_dict_reg['supports'],i_dict_mult['weapon_arts'],i_dict_reg['recruit_convo'])
            else:
                print('Illegal')
                
            for M in i_dict_upd:
                setattr(char,M,i_dict_upd[M])
            non_equipped_skills=[]
            for N in i_dict_upd_mult['skills_all']:
                if N not in i_dict_upd_mult['skills']:
                    non_equipped_skills.append(N)
            for O in i_dict_upd_mult['skills']:
                for P in skill.skill_list:
                    if P.name==O:
                        if P not in char.skills:
                            char.add_skill(P)
            for Q in non_equipped_skills:
                for R in skill.skill_list:
                    if R.name==Q:
                        if R not in char.skills_all:
                            char.skills_all.append(R)
    for i in character.character_list:
        for j in mapLevel.map_list:
            if i.joinMap==j.mapNum:
                if i.alignment==player and i not in j.player_roster:
                    j.player_roster.append(i)
                elif i.alignment==enemy and i not in j.enemy_roster:
                    j.enemy_roster.append(i)
            else:
                if i.alignment==player and i in j.player_roster:
                    j.player_roster.pop(i)
                elif i.alignment==enemy and i in j.enemy_roster:
                    j.enemy_roster.pop(i)
    j = open(f"save_data{kind}.txt", "r")
    saveData=j.read().splitlines()
    j.close()
    for i in saveData:
        if i=='map':
            path='map'
        elif i=='time':
            path='time'
        elif i=='roster':
            path='roster'
        elif i=='support':
            path='support'
        elif i=='battlesaves':
            path='battlesaves'
        elif i=='turncount':
            path='turncount'
        else:
            if path=='roster':
                for j in character.character_list:
                    if j.name==i:
                        player.roster.append(j)
            elif path=='support':
               player.support_master=eval(i)
            elif path=='time':
                global timemodifier
                timemodifier+=int(i)
    if curMap.battle_saves>0:
        for i in curMap.enemy_roster:
            if i.status=='Alive':
                enemy.roster.append(i)
        for i in enemy.roster:
            i.update_location(i.location)
        for i in player.roster:
            if i.deployed==True:
               i.update_location(i.location) 



def create_character():
    #Choosing alignment
    print('Welcome to the character creator')
    cont=False
    while cont==False:        
        align_input=input('Input P to make this a player unit, E to make this a generic enemy unit with autoleveled stats, B to make this a unique enemy unit with set stats, or R to make this a recruitable enemy unit\n')
        if align_input.lower()=='p':
            confirm=input('To confirm your character will be a player unit input Y, input anything else to cancel\n')
            if confirm.lower()=='y':
                align=player
                unit_type='Player'
                manual=True
                cont=True
        elif align_input.lower()=='e':
            confirm=input('To confirm your character will be a generic enemy input Y, input anything else to cancel\n')
            if confirm.lower()=='y':
                unit_type='Generic'
                align=enemy
                cont=True
        elif align_input.lower()=='b':
            confirm=input('To confirm your character will be a unique enemy input Y, input anything else to cancel\n')
            if confirm.lower()=='y':
                unit_type='Unique'
                align=enemy
                cont=True
        elif align_input.lower()=='r':
            confirm=input('To confirm your character will be a recruitable enemy input Y, input anything else to cancel\n')
            if confirm.lower()=='y':
                unit_type='Recruitable'
                align=enemy
                cont=True 
        else:
            print('Invalid input, try again')
    #naming character
    cont=False
    while cont==False:
        name=input('Input the name for your character\n')
        end_name=input(f'Your character will be named {name}, input Y to confirm or anything else to reenter the name\n')
        if end_name.lower()=='y':
            cont=True
    #set level
    cont=False
    while cont==False:
        level=input('Input what level you would like your character to be\n')
        try:
            level=int(level)
            if level>0 and level<=20:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #set join map
    cont=False
    while cont==False:
        existing_maps=[]
        for i in mapLevel.map_list:
            print(f'Map Number {i.mapNum}: {i.name}')
        join_map=input('Input the number of the map that you would like this character to join/be on, for example if you want them to join in the first map enter 1\n')
        try:
            join_map=int(join_map)
            for i in mapLevel.map_list:
                if join_map==i.mapNum:
                    mapX=i
                    cont=True
            if cont!=True:
                print('Invalid input, try again')
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #Choosing class
    cont=False
    while cont==False:
        print('Choose a class')
        for i in range(0,len(classType.class_list)):
            print(f'{i}: {classType.class_list[i].name}')
        class_choice=input('Input the number of the class you want this character to be\n')
        try:
            classType.class_list[int(class_choice)].info()
            end_class=input(f'Input Y to confirm you wish {name} to be a {classType.class_list[int(class_choice)].name}, and anything else to cancel\n')
            if end_class.lower()=='y':
                class_type=classType.class_list[int(class_choice)]
                class_name=classType.class_list[int(class_choice)].name
                cont=True
            else:
                pass
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #Setting weapon levels
    cont=False
    weapon_type={}
    if unit_type=='Generic':
        cont=True
    while cont==False:
        for i in class_type.weaponType:
            print(f'{i} : Level {class_type.weaponType[i]}')
        for i in weapon_type:
            print(f'{i} : Level {weapon_type[i]}')
        print(f"The current usable weapon types and weapon level for {name} are printed above\n")
        print('Here you can add new usable types or change the weapon level for existing ones\n')
        weapon_type_add=input('Input 1 to add/edit Sword, 2 for Lance, 3 for Axe, 4 for Bow, 5 for Tome, 6 for Fist, or x to exit\n')
        if weapon_type_add.lower()=='x':
            cont=True
        elif weapon_type_add=='1':
            weapon_level=input('Input the weapon level for Swords\n')
            try:
                weapon_type['Sword']=int(weapon_level)
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to choice')
        elif weapon_type_add=='2':
            weapon_level=input('Input the weapon level for Lances\n')
            try:
                weapon_type['Lance']=int(weapon_level)
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to choice')
        elif weapon_type_add=='3':
            weapon_level=input('Input the weapon level for Axes\n')
            try:
                weapon_type['Axe']=int(weapon_level)
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to choice')
        elif weapon_type_add=='4':
            weapon_level=input('Input the weapon level for Bows\n')
            try:
                weapon_type['Bow']=int(weapon_level)
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to choice')
        elif weapon_type_add=='5':
            weapon_level=input('Input the weapon level for Tomes\n')
            try:
                weapon_type['Tome']=int(weapon_level)
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to choice')
        elif weapon_type_add=='6':
            weapon_level=input('Input the weapon level for Fists\n')
            try:
                weapon_type['Fist']=int(weapon_level)
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to choice')
    #Creating the inventory
    cont=False
    print(f"Now you will stock {name}'s inventory")
    inventory=stock_inventory('inventory')
    #Setting active item
    cont=False
    while cont==False:
        possible_active_items={}
        for i in range(0,len(inventory)):
            if isinstance(inventory[i],weapon):
                if (inventory[i].weapontype in class_type.weaponType and inventory[i].weaponlevel>=class_type.weaponType[inventory[i].weapontype]) or (inventory[i].weapontype in weapon_type and inventory[i].weaponlevel>=weapon_type[inventory[i].weapontype]):
                    possible_active_items[i]=inventory[i]
        if len(possible_active_items)==0:
            cont=True
        else:
            for i in possible_active_items:
                print(f'{i} : {possible_active_items[i].name}')
            active_choice=input(f"Input the item that you want to be {name}'s active item\n")
            try:
                possible_active_items[int(active_choice)]
                inventory.insert(0,inventory.pop(int(active_choice)))
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, please try again')
    #Supports
    if unit_type=='Player' or unit_type=='Recruitable':
        supports={}
        cont=False
        print('In this step you will enter the names of all characters that you want this character to support one at a time. This is for all possible support partners, not just characters you have currently made')
        while cont==False:
            support_char=input(f'Enter the name of one character you would like {name} to support, or x to finish\n')
            if support_char.lower()=='x':
                end=input(f'Input X to confirm you are finished, Y to cancel, or Z to name a character X\n')
                if end.lower()=='x':
                    cont=True
                elif end.lower()=='y':
                    pass
                elif end.lower()=='z':
                    supports[support_char]=0
            else:
                confirm=input(f'Input Y to confirm that you want to add {support_char} as a support option for {name} or anything else to cancel\n')
                if confirm.lower()=='y':
                    supports[support_char]=0
        weapon_arts=[]
        cont=False
        print(f"In this step you will choose {name}'s starting weapon arts")
        while cont==False:
            if len(weapon_arts)==len(weapon_art.weapon_art_list):
                cont=True
            for i in range(0,len(weapon_art.weapon_art_list)):
                if weapon_art.weapon_art_list[i] not in weapon_arts:
                    print(f"{i}: {weapon_art.weapon_art_list[i].name}")
            weapon_art_add=input("Input the number of the weapon art you would like to add or X to finish\n")
            if weapon_art_add.lower()=='x':
                confirm=input("Input Y to confirm that you're done adding weapon arts and anything else to cancel")
                if confirm.lower()=='y':
                    cont=True
            else:
                try:
                    if weapon_art.weapon_art_list[int(weapon_art_add)] not in weapon_arts:
                        weapon_arts.append(weapon_art.weapon_art_list[int(weapon_art_add)])
                    else:
                        print('Invalid input, try again')
                except:
                    print(traceback.format_exc())
                    print('Invalid input, try again')
    #Enemy exclusive path
    if align==enemy:
        #setting spawn
        cont=False
        while cont==False:
            print('Input the coordinates where you would like this unit to spawn on their map in x,y integer form, with 0,0 being the top left and 1,1 being down and to the right of that')
            print('Any x,y pair will work as long as its on the map, not just 0,0 or 1,1')
            spawn=input('Enter the coordinates now\n')
            try:
                spawn=spawn.split(',')
                spawn[0]=int(spawn[0])
                spawn[1]=int(spawn[1])
                contCont=True
                if [spawn[0],spawn[1]] not in mapX.spawns and (spawn[0],spawn[1]) in mapX.spaces:
                    if (spawn[0],spawn[1]) in mapX.objectList:
                        if mapX.objectList[spawn[0],spawn[1]].name=='Door':
                            contCont=False
                        elif mapX.objectList[spawn[0],spawn[1]].name=='Void' and class_choice.moveType!='Flying':
                            contCont=False
                        elif mapX.objectList[spawn[0],spawn[1]].name=='Void' and (class_choice.moveType!='Flying' and class_choice.moveType!='Pirate'):
                            contCont=False
                    if contCont==True:
                        cont=True
                elif [spawn[0],spawn[1]] in mapX.spawns:
                    print('A player unit spawns there, invalid input')
                else:
                    print('Invalid spawn, try again')
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
    #Creating the recruitment convo
    if unit_type=='Recruitable':
        cont=False
        while cont==False:
            recruit_convo=input('Write out the dialogue you would like to play when this character is recruited\n')
            confirm=input(f'Input Y to confirm that the following is what you want to play or any other input to rewrite it\n{recruit_convo}\n')
            if confirm.lower()=='y':
                cont=True
    #setting bases and growths
    if unit_type=='Player' or unit_type=='Unique' or unit_type=='Recruitable':
        print('Here you will set the bases and growths of your character.\nGrowths should be input in decimal notation, and represent the probability of acquiring a stat on level up.\nFor example a .65 HP growth would make it so that a character has a 65% chance of gaining +1 in HP on level up.')
        cont=False
        while cont==False:
            try:
                hp=input('HP\n')
                hp=int(hp)
                if unit_type!='Unique':
                    hpG=input('HP Growth (decimal notation)\n')
                    hpG=float(hpG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                atk=input('Attack\n')
                atk=int(atk)
                if unit_type!='Unique':
                    atkG=input('Attack Growth (decimal notation)\n')
                    atkG=float(atkG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                mag=input('Magic\n')
                mag=int(atk)
                if unit_type!='Unique':
                    magG=input('Magic Growth (decimal notation)\n')
                    magG=float(magG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                skill=input('Skill\n')
                skill=int(skill)
                if unit_type!='Unique':
                    skillG=input('Skill Growth (decimal notation\n')
                    skillG=float(skillG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                luck=input('Luck\n')
                luck=int(luck)
                if unit_type!='Unique':
                    luckG=input('Luck Growth (decimal notation)\n')
                    luckG=float(luckG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                defense=input('Defense\n')
                defense=int(defense)
                if unit_type!='Unique':
                    defG=input('Defense Growth (decimal notation)\n')
                    defG=float(defG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                res=input('Resistance\n')
                res=int(res)
                if unit_type!='Unique':
                    resG=input('Resistance Growth (decimal notation)\n')
                    resG=float(resG)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        cont=False
        while cont==False:
            try:
                spd=input('Speed\n')
                spd=int(spd)
                if unit_type!='Unique':
                    spdG=input('Speed Growth\n')
                    spdG=float(spdG)
                mov=input('Move modifier (how many more spaces this character can move than normal units of their class)\n')
                mov=int(mov)
                cont=True
            except:
                print(traceback.format_exc())
                print('Invalid input, try again')
        #Creating the character
#player_char(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,support_list,weapon_arts)
#enemy_char(name,classType,joinMap,[inventory],level,[spawn])
#recruitable(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,spawn,support_list,weapon_arts,recruit_convo)
#boss(name,curhp,hp,atk,mag,skill,luck,defense,res,spd,mov,classType,weaponType,joinMap,inventory,level,spawn)
        if unit_type=='Player':
            player_char(name,hp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,class_name,weapon_type,join_map,inventory,level,supports,weapon_arts)
        elif unit_type=='Unique':
            boss(name,hp,hp,atk,mag,skill,luck,defense,res,spd,mov,class_name,weapon_type,join_map,inventory,level,spawn)
        elif unit_type=='Recruitable':
            recruitable(name,hp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,class_name,weapon_type,join_map,inventory,level,spawn,supports,weapon_arts,recruit_convo)
    elif unit_type=='Generic':
        enemy_char(name,class_name,join_map,inventory,level,spawn)
    print('Character created!')


def create_map():
    print('Welcome to the map creator')
    #naming the map
    cont=False
    while cont==False:
        name=input('Input the name for this map\n')
        confirm=input(f'Input Y to confirm {name} as this maps name, anything else to rename it\n')
        for i in mapLevel.map_list:
            if i.name==name:
                confirm='There already exists a level with that name'
        if confirm.lower()=='y':
            cont=True
        elif confirm=='There already exists a level with that name':
            print(confirm)
    #setting the map number
    cont=False
    while cont==False:
        existing_list=[]
        for i in mapLevel.map_list:
            existing_list.append(i.mapNum)
        existing_list.sort()        
        print(f'The existing maps are {existing_list}')
        map_num=input('Input the number map that you want this to be. For example, if you want this to be the 23rd map you play in the story you would enter 23 here\n')
        try:
            base_name=name
            delete=None           
            map_num=int(map_num)
            map_num=map_ordering(name,int(map_num))
            for i in mapLevel.map_list:
                if isinstance(i,tempMap):
                    mapLevel.map_list.pop(i)
            cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #setting the map size
    cont=False
    while cont==False:
        x_size=input('Input how many tiles wide you want this map to be\n')
        y_size=input('Input how many tiles tall you want this map to be\n')
        try:
            x_size=int(x_size)
            y_size=int(y_size)
            if x_size>0 and y_size>0:
                cont=True
            else:
                print('Map dimensions must be above 0 in each direction')
        except:
            print(traceback.format_exc())
            print('Invalid input, please try again')
    #setting deployment number
    cont=False
    while cont==False:
        spawn_count=input('Input how many player units you want allowed for this map\n')
        try:
            spawn_count=int(spawn_count)
            confirm=input(f'Are you sure you want {spawn_count} units? Input Y to confirm and anything else to cancel\n')
            if confirm.lower()=='y' and spawn_count<x_size*y_size and spawn_count>0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #setting spawns
    cont=False
    spawns=[]
    while len(spawns)<spawn_count:
        print('Input the coordinates where you would like a unit to spawn on their map in x,y integer form, with 0,0 being the top left and 1,1 being down and to the right of that')
        print('Any x,y pair will work as long as its on the map, not just 0,0 or 1,1')
        if len(spawns)>0:
            print(f'The current spawn points are {spawns}')
        spawn=input('Enter the coordinates now\n')
        try:
            spawn=spawn.split(',')
            spawn[0]=int(spawn[0])
            spawn[1]=int(spawn[1])
            if spawn[0]<x_size and spawn[1]<y_size and spawn[0]>=0 and spawn[1]>=0:
                confirm=input(f'Input Y to confirm adding a spawn at {spawn} or anything else to cancel\n')
                if confirm.lower()=='y' and spawn not in spawns:
                    spawns.append(spawn)
            else:
                print(f'Invalid input, your map dimensions are {x_size} wide by {y_size} tall')
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #creating the map
    mapCreated=mapLevel(name,y_size,x_size,map_num,spawns,[],[])
    #Adding objects to the map
    add_map_objects()
    print('Map Created!')

                                
def create_unique_weapon():
    #(name,maxUses,dmg,dmgtype,rng,crit,hit,weapontype,droppable,cost,rank,super_effective):
    print('Welcome to the weapon creator')
    #Name
    cont=True
    while cont==True:
        name=input(f'Enter the name for this weapon\n')
        confirm=input(f'Input Y to confirm that you wish to name this weapon {name} or anything else to cancel\n')
        if confirm.lower()=='y':
            cont=False
    #Weapon type
    cont=True
    while cont==True:
        weptype=input(f'Input 1 to make this a sword, 2 a lance, 3 an axe, 4 a bow, 5 a tome, or 6 a gauntlet\n')
        if weptype=='1':
            weapontype='Sword'
            cont=False
        elif weptype=='2':
            weapontype='Lance'
            cont=False
        elif weptype=='3':
            weapontype='Axe'
            cont=False
        elif weptype=='4':
            weapontype='Bow'
            cont=False
        elif weptype=='5':
            weapontype='Tome'
            cont=False
        elif weptype=='6':
            weapontype='Fist'
            cont=False
        else:
            print('Invalid input, try again')
    #Damage type
    cont=True
    while cont==True:
        damagetype=input(f'Input P to make this a physical weapon or M to make it a magical weapon\n')
        if damagetype.lower()=='p':
            dmgtype='Phys'
            cont=False
        elif damagetype.lower()=='m':
            dmgtype='Magic'
            cont=False
        else:
            print('Invalid input, try again')
    #range
    cont=False
    while cont==False:
        rng=[]
        print('Input the ranges that you want this weapon to be able to attack from seperated by commas.')
        print('For example if you wanted this weapon to be able to attack enemies 1,2, or 3 tiles away you would enter 1,2,3')
        ranges=input(f'Input the range now\n')
        try:
            ranges=ranges.split(',')
            er=False
            for i in range(0,len(ranges)):
                ranges[i]=int(ranges[i])
                if i<=0:
                    er=True
            if er!=True:
                rng=ranges
                cont=True
            else:
                print('Invalid input, ranges must be 1 or above')
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #stats
    #(maxUses,dmg,crit,hit,droppable,cost,rank,super_effective):
    print('In this step you will set the stats for this weapon. Each stat must be a positive integer') 
    cont=False
    while cont==False:
        try:
            maxUses=input('Weapon Uses\n')
            maxUses=int(maxUses)
            if maxUses>0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=False
    while cont==False:
        try:
            dmg=input('Damage\n')
            dmg=int(dmg)
            if dmg>=0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=False
    while cont==False:
        try:
            hit=input('Hit Rate (between 0 and 200, higher numbers are more accurate)\n')
            hit=int(hit)
            if hit>=0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=False
    while cont==False:
        try:
            crit=input('Crit Rate\n')
            crit=int(crit)
            if crit>=0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=False
    while cont==False:
        try:
            cost=input('Shop Cost\n')
            cost=int(cost)
            if cost>=0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=False
    while cont==False:
        try:
            rank=input('Weapon Rank (what a characters weapon level has to be to use this)\n')
            rank=int(rank)
            if cost>=0:
                cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    #Droppable
    cont=False
    while cont==False:
        dropY=input('Input y to make this weapon drop on death or x to no\n')
        if dropY.lower()=='y':
            droppable=True
            cont=True
        elif dropY.lower()=='x':
            droppable=False
            cont=True
        else:
            print('Invalid input, try again')
    #super_effective
    cont=False
    super_effective={}
    print(f'In this step you will choose the classes you want this weapon to be super effective against\n')
    print(f'If the class you want it to be super effective against hasnt been made yet thats fine, just enter the name now and create that class later')
    print(f'As long as a class with the input name is made at some point it will work')
    print(f'You can add multiple classes to be super effective against as long as its done one at a time')
    print(f'If you dont want this weapon to be super effective against any unit types just immediately input X to finish')
    while cont==False:
        print(f'Current classes this weapon is super effective against: {super_effective}')
        for i in range(0,len(classType.class_list)):
            print(f'{i}: {classType.class_list[i].name}')
        super_effective_route=input(f'Input the number/name of the class or X to finish\n')
        if super_effective_route.lower()=='x':
            cont=True
        elif super_effective_route.isdigit():
            if int(super_effective_route)>=0 and int(super_effective_route)<len(classType.class_list):
                if classType.class_list[int(super_effective_route)].name not in super_effective:
                    multiplier=input(f'Input the integer damage multiplier for this weapon against {classType.class_list[int(super_effective_route)].name}s or x to cancel\n')
                    if multiplier.isdigit():
                        super_effective[classType.class_list[int(super_effective_route)].name]=int(multiplier)
                    elif multiplier.lower()=='x':
                        pass
                    else:
                        print('The multiplier must be an integer')
                else:
                    print('This weapon is already super effective against that enemy type')
            else:
                print('Class type names cant be numbers!')
        else:
            confirm=(f'Input y to confirm that you want this weapon to be super effective against {super_effective_route}s or anything else to cancel\n')
            if confirm.lower()=='y':
                if super_effective_route not in super_effective:
                    multiplier=input(f'Input the integer damage multiplier for this weapon against {super_effective_route}s or x to cancel\n')
                    if multiplier.isdigit():
                        super_effective[super_effective_route]=int(multiplier)
                    elif multiplier.lower()=='x':
                        pass
                    else:
                        print('The multiplier must be an integer')
                else:
                    print('This weapon is already super effective against that enemy type')
    global unique_weapons
    unique_weapons.append(weapon(name,maxUses,dmg,dmgtype,rng,crit,hit,weapontype,droppable,cost,rank,super_effective))
    print(f'{name} has been created. You can put it in an inventory, chest, or shop via the character/map editors')
                        
def create_skill():
    #Skills (name,trigger_chance,trigger_stat,effect_stat,effect_change,effect_operator,effect_temp,effect_target,*relative_stat):
    print('Welcome to the skill creator')
    #Name
    cont=False
    while cont==False:
        name=input('Enter the name for this skill\n')
        confirm=input(f'Input y to confirm that you want this skill to be called {name} or anything else to cancel\n')
        if confirm.lower()=='y':
            cont=True
    #Trigger chance
    #Trigger stat
    #effect stat
    #Effect change
    #Effect operator
    #effect temp
    #effect target
    #relative stat

def create_weapon_art():
    #Weapon Arts (name,cost,accuracy,effect_stat,effect_change,effect_operator,weapontype,super_effective,rng):
    print('Welcome to the weapon art creator')
    #Name
    cont=False
    while cont==False:
        name=input('Enter the name for this weapon art\n')
        confirm=input(f'Input y to confirm that you want this weapon art to be called {name} or anything else to cancel\n')
        if confirm.lower()=='y':
            cont=True
    #cost,accuracy,effect_change
    #effect_stat
    #effect_operator
    #super effective
    #weapontype
    #range

def create_class():
    #Classes (advanced classes on top) (name,moveType,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,moveRange,weaponType,promotions,skill_list)
    print('Welcome to the class creator')
    #Name
    cont=False
    while cont==False:
        name=input('Enter the name for this class\n')
        confirm=input(f'Input y to confirm that you want this class to be called {name} or anything else to cancel\n')
        if confirm.lower()=='y':
            cont=True
    #move type
    cont=False
    print('Here you will set the move type for this class. Move range and move type are completely seperate, all move type effects is the movement cost for certain tile types')
    while cont==False:
        print(f'0: Foot, the default move type. No strengths or weaknesses')
        print(f'1: Flying, nearly every tile type only costs one move')
        print(f'2: Horse, generally poor at moving through many tile types')
        print(f'3: Mage, foot but good at moving through deserts')
        print(f'4: Pirate, foot but good at moving through water')
        route=input('Enter the number of the movement type you want\n')
        if route=='0':
            moveType='Foot'
            cont=True
        elif route=='1':
            moveType='Flying'
            cont=True
        elif route=='2':
            moveType='Horse'
            cont=True
        elif route=='3':
            moveType='Mage'
            cont=True
        elif route=='4':
            moveType='Pirate'
            cont=True
        else:
            print('Invalid input, try again')
    #Bases and growths
    bases={}
    growths={}
    for i in character.stats:
        pass
    for i in character.growths:
        pass
    #Weapon type
    #promotions
    #skill_list
    pass

def write_support():
    print('Welcome to the support writer')
    cont=False
    while cont==False:
        character1=input('Enter the name of the first character for this support\n')
        character2=input('Enter the name of the second character for this support\n')
        confirm=input(f'Input Y to confirm that you want this support to be between {character1} and {character2} or anything else to cancel\n')
        if confirm.lower()=='y':
            cont=True
    cont=False
    while cont==False:
        num_levels=input('Enter how many support conversations you want there to be for this support chain\n')
        if num_levels.isdigit():
            confirm=input(f'Input y to confirm that you want {num_levels} support conversations or anything else to cancel\n')
            if confirm.lower()=='y':
                num_levels=int(num_levels)
                cont=True
    support_convos=[0]
    j=1
    while num_levels>0:
        convo=input(f'Write the conversation you would like to play at level {j}. Use \\n to insert a newline.\n')
        confirm=input(f'Input y to confirm that you want that to be support level {j}\n')
        if confirm.lower()=='y':
            j+=1
            support_convos.appens(convo)
            num_levels-=1
    player.support_master[character1,character2]=support_convos
    print('Support created!')
            

def edit_map():
    cont=True
    while cont==True:
        for i in range(0,len(mapLevel.map_list)):
            print(f'{i}: {mapLevel.map_list[i].name}')
        map_choice=input(f'Input the number for the map you would like to edit\n')
        try:            
            mapX=mapLevel.map_list[int(map_choice)]
            cont=False
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=True
    while cont==True:
        path=input('Input 1 to edit this maps objects, 2 to edit the map number, 3 to edit the player spawns, 4 to edit the size, 5 to edit the rosters, or x to finish\n')
        if path.lower()=='x':
            cont=False
        elif path=='1':
            #edit objects
            mapX.display('base')
            #add,delete, edit
            object_path=input('Input 1 to add objects, 2 to delete objects, 3 to edit the contents of chests/shops, or X to exit\n')
            if object_path=='1':
                mapX.add_map_objects()
            elif object_path=='2':
                mapX.delete_map_objects()
            elif object_path=='3':
                #edit shop/chest contents
                count=0
                for i in mapX.objectList:
                    if isinstance(mapX.objectList[i],treasure_chest) or isinstance(mapX.objectList[i],shop):
                        print(f'{i}: {mapX.objectList[i].name}')
                        count+=1
                if count>0:
                    route=input(f'Input the coordinates of the shop or chest whose contents you wish to edit in x,y form or x to cancel\n')
                    if route.lower()=='x':
                        pass
                    else:
                        try:
                            route=route.split(',')
                            route[0]=int(route[0])
                            route[1]=int(route[1])
                            mapX.objectList[route[0],route[1]].edit_contents()
                        except:
                            print(traceback.format_exc())
                            print('Invalid input, try again')
                else:
                    print('There are no shops or chests on this map, returning to menu')
        elif path=='2':
            #edit mapnum
            new_num=input(f'Enter the new number that you want this map to be, its current number is {mapX.mapNum}\n')
            if isdigit(new_num):
                map_ordering(mapX.name,int(new_num),mapX)
            else:
                print('Invalid input, returning to menu')
        elif path=='3':
            #edit spawns
            path=input('Enter 1 to add spawns, 2 to remove spawns, or anything else to cancel\n')
            pass
        elif path=='4':
            #edit size
            print(f'This map is currently {mapX.x_size} wide and {mapX.y_size} tall')
            new_size=input(f'Input the new map size in X,Y form or input X to cancel\n')
            if new_size.lower()=='x':
                pass
            else:
                try:
                    new_size=new_size.split(',')
                    new_size[0]=int(new_size[0])
                    new_size[1]=int(new_size[1])
                    missing_enemy=[]
                    missing_spawn=[]
                    missing_object=[]
                    for i in mapX.spaces:
                        if i[0]>new_size[0]-1 or i[1]>new_size[1]-1:
                            del mapX.spaces[i]
                    if new_size[0]>mapX.x_size:
                        for i in range(mapX.x_size,new_size[0]):
                            for j in range(0,mapX.y_size):
                                mapX.spaces[i,j]=[False]
                    mapX.x_size=new_size[0]
                    if new_size[1]>mapX.y_size:
                        for j in range(mapX.y_size,new_size[1]):
                            for i in range(0,mapX.x_size):
                                mapX.spaces[i,j]=[False]
                    mapX.y_size=new_size[1]
                    for j in mapX.enemy_roster:
                        if (j.spawn[0],j.spawn[1]) not in mapX.spaces:
                            missing_enemy.append(mapX.enemy_roster.pop(j))
                    for k in mapX.spawns:
                        if (k[0],k[1]) not in mapX.spaces:
                            missing_spawn.append(mapX.spaces.pop(k))
                    for l in mapX.objectList:
                        if l not in mapX.spaces:
                            missing_object.append(mapX.objectList[l])
                            del mapX.objectList[l]
                    contFix=True
                    while contFix==True:
                        if len(missing_enemy)==0 and len(missing_object)==0:
                            contFix=False
                        mapX.display('base')
                        print(f'There are {len(missing_enemy)} enemies that need to have their spawn changed, {len(missing_object)} objects that need to be moved, and {len(missing_spawn)} player spawns have been deleted')
                        while len(missing_enemy)>0:
                            #update spawm
                            length=len(missing_enemy)
                            for aqw in range(0,length):
                                contZ=False
                                mapX.display('base')
                                while contZ==False:
                                    print(f'Input the coordinates where you would like {missing_enemy[0].name} to spawn on their map in x,y integer form, with 0,0 being the top left and 1,1 being down and to the right of that')
                                    print('Any x,y pair will work as long as its on the map, not just 0,0 or 1,1')
                                    spawn=input('Enter the coordinates now, or input X to delete this unit\n')
                                    if spawn.lower()=='x':
                                        missing_enemy.pop(0)
                                        contZ=True
                                    try:
                                        spawn=spawn.split(',')
                                        spawn[0]=int(spawn[0])
                                        spawn[1]=int(spawn[1])
                                        contCont=True
                                        if [spawn[0],spawn[1]] not in mapX.spawns and (spawn[0],spawn[1]) in mapX.spaces:
                                            if (spawn[0],spawn[1]) in mapX.objectList:
                                                if mapX.objectList[spawn[0],spawn[1]].name=='Door':
                                                    contCont=False
                                                elif mapX.objectList[spawn[0],spawn[1]].name=='Void' and class_choice.moveType!='Flying':
                                                    contCont=False
                                                elif mapX.objectList[spawn[0],spawn[1]].name=='Void' and (class_choice.moveType!='Flying' and class_choice.moveType!='Pirate'):
                                                    contCont=False
                                            if contCont==True:
                                                missing_enemy[0].spawn=[spawn[0],spawn[1]]
                                                missing_enemy.pop(0)
                                                contZ=True
                                        elif [spawn[0],spawn[1]] in mapX.spawns:
                                            print('A player unit spawns there, invalid input')
                                        else:
                                            print('Invalid spawn, try again')
                                    except:
                                        print(traceback.format_exc())
                                        print('Invalid input, try again')
                        while len(missing_object)>0:
                            length=len(missing_object)
                            for acq in range(0,length):
                                contZ=False
                                mapX.display('base')
                                while contZ==False:
                                    print(f'Input the coordinates where you would like {missing_object[0].name} to be in x,y integer form, with 0,0 being the top left and 1,1 being down and to the right of that')
                                    print('Any x,y pair will work as long as its on the map, not just 0,0 or 1,1')
                                    spawn=input('Enter the coordinates now, or input X to delete this object\n')
                                    if spawn.lower()=='x':
                                        missing_object.pop(0)
                                        contZ=True
                                    try:
                                        spawn=spawn.split(',')
                                        spawn[0]=int(spawn[0])
                                        spawn[1]=int(spawn[1])
                                        contCont=True
                                        if (spawn[0],spawn[1]) in mapX.spaces:
                                            if (spawn[0],spawn[1]) in mapX.objectList:
                                                print('Theres already an object there, find somewhere else to put this')
                                                contCont=False
                                            if [spawn[0],spawn[1]] in mapX.spawns:
                                                if missing_object[0].name=='Void' or missing_object[0].name=='Water' or missing_object[0].name=='Door':
                                                    print('Theres already a player unit spawn there, find somewhere else to put this')
                                                    contCont=False
                                            for i in mapX.enemy_roster:
                                                if i.spawn==[spawn[0],spawn[1]] and (missing_object[0].name=='Void' or missing_object[0].name=='Water' or missing_object[0].name=='Door'):
                                                    print('Theres already an enemy unit spawn there, find somewhere else to put this')
                                                    contCont=False
                                            if contCont==True:
                                                missing_object[0].location=[spawn[0],spawn[1]]                                                
                                                mapX.objectList[spawn[0],spawn[1]]=missing_enemy.pop(0)
                                                contZ=True
                                        else:
                                            print('Invalid location, try again')
                                    except:
                                        print(traceback.format_exc())
                                        print('Invalid input, try again')
                    print('Map resized')
                except:
                    print(traceback.format_exc())
        elif path=='5':
            #edit rosters
            pass
        else:
            print('Invalid input, returning to menu')

def edit_char():
    cont=False
    while cont==False:
        for i in range(0,len(character.character_list)):
            print(f'{i}: {character.character_list[i].name}')
        char_choice=input(f'Input the number for the character you would like to edit\n')
        try:            
            char=character.character_list[int(char_choice)]
            cont=True
        except:
            print(traceback.format_exc())
            print('Invalid input, try again')
    cont=True
    while cont==True:
        path=input('Input 1 to edit this characters stats and growths, 2 to edit their join map, 3 to edit their level/experience, 4 to edit their class, 5 to edit their skills, 6 to edit their inventory, or x to finish\n')
        if path=='1':
            #stats and growths
            cont=True
            while cont==True:
                print('The stats you can change are as follows:')
                for i in stats:
                    print(i)
                print('The G stats are growths, and movModifer is how many extra spaces a character can move compared to a default member of their class')
                print('Growths are decimals, and represent the change that a character gains that stat when leveling up')
                print('For example a .6 hpG would mean that a character has a 60% chance of gaining 1 hp on level up and a 40% chance of gaining 0')
                stat_change=input(f"Input the abreviation for the stat you'd like to change or x to finish\n")
                if stat_change in character.stats or stat_change in character.growths:
                    print(f"The current value for {char.name}'s {stat_change} is {getattr(char,eval(stat_change))}")
                    new_value=input(f"Input the new value you want {stat_change} to be\n")
                    try:
                        if stat_change in character.stats:
                            if stat_change!='hp' and stat_change!='movModifier':
                                if int(new_value)>=0:
                                    confirm=input(f"Input Y to confirm that you want to change {stat_change} to {new_value} or anything else to cancel\n")
                                    if confirm.lower()=='y':
                                        setattr(char,stat_change,int(new_value))
                                else:
                                    print('Stats must be positive integers')
                            elif stat_change=='hp':
                                if int(new_value)>0:
                                    confirm=input(f"Input Y to confirm that you want to change {stat_change} to {new_value} or anything else to cancel\n")
                                    if confirm.lower()=='y':
                                        setattr(char,stat_change,int(new_value))
                                else:
                                    print('Stats must be positive integers')
                            elif stat_change=='movModifier':
                                if int(new_value)>=-3:
                                    confirm=input(f"Input Y to confirm that you want to change {stat_change} to {new_value} or anything else to cancel\n")
                                    if confirm.lower()=='y':
                                        curMod=getattr(char,stat_change)
                                        setattr(char,stat_change,int(new_value))
                                        char.mov+=new_value-curMod
                                else:
                                    print('The minimum value for the move modifier is -3')                                    
                        elif stat_change in character.growths:
                            if float(new_value)>=0:
                                confirm=input(f"Input Y to confirm that you want to change {stat_change} to {new_value} or anything else to cancel\n")
                                if confirm.lower()=='y':
                                    setattr(char,stat_change,float(new_value))
                            else:
                                print('WARNING: YOU HAVE INPUT A NEGATIVE VALUE AS A GROWTH')
                                print(f'THIS MEANS THAT THIS CHARACTER WILL NEVER GAIN A STAT IN THIS LEVEL, AND HAS A {float(new_value)*100}\% CHANCE OF LOSING A POINT IN THE STAT ON LEVEL UP')
                                confirm=input(f"IF YOU ARE ABSOLUTELY SURE THIS IS WHAT YOU WANT\nInput Y to confirm that you want to change {stat_change} to {new_value} or anything else to cancel\n")
                                if confirm.lower()=='y':
                                    setattr(char,stat_change,float(new_value))                             
                    except:
                        print(traceback.format_exc())
                        print('Invalid input, try again')
                elif stat_change.lower()=='x':
                    cont=False
                else:
                    print('Invalid input, try again')
        elif path=='2':
            #join map
            existing_levels=[]
            for i in mapLevel.map_list:
                existing_levels.append(i.mapNum)
            existing_levels.sort()
            print(f"The existing levels are {existing_levels}")
            print(f"{char.name}'s current join map is {char.joinMap}")
            new_join=input(f'Input which number level do you want {char.name} to join on\n')
            if int(new_join) in existing_levels:
                if char.alignment==player:
                    for i in mapLevel.map_list:
                        if i.mapNum==int(new_join):
                            i.player_roster.append(char)
                        elif i.mapNum==char.joinMap:
                            i.player_roster.pop(char)
                else:
                    for i in mapLevel.map_list:
                        if i.mapNum==int(new_join):
                            i.enemy_roster.append(char)
                            cont2=True
                            while cont2==True:
                                print(f"{char.name}'s spawn has to be edited for the new map")
                                taken=[]
                                for j in i.enemy_roster:
                                    if j!=char:
                                        taken.append(j.spawn)
                                for k in i.spawns:
                                    taken.append(k)
                                print(f"The current occupied spaces on this map are {taken}\nAnd the map looks like this")
                                i.display('base')
                                new_spawn=input('Input this characters new spawn point in x,y form seperated by a comma\n')
                                try:
                                    new_spawn=new_spawn.split(',')
                                    new_spawn[0]=int(new_spawn[0])
                                    new_spawn[1]=int(new_spawn[1])
                                    if (new_spawn[0],new_spawn[1]) not in taken:
                                        char.spawn=[new_spawn[0],new_spawn[1]]
                                        cont2=True
                                    else:
                                        print('That space is already taken, try again')
                                except:
                                    print(traceback.format_exc())
                                    print('Invalid input, try again')
                        elif i.mapNum==char.joinMap:
                            i.enemy_roster.pop(char)
                char.joinMap=int(new_join)
                print(f"{char.name}'s join map has been updated")
        elif path=='3':
            #level/exp
            print(f"Level: {char.level} Exp: {char.exp}")
            lev=input(f'Enter their new level\n')
            exp=input(f'Enter their new EXP\n')
            try:
                if int(lev)<=20 and int(exp)<100:
                    if int(lev)>char.level:
                        gain_stats=input('Since you are raising this characters level, input Y to make them gain stats as if leveling up or anything else to keep their stats the same\n')
                        if gain_stats.lower()=='y':
                            while char.level<int(lev):
                                char.level_up(1)
                        else:
                            char.level=int(lev)
                    else:
                        char.level=int(lev)
                    char.exp=int(exp)
                    print(f"{char.name}'s level and exp have been updated")
                else:
                    print('Invalid input, returning to menu')
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to menu')
        elif path=='4':
            #class
            for i in range(0,len(classType.class_list)):
                print(f'{i}: {classType.class_list[i].name}')
            class_choice=input('Input the class number that you would like to reclass to\n')
            try:
                newClass=classType.class_list[int(class_choice)]
                confirm=input(f'Input y to confirm that you wish to change {char.name} to {newClass.name} or anything else to cancel\n')
                if confirm.lower()=='y':
                    stat_change=input(f"Input Y to update {char.name}'s stats based off of this new clas or anything else to keep them the same\n")
                    if stat_change.lower()=='y':
                        char.reclass(newClass)
                    else:
                        char.classType=newClass
            except:
                print(traceback.format_exc())
                print('Invalid input, returning to menu')
        elif path=='5':
            #skills
            skills_path=input(f'Input A to add a skill, D to drop a skill, or X to finish\n')
            if skills_path.lower()=='a':
                cont=False
                while cont==False:
                    viable=[]            
                    for i in range(0,len(skill.skill_list)):
                        if skill.skill_list[i] not in char.skills_all:
                            print(f"{i}: {skill.skill_list[i].name}")
                            viable.append(i)
                    skill_add=input(f"Input the number of the skill you would like to add or x to finish\n")
                    if skill_add.lower()=='x':
                        cont=True
                    else:
                        try:
                            if int(skill_add) in viable:
                                char.add_skill(skill.skill_list[i])
                                print(f'{skill.skill_list[i].name} added')
                            else:
                                print('Invalid input, try again')
                        except:
                            print(traceback.format_exc())
                            print('Invalid input,try again')
            elif skills_path.lower()=='d':
                cont=False
                while cont==False:
                    for i in range(0,len(self.skills_all)):
                        print(f'{i}: {self.skills_all[i].name}')
                    skill_drop=input(f'Input the number of the skill you would like to drop or X to finish\n')
                    if skill_drop.lower()=='x':
                        cont=True
                    else:
                        try:
                            confirm=input(f'Input Y to confirm that you wish to drop {self.skills_all[int(skill_drop)].name} or anything else to cancel\n')
                            if confirm.lower()=='y':
                                dropped_skill=self.skills_all.pop(int(skill_drop))
                                if dropped_skill in self.skills:
                                    self.skills.pop(dropped_skill)
                                print(f'{dropped_skill.name} dropped')
                        except:
                            print(traceback.format_exc())
                            print('Invalid input, try again')   
        elif path=='6':
            #inventory
            inventory_path=input(f"Input A to add items to {char.name}'s inventory or D to drop items\n")
            if inventory_path.lower()=='a':
                char.inventory=stock_inventory('inventory',char.inventory)
                print(f"{char.name}'s inventory has been updated")
            elif inventory_path.lower()=='d':
                cont2=True
                while cont2==True:
                    for i in range(0,len(char.inventory)):
                        print(f"{i}: {char.inventory[i].name}")
                    drop_route=input(f"Input the items number that you wish to drop, type info to get info on an item, or X to finish dropping items\n")
                    if drop_route.lower()=='x':
                        cont2=False
                    elif drop_route.lower()=='info':
                        item_info=input(f"Enter the item number that you want info on\n")
                        try:
                            char.inventory[int(item_info)].info()
                        except:
                            print(traceback.format_exc())
                            print('Invalid input, try again')
                    else:
                        try:
                            dropY=char.drop_item(int(drop_route))
                            print(f"{dropY.name} was dropped")
                        except:
                            print(traceback.format_exc())
                            print('Invalid input, try again')
            else:
                print('Invalid input, returning to menu')
        elif path.lower()=='x':
            cont=False
        else:
            print('Invalid input, try again')
                            
"""
water's movecost is 998, void is 9999, enemy is 999
"""
timemodifier=0
lordDied=False
#maps (name,x_size,y_size,mapNum,spawns)
#map objects (name,mapLevel,location,defBonus,avoidBonus,hpBonus,moveCost,display)
#chartriggers(name,mapLevel,event,characters,*location)
#triggers(name,mapLevel,location,event,*character)
#treasure_chest(mapLevel,location,contents)
#shop(mapLevel,location,contents)
baseShop=shop(None,[-1,-1],[[base_silver_axe,1],[base_shield,1]])
map1=mapLevel('Tutorial',11,15,1,[[0,0],[0,1]],[],[])
fort(map1,[0,0])
throne(map1,[0,1])
void(map1,[8,0])
void(map1,[8,1])
shop(map1,[3,2],[[base_silver_axe,1],[base_shield,1]])
treasure_chest(map1,[5,4],shield(False))
trigger('Save Tutorial',map1,[0,0],'Hi \nDid you know you can save?')
char_trigger('Discussion of games',map1,'Hi King\nGet pwnd Saitama',('Saitama','King'),[0,0])
map2=mapLevel('Map 2',11,10,2,[[0,0],[0,1],[0,2]],[],[])
throne(map2,[0,1])
mapNum=1
###alignments
enemy=alignment('Enemy')
player=alignment('Player')
player.support_master={('Saitama','King'):[0,'Hi','Yo','Final'],('King','Zatch'):[0,'Hello','No Way']}
###Skills (name,trigger_chance,trigger_stat,effect_stat,effect_change,effect_operator,effect_temp,effect_target,*relative_stat):
luna=skill('Luna',9,'skill','defense',.5,'*',True,'enemy')
sol=skill('Sol',5,'skill','curhp',10,'+',False,'self','atk')
astra=skill('Astra',5,'skill','atk',2.5,'*',True,'self')
mag_up=skill('Mag Up',100,'skill','atk',5,'+',True,'self')
mag_up_2=skill('Mag Up 2',100,'skill','atk',5,'+',True,'self')
armsthrift=skill('Armsthrift',5,'luck','curUses',1,'+',False,'weapon')
placeholder=skill('Placeholder',0,'luck','atk',0,'+',True,'self')
paragon=skill('Paragon',0,'luck','atk',0,'+',False,'self')
galeforce=skill('Galeforce',0,'luck','atk',0,'+',False,'self')
###Weapon Arts (name,cost,accuracy,effect_stat,effect_change,effect_operator,weapontype,super_effective,rng):
grounder=weapon_art('Grounder',3,10,'atk',2,'*','Sword',[],[1,2,3,4])
###Classes (advanced classes on top) (name,moveType,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,moveRange,weaponType,promotions,skill_list)
wyvern=classType('Wyvern','Flying',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,8,{'Axe':0,'Lance':0},[],['Luna','Placeholder','Placeholder'])
swordmaster=classType('Swordmaster','Foot',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,6,{'Sword':0},[],['Sol','Placeholder','Placeholder'])
hero=classType('Hero','Foot',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,6,{'Sword':0,'Axe':0},[],['Placeholder','Placeholder','Placeholder'])
paladin=classType('Paladin','Horse',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,7,{'Axe':0,'Lance':0,'Sword':0},[],['Placeholder','Placeholder','Placeholder'])
sage=classType('Sage','Mage',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,5,{'Tome':0},[],['Mag Up 2','Placeholder','Placeholder'])
myrmidom=classType('Myrmidom','Foot',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,5,{'Sword':0},['Swordmaster'],['Astra','Placeholder','Placeholder'])
mercenary=classType('Mercenary','Foot',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,5,{'Sword':0,'Fist':0},['Hero'],['Armsthrift','Placeholder','Placeholder'])
mage=classType('Mage','Mage',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,4,{'Tome':0},[],['Mag Up','Placeholder','Placeholder'])
pirate=classType('Pirate','Pirate',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,4,{'Axe':0},[],['Placeholder','Placeholder','Placeholder'])
lord=classType('Lord','Foot',25,.6,10,.4,0,0,6,.8,2,.35,4,.25,6,.1,7,.5,6,{'Sword':0},[],['Placeholder','Placeholder','Placeholder'])
###player_char(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,{weaponType},joinMap,[inventory],level,{supports},[weapon_arts])
###enemy_char(name,classType,joinMap,[inventory],level,[spawn])
###recruitable(name,curhp,hp,hpG,atk,atkG,mag,magG,skill,skillG,luck,luckG,defense,defG,res,resG,spd,spdG,mov,classType,weaponType,joinMap,inventory,level,spawn,support_list,weapon_arts,recruit_convo)
###boss(name,curhp,hp,atk,mag,skill,luck,defense,res,spd,mov,classType,weaponType,joinMap,inventory,level,spawn):
garou=enemy_char('Garou','Wyvern',1,[javelin(False),iron_axe(True)],1,[1,1])
boss=boss('Boss',25,25,13,1,12,4,8,7,10,0,'Hero',{},1,[iron_axe(True)],10,[5,8])
judas=recruitable('Judas',25,25,.5,13,.7,1,.1,12,.4,4,0,8,.2,7,.4,10,.25,0,'Hero',{},1,[iron_axe(True)],10,[5,8],{},[],'Hey')
hao=enemy_char('Hao','Pirate',1,[iron_axe(False)],1,[1,0])
mumen=enemy_char('Mumen','Pirate',1,[iron_axe(False)],1,[1,2])
ash=enemy_char('Ash','Pirate',1,[silver_axe(False)],1,[9,1])
yuffie=enemy_char('Yuffie','Wyvern',2,[javelin(False)],2,[9,1])
saitama=player_char('Saitama',25,25,.6,10,.4,3,.25,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Swordmaster',{},1,[levin_sword(False),levin_sword(False),gauntlet(False),shield(False),vulnary(False)],10,{'King':0},['Grounder'])
saitama.add_skill(luna)
saitama.add_skill(armsthrift)
king=player_char('King',3,3,.6,10,.4,8,.4,6,.8,2,.35,4,.25,6,.1,2,.5,0,'Lord',{},1,[iron_sword(False),key(False)],1,{'Saitama':0,'Zatch':0},[])
zatch=player_char('Zatch',25,25,.6,10,.4,12,.5,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Mercenary',{},2,[iron_sword(False)],1,{'King':0},[])
###Loading
print('Welcome to FE Builder, created by Schwa')
loadX='placeholder'
tic = time.perf_counter()
if os.path.exists('save_data.txt') or os.path.exists('save_data_battle.txt'):
    if os.path.exists('save_data_battle.txt'):
        j = open("save_data_battle.txt", "r")
        listY=j.read().splitlines()
        j.close()
        print(f'Battlesave: Chapter {int(listY[3])} Playtime {datetime.timedelta(seconds=float(listY[1]))}')
    if os.path.exists('save_data.txt'):
        j = open("save_data.txt", "r")
        listX=j.read().splitlines()
        j.close()
        print(f'File 1: Chapter {int(listX[3])} Playtime {datetime.timedelta(seconds=float(listX[1]))}')
    if os.path.exists('save_data_battle.txt') and os.path.exists('save_data.txt'):
        loadX=input('Would you like to load? Press Y to load, N to start the map over, or X to delete your save file \n')
        if loadX.lower()=='y':
            load('_battle')
        elif loadX.lower()=='n':
            load()
        elif loadX.lower()=='x':
            try:
                os.remove('save_data.txt')
                os.remove('save_data_other.txt')
                os.remove('save_data_maps.txt')
                os.remove('save_data_maps_battle.txt')
                os.remove('save_data_battle.txt')
                os.remove('save_data_other_battle.txt')
            except:
                print(traceback.format_exc())
                pass
            print('Save file deleted')
    elif os.path.exists('save_data_battle.txt') and not os.path.exists('save_data.txt'):
        loadX=input('Would you like to load? Press Y to load or X to delete your save file \n')
        if loadX.lower()=='y':
            load('_battle')
            print('Data loaded')
        elif loadX.lower()=='x':
            try:
                os.remove('save_data_battle.txt')
                os.remove('save_data_maps_battle.txt')
                os.remove('save_data_other_battle.txt')
            except:
                print(traceback.format_exc())
                pass
            print('Save file deleted')
    elif os.path.exists('save_data.txt') and not os.path.exists('save_data_battle.txt'):
        loadX=input('Would you like to load? Press Y to load or X to delete your save file \n')
        if loadX.lower()=='y':
            load()
        elif loadX.lower()=='x':
            try:
                os.remove('save_data.txt')
                os.remove('save_data_other.txt')
                os.remove('save_data_maps.txt')
            except:
                print(traceback.format_exc())
                pass
            print('Save file deleted')
###Creative mode
zerogrowth=False
neggrowth=False
nosupport=False
fullgrowth=False
notriangle=False
if not os.path.exists('cheatshown.txt'):
    cheatshown=False
else:
    cheatshown=True
saveallowed=True
cheatallowed=True
bighead=False
cheat_codes=['uuddlrlrab','630660714755868972','nobitches','superjack','oldschool','bestboy','ultimatelifeform','edgelord','galaxybrain','gettinghead','alphamale']
print('In this there are 2 main modes, creative and survival.\nIn creative mode you can create maps, edit characters, write supports, whatever you like.\nIn survival mode you can use your creations, or just use premade ones if you just want to get into the action.\n')
debug=input('Input Y for creative mode or anything else for survival\n')
while debug.lower()=='y':
    print('0 Character Creator')
    print('1 Map Creator')
    print('2 Weapon Creator')
    print('3 Class Creator')
    print('4 Weapon Art Creator')
    print('5 Skill Creator')
    print('6 Support Writer')
    print('7 Character Editor')
    print('8 Map Editor')    
    path=input('Input which path you would like to take, or x to move to survival mode\n')
    if path=='1':
        create_map()
        cheatallowed=False
    elif path=='0':
        create_character()
        cheatallowed=False
    elif path=='7':
        edit_char()
        cheatallowed=False
    elif path=='8':
        edit_map()
        cheatallowed=False
    elif path=='2':
        create_unique_weapon()
        cheatallowed=False
    elif path=='3':
        create_class()
        cheatallowed=False
    elif path=='4':
        create_weapon_art()
        cheatallowed=False
    elif path=='5':
        create_skill()
        cheatallowed=False
    elif path=='6':
        write_support()
        cheatallowed=False
    elif path.lower()=='x':
        debug='x'
    elif cheatshown==False and (path.lower()=='cheat code' or path.lower()=='password' or path.lower()=='secret'):
        print(cheat_codes[rand.randrange(0,len(cheat_codes))])
        cheatshown=True
        open('cheatshown.txt', 'w')
    elif path.lower()=='uuddlrlrab' and zerogrowth==False and fullgrowth==False and cheatallowed:
        #negative growth mode
        #disable saving
        neggrowth=True
        saveallowed=False
        print('Negative growth mode has been activated. Wither away to dust with a smile!')
        print('Saving has been disabled')
    elif path.lower()=='630660714755868972' and fullgrowth==False and fullgrowth==False and cheatallowed:
        #0% growth mode
        #disable saving
        saveallowed=False
        zerogrowth=True
        print('Zero percent growth mode has been activated. Showing no personal growth has never felt so good!')
        print('Saving has been disabled')
    elif path.lower()=='nobitches' and cheatallowed:
        #no support mode
        nosupport=True
        print('No support mode has been activated. Prepare to die alone!')
    elif path.lower()=='superjack' and zerogrowth==False and neggrowth==False and cheatallowed:
        #100% growth mode
        #disable saving
        print('100% growth mode has been activated. This should be easy, right?')
        print('Saving has been disabled')
    elif path.lower()=='oldschool' and cheatallowed:
        #no triangle mode
        notriangle=True
        print("No weapon triangle mode has been activated. Rock paper scisors waifu chess has been reduced to just chess at this point!")
    elif path.lower()=='bestboy' and cheatallowed:
        #unlock laslow
        laslow=player_char('Laslow',25,25,.6,10,.4,3,.25,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Hero',{},1,[levin_sword(False),levin_sword(False),gauntlet(False),shield(False),vulnary(False)],10,{},['Grounder'])
    elif path.lower()=='ultimatelifeform' and cheatallowed:
        #unlock shadow
        shadow=player_char('Shadow',25,25,.6,10,.4,3,.25,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Swordmaster',{},1,[levin_sword(False),levin_sword(False),gauntlet(False),shield(False),vulnary(False)],10,{},['Grounder'])
    elif path.lower()=='edgelord' and cheatallowed:
        #unlock schwa
        schwa=player_char('Schwa',25,25,.6,10,.4,3,.25,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Swordmaster',{},1,[levin_sword(False),levin_sword(False),gauntlet(False),shield(False),vulnary(False)],10,{},['Grounder'])
    elif path.lower()=='galaxybrain' and cheatallowed:
        #unlock kie
        kie=player_char('Kie',25,25,.6,10,.4,3,.25,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Swordmaster',{},1,[levin_sword(False),levin_sword(False),gauntlet(False),shield(False),vulnary(False)],10,{},['Grounder'])
    elif path.lower()=='gettinghead' and cheatallowed:
        #unlock big head mode
        bighead=True
    elif path.lower()=='alphamale' and cheatallowed:
        #unlock all the alpha characters
        saitama=player_char('Saitama',25,25,.6,10,.4,3,.25,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Swordmaster',{},1,[levin_sword(False),levin_sword(False),gauntlet(False),shield(False),vulnary(False)],10,{},['Grounder'])
        saitama.add_skill(luna)
        saitama.add_skill(armsthrift)
        king=player_char('King',3,3,.6,10,.4,8,.4,6,.8,2,.35,4,.25,6,.1,2,.5,0,'Lord',{},1,[iron_sword(False),key(False)],1,{},[])
        zatch=player_char('Zatch',25,25,.6,10,.4,12,.5,6,.8,2,.35,4,.25,6,.1,20,.5,0,'Mercenary',{},2,[iron_sword(False)],1,{},[])
    else:
        pass
#Gameplay loop
if zerogrowth or neggrowth or fullgrowth:
    for char in characters.character_list:
        for growth in characters.growths:
            if zerogrowth:
                setattr(char,growth,0)
            elif neggrowth:
                if getattr(char,growth)>=0:
                    setattr(char,growth,-getattr(char,growth))
            elif fullgrowth:
                setattr(char,growth,1)
while mapNum<=len(mapLevel.map_list):
    for i in mapLevel.map_list:
        if mapNum==i.mapNum:
            curMap=i
    if curMap.battle_saves==0:
        curMap.start_map()
    else:
        levelComplete=False
    while levelComplete==False and lordDied==False:
        if len(player.roster)>0 and len(enemy.roster)>0:
            gameplay(player)
            ai(enemy)
            curMap.turn_count+=1
        else:
            levelComplete=True
    if len(player.roster)<=0 or lordDied==True:
        print("Your lord has died")
        print("Game over")
        quit()
    else:
        print("You beat the level!")
        curMap.completion_turns=curMap.turn_count
        mapNum+=1
        if saveallowed:
            saveX=input('Would you like to save the game? Input Y to save. \n')
            if saveX.lower()=='y':
                save()
                if os.path.exists('save_data_battle.txt'):
                    listBS=['save_data_battle.txt','save_data_other_battle.txt','save_data_maps_battle.txt']
                    for i in listBS:
                        try:
                            os.remove(i)
                        except:
                            pass
#Ending
print("You beat the game!")
total_turns=0
for i in mapLevel.map_list:
    print(f'{i.name}: {i.completion_turns} turns')
    total_turns+=i.completion_turns
print(f'Total turns: {total_turns}')
total_kills=0
total_battles=0
for i in player_char.player_char_list:
    print(f"{i.name}: {i.kills} kills in {i.battles} battles, {i.status}")
    total_kills+=i.kills
    total_battles+=i.battles
for i in recruitable.recruitable_list:
    print(f"{i.name}: {i.kills} kills in {i.battles} battles, {i.status}, {i.alignment.name}")
    if i.alignment==player:
        total_kills+=i.kills
        total_battles+=i.battles    
print(f'Total battles: {total_battles}')
print(f'Total kills: {total_kills}')
