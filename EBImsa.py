import argparse
import os
import requests
import sys
import time
import webbrowser

def submit_alignment_job(fasta_sequence, email: str, algorithm: str):
    """Submit the alignment job to EMBL-EBI and return the job ID."""
    url = f"http://www.ebi.ac.uk/Tools/services/rest/{algorithm}/run/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "sequence": fasta_sequence,
        "email": email,
        "order": "input",
    }

    response = requests.post(url, headers=headers, data=data)
    if response.ok:
        return response.text
    else:
        raise Exception(f"Error submitting job: {response.content.decode()}")


def check_job_status(job_id, algorithm: str):
    """Check the status of the submitted job."""
    status_url = f"http://www.ebi.ac.uk/Tools/services/rest/{algorithm}/status/{job_id}"
    response = requests.get(status_url)
    return response.text


def download_alignment(job_id, output_file, algorithm: str):
    """Download the alignment result."""
    result_url = (
        f"http://www.ebi.ac.uk/Tools/services/rest/{algorithm}/result/{job_id}/fa"
    )

    response = requests.get(result_url)
    if response.ok:
        with open(output_file, "w") as file:
            file.write(response.text)
        print(f"Alignment saved to {output_file}")
    else:
        raise Exception(
            f"Error downloading alignment: {response.content.decode()}")


def load_fasta_file(file_path):
    """Load the FASTA file from the given path."""
    with open(file_path, "r", encoding="utf-8-sig") as file:
        fasta_sequences = file.read()
    return fasta_sequences


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Submit a multiple sequence alignment job."
    )
    parser.add_argument(
        "-f", "--file", required=True, help="Path to the input FASTA file."
    )
    parser.add_argument(
        "-e",
        "--email",
        required=True,
        help="Email address to use with the EMBL-EBI service.",
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=["clustalo", "mafft", "muscle",
                 "tcoffee", "emboss_cons", "kalign"],
        default="clustalo",
        help="Alignment algorithm to use.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed job status messages.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    fasta_sequences = load_fasta_file(args.file)
    base_name = os.path.basename(args.file).rpartition(".")[0]
    output_file_path = f"{base_name}_{args.algorithm}.fasta"

    try:
        job_id = submit_alignment_job(
            fasta_sequences, args.email, args.algorithm)
        print(f"Job submitted. Job ID: {job_id}")
        print(f"You can check it at: http://www.ebi.ac.uk/jdispatcher/msa/{args.algorithm}/summary?jobId={job_id}")

        while check_job_status(job_id, args.algorithm) != "FINISHED":
            if args.verbose:
                print("Checking job status...")
            time.sleep(10)

        download_alignment(
            job_id, output_file=output_file_path, algorithm=args.algorithm
        )
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
