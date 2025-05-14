import math, numpy as np

from shape import EmptyShape

###

empty_shape =   lambda obj:    isinstance(obj, EmptyShape)
full_row =      lambda idx:    idx%2 != 0
half_row =      lambda idx:    idx%2 == 0

side_west =     lambda jdx:     jdx == 0
side_east =     lambda jdx:     jdx == N_COLUMN - 1
side_south =    lambda idx:     idx == N_ROW - 1
side_north =    lambda idx:     idx == 0

door_west =     lambda doors:   "w" in doors
door_east =     lambda doors:   "e" in doors
door_north =    lambda doors:   "n" in doors
door_south =    lambda doors:   "s" in doors

c1 =            lambda parameters:   parameters.split(',')[0] == "c1" 
c2 =            lambda parameters:   parameters.split(',')[0] == "c2" 
c3 =            lambda parameters:   parameters.split(',')[0] == "c3" 
c4 =            lambda parameters:   parameters.split(',')[0] == "c4" 


def rotate_border_regions(asset, corridor, idx, jdx):
    if c1(asset):
        if full_row(idx) and (side_west(jdx) or side_east(jdx)): 
                                                      corridor.rotate(90)
        if full_row(idx):                             corridor.rotate(90)

    if c2(asset):
        if side_south(idx):                           corridor.rotate(180)
        if side_north(idx):                           corridor.rotate(90)
        elif full_row(idx) and side_east(jdx):        corridor.rotate(90)
        elif half_row(idx) and side_east(jdx):        corridor.rotate(180)
        elif half_row(idx):                           corridor.rotate(180)

    if c3(asset):
        if side_south(idx):                           corridor.rotate(270)
        elif side_north(idx):                         corridor.rotate(90)
        elif full_row(idx) and side_east(jdx):        corridor.rotate(180)
        elif half_row(idx) and side_east(jdx):        corridor.rotate(270)
        elif half_row(idx):                           corridor.rotate(270)


def quickSort(array: list):  # O(n * log(n))
    if array.__len__() <= 1:  return array

    distance = [0] * array.__len__()
    for idx in range(array.__len__()):
        distance[idx] = math.sqrt(array[idx][0]**2 + array[idx][1]**2)

    pivot = np.random.randint(0, array.__len__())

    idx = 0;  left = 0
    while idx < array.__len__():
        if idx == pivot:  idx += 1;  continue

        if distance[idx] < distance[pivot]:  left += 1
        idx += 1

    tmp_left  = [0] * left
    tmp_right = [0] * (array.__len__() - left - 1)

    idx = 0;  idx_left = 0;  idx_right = 0
    while idx < array.__len__():
        if idx == pivot:  idx += 1;  continue

        if distance[idx] < distance[pivot]:  tmp_left[idx_left] = array[idx];    idx_left += 1
        else:                                tmp_right[idx_right] = array[idx];  idx_right += 1
        idx += 1
    
    return quickSort(tmp_left) + [array[pivot]] + quickSort(tmp_right)
