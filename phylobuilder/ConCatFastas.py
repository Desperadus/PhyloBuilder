import argparse
from Bio import SeqIO


def read_species_list(species_list_file):
    with open(species_list_file, "r") as slf:
        species_names = [line.strip() for line in slf.readlines()]
    return species_names


def replace_headers_and_concatenate(fasta_files, species_list, output_file):
    species_names = read_species_list(species_list)
    sequences = []

    for fasta_file in fasta_files:
        batch = []
        for i, record in enumerate(SeqIO.parse(fasta_file, "fasta")):
            batch.append(str(record.seq))
            if i >= len(species_names):
                raise ValueError(
                    f"Number of sequences in {fasta_file} is greater than the number of species in {species_list}."
                )
        sequences.append(batch)

    concatenated_seqs = []
    for i in range(len(species_names)):
        concatenated_seq = "".join([seq[i] for seq in sequences])
        concatenated_seqs.append(concatenated_seq)

    with open(output_file, "w") as of:
        result = ""
        with open(output_file, "w") as of:
            for i, species in enumerate(species_names):
                result += f">{species}\n{concatenated_seqs[i]}\n\n"
            of.write(result)


def main():
    parser = argparse.ArgumentParser(
        description="Replace FASTA headers with species names and concatenate files."
    )
    parser.add_argument(
        "-f", "--fasta_files", nargs="+", help="Input FASTA files.", required=True
    )
    parser.add_argument(
        "-s",
        "--species_list",
        required=True,
        help="File containing species names, one per line.",
    )
    parser.add_argument("-o", "--output_file", required=True, help="Output FASTA file.")

    args = parser.parse_args()

    replace_headers_and_concatenate(
        args.fasta_files, args.species_list, args.output_file
    )


if __name__ == "__main__":
    main()
