import seaborn as sns
import os, pickle, torch
import matplotlib.pyplot as plt

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
data = list_and_unpickle(SUBTGRAPH_PATH + '/data/metrics/sine')

for idx in range(len(data)):
    ssim_elem_total = []

    mat1 = torch.from_numpy(data[idx])
    mat1 = mat1.reshape((1, *mat1.shape))

    for jdx in range(len(data)):

        mat2 = torch.from_numpy(data[jdx])
        mat2 = mat2.reshape((1, *mat2.shape))

        ssim = StructuralSimilarityIndexMeasure(data_range=1.0)
        ssim_elem_total.append(ssim(mat1, mat2))

    ssim_total.append(ssim_elem_total)

plt.figure(figsize=(8, 6))
sns.heatmap(ssim_total, annot=False, fmt='g')
plt.xlabel('Graph ID')
plt.ylabel('Graph ID')
plt.show()
