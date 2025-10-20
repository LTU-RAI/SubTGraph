import seaborn as sns
import os, pickle, torch
import matplotlib.pyplot as plt
import torch.nn.functional as F

from utils import *
from torchmetrics.image import StructuralSimilarityIndexMeasure

###

def list_and_unpickle(directory: str):
    dir_array = os.listdir(directory)
    data_array = []

    for dir in dir_array:
        files = os.listdir(os.path.join(directory, dir, 'pkl'))
        pickle_files = [f for f in files if f.endswith('structural.pkl')]
        
        for pkl_file in pickle_files:
            file_path = os.path.join(directory, dir, 'pkl', pkl_file)
            with open(file_path, 'rb') as file:
                try:                    data_array.append(pickle.load(file))
                except Exception as e:  pass
    
    return data_array

###

ssim_total = []
data = list_and_unpickle(SUBTGRAPH_PATH + '/data/benchmark/lavatube')

for idx in range(len(data)):
    ssim_elem_total = []

    mat1 = torch.from_numpy(data[idx]).float()
    mat1 = mat1.reshape((1, *mat1.shape))

    for jdx in range(len(data)):
        mat2 = torch.from_numpy(data[jdx]).float()
        mat2 = mat2.reshape((1, *mat2.shape))

        shape1 = mat1.shape  # (1, x1, y1, z1)
        shape2 = mat2.shape  # (1, x2, y2, z2)
        max_shape = tuple(max(s1, s2) for s1, s2 in zip(shape1, shape2))

        def pad_to_shape(mat, target_shape):
            """Pad tensor with zeros (centered) to match target shape."""
            pad = []
            for dim, target, current in zip(reversed(range(len(mat.shape))), reversed(target_shape), reversed(mat.shape)):
                diff = target - current
                if diff > 0:
                    pad_left = diff // 2
                    pad_right = diff - pad_left
                    pad.extend([pad_left, pad_right])
                else:
                    pad.extend([0, 0])
            return F.pad(mat, pad, mode='constant', value=0)

        mat1_padded = pad_to_shape(mat1, max_shape)
        mat2_padded = pad_to_shape(mat2, max_shape)

        ssim = StructuralSimilarityIndexMeasure(data_range=1.0)
        score = ssim(mat1_padded, mat2_padded)
        ssim_elem_total.append(score.item())

    ssim_total.append(ssim_elem_total)

plt.figure(figsize=(8, 6))
sns.heatmap(ssim_total, annot=False, fmt='g')
plt.show()
