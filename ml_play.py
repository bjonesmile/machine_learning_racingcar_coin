import numpy as np
from scipy.spatial.distance import pdist

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0
        self.car_pos = (0,0)
        self.last_cmd = ""
        self.brake_lim = 0
        pass

    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        def search_lane(direct,org_pos):
            ser_range = org_pos
            leftcar_pos = (-1,-1)
            rightcar_pos = (-1,-1)
            if(org_pos[0]>570 or org_pos[0]<60):
                return (-1,-1)
            else:
                if direct == "right":
                    ser_range = (org_pos[0]+65,org_pos[1]+40 )
                    for car in scene_info["cars_info"]:
                        if car["id"]==self.player_no:
                            continue
                        pos = car["pos"]
                        if(pos[0]-20 >self.car_pos[0]+20 and pos[0]<ser_range[0]) and (pos[1]+40<self.car_pos[1]+100 and pos[1]>ser_range[1]):
                            if pos[1] > rightcar_pos[1]:
                                rightcar_pos = pos
                    return rightcar_pos
                else:
                    ser_range = (org_pos[0]-65,org_pos[1]+40 )
                    for car in scene_info["cars_info"]:
                        if car["id"]==self.player_no:
                            continue
                        pos = car["pos"]
                        if(pos[0]-20 <self.car_pos[0]+20 and pos[0]>ser_range[0]) and (pos[1]+40<self.car_pos[1]+100 and pos[1]>ser_range[1]):
                            if pos[1] > leftcar_pos[1]:
                                leftcar_pos = pos
                    return leftcar_pos
        def search_back_lane():
            leftcar_pos = (-1,-1)
            rightcar_pos = (-1,-1)
            # consider back right
            ser_range = (self.car_pos[0]+65,self.car_pos[1]+120 )
            for car in scene_info["cars_info"]:
                if car["id"]!=self.player_no:
                    continue
                pos = car["pos"]
                if(pos[0]-20 >self.car_pos[0]+20 and pos[0]<ser_range[0]) and (pos[1]-40<self.car_pos[1]+50 and pos[1]>ser_range[1]):
                    if pos[1] > rightcar_pos[1]:
                        rightcar_pos = pos
            # consider back left
            ser_range = (self.car_pos[0]-65,self.car_pos[1]+120 )
            for car in scene_info["cars_info"]:
                if car["id"]!=self.player_no:
                    continue
                pos = car["pos"]
                if(pos[0]+20 <self.car_pos[0]-20 and pos[0]>ser_range[0]) and (pos[1]-40<self.car_pos[1]+50 and pos[1]>ser_range[1]):
                    if pos[1] > leftcar_pos[1]:
                        leftcar_pos = pos
            
            if rightcar_pos[1] != -1 and leftcar_pos[1] != -1:
                if rightcar_pos[1] > leftcar_pos[1]:
                    return "right"
                else:
                    return "left"
            elif rightcar_pos[1] != -1 and leftcar_pos[1] == -1:
                return "left"
            elif rightcar_pos[1] == -1 and leftcar_pos[1] != -1:
                return "right"
            else:
                if (self.car_pos[0]-315)>0:
                    return "left"
                else:
                    return "right"
                
        isBrake = False
        self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]
                self.coin_num = car["coin_num"]
                #print(self.car_vel)
                break
        
        if scene_info["status"] != "ALIVE":
            return ["RESET"]
        if self.car_vel ==0 and scene_info["frame"]>10: #check for divid zero error when car is out
            return ["RESET"]
        if not all(self.car_pos): #check for out of range tuple error
            return ["RESET"]

        #init some variable
        ser_x = -1
        ser_y = -1
        ser_vel = -1
        min_distance = 10000
        if self.last_cmd != "BRAKE":
            self.brake_lim = 0
        for car in scene_info["cars_info"]:
            if car["id"]!=self.player_no:
                pos = car["pos"]
                #if pos[1] < 0:
                    #continue  
                if(pos[1] < self.car_pos[1]+40 and abs(pos[0]-self.car_pos[0])<50):
                    #X = np.array([[pos[0],pos[1]],[self.car_pos[0],self.car_pos[1]]],dtype='float64')
                    #distance = pdist(X, 'euclidean')
                    ydistance = abs(pos[1]-self.car_pos[1])
                    if abs(self.car_vel-car["velocity"]) == 0:
                        continue
                    if((ydistance-80)//abs(self.car_vel-car["velocity"])< 150//3 and min_distance > ydistance):
                        min_distance = ydistance
                        ser_vel = car["velocity"]
                        ser_x = self.car_pos[0]
                        ser_y = pos[1]
                        isBrake = True
        """
        if min_distance <= 120: #dircetly brake when too close
            self.last_cmd = "BRAKE"
            return ["BRAKE"]
        """
        rightcar_pos = (-1,-1)
        leftcar_pos = (-1,-1)
        isMoveRight = True
        isMoveLeft = True
        if(isBrake):
            #consider move right
            rightcar_pos = search_lane(direct = "right",org_pos = (ser_x,ser_y))
            if rightcar_pos[1] != -1:
                isMoveRight =False
            #consider move left
            leftcar_pos = search_lane(direct = "left",org_pos = (ser_x,ser_y))
            if leftcar_pos[1] != -1:
                isMoveLeft =False

            if(isMoveRight and isMoveLeft):
                if rightcar_pos[1] < leftcar_pos[1]:
                    isMoveLeft =False
                else:
                    isMoveRight =False
        else:
            near_coin = (-1,-1)
            for coin in scene_info["coins"]:
                coin_xdistance = abs(self.car_pos[0]-coin[0])
                coin_ydistance = abs(self.car_pos[1]-coin[1])
                if coin[1] < self.car_pos[1]+50 and coin_xdistance//3 <  coin_ydistance//5:
                    if near_coin[1] < coin[1]:
                        near_coin = coin
            
            if near_coin[0] == -1: # no coin can get
                isMoveRight = False
                isMoveLeft = False
            else:
                if abs(near_coin[0]-self.car_pos[0]) <15:  # front coin
                    isMoveRight = False
                    isMoveLeft = False
                else:
                    if near_coin[0] > self.car_pos[0]+10:# right coin
                        isMoveLeft = False
                        rightcar_pos = search_lane(direct = "right",org_pos = (self.car_pos[0],near_coin[1]-80))
                        if rightcar_pos[1] != -1:
                            isMoveRight = False
                    elif near_coin[0] < self.car_pos[0]-10:# left coin
                        isMoveRight = False
                        leftcar_pos = search_lane(direct = "left",org_pos = (self.car_pos[0],near_coin[1]-80))
                        if leftcar_pos[1] != -1:
                            isMoveLeft = False
        if scene_info["status"] != "ALIVE":
            return "RESET"
        else:
            if(isBrake):
                if isMoveLeft == False and isMoveRight == False:
                    if self.last_cmd != "BRAKE" and self.brake_lim == 0:
                        self.brake_lim = abs(ser_vel - self.car_vel)//1.7 + scene_info["frame"]
                    brake_direct = search_back_lane() 
                    self.last_cmd = "BRAKE"
                    if scene_info["frame"] < self.brake_lim:
                        if brake_direct == "right":
                            return ["MOVE_RIGHT", "BRAKE"]
                        else:
                            return ["MOVE_LEFT", "BRAKE"]
                    else:
                        if brake_direct == "right":
                            return ["MOVE_RIGHT"]
                        else:
                            return ["MOVE_LEFT"]
                if(isMoveRight):
                    if self.car_pos[0]+20 < 575:
                        self.last_cmd = "BRAKE"
                        return ["MOVE_LEFT", "BRAKE"]
                    self.last_cmd = "MOVE_RIGHT"
                    return ["MOVE_RIGHT", "SPEED"]
                if(isMoveLeft):
                    if self.car_pos[0]-20 < 45:
                        self.last_cmd = "BRAKE"
                        return ["MOVE_RIGHT", "BRAKE"]
                    self.last_cmd = "MOVE_LEFT"
                    return ["MOVE_LEFT", "SPEED"]
            else:
                if(isMoveRight):
                    self.last_cmd = "MOVE_RIGHT"
                    return ["MOVE_RIGHT", "SPEED"]
                elif(isMoveLeft):
                    self.last_cmd = "MOVE_LEFT"
                    return ["MOVE_LEFT", "SPEED"]
            
            right_car_close = False
            left_car_close = False
            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    continue
                pos = car["pos"]
                if(abs(pos[0] - self.car_pos[0])<40 and abs(pos[1] - self.car_pos[1])<20):
                    if pos[0] > self.car_pos[0]:
                        right_car_close = True
            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    continue
                pos = car["pos"]
                if(abs(pos[0] - self.car_pos[0])<40 and abs(pos[1] - self.car_pos[1])<20):
                    if pos[0] < self.car_pos[0]:
                        left_car_close = True
            
            if right_car_close or left_car_close:
                self.last_cmd = "SPEED"
                return ["SPEED"]
            elif right_car_close == True and left_car_close == False:
                self.last_cmd = "MOVE_LEFT"
                return ["MOVE_LEFT", "SPEED"]
            elif right_car_close == False and left_car_close == True:
                self.last_cmd = "MOVE_RIGHT"
                return ["MOVE_RIGHT", "SPEED"]
            else:
                self.last_cmd = "SPEED"
                return ["SPEED"]
    def reset(self):
        """
        Reset the status
        """
        pass
