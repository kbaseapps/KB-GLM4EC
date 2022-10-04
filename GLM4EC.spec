/*
A KBase module: GLM4EC
*/

module GLM4EC {
	typedef structure {
		mapping<string gene_id,string sequence> proteins;
    } AnnotateProteinsParams;    

	typedef structure {
		mapping<string gene_id,list<string> functions> annotations;
    } AnnotateProteinsResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef annotate_proteins(AnnotateProteinsParams params) returns (AnnotateProteinsResults output) authentication required;

};
