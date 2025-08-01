# Take Home Exercise - Aganitha

This CLI tool fetches PubMed papers with at least one author affiliated with a pharmaceutical or biotech company. It uses the PubMed API and outputs the results in CSV format.

## Usage

```bash
poetry run get-papers-list "cancer immunotherapy" -n 10 -f results.csv
