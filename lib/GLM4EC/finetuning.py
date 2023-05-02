import numpy as np
from .tokenization import ADDED_TOKENS_PER_SEQ

class OutputType:
    
    def __init__(self, is_seq, output_type):
        self.is_seq = is_seq
        self.output_type = output_type 
        self.is_MLC = (output_type == 'MLC')
        
    def __str__(self):
        if self.is_seq:
            return '%s sequence' % self.output_type
        else:
            return 'global %s' % self.output_type


class OutputSpec:

    def __init__(self, output_type, unique_labels = None):
        
        if output_type.is_MLC:
            assert unique_labels is not None
        else:
            raise ValueError('Unexpected output type: %s' % output_type)
        
        self.output_type = output_type
        self.unique_labels = unique_labels
        
        if unique_labels is not None:
            self.n_unique_labels = len(unique_labels)


def evaluate_by_len(model_generator, input_encoder, output_spec, dataset, start_seq_len = 512, start_batch_size = 32, increase_factor = 2):
    
    assert model_generator.optimizer_weights is None
           
    y_preds = []
    ids_list = []
    
    for len_matching_dataset, seq_len, batch_size in split_dataset_by_len(dataset, start_seq_len = start_seq_len, start_batch_size = start_batch_size,
            increase_factor = increase_factor):

        X, ids, sample_weights = encode_dataset(len_matching_dataset, input_encoder, output_spec,
                seq_len = seq_len, needs_filtering = False)
        
        assert set(np.unique(sample_weights)) <= {0.0, 1.0}
        
        model = model_generator.create_model(seq_len)
        y_pred = model.predict(X, batch_size = batch_size)
        y_preds.append(y_pred)
        for i in ids:
            ids_list.append(i)
    
    y_pred = np.concatenate(y_preds, axis = 0)
 
    return ids_list, y_pred


def encode_dataset(data, input_encoder, output_spec, seq_len = 512, needs_filtering = True, dataset_name = 'Dataset', verbose = True):

    if needs_filtering:
        dataset = filter_dataset_by_len(data, seq_len = seq_len, dataset_name = dataset_name, verbose = verbose)
        seqs = dataset['seq']
        ids = dataset['id']
    else:
        seqs = data['seq']
        ids = data['id']
   
    X = input_encoder.encode_X(seqs, seq_len)
    sample_weigths = encode_Y(output_spec)
   
    return X, ids, sample_weigths


def encode_Y(output_spec):
     
    if output_spec.output_type.is_MLC:
        return np.ones((1, output_spec.n_unique_labels, 1))
    else:
        raise ValueError('Unexpected output type: %s' % output_spec.output_type)


def filter_dataset_by_len(dataset, seq_len = 512, seq_col_name = 'seq', dataset_name = 'Dataset', verbose = True):
    
    max_allowed_input_seq_len = seq_len - ADDED_TOKENS_PER_SEQ
    filtered_dataset = dataset[dataset[seq_col_name].str.len() <= max_allowed_input_seq_len]
    n_removed_records = len(dataset) - len(filtered_dataset)
    
    if verbose:
        log('%s: Filtered out %d of %d (%.1f%%) records of lengths exceeding %d.' % (dataset_name, n_removed_records, len(dataset), 100 * n_removed_records / len(dataset), \
                max_allowed_input_seq_len))
    
    return filtered_dataset
    
    
def split_dataset_by_len(dataset, seq_col_name = 'seq', start_seq_len = 512, start_batch_size = 32, increase_factor = 2):

    seq_len = start_seq_len
    batch_size = start_batch_size
    
    while len(dataset) > 0:
        max_allowed_input_seq_len = seq_len - ADDED_TOKENS_PER_SEQ
        len_mask = (dataset[seq_col_name].str.len() <= max_allowed_input_seq_len)
        len_matching_dataset = dataset[len_mask]
        if len(len_matching_dataset) == 0:
            pass
        else:    
            yield len_matching_dataset, seq_len, batch_size
        dataset = dataset[~len_mask]
        seq_len *= increase_factor
        batch_size = max(batch_size // increase_factor, 1)
