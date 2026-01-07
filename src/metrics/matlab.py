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

###

repo_array = ['operational', 'natural', 'lavatube']
for rdx, repo in enumerate(repo_array):

    spatial = list_and_unpickle(SUBTGRAPH_PATH + '/data/benchmark/' + repo, 'spatial')
    structural = list_and_unpickle(SUBTGRAPH_PATH + '/data/benchmark/' + repo, 'structural')
    topological = list_and_unpickle(SUBTGRAPH_PATH + '/data/benchmark/' + repo, 'topological')
    for idx in range(len(data)):
        mat = torch.from_numpy(data[idx])
        # Save matrices in a format understandable by Matlab