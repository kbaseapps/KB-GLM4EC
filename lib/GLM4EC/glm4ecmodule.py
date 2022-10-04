from __future__ import absolute_import

import os
import sys
import uuid
import logging
import json
import pandas as pd
from GLM4EC.basemodule import BaseModule

logger = logging.getLogger(__name__)

class GLM4ECModule(BaseModule):
    def __init__(self,name,ws_client,working_dir,module_dir,config):
        BaseModule.__init__(self,name,ws_client,working_dir,config)
        self.module_dir = module_dir
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        
    def annotate_proteins(self,params):
        self.initialize_call("annotate_proteins",params,True)
        output = {"annotation":{}}
        for gene_id in params["proteins"]:
            print(params["proteins"][gene_id])
        #Code for method goes here
        return output