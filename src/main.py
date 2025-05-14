import pickle, string, random, bpy, numpy as np

from utils import *

from logic.dijkstra import dijkstra
from logic.grid import GridMap
from build import FactoryObj

###

factory_obj = FactoryObj()
grid = GridMap()

origin = np.random.randint(low=0, high=N_ROW, size=2)
visitation = np.zeros([N_ROW, N_COLUMN])

def contiguous_room(room, room_list):
    check = False
    for i in range(len(room_list)):
        check = check or \
        (room[0] + 1 == room_list[i][0] and room[1]     == room_list[i][1]) or \
        (room[0] - 1 == room_list[i][0] and room[1]     == room_list[i][1]) or \
        (room[0]     == room_list[i][0] and room[1] + 1 == room_list[i][1]) or \
        (room[0]     == room_list[i][0] and room[1] - 1 == room_list[i][1])
    return check

room_list = []
for _ in range(N_ROOMS):    

    room = None
    while True:
        room = np.random.randint(low=0, high=N_ROW, size=2)
        if not contiguous_room(room, room_list):  break
    room_list.append(room)

    _, visited, _ = dijkstra(origin, room, N_ROW)
    visitation += visited

for room in room_list:
    visitation[room[0], room[1]] = 1000
    
grid.dijkstra_grid(visitation)
room_list = quickSort(room_list)

filename = ''.join(random.choice(string.ascii_letters) for i in range(8))
# room_file = open('../repo/out/' + filename + '.csv', 'w')
# for room in room_list:
#     room_file.write(str(room[0]/N_ROW) + ',' + str(room[1]/N_COLUMN) + '\n')

print(grid.__str__())
# struct_file = open('../repo/out/' + filename + '.txt', 'w')
# struct_file.write(grid.__str__())

factory_obj.grid(grid.grid_map)
bpy.ops.wm.obj_export(filepath='../repo/out/' + filename + '.obj')

# room_file.close();struct_file.close()
