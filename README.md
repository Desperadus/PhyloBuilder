# PhyloBuilder
Python package to help automate process of building a phylogenetic tree by downloading relevant fasta files, doing MSA and then constructing the tree

## Installation

Before using the tools, ensure you have Python 3.9+ and git installed on your system. Then, install the toolkit using pip:

```bash
pip install git+https://github.com/Desperadus/PhyloBuilder.git
```

## Tools

You should have you species list file newline seperated with a species name on each row.
Example of species list is located in `examples/species_list.txt` which can be used for obtaining the fastas.

### GetFastas

Fetch gene sequences for a list of species from the specified database.

#### Usage

```bash
GetFastas -f <file> -g <gene> -e <email> [options]
```

- `-f`, `--file`: File containing species names, one per line. (required)
- `-o`, `--output`: Output file to save the fetched sequences. Default is `output.fasta`.
- `-g`, `--gene`: Gene name to fetch sequences for. (required)
- `-e`, `--email`: Email address to use with the Entrez API for tracking purposes. (required)
- `-min`, `--min_length`: Minimum length of gene sequences to fetch. Defaults to 0.
- `-max`, `--max_length`: Maximum length of gene sequences to fetch. Defaults to 1,000,000.
- `-v`, `--verbose`: Prints additional information if set.
- `-se`, `--skip_errors`: Skips adding sequences that could not be obtained if set.
- `-sw`, `--skip_warnings`: Skips adding sequences where species name does not match header if set.

If either -se, -sw or both flags are used then a file called *used_species.txt* is generated of species that were added to the resulting .fasta file.

If you dont specify these flags and fasta for certain species of desired gene could not be obtained you will need to add their fastas to the file manualy.
Empty fasta header will be created in the output file where you should place it so the order remains the same as in the input file.

Be careful and inspect the warnings manualy.

### EBImsa

Submit a multiple sequence alignment job to the EMBL-EBI service.

#### Usage

```bash
EBImsa -f <file> -e <email> [options]
```

- `-f`, `--file`: Path to the input FASTA file. (required)
- `-e`, `--email`: Email address to use with the EMBL-EBI service. (required)
- `-a`, `--algorithm`: Alignment algorithm to use. Choices are `clustalo`, `mafft`, `muscle`, `tcoffee`, `emboss_cons`, `kalign`. Default is `clustalo`.
- `-v`, `--verbose`: Print detailed job status messages if set.

resulting file is saved as <input_file_name>_<algorithm>.fasta

### ConCatFastas

Replace FASTA headers with species names and concatenate files. Note that the species in FASTA files and also in species list must be in the same order so they can be concatenated correctly.
Can also be used only for changing the fasta headers.

#### Usage

```bash
ConCatFastas -f <fasta_files> -s <species_list> -o <output_file>
```

- `-f`, `--fasta_files`: Input FASTA files. (required)
- `-s`, `--species_list`: File containing species names, one per line. (required)
- `-o`, `--output_file`: Output file name. (required)

## Support

For issues, questions, or contributions, please refer to the project's GitHub issues or contact me at `tomgolf.jelinek@gmail.com`.

## License
GPL-3.0
