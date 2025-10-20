import os, torch, pickle
import matplotlib.pyplot as plt
import seaborn as sns, numpy as np

from utils import *
from scipy.ndimage import rotate

###

def list_and_unpickle(directory: str, matrix_type: str):
    dir_array = os.listdir(directory)
    data_array = []

    for dir in dir_array:
        files = os.listdir(os.path.join(directory, dir, 'pkl'))
        pickle_files = [f for f in files if f.endswith(matrix_type + '.pkl')]
        
        for pkl_file in pickle_files:
            file_path = os.path.join(directory, dir, 'pkl', pkl_file)
            with open(file_path, 'rb') as file:
                try:                    data_array.append(pickle.load(file))
                except Exception as e:  pass
    
    return data_array


def symmetry_metric(mat):
    """Compute horizontal and vertical symmetry IoU."""
    mat_horiz_mirror = mat.flip(dims=(2,))   # Horizontal mirror
    mat_vert_mirror  = mat.flip(dims=(1,))   # Vertical mirror

    iou_horiz = intersection_over_union(mat, mat_horiz_mirror)
    iou_vert  = intersection_over_union(mat, mat_vert_mirror)

    return iou_horiz, iou_vert


def rotation_symmetry_metric(mat):
    """Compute rotational symmetry IoU."""
    rotations = [rotate(mat, angle, reshape=False) for angle in [90, 180, 270]]
    ious = [intersection_over_union(mat, torch.from_numpy(rotated)) for rotated in rotations]
    return np.mean([iou.item() for iou in ious])

###

if False:  # Symmetry vs. asymmetry: Higher asymmetry may correlate with more “natural” or rich environments.

    iou_symmetry_total = []
    iou_rotation_total = []

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    repo_array = ['operational', 'natural', 'lavatube']
    for rdx, repo in enumerate(repo_array):

        iou_symmetry_horiz = 0
        iou_symmetry_vert = 0
        iou_rotation = 0

        data = list_and_unpickle(SUBTGRAPH_PATH + '/data/benchmark/' + repo, 'structural')
        for idx in range(len(data)):
            mat = torch.from_numpy(data[idx])

            iou_horiz, iou_vert = symmetry_metric(mat)
            iou_symmetry_horiz += iou_horiz.item()
            iou_symmetry_vert += iou_vert.item()

            iou_rot = rotation_symmetry_metric(mat)
            iou_rotation += iou_rot
            
        sns.barplot(
            x=['Horizontal', 'Vertical', 'Rotation'], 
            y=[
                iou_symmetry_horiz/len(data), 
                iou_symmetry_vert/len(data), 
                iou_rotation/len(data)
            ], 
            ax=axes[rdx], 
            palette='rocket'
        )

        axes[rdx].set_title(repo_array[rdx][0].upper() + repo_array[rdx][1:] + ' generation')
        axes[rdx].set_ylabel('IoU')
        axes[rdx].set_ylim(0, 0.25)

    plt.tight_layout()
    plt.show()

###

if False:  # Topological diversity: Count and type of spaces (e.g., rooms, corridors, outdoor/indoor).

    value_types = {
        1:   'Node',
        2 :  'Straight',
        3 :  'Corner',
        4 :  'Junction',
        5 :  'Intersection'
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    repo_array = ['operational', 'natural', 'lavatube']
    for rdx, repo in enumerate(repo_array):

        histogram = {}
        for value in value_types.keys():  histogram.update({value : []})

        data = list_and_unpickle(SUBTGRAPH_PATH + '/data/benchmark/' + repo, 'spatial')
        for idx in range(len(data)):
            mat = torch.from_numpy(data[idx])

            for idx in range(mat.shape[2]):
                for jdx in range(mat.shape[1]):
                    for kdx in range(mat.shape[0]):
                        if mat[kdx, jdx, idx] == 0 or mat[kdx, jdx, idx] == 11 or mat[kdx, jdx, idx] == 111:  continue
                        key = int(mat[kdx, jdx, idx])
                        histogram.update({key: histogram.get(key) + [key]})

        values = list(histogram.values())
        values_np = np.array([], dtype=np.int8)

        for l in values:
            for v in l:
                values_np = np.append(values_np, v)

        colors = sns.color_palette("rocket", len(value_types.keys()))
        hist_data = sns.histplot(values_np, bins=range(min(values_np), max(values_np) + 2), kde=False, ax=axes[rdx], stat="percent")

        for patch, color in zip(hist_data.patches, colors):
            patch.set_facecolor(color)

        axes[rdx].set_title(repo_array[rdx][0].upper() + repo_array[rdx][1:] + ' generation')
        axes[rdx].set_ylabel('Probability (%)')

        bin_edges = hist_data.patches[0].get_x()      # Get the x-position of the first bar
        bin_width = hist_data.patches[0].get_width()  # Get the width of the bars
        xticks_positions = [bin_edges + bin_width / 2 for bin_edges in range(min(values_np), max(values_np) + 1)]

        axes[rdx].set_xticks(xticks_positions, [str(i) for i in range(min(values_np), max(values_np) + 1)])
        axes[rdx].set_xticklabels([value_types[key] for key in value_types.keys()])
        axes[rdx].set_ylim(0, 100)

    plt.tight_layout()
    plt.show()