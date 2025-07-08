import os, torch, pickle, numpy as np

from scipy.ndimage import rotate
from torchmetrics.image import StructuralSimilarityIndexMeasure

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
    mat_horiz_mirror = mat.flip(dims=(2,))   # Horizontal mirror
    mat_vert_mirror  = mat.flip(dims=(1,))   # Vertical mirror

    ssim = StructuralSimilarityIndexMeasure(data_range=1.0)

    # Compute SSIM between the original matrix and its mirrored versions
    ssim_horiz = ssim(mat.reshape((1, *mat.shape)), mat_horiz_mirror.reshape((1, *mat_horiz_mirror.shape)))
    ssim_vert  = ssim(mat.reshape((1, *mat.shape)), mat_vert_mirror.reshape((1, *mat_vert_mirror.shape)))

    return (ssim_horiz + ssim_vert) / 2.0


def rotation_symmetry_metric(mat):
    rotations = [rotate(mat, angle, reshape=False) for angle in [90, 180, 270]]

    ssim = StructuralSimilarityIndexMeasure(data_range=1.0)

    # Compute SSIM for each rotation compared to the original matrix
    similarities = [ssim(mat.reshape((1, *mat.shape)), torch.from_numpy(rotated).reshape((1, *rotated.shape))) for rotated in rotations]
    
    return np.mean(similarities)

###

# Symmetry vs. asymmetry: Higher asymmetry may correlate with more “natural” or rich environments.

# For a matrix representing occupancy (e.g., a 2D or 3D grid where each element is either 0 or 1), symmetry typically means that the distribution of occupied (1) and unoccupied (0) cells is mirrored in some way. 
# Asymmetry would then imply a distribution that is not mirrored along one or more axes.

# * **Mirror Symmetry**: Symmetry around an axis, either horizontal or vertical (for 2D matrices).
# * **Rotational Symmetry**: Symmetry around a center, where rotating the matrix by 90°, 180°, etc., results in the same structure.
# * **Reflectional Symmetry**: Symmetry across a plane (for 3D matrices).

# To create a metric for symmetry, you can compute how similar the matrix is to its mirrored or rotated counterparts. 
# If the matrix is highly symmetric, this metric should yield a high value (close to 1), and for asymmetry, the value should be lower.

# In environments where asymmetry is expected (such as natural landscapes, city layouts, or complex systems), this metric can help assess whether the space is "rich" or "complex." 
# If a matrix is highly asymmetric, it might be indicative of such a "natural" structure, while perfectly symmetric matrices might represent artificial or overly structured environments.


ssim_symmetry_total = 0
ssim_rotation_total = 0

data = list_and_unpickle('../repo', 'structural')
for idx in range(len(data)):
    mat = torch.from_numpy(data[idx])

    ssim_symmetry_total += symmetry_metric(mat)
    ssim_rotation_total += rotation_symmetry_metric(mat)

print(f"Mirror Symmetry average over {len(data)} instances:\t{ssim_symmetry_total/len(data)}")
print(f"Rotation Symmetry average over {len(data)} instances:\t{ssim_rotation_total/len(data)}\n")

###

# Topological diversity: Count and type of spaces (e.g., rooms, corridors, outdoor/indoor).

value_types = {
    1:   'Node',
    11:  'Origin Shaft',
    111: 'Destination Shaft',
             
    2 :  'Straight',
    3 :  'Corner',
    4 :  'Junction',
    5 :  'Intersection'
}

histogram = {}
for value in value_types.keys():  histogram.update({value : 0})

data = list_and_unpickle('../repo', 'spatial')
for idx in range(len(data)):
    mat = torch.from_numpy(data[idx])

    for idx in range(mat.shape[2]):
        for jdx in range(mat.shape[1]):
            for kdx in range(mat.shape[0]):
                if mat[kdx, jdx, idx] == 0:  continue
                key = int(mat[kdx, jdx, idx])
                histogram.update({key: histogram.get(key) + 1})

print(f"Average Topological Appearances:\n \
        Node: {histogram.get(1) / len(data)} \
        Origin Shaft: {histogram.get(11) / len(data)} \
        Destination Shaft: {histogram.get(111) / len(data)} \
        Straight: {histogram.get(2) / len(data)} \
        Corner: {histogram.get(3) / len(data)} \
        Junction: {histogram.get(4) / len(data)} \
        Intersection: {histogram.get(5) / len(data)}\n")
