import os
from .model_generation import load_pretrained_model_from_dump
from .conv_and_global_attention_model import create_model
from tensorflow import keras


DEFAULT_LOCAL_MODEL_DUMP_DIR = '../data'
DEFAULT_LOCAL_MODEL_DUMP_FILE_NAME = 'pretrained_model2.pkl'

def load_pretrained_model(local_model_dump_dir = DEFAULT_LOCAL_MODEL_DUMP_DIR, local_model_dump_file_name = DEFAULT_LOCAL_MODEL_DUMP_FILE_NAME, \
        create_model_function = create_model, create_model_kwargs = {}, optimizer_class = keras.optimizers.Adam, lr = 2e-04, \
        other_optimizer_kwargs = {}, annots_loss_weight = 1, load_optimizer_weights = False):
    
    local_model_dump_dir = os.path.expanduser(local_model_dump_dir)
    dump_file_path = os.path.join(local_model_dump_dir, local_model_dump_file_name)

    return load_pretrained_model_from_dump(dump_file_path, create_model_function, create_model_kwargs = create_model_kwargs, optimizer_class = optimizer_class, lr = lr, \
            other_optimizer_kwargs = other_optimizer_kwargs, annots_loss_weight = annots_loss_weight, load_optimizer_weights = load_optimizer_weights)
