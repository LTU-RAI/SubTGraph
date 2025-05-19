import re
import numpy as np

from utils import *

###

REGEX = r'(?<!\*)\*(?!\*)'

def north_split(door_split):
    return door_split[0] + "  " + door_split[1] + "**" + door_split[2] if door_split.__len__() > 2 else \
           door_split[0] + "  " + door_split[1]

def south_split(door_split):
    return door_split[0] + "**" + door_split[1] + "  " + door_split[2] if door_split.__len__() > 2 else \
           door_split[0] + "  " + door_split[1]

def west_split(door_split):
    return door_split[0] + " " + door_split[1] + "*" + door_split[2] if door_split.__len__() > 2 else \
           door_split[0] + " " + door_split[1]

def east_split(door_split):
    return door_split[0] + "*" + door_split[1] + " " + door_split[2] if door_split.__len__() > 2 else \
           door_split[0] + " " + door_split[1]

###

class CorridorShape:

    def __init__(self, corridor_type, doors):
        assert(corridor_type in ["c1", "c2", "c3", "c4"])
        self.corridor_type = corridor_type
        self.doors = doors

        self.c_base = "";  self.c_asset = ""
        self.c_angle = 0

        if self.corridor_type == "c1":
            self.c_base =   "              \n" + \
                            "              \n" + \
                            " ____________ \n" + \
                            "*____________*\n" + \
                            "              \n" + \
                            "              \n"
            self.c_asset = 'corridor_01'

        if self.corridor_type == "c2":
            self.c_base =   "              \n" + \
                            "              \n" + \
                            "      _______ \n" + \
                            "     |   ____*\n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
            self.c_asset = 'corridor_02'

        if self.corridor_type == "c3": 
            self.c_base =   "      **      \n" + \
                            "     |  |     \n" + \
                            "     |  |____ \n" + \
                            "     |   ____*\n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
            self.c_asset = 'corridor_03'

        if self.corridor_type == "c4":
            self.c_base =   "      **      \n" + \
                            "     |  |     \n" + \
                            " ____|  |____ \n" + \
                            "*____    ____*\n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
            self.c_asset = 'corridor_04'
        
        self.c = self.c_base

    def get_shape(self):
        return self.c

    def rand_doors(self, doors):
        low = np.random.randint(low=0, high=len(doors), size=1)[0]
        self.doors = doors[low:]

    def reset(self):
        self.c = self.c_base
        self.c_angle = 0

    def rotate(self, angle):
        assert(angle in [90, 180, 270])

        self.c_angle = angle
        if self.corridor_type == "c1": 
            if angle == 90 or angle == 270:
                self.c =    "      **      \n" + \
                            "     |  |     \n" + \
                            "     |  |     \n" + \
                            "     |  |     \n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
                self.rand_doors("n,s".split(','))

        if self.corridor_type == "c2": 
            if angle == 90:
                self.c =    "              \n" + \
                            "              \n" + \
                            " _______      \n" + \
                            "*____   |     \n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
                            
                self.rand_doors("s,w".split(','))
            if angle == 180:
                self.c =    "     |**|     \n" + \
                            "     |  |     \n" + \
                            " ____|  |     \n" + \
                            "*_______|     \n" + \
                            "              \n" + \
                            "              \n"
                self.rand_doors("n,w".split(','))
            if angle == 270:
                self.c =    "      **      \n" + \
                            "     |  |     \n" + \
                            "     |  |____ \n" + \
                            "     |_______*\n" + \
                            "              \n" + \
                            "              \n"
                self.rand_doors("e,n".split(','))

        if self.corridor_type == "c3": 
            if angle == 90:
                self.c =    "              \n" + \
                            "              \n" + \
                            " ____________ \n" + \
                            "*____    ____*\n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
                            
                self.rand_doors("e,s,w".split(','))
            if angle == 180:
                self.c =    "      **      \n" + \
                            "     |  |     \n" + \
                            " ____|  |     \n" + \
                            "*____   |     \n" + \
                            "     |  |     \n" + \
                            "     |**|     \n"
                self.rand_doors("n,s,w".split(','))
            if angle == 270:
                self.c =    "      **      \n" + \
                            "     |  |     \n" + \
                            " ____|  |____ \n" + \
                            "*____________*\n" + \
                            "              \n" + \
                            "              \n"
                self.rand_doors("e,n,w".split(','))
        if self.corridor_type == "c4": 
            self.rand_doors("e,n,s,w".split(','))

    def door(self, direction):
        assert(direction in ["e", "n", "s", "w"])

        if self.corridor_type == "c1": 
            if direction == "e" and (self.c_angle == 0  or self.c_angle == 180):                            self.c = east_split(re.split(REGEX, self.c))
            if direction == "n" and (self.c_angle == 90 or self.c_angle == 270):                            self.c = north_split(self.c.split("**"))
            if direction == "s" and (self.c_angle == 90 or self.c_angle == 270):                            self.c = south_split(self.c.split("**"))
            if direction == "w" and (self.c_angle == 0  or self.c_angle == 180):                            self.c = west_split(re.split(REGEX, self.c))

        if self.corridor_type == "c2":
            if direction == "e" and (self.c_angle == 0 or self.c_angle == 270):                             door_split = re.split(REGEX, self.c);           self.c = door_split[0] + " "  + door_split[1]
            if direction == "n" and (self.c_angle == 180 or self.c_angle == 270):                           door_split = self.c.split("**");                self.c = door_split[0] + "  " + door_split[1]
            if direction == "s" and (self.c_angle == 0 or self.c_angle == 90):                              door_split = self.c.split("**");                self.c = door_split[0] + "  " + door_split[1]
            if direction == "w" and (self.c_angle == 90 or self.c_angle == 180):                            door_split = re.split(REGEX, self.c);           self.c = door_split[0] + " "  + door_split[1]

        if self.corridor_type == "c3":
            if direction == "e" and (self.c_angle == 0 or self.c_angle == 90 or self.c_angle == 270):       self.c = east_split(re.split(REGEX, self.c))
            if direction == "n":
                if self.c_angle == 0 or self.c_angle == 180:                                                self.c = north_split(self.c.split("**"))
                if self.c_angle == 270:                                                                     door_split = self.c.split("**");                self.c = door_split[0] + "  " + door_split[1]
            if direction == "s":
                if self.c_angle == 0 or self.c_angle == 180:                                                self.c = south_split(self.c.split("**"))
                if self.c_angle == 90:                                                                      door_split = self.c.split("**");                self.c = door_split[0] + "  " + door_split[1]
            if direction == "w" and (self.c_angle == 90 or self.c_angle == 180 or self.c_angle == 270):     self.c = west_split(re.split(REGEX, self.c))

        if self.corridor_type == "c4":  
            if direction == "e":                                                                            self.c = east_split(re.split(REGEX, self.c))
            if direction == "n":                                                                            self.c = north_split(self.c.split("**"))
            if direction == "s":                                                                            self.c = south_split(self.c.split("**"))
            if direction == "w":                                                                            self.c = west_split(re.split(REGEX, self.c))


class RoomShape:

    def __init__(self):
        self.r_base =   "              \n" + \
                        "   ___**___   \n" + \
                        "  |        |  \n" + \
                        "  *        *  \n" + \
                        "  |___**___|  \n" + \
                        "              \n"
        self.r = self.r_base
        self.r_asset = 'room'
        self.doors = "e,n,s,w".split(',')

    def get_shape(self):
        return self.r

    def reset(self):
        self.c = self.r_base

    def door(self, direction):
        assert(direction in ["e", "n", "s", "w"])

        if direction == "e":   self.r = east_split(re.split(REGEX, self.r));    self.doors.remove("e")
        if direction == "n":   self.r = north_split(self.r.split("**"));        self.doors.remove("n")
        if direction == "s":   self.r = south_split(self.r.split("**"));        self.doors.remove("s")
        if direction == "w":   self.r = west_split(re.split(REGEX, self.r));    self.doors.remove("w")


class EmptyShape:

    def __init__(self):
        self.e =        "              \n" + \
                        "              \n" + \
                        "              \n" + \
                        "              \n" + \
                        "              \n" + \
                        "              \n"

    def get_shape(self):
        return self.e