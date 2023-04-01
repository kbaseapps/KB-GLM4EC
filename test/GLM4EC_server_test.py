# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from GLM4EC.GLM4ECImpl import GLM4EC
from GLM4EC.GLM4ECServer import MethodContext
from installed_clients.authclient import KBaseAuth as _KBaseAuth
from installed_clients.WorkspaceClient import Workspace


PROTEINS = {"A0A820Q4W8":"MNININSSLKKLICNARMGKLRQKEREVAARASAAEIYYVSQRTLRYTIRNPVLFLAQVVVAIVLGLVVGFVFNSLEKSIDPGIQNRLGAIFFMVVSQTLGTITSLEPLIKKRVSYIHKTISAYYRTTTFFIVKVICDVLSMRIVSSILFSLIAYCMTGLEQSAG", "A0A7Z7NP06":"MASQSPAPQRADLLFRHATVVDGTGATRRTADVAVTGDRIIAVGDCAGIAADHTVDCSGRVLAPGFIDAHTHDDGYLLVHRDMTPKVSQGITTVVTGNCGISVAPLVSGAPPQPLDLLGPPALFRFDTFAQWLDALRAAPANVNVVPLLGHSTLRVRAMPELDRPANDAEIAAMRDEVRLAMEAGAFGVSTGTFYPPAAAATEAEIVAVCGPVRSHGGIYSTHLRDETDAIVPSIEEALRIGRALDCPVVFSHHKVAGKRNHGRSVETLGLLAEAARLQPLCLDCHPYPATSTMLRLDRVRQSTRTLITWSTGYPAAGGRDFHELMQELGLDEEALLARLRPAAAIYFIMDERDVARIAQFPLTIFGSDGLPFDPRPHPRQWGTFPRILARMVREDQLMTLEAAIHKMSGLAAQQYGLEDRGRIAPGAFADLVLFDAGRVQDRATFEDPLQLSTGIDGVWVNGAQVWQQSARDGAGDTAGSALPAFSGRVLRRLASDNPSAARR"}
BAD_PROTEINS = ["MVIVLSRTIRAIAVDVDGTLTDTSRKVSCPAIEALRRQADKGIIVMLVTGNVLPIAYALRHYLGMNGPVIAENGGIVYHDEHVHYLSSKDEPQKAFDQLSKSMKVERIFSDRWRETEIAIRPTYDIELIRKHVRGFDVKVLPSGWAHHLMHKDTDKAKALKWICDNWLRIDMEHVAAIGDSDNDYRMIEIAGFGATPANGSQKCKERADYVASRPYGDGIVEILRVLGLEP", "MNININSSLKKLICNARMGKLRQKEREVAARASAAEIYYVSQRTLRYTIRNPVLFLAQVVVAIVLGLVVGFVFNSLEKSIDPGIQNRLGAIFFMVVSQTLGTITSLEPLIKKRVSYIHKTISAYYRTTTFFIVKVICDVLSMRIVSSILFSLIAYCMTGLEQSAG", "MASQSPAPQRADLLFRHATVVDGTGATRRTADVAVTGDRIIAVGDCAGIAADHTVDCSGRVLAPGFIDAHTHDDGYLLVHRDMTPKVSQGITTVVTGNCGISVAPLVSGAPPQPLDLLGPPALFRFDTFAQWLDALRAAPANVNVVPLLGHSTLRVRAMPELDRPANDAEIAAMRDEVRLAMEAGAFGVSTGTFYPPAAAATEAEIVAVCGPVRSHGGIYSTHLRDETDAIVPSIEEALRIGRALDCPVVFSHHKVAGKRNHGRSVETLGLLAEAARLQPLCLDCHPYPATSTMLRLDRVRQSTRTLITWSTGYPAAGGRDFHELMQELGLDEEALLARLRPAAAIYFIMDERDVARIAQFPLTIFGSDGLPFDPRPHPRQWGTFPRILARMVREDQLMTLEAAIHKMSGLAAQQYGLEDRGRIAPGAFADLVLFDAGRVQDRATFEDPLQLSTGIDGVWVNGAQVWQQSARDGAGDTAGSALPAFSGRVLRRLASDNPSAARR"]
FASTA_FILE = '../data/sample.fasta'
DNA_SEQ = {"A0A7J3ALL0":"tgatcggtaattgtttgagtagtctaggcacagtgccgctgttaaacatagacatcttcccgcattcatgttcccgacaaattgagcactggatacatgacagtttatctcacgaggccatactcagtcgggccccgaacgcattgatcgaggttgtcgaaacacctttcgcctgcccagcgtcggttccaagggacgaacgcccataggcgcttcgtcccacaatgcccgcagagcgtaatgtgccttagactcactggtggatataacagaaaacactgggtgcgggcaacgtaggtt"}
 

class GLM4ECTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('GLM4EC'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'GLM4EC',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = GLM4EC(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')
            
            
    
    #You can comment the test_GLM4EC function and then uncomment one of the tests in the following function.
    
    def test_GLM4EC_bad_params(self):
        '''
        # missing params
        with self.assertRaises(KeyError, msg="No input provided. Please provide either fasta file or proteins hash"):
            self.serviceImpl.annotate_proteins(self.ctx, {'workspace_name': self.wsName})
        '''
        
        '''
        # get both proteins and fasta file at the same time
        with self.assertRaises(AssertionError, msg='Cannot get both proteins and fasta file. Please choose one.'):
            self.serviceImpl.annotate_proteins(self.ctx, {'workspace_name': self.wsName,
                                                            'proteins': PROTEINS,
                                                            'fasta_file': FASTA_FILE, "file_output":True})
        '''
        
        '''
        # incorrect protein format
        with self.assertRaises(ValueError, msg='Protein format is incorrect. Please check your input. correct format: {"protein_id": "protein_sequence"}'):
            self.serviceImpl.annotate_proteins(self.ctx, {'workspace_name': self.wsName,
                                                    'proteins': BAD_PROTEINS})
        '''
        
        '''
        # not protein sequence
        with self.assertRaises(AssertionError, msg="This is a sequence of nucleotides! Please search an aminoacid sequence."):
            self.serviceImpl.annotate_proteins(self.ctx, {'workspace_name': self.wsName,
                                                    'proteins': DNA_SEQ})
        '''   
    
    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_GLM4EC(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        params = {'workspace_name': self.wsName,
                    'proteins': PROTEINS, "file_output":True}
        
        ret = self.serviceImpl.annotate_proteins(self.ctx, params)
        self.assertTrue(len(ret))
    


