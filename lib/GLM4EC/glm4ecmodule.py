from __future__ import absolute_import

import os
import sys
import uuid
import logging
import json
import pandas as pd
from Bio import SeqIO
from .basemodule import BaseModule
from IPython.display import display
import os
import warnings
import pickle
from .finetuning import OutputType, OutputSpec, evaluate_by_len
from .existing_model_loading import load_pretrained_model
from .tokenization import ADDED_TOKENS_PER_SEQ
from .model_generation import FinetuningModelGenerator
import numpy as np
from .conv_and_global_attention_model import get_model_with_hidden_layers_as_outputs
import gc

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class GLM4ECModule(BaseModule):
    def __init__(self,name,working_dir,module_dir,config):
        BaseModule.__init__(self,name,None,working_dir,config)
        self.module_dir = module_dir
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
    
    #Most basic utility function that annotates input protein sequences    
    def annotate_proteins(self,params):
    

        #Initializes and preserves provenance information essential for functions that save objects to KBase
        self.initialize_call("annotate_proteins",params,True)
        #Function ensures required arguments are provided and optional arguments have default values
        params = self.validate_args(params,[],{
            "p_threshold":0.5,     # If the probability of an EC number is greater than or equal this threshold return the EC number.
            "proteins":None,
            "fasta_file":None,
            "file_output":True
        })
        output = {"annotation":{}}
        if params["fasta_file"] and os.path.isfile(params["fasta_file"]):
            #Loading proteins from FASTA file into proteins hash
            params["proteins"] = {}
            for record in SeqIO.parse(str(params["fasta_file"]), "fasta"):
                params["proteins"][record.id] = str(record.seq).upper()
        elif params["proteins"] and len(params["proteins"]) > 0:
            pass
        else:
            logging.critical("Either a fasta file or proteins hash must be provided as input")
        #######################################
        #Code for method goes here
        
        nucleotides = 'ACTG' #Nucleotides list; to check if the sequence is DNA or not
        model_path = '../data/fine_tuned_fliped_common_2048_two.pkl'  #finetuned model path
        dict_path = '../data/dict_annotation_fliped_common_2048_two.csv'  #EC numbers and their corresponding orders in the model 
        pretrained_model_generator, input_encoder = load_pretrained_model()   #load pretrained model2 and its input encoder
        
        with open(model_path, 'rb') as f:
                model_weights, optimizer_weights = pickle.load(f)   #load weights of finetuned model
            
        dict_annotation = pd.read_csv(dict_path, header=None)
        UNIQUE_LABELS = dict_annotation.iloc[:, 0].tolist()  #3332 unique EC numbers are covered by current model.

        OUTPUT_TYPE = OutputType(False, 'MLC') #MLC: multi-label classification

        OUTPUT_SPEC = OutputSpec(OUTPUT_TYPE, UNIQUE_LABELS) 

        #  Load the finetune model generator
        model_generator = FinetuningModelGenerator(
                        pretrained_model_generator, OUTPUT_SPEC, pretraining_model_manipulation_function = \
                        get_model_with_hidden_layers_as_outputs, dropout_rate = 0.5,
                        model_weights=model_weights
                        )
        # Create the finetune model                
        fine_tuned_model = model_generator.create_model(512)

        for id in params['proteins']:
            # A check to make sure the sequences are amino acids and not nucleotides
            if all(i in nucleotides for i in params["proteins"][id]) == False:

                # Predict the EC numbers
                y_pred = evaluate_by_len(fine_tuned_model, input_encoder, OUTPUT_SPEC, [params["proteins"][id]],
                                start_seq_len = 512, start_batch_size = 32)      
                pred_annotation = []
                for i in range(y_pred.shape[0]):
                    for j in range(y_pred.shape[1]):
                        if y_pred[i, j] >= params['p_threshold']: #If the probability of an EC number is greater than or equal this threshold return the EC number.
                            pred_annotation.append((dict_annotation.iloc[j, 0], y_pred[i, j]))
                if pred_annotation == []:
                   # if the model cannot predict any EC number for a protein, call the following log
                   logging.critical("Sorry! No EC numbers are found for your input sequence with id:{0}.".format(id))
                else:
                    output["annotation"][id] = list(set(pred_annotation))
            else:
                logging.critical("This is a sequence of nucleotides! Please search an aminoacid sequence.")
            
            gc.collect()  # garbage collector; release the memory for the next protein

        print(output)        

        #######################################
        #If file output requested, converting hash to dataframe and saving CSV; it has three columns: "id, EC number, probabiliy of prediction of that EC number"
        if params["file_output"]:
            data = {"id":[],"function":[], "probability":[]}
            for gene_id in output["annotation"]:
                for func in output["annotation"][gene_id]:
                    #Note - multifunctional genes are handled by having multiple lines in the file
                    data["id"].append(gene_id)
                    data["function"].append(func[0]) # EC number 
                    data["probability"].append(func[1]) # probability of the predicted EC number 
            results = pd.DataFrame(data)
            results.to_csv(self.working_dir+"/annotations.tsv") #save the results in a tsv file
            output["filename"] = self.working_dir+"/annotations.tsv"  #file is saving into the data directory of the module
            del output["annotation"] #removing annotation hash from output
        return output 