/*
A KBase module: GLM4EC
*/

module GLM4EC {
	typedef structure {
		string workspace;
		list<string> references;
		float p_threshold;
		string suffix;
		int save_objects;
		int create_report;
		int return_data_directly;
		int save_annotations_to_file;
    } AnnotateMicrobesParams;    

	typedef structure {
		string output_workspace;
        string report_name;
        string report_ref;
        UnspecifiedObject data;
        mapping<string reference,string filename> filenames; 
    } AnnotateMicrobesResults;

    /*
        Annotates KBase objects adding the functions into the object datastructure
    */
    funcdef annotate_microbes_with_GLM4EC(AnnotateMicrobesParams params) returns (AnnotateMicrobesResults output) authentication required;

	typedef structure {
		mapping<string gene_id,string sequence> proteins;
		float p_threshold;
		string fasta_file;
		int return_data_directly;
		int save_annotations_to_file;
    } AnnotateProteinsParams;    

	typedef structure {
		string filename;
		UnspecifiedObject data;
    } AnnotateProteinsResults;

    /*
        Annotates protein sequences either provided in a hash or in an input FASTA file, and saves results either in output hash or TSV file
    */
    funcdef annotate_proteins_with_GLM4EC(AnnotateProteinsParams params) returns (AnnotateProteinsResults output) authentication required;
};
