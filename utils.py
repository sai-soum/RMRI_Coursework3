import torch
import torch.nn as nn
import numpy as np
import os

from settings import *

# Custom loss function
class CategoricalCrossEntropy(nn.Module):
    def __init__( self):
        super().__init__()

    def forward( self, model_out, target):

        loss = nn.NLLLoss()(torch.log(model_out), target)  
        return loss

def getDevice():
      # torch.cuda.is_available() checks and returns a Boolean True if a GPU is available, else it'll return False
    is_cuda = torch.cuda.is_available()

    # If we have a GPU available, we'll set our device to GPU
    if is_cuda:
        dev = torch.device("cuda")
        print('Using GPU')
    else:
        dev = torch.device("cpu")
        print('GPU not available, using CPU')

    return dev

def to_categorical(y, num_classes):
    """ 1-hot encodes a tensor """
    return np.eye(num_classes, dtype='uint8')[y]

def load_features(filenames, model_name, dataset_mean):
    features = list()
    for filename in filenames:
        feature_filename = os.path.join(IRMAS_TRAIN_FEATURE_BASEPATH, model_name,
                                        "{}.npy".format(filename))
        feature = np.load(feature_filename)
        feature -= dataset_mean
        features.append(feature)

    #if K.image_dim_ordering() == 'th':
    #    features = np.array(features).reshape(-1, 1, N_MEL_BANDS, SEGMENT_DUR)
    #else:
    #    features = np.array(features).reshape(-1, N_MEL_BANDS, SEGMENT_DUR, 1)

    features = np.array(features).reshape(-1, 1, N_MEL_BANDS, SEGMENT_DUR)
    
    return features

def get_extended_data(inputs, targets):
    extended_inputs = list()
    for i in range(0, N_SEGMENTS_PER_TRAINING_FILE):
        extended_inputs.extend(['_'.join(list(x)) for x in zip(inputs, [str(i)]*len(inputs))])
    extended_inputs = np.array(extended_inputs)
    extended_targets = np.tile(np.array(targets).reshape(-1),
                                N_SEGMENTS_PER_TRAINING_FILE).reshape(-1, IRMAS_N_CLASSES)
    return extended_inputs, extended_targets

def batch_generator(self, inputs, targets):
    assert len(inputs) == len(targets)
    while True:
        indices = np.arange(len(inputs))
        np.random.shuffle(indices)
        for start_idx in range(0, len(inputs) - BATCH_SIZE + 1, BATCH_SIZE):
            excerpt = indices[start_idx:start_idx + BATCH_SIZE]
            if self.in_memory_data:
                yield inputs[excerpt], targets[excerpt]
            else:
                yield self._load_features(inputs[excerpt]), targets[excerpt]

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()