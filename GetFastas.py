from typing import List, Optional, Tuple
from Bio import Entrez, SeqIO
from tqdm import tqdm

def fetch_gene_sequences(
    species_list: List[str],
    gene_name: str,
    email: str,
    min_length: int = 0,
    max_length: int = 1_000_000,
    prompt_template: Optional[str] = None,
    template_values: Optional[Tuple] = None,
    verbose: bool = False,
    skip_errors: bool = False,
    skip_warnings: bool = False,
    **kwargs,
) -> None:
    """
    Fetches gene sequences for a given list of species based on a custom prompt.
    
    Parameters:
    - species_list: A list of species names for which the gene sequences are to be fetched.
    - gene_name: The name of the gene to fetch sequences for.
    - email: Email address to use with the Entrez API for tracking purposes.
    - min_length: The minimum length of the gene sequences to be fetched. Defaults to 0.
    - max_length: The maximum length of the gene sequences to be fetched. Defaults to 1000000.
    - prompt_template: An optional string to customize the prompt for fetching gene sequences.
    - template_values: An optional tuple of values to format the `prompt_template` string.
    - verbose: If True, prints additional information. Defaults to False.
    - skip_errors: If True, skips adding sequences that could not be obtained. Defaults to False.
    - skip_warnings: If True, skips adding sequences where species name does not match header. Defaults to False.
    """
    Entrez.email = email  # Set the Entrez API email

    found_species, unfound_species, warnings = [], [], ""
    fasta_sequences, used_species = [], []

    for species in tqdm(species_list):
        search_query = construct_search_query(species, gene_name, min_length, max_length, prompt_template, template_values)
        sequence_id, fasta_sequence = fetch_sequence(search_query, skip_errors, **kwargs)

        if sequence_id and fasta_sequence:
            fasta_sequences.append(fasta_sequence)
            report_sequence_found(species, gene_name, sequence_id, fasta_sequence, verbose)
            found_species.append((species, fasta_sequence.splitlines()[0].split(" ")[0][1:]))
            used_species.append(species)

            if species.lower() not in fasta_sequence.lower() and not skip_warnings:
                warning = generate_warning(species, fasta_sequence)
                tqdm.write(warning)
                warnings += warning + "\n"
        else:
            handle_not_found(species, gene_name, unfound_species, fasta_sequences, skip_errors)

    finalize_report(found_species, unfound_species, warnings, fasta_sequences, used_species, skip_errors, skip_warnings)

def construct_search_query(species: str, gene_name: str, min_length: int, max_length: int, prompt_template: Optional[str], template_values: Optional[Tuple]) -> str:
    """
    Constructs the search query based on the provided parameters.
    """
    if prompt_template and template_values:
        search_query = prompt_template.format(*template_values, species=species, gene_name=gene_name, min_length=min_length, max_length=max_length)
    else:
        search_query = f"{species}[Organism] AND {gene_name}[All Fields] AND {min_length}:{max_length}[Sequence Length]"
    return search_query

def fetch_sequence(search_query: str, skip_errors: bool, **kwargs) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the sequence for a given search query. Returns a tuple of sequence_id and fasta_sequence.
    """
    try:
        search_handle = Entrez.esearch(db="nucleotide", term=search_query, sort = "relevance", **kwargs)
        search_results = Entrez.read(search_handle)
        search_handle.close()

        if search_results["IdList"]:
            sequence_id = search_results["IdList"][0]
            fetch_handle = Entrez.efetch(db="nucleotide", id=sequence_id, rettype="fasta", retmode="text")
            fasta_sequence = fetch_handle.read()
            fetch_handle.close()
            return sequence_id, fasta_sequence
    except Exception as e:
        if not skip_errors:
            tqdm.write(f"Error fetching sequence for query: {search_query}. Error: {e}")
    return None, None

def report_sequence_found(species: str, gene_name: str, sequence_id: str, fasta_sequence: str, verbose: bool) -> None:
    """
    Reports a found sequence.
    """
    if verbose:
        print(f"For {species} {gene_name}, found {sequence_id} with length {len(fasta_sequence)}.")

def generate_warning(species: str, fasta_sequence: str) -> str:
    """
    Generates a warning message for sequences where the species name does not match the header.
    """
    return f"WARNING: Full/Same name for {species} not found in fasta header, check it manually!"

def handle_not_found(species: str, gene_name: str, unfound_species: List[str], fasta_sequences: List[str], skip_errors: bool) -> None:
    """
    Handles species for which no sequences were found.
    """
    unfound_species.append(species)
    if not skip_errors:
        fasta_sequences.append(f">{species} {gene_name} not found.\n\n")

def finalize_report(found_species: List[str], unfound_species: List[str], warnings: str, fasta_sequences: List[str], used_species: List[str], skip_errors: bool, skip_warnings: bool) -> None:
    """
    Finalizes the report, printing found and unfound species, and saving outputs.
    """
    print(f"Found species: {found_species}\n")
    print(f"Unfound species: {unfound_species}\n")
    if warnings:
        print(warnings)

    with open("output.fasta", "w") as file:
        file.writelines(fasta_sequences)

    if skip_errors or skip_warnings:
        with open("used_species.txt", "w") as file:
            file.writelines(f"{species}\n" for species in used_species)

if __name__ == "__main__":
    species_names = ["Homo sapiens", "Mus musculus", "Canis lupus"]
    fetch_gene_sequences(species_names, "BRCA1", "example@email.com", 900, 1300, verbose=True, skip_errors=True, skip_warnings=False)
