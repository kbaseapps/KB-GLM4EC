from __future__ import absolute_import

import os
import sys
import uuid
import logging
import json
import jinja2
import pandas as pd
from Bio import SeqIO
from kbbasemodules.baseannotationmodule import BaseAnnotationModule
from IPython.display import display
import os
import warnings
import pickle
from .finetuning import OutputType, OutputSpec, evaluate_by_len
from .existing_model_loading import load_pretrained_model
from .model_generation import FinetuningModelGenerator
from .conv_and_global_attention_model import get_model_with_hidden_layers_as_outputs
import gc
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)
        
class GLM4ECModule(BaseAnnotationModule):
    def __init__(self,name,config,module_dir="/kb/module",working_dir=None,token=None,clients={},callback=None):     
        BaseAnnotationModule.__init__(self,name,config,module_dir,working_dir,token,clients,callback)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
    
    #########ACTUAL KBASE API#######################
    def annotate_microbes_with_GLM4EC(self,params):
        self.initialize_call("annotate_microbes_with_GLM4EC",params,True)
        self.validate_args(params,["workspace","references"],{
            "p_threshold":0.5,     # If the probability of an EC number is greater than or equal this threshold return the EC number.
            "suffix":".glm4ec",
            "save_objects":1,
            "create_report":1,
            "return_data_directly":0,
            "save_annotations_to_file":0
        })
        references = self.process_genome_list(params["references"])
        annotated_object_table = []
        all_annotations_output = {}
        
        output = None
        for ref in references:
            all_annotations_output[ref] = self.annotate_kbase_object_utility(ref,params["suffix"],params["p_threshold"],params["save_objects"])
            if params["save_annotations_to_file"] == 1:
                if "filenames" not in output:
                    output["filenames"] = {}
                output["filenames"][ref] = self.working_dir+"/GLM4EC/"+self.object_info_hash[ref][1]+".csv"
                os.makedirs(self.working_dir+"/GLM4EC/", exist_ok=True)
                all_annotations_output[ref]["table"].to_csv(self.working_dir+"/GLM4EC/"+self.object_info_hash[ref][1]+".csv")
            annotated_object_table.append({"Object":self.object_info_hash[ref][1],"Type":self.object_info_hash[ref][2],"Total genes":all_annotations_output[ref]["total_genes"],"Annotated genes":all_annotations_output[ref]["annotated"]})
        
        if params["create_report"] == 1:
            annotated_object_table = pd.DataFrame.from_records(annotated_object_table)
            self.build_dataframe_report(annotated_object_table)
            #Printing genome annotations into a JSON file that can be dynamically loaded into the report
            for ref in all_annotations_output:
                json_str = all_annotations_output[ref]["table"].to_json(orient='records')
                with open(self.working_dir+"/html/"+self.object_info_hash[ref][1]+".json", 'w') as f:
                    f.write('{"data":'+json_str+"}")
            output = self.save_report_to_kbase()
        elif params["return_data_directly"] == 1:
            #Stashing all annotations data into an output datastructure
            for ref in all_annotations_output:
                output["data"][ref] = all_annotations_output[ref]["table"].to_dict('records')
        self.reset_attributes()
        return output
    
    def annotate_proteins_with_GLM4EC(self,params):
        #Initializes and preserves provenance information essential for functions that save objects to KBase
        self.initialize_call("annotate_proteins_with_GLM4EC",params,True)
        #Function ensures required arguments are provided and optional arguments have default values
        params = self.validate_args(params,[],{
            "p_threshold":0.5,     # If the probability of an EC number is greater than or equal this threshold return the EC number.
            "proteins":None,
            "fasta_file":None,
            "return_data_directly":0,
            "save_annotations_to_file":1
        })
        #Check if fasta file and proteins don't exist at the same time
        if params["fasta_file"] and params["proteins"]:
            logging.critical("Both fasta file ({}) and proteins hash ({}) cannot be provided as input".format(params["fasta_file"],params["proteins"]))
            raise AssertionError("Both fasta file ({}) and proteins hash ({}) cannot be provided as input".format(params["fasta_file"],params["proteins"]))

        if params["fasta_file"] and os.path.isfile(params["fasta_file"]):
            #Loading proteins from FASTA file into proteins hash
            params["proteins"] = {}
            for record in SeqIO.parse(str(params["fasta_file"]), "fasta"):
                params["proteins"][record.id] = str(record.seq).upper()
        elif params["proteins"] and len(params["proteins"]) > 0:
            if isinstance(params["proteins"], dict):
                pass
            else:
                raise ValueError('Protein format ({}) is incorrect. Please check your input. correct format: {"protein_id": "protein_sequence"}'.format(type(params["proteins"])))
        else:
            raise KeyError("No input provided. Please provide either fasta file or proteins hash")
        
        annotations = self.annotate_proteins_utility(params["proteins"],params["p_threshold"])
        
        #If file output requested, converting hash to dataframe and saving CSV; it has three columns: "id, EC number, probabiliy of prediction of that EC number"
        output = {}
        if params["save_annotations_to_file"] == 1:
            annotations.to_csv(self.working_dir+"/annotations.tsv") #save the results in a tsv file
            output["filename"] = self.working_dir+"/annotations.tsv"  #file is saving into the data directory of the module
        elif params["return_data_directly"] == 1:
            output["data"] = annotations.to_dict('records')
        self.reset_attributes()
        return output
    
    #########UTILITY FUNCTIONS#######################
    def annotate_kbase_object_utility(self,reference,suffix,threshold,save_objects):
        sequence_list = self.object_to_proteins(reference)
        protein_hash = {}
        total_genes = 0
        for item in sequence_list:
            total_genes += 1
            protein_hash[item[0]] = item[1]
        
        annotations = self.annotate_proteins_utility(protein_hash,threshold)
        
        anno_ont_input = {}
        anno_count = 0
        for index, row in annotations.iterrows():
            anno_count += 1
            if row["id"] not in anno_ont_input:
                anno_ont_input[row["id"]] = {"EC":{}}
            anno_ont_input[row["id"]]["EC"][row["function"]] = {"scores":{"probability":row["score"]}}
        
        if save_objects == 1:
            self.add_annotations_to_object(reference,suffix,anno_ont_input)
        return {"table":annotations,"total_genes":total_genes,"annotated":anno_count}
                 
    
    def annotate_proteins_utility(self,proteins,threshold):
        
        def is_sequence_constructed_from_nucleotides(sequence, nucleotides):
            return all(char in nucleotides for char in sequence)
    
        output = []
        nucleotides = 'ACTG' #Nucleotides list; to check if the sequence is DNA or not
        model_path = self.config["data"]+'/fine_tuned_fliped_common_2048_two.pkl'  #finetuned model path
        dict_path = self.module_dir+'/data/dict_annotation_fliped_common_2048_two.csv'  #EC numbers and their corresponding orders in the model 
        pretrained_model_generator, input_encoder = load_pretrained_model(self.config["data"]+'/pretrained_model2.pkl')   #load pretrained model2 and its input encoder
        
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
         
        #value = list(proteins.values())
        list_of_invalid_proteins = []
        
        # raise error if a sequence in proteins dictionary is a nucleotide sequence
        for key, value in proteins.items():
            if is_sequence_constructed_from_nucleotides(value, nucleotides):
                list_of_invalid_proteins.append(key)
                logging.warning("The sequence of protein {} is a nucleotide sequence.".format(key))
        
        # remove invalid proteins from the dictionary
        for key in list_of_invalid_proteins:
            del proteins[key]
        
        ids_list, y_pred = evaluate_by_len(model_generator, input_encoder, OUTPUT_SPEC, 
                        proteins, start_seq_len = 512, start_batch_size = 32)      
        
        for i in range(y_pred.shape[0]):
            pred_annotation = []
            for j in range(y_pred.shape[1]):
                if y_pred[i, j] >= threshold: #If the probability of an EC number is greater than or equal this threshold return the EC number.
                    pred_annotation.append((dict_annotation.iloc[j, 0], y_pred[i, j]))
            ecs = list(set(pred_annotation))
            for item in ecs:
                output.append({"id":ids_list[i],"function":item[0],"scoretype":"probability","score":item[1]})
            
            gc.collect()  # garbage collector; release the memory for the next protein

        output = pd.DataFrame.from_records(output)
        return output
    
    
    def build_dataframe_report(self,table):        
        context = {
            "initial_genome":table.iloc[0]["Object"]
        }
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.module_dir+"/data/"),
            autoescape=jinja2.select_autoescape(['html', 'xml']))
        html = env.get_template("ReportTemplate.html").render(context)
        os.makedirs(self.working_dir+"/html", exist_ok=True)
        with open(self.working_dir+"/html/index.html", 'w') as f:
            f.write(html)
        #Creating data table file
        for index, row in table.iterrows():
            table.at[index,'Object'] = '<a href="javascript:view_annotations('+"'"+row["Object"]+"'"+')">'+row["Object"]+"</a>"
        json_str = '{"data":'+table.to_json(orient='records')+'}'
        with open(self.working_dir+"/html/data.json", 'w') as f:
            f.write(json_str)
        