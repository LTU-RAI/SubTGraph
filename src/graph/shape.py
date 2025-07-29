import re

from utils import *

###

REGEX = r'(?<!\*)\*(?!\*)'  # Regular expression for identifying openings as *

# Anonymous functions to split string of the asset when creating openings

north_split = lambda string_split: string_split[0] + "  " + string_split[1] + "**" + string_split[2] if string_split.__len__() > 2 else \
                                   string_split[0] + "  " + string_split[1]

south_split = lambda string_split: string_split[0] + "**" + string_split[1] + "  " + string_split[2] if string_split.__len__() > 2 else \
                                   string_split[0] + "  " + string_split[1]

west_split = lambda string_split: string_split[0] + " " + string_split[1] + "*" + string_split[2] if string_split.__len__() > 2 else \
                                  string_split[0] + " " + string_split[1]

east_split = lambda string_split: string_split[0] + "*" + string_split[1] + " " + string_split[2] if string_split.__len__() > 2 else \
                                  string_split[0] + " " + string_split[1]

###

class ConnectionShape:

    def __init__(self, connection_type, openings):
        assert(connection_type in ["straight", "corner", "junction", "intersection"])

        self.angle = 0
        self.base = ""
        self.openings = openings
        self.connection_type = connection_type

        if self.connection_type == "straight":
            self.id = 2
            self.base =   "              \n" + \
                          "              \n" + \
                          " ____________ \n" + \
                          "*____________*\n" + \
                          "              \n" + \
                          "              \n"

        if self.connection_type == "corner":
            self.id = 3
            self.base =   "              \n" + \
                          "              \n" + \
                          "      _______ \n" + \
                          "     |   ____*\n" + \
                          "     |  |     \n" + \
                          "     |**|     \n"

        if self.connection_type == "junction": 
            self.id = 4
            self.base =   "      **      \n" + \
                          "     |  |     \n" + \
                          "     |  |____ \n" + \
                          "     |   ____*\n" + \
                          "     |  |     \n" + \
                          "     |**|     \n"

        if self.connection_type == "intersection":
            self.id = 5
            self.base =   "      **      \n" + \
                          "     |  |     \n" + \
                          " ____|  |____ \n" + \
                          "*____    ____*\n" + \
                          "     |  |     \n" + \
                          "     |**|     \n"
        
        self.shape = self.base

    def get_shape(self):
        return self.shape

    def reset(self):
        self.shape = self.base
        self.angle = 0

    def rotate(self, angle):
        assert(angle in [90, 180, 270])

        self.angle = angle
        if self.connection_type == "straight": 
            if angle == 90 or angle == 270:
                self.shape = "      **      \n" + \
                             "     |  |     \n" + \
                             "     |  |     \n" + \
                             "     |  |     \n" + \
                             "     |  |     \n" + \
                             "     |**|     \n"
                self.openings = "n,s".split(',')

        if self.connection_type == "corner": 
            if angle == 90:
                self.shape = "              \n" + \
                             "              \n" + \
                             " _______      \n" + \
                             "*____   |     \n" + \
                             "     |  |     \n" + \
                             "     |**|     \n"
                            
                self.openings = "s,w".split(',')
            if angle == 180:
                self.shape = "     |**|     \n" + \
                             "     |  |     \n" + \
                             " ____|  |     \n" + \
                             "*_______|     \n" + \
                             "              \n" + \
                             "              \n"
                self.openings = "n,w".split(',')
            if angle == 270:
                self.shape = "      **      \n" + \
                             "     |  |     \n" + \
                             "     |  |____ \n" + \
                             "     |_______*\n" + \
                             "              \n" + \
                             "              \n"
                self.openings = "e,n".split(',')

        if self.connection_type == "junction": 
            if angle == 90:
                self.shape = "              \n" + \
                             "              \n" + \
                             " ____________ \n" + \
                             "*____    ____*\n" + \
                             "     |  |     \n" + \
                             "     |**|     \n"
                            
                self.openings = "e,s,w".split(',')
            if angle == 180:
                self.shape = "      **      \n" + \
                             "     |  |     \n" + \
                             " ____|  |     \n" + \
                             "*____   |     \n" + \
                             "     |  |     \n" + \
                             "     |**|     \n"
                self.openings = "n,s,w".split(',')
            if angle == 270:
                self.shape = "      **      \n" + \
                             "     |  |     \n" + \
                             " ____|  |____ \n" + \
                             "*____________*\n" + \
                             "              \n" + \
                             "              \n"
                self.openings = "e,n,w".split(',')

        if self.connection_type == "intersection": 
            self.openings = "e,n,s,w".split(',')

    def opening(self, direction):
        assert(direction in ["e", "n", "s", "w"])

        if self.connection_type == "straight": 
            if direction == "e" and (self.angle == 0  or self.angle == 180):                            self.shape = east_split(re.split(REGEX, self.shape))
            if direction == "w" and (self.angle == 0  or self.angle == 180):                            self.shape = west_split(re.split(REGEX, self.shape))

            if direction == "n" and (self.angle == 90 or self.angle == 270):                            self.shape = north_split(self.shape.split("**"))
            if direction == "s" and (self.angle == 90 or self.angle == 270):                            self.shape = south_split(self.shape.split("**"))

        if self.connection_type == "corner":
            if direction == "e" and (self.angle == 0 or self.angle == 270):                             door_split = re.split(REGEX, self.shape);           self.shape = door_split[0] + " "  + door_split[1]
            if direction == "n" and (self.angle == 180 or self.angle == 270):                           door_split = self.shape.split("**");                self.shape = door_split[0] + "  " + door_split[1]
            if direction == "s" and (self.angle == 0 or self.angle == 90):                              door_split = self.shape.split("**");                self.shape = door_split[0] + "  " + door_split[1]
            if direction == "w" and (self.angle == 90 or self.angle == 180):                            door_split = re.split(REGEX, self.shape);           self.shape = door_split[0] + " "  + door_split[1]

        if self.connection_type == "junction":
            if direction == "e" and (self.angle == 0 or self.angle == 90 or self.angle == 270):         self.shape = east_split(re.split(REGEX, self.shape))
            if direction == "n":
                if self.angle == 0 or self.angle == 180:                                                self.shape = north_split(self.shape.split("**"))
                if self.angle == 270:                                                                   door_split = self.shape.split("**");                self.shape = door_split[0] + "  " + door_split[1]
            if direction == "s":
                if self.angle == 0 or self.angle == 180:                                                self.shape = south_split(self.shape.split("**"))
                if self.angle == 90:                                                                    door_split = self.shape.split("**");                self.shape = door_split[0] + "  " + door_split[1]
            if direction == "w" and (self.angle == 90 or self.angle == 180 or self.angle == 270):       self.shape = west_split(re.split(REGEX, self.shape))

        if self.connection_type == "intersection":  
            if direction == "e":                                                                        self.shape = east_split(re.split(REGEX, self.shape))
            if direction == "n":                                                                        self.shape = north_split(self.shape.split("**"))
            if direction == "s":                                                                        self.shape = south_split(self.shape.split("**"))
            if direction == "w":                                                                        self.shape = west_split(re.split(REGEX, self.shape))


class NodeShape:

    def __init__(self):
        self.id = 1
        self.base =  "              \n" + \
                     "   ___**___   \n" + \
                     "  |        |  \n" + \
                     "  *        *  \n" + \
                     "  |___**___|  \n" + \
                     "              \n"

        self.connection_type = 'node'
        self.shape = self.base
        self.openings = "e,n,s,w".split(',')

    def set_origin_shaft(self):
        self.id = 11
        self.connection_type = 'shaft'
        self.shape = "              \n" + \
                     "   ___**___   \n" + \
                     "  |        |  \n" + \
                     "  *   OS   *  \n" + \
                     "  |___**___|  \n" + \
                     "              \n"
        self.org_diff = list(set(['n', 's', 'e', 'w']) - set(self.openings))
        for direction in self.org_diff:
            if direction == "e":   self.shape = east_split(re.split(REGEX, self.shape))
            if direction == "n":   self.shape = north_split(self.shape.split("**"))
            if direction == "s":   self.shape = south_split(self.shape.split("**"))
            if direction == "w":   self.shape = west_split(re.split(REGEX, self.shape))

    def set_destination_shaft(self):
        self.id = 111
        self.connection_type = 'shaft_aux'
        self.shape = "              \n" + \
                     "   ___**___   \n" + \
                     "  |        |  \n" + \
                     "  *   DS   *  \n" + \
                     "  |___**___|  \n" + \
                     "              \n"
        self.dst_diff = list(set(['n', 's', 'e', 'w']) - set(self.openings))
        for direction in self.dst_diff:
            if direction == "e":   self.shape = east_split(re.split(REGEX, self.shape))
            if direction == "n":   self.shape = north_split(self.shape.split("**"))
            if direction == "s":   self.shape = south_split(self.shape.split("**"))
            if direction == "w":   self.shape = west_split(re.split(REGEX, self.shape))

    def get_shape(self):
        return self.shape

    def reset(self):
        self.shape = self.base

    def opening(self, direction):
        assert(direction in ["e", "n", "s", "w"])

        if direction == "e":   self.shape = east_split(re.split(REGEX, self.shape));    self.openings.remove("e")
        if direction == "n":   self.shape = north_split(self.shape.split("**"));        self.openings.remove("n")
        if direction == "s":   self.shape = south_split(self.shape.split("**"));        self.openings.remove("s")
        if direction == "w":   self.shape = west_split(re.split(REGEX, self.shape));    self.openings.remove("w")

        if self.openings.__len__() == 2:  
            if ((self.openings.__contains__("n") and self.openings.__contains__("s")) or (self.openings.__contains__("e") and self.openings.__contains__("w"))): self.connection_type = "straight"
            else:  self.connection_type = "corner"
        if self.openings.__len__() == 1:  self.connection_type = "junction"
        if self.openings.__len__() == 0:  self.connection_type = "intersection"


class EmptyShape:

    def __init__(self):
        self.id = 0
        self.shape =    "              \n" + \
                        "              \n" + \
                        "              \n" + \
                        "              \n" + \
                        "              \n" + \
                        "              \n"

    def get_shape(self):
        return self.shape