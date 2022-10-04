from __future__ import absolute_import

import os
import sys
import uuid
import logging
import json
import pandas as pd
from Bio import SeqIO
from GLM4EC.basemodule import BaseModule

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
            "proteins":None,
            "fasta_file":None,
            "file_output":False
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
        #Probably should include a check to make sure the sequences are amino acids and not nucleotides
        #######################################
        #If file output requested, converting hash to dataframe and saving CSV
        if params["file_output"]:
            data = {"id":[],"function":[]}
            for gene_id in output["annotation"]:
                for func in output["annotation"]:
                    #Note - multifunctional genes are handled by having multiple lines in the file
                    data["id"].append(gene_id)
                    data["function"].append(func)
            results = pd.DataFrame(data)
            results.to_csv(self.working_dir+"/annotations.tsv")
            output["filename"] = self.working_dir+"/annotations.tsv"
            del output["annotation"]
        return output