# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import sys
import json
from os.path import exists
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
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/KB-GLM4EC.git"
    GIT_COMMIT_HASH = "HEAD"

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
        self.glm4ec = GLM4ECModule("GLM4EC",self.wsclient,config['scratch'],"/kb/module",self.config)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def annotate_proteins(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of type "AnnotateProteinsParams" ->
           structure: parameter "proteins" of mapping from String to String
        :returns: instance of type "AnnotateProteinsResults" -> structure:
           parameter "annotations" of mapping from String to list of String
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
