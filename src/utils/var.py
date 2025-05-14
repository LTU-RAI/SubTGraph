# ****************************************************************************************************************
# Spatial description of the environment

N_ROW = 10          # minibla
N_COLUMN = 10       # minibla
N_ROOMS = 5         # minibla


# ****************************************************************************************************************
# Repository paths

# minibla
ASSET_PATH = '~/rai-stochastic-factory/assets/.obj/indoor/models/'

# minibla
DARPA_DIMENSIONS = '~/rai-stochastic-factory/config/darpa/dimensions.yaml'


# ****************************************************************************************************************
# Asset names and descriptions

# minibla
ENV_ROOM_ASSET_LIST =     [('room_01', 'r,1,'), ('room_02', 'r,2,'), ('room_03', 'r,3,'), ('room_04', 'r,4,')]

# minibla
ENV_CORRIDOR_ASSET_LIST = [('corridor_01_01', 'c1,1,e'), ('corridor_01_02', 'c1,2,e,w'),
                           ('corridor_02_01', 'c2,1,e'), ('corridor_02_02', 'c2,2,e,s'), 
                           ('corridor_03_01', 'c3,1,e'), ('corridor_03_02', 'c3,2,e,s'), ('corridor_03_03', 'c3,3,e,n,s'),
                           ('corridor_04_01', 'c4,1,e'), ('corridor_04_02', 'c4,2,e,w'), ('corridor_04_03', 'c4,3,e,s,w'), ('corridor_04_04', 'c4,4,e,n,s,w')]
