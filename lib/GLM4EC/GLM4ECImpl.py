# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import sys
from GLM4EC.glm4ecmodule import GLM4ECModule
from installed_clients.WorkspaceClient import Workspace
#END_HEADER


class GLM4EC:
    '''
    Module Name:
    GLM4EC

    Module Description:
    A KBase module: GLM4EC
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.1.0"
    GIT_URL = "https://github.com/kbaseapps/KB-GLM4EC.git"
    GIT_COMMIT_HASH = "2472d475ab13696092402949052a1b81a6d3c9db"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.token = os.environ['KB_AUTH_TOKEN']
        self.wsclient = Workspace(self.config["workspace-url"], token=self.token)
        config["version"] = self.VERSION
        self.glm4ec = GLM4ECModule("GLM4EC",config['scratch'],"/kb/module",self.config)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def annotate_proteins(self, ctx, params):
        """
        Annotates protein sequences either provided in a hash or in an input FASTA file, and saves results either in output hash or TSV file
        :param params: instance of type "AnnotateProteinsParams" ->
           structure: parameter "proteins" of mapping from String to String,
           parameter "fasta_file" of String, parameter "file_output" of Long
        :returns: instance of type "AnnotateProteinsResults" -> structure:
           parameter "filename" of String, parameter "annotations" of mapping
           from String to list of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN annotate_proteins
        output = self.glm4ec.annotate_proteins(params)
        #END annotate_proteins

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method annotate_proteins return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
