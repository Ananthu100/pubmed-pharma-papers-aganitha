# PubMed Pharma Papers Fetcher

This project fetches research papers from PubMed based on a user-defined query and extracts articles with at least one author affiliated with a pharmaceutical or biotech company.

---

## 📁 Code Organization

pubmedfetcher/
└── main.py # Entry point for fetching and filtering papers
pyproject.toml # Poetry configuration for dependencies and packaging
poetry.lock # Poetry lock file
README.md # Project documentation
results.csv # Output file with filtered paper details 

---

## 🧪 Features

- Accepts full PubMed query syntax (e.g., `"cancer immunotherapy 2023[PDAT]"`)
- Extracts:
  - PubMed ID
  - Title
  - Publication Date
  - Non-academic Author Name
  - Company Affiliation
  - Corresponding Author Email
- Filters authors affiliated with pharma/biotech institutions based on a keyword list
- Outputs to CSV file or prints to console
- Debug mode to view detailed processing logs

---

## ⚙️ Installation

Make sure you have Python (≥3.9 recommended) and [Poetry](https://python-poetry.org/) installed.

### 1. Clone the Repository
```bash
git clone https://github.com/Ananthu100/pubmed-pharma-papers-aganitha.git
cd pubmed-pharma-papers-aganitha
2. Install Dependencies
poetry install

Run the tool with a query:
poetry run python pubmedfetcher/main.py "cancer immunotherapy 2023[PDAT]" -n 25 -f results.csv -d

Tools & Libraries Used
requests – for making API calls
pandas – for tabular data handling and CSV export
Poetry – for dependency management and packaging
PubMed E-Utilities API – for querying and retrieving biomedical articles

Notes:
Make sure you are connected to the internet for API access.
The tool uses basic keyword matching for pharma/biotech affiliations.
