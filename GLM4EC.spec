/*
A KBase module: GLM4EC
*/

module GLM4EC {
	typedef structure {
		mapping<string gene_id,string sequence> proteins;
		string fasta_file;
		int file_output;
    } AnnotateProteinsParams;    

	typedef structure {
		string filename;
		mapping<string gene_id,list<string> functions> annotations;
    } AnnotateProteinsResults;

    /*
        Annotates protein sequences either provided in a hash or in an input FASTA file, and saves results either in output hash or TSV file
    */
    funcdef annotate_proteins(AnnotateProteinsParams params) returns (AnnotateProteinsResults output) authentication required;

};
