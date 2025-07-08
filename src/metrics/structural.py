import os, pickle, torch
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

ssim_total = 0
data = list_and_unpickle('../repo')

for idx in range(len(data)):
    ssim_elem_total = 0

    mat1 = torch.from_numpy(data[idx])
    mat1 = mat1.reshape((1, *mat1.shape))

    data_without_idx = data[:idx] + data[idx+1:]
    for jdx in range(len(data_without_idx)):

        mat2 = torch.from_numpy(data_without_idx[jdx])
        mat2 = mat2.reshape((1, *mat2.shape))

        ssim = StructuralSimilarityIndexMeasure(data_range=1.0)
        ssim_elem_total += ssim(mat1, mat2)

    ssim_total += ssim_elem_total / len(data_without_idx)

print(f'SSIM average over {len(data)} instances: {ssim_total/len(data)}\n')