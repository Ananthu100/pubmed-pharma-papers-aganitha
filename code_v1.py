import argparse
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import re
import time
import sys

PHARMA_KEYWORDS = [
    "pharma", "biotech", "biosciences", "therapeutics", "diagnostics",
    "life sciences", "laboratories", "inc", "corp", "ltd", "gmbh",
    "pharmaceutical", "genomics", "healthcare", "bioscience", "biopharma"
]

def is_pharma_affiliation(aff):
    return any(kw in (aff or "").lower() for kw in PHARMA_KEYWORDS)

def extract_email(text):
    if not text:
        return ""
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""

def fetch_pmids(query, retmax=100, debug=False):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json"
    }
    if debug:
        print(f"[DEBUG] ESearch URL: {url}")
        print(f"[DEBUG] ESearch Params: {params}")
    response = requests.get(url, params=params)
    response.raise_for_status()
    pmids = response.json()["esearchresult"]["idlist"]
    if debug:
        print(f"[DEBUG] Found {len(pmids)} articles for query.")
    return pmids

def fetch_article_xml(pmids, debug=False):
    articles = []
    batch_size = 50
    for i in range(0, len(pmids), batch_size):
        batch_ids = ",".join(pmids[i:i+batch_size])
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {"db": "pubmed", "id": batch_ids, "retmode": "xml"}
        if debug:
            print(f"[DEBUG] Fetching {len(batch_ids.split(','))} articles: {params['id']}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles.append(response.text)
        time.sleep(0.34)  # to comply with NCBI usage policy
    return articles

def parse_articles(xml_strings, debug=False):
    results = []
    for xml_str in xml_strings:
        root = ET.fromstring(xml_str)
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            title = art.findtext(".//ArticleTitle")
            pub_date = (
                art.findtext(".//PubDate/Year") or
                art.findtext(".//ArticleDate/Year") or
                ""
            )
            non_acad_author = ""
            company_aff = ""
            corr_email = ""
            authors = art.findall(".//AuthorList/Author")
            for a in authors:
                affs = a.findall(".//AffiliationInfo/Affiliation")
                for aff in affs:
                    aff_txt = aff.text or ""
                    if is_pharma_affiliation(aff_txt) and not company_aff:
                        company_aff = aff_txt
                        fname = a.findtext("ForeName") or ""
                        lname = a.findtext("LastName") or ""
                        non_acad_author = f"{fname} {lname}".strip()
                        email = extract_email(aff_txt)
                        if email:
                            corr_email = email
            if company_aff:
                results.append({
                    "PubmedID": pmid or "",
                    "Title": title or "",
                    "Publication Date": pub_date,
                    "Company Affiliation": company_aff,
                    "Non-academic Author": non_acad_author,
                    "Corresponding Author Email": corr_email
                })
                if debug:
                    print(f"[DEBUG] Matched: PMID={pmid} Author='{non_acad_author}' Company='{company_aff}' Email='{corr_email}'")
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Fetches PubMed papers matching a query with at least one pharma/biotech company author. Outputs CSV or prints table.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "query",
        type=str,
        nargs='*',
        help="PubMed search query (use quotes for multi-word queries and PubMed syntax)"
    )
    parser.add_argument(
        "-n", "--num", type=int, default=100,
        help="Number of results to fetch (default: 100)"
    )
    parser.add_argument(
        "-f", "--file", type=str, default=None,
        help="Filename to save CSV output; if not given, prints to console"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="Print debug information during execution"
    )
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(1)
    user_query = " ".join(args.query)

    debug = args.debug
    nmax = args.num
    out_file = args.file

    if debug:
        print(f"[DEBUG] Query: '{user_query}'")
        print(f"[DEBUG] Number of results: {nmax}")
        print(f"[DEBUG] Output file: {out_file or '[console]'}")

    try:
        pmids = fetch_pmids(user_query, retmax=nmax, debug=debug)
    except Exception as e:
        print(f"Error fetching PMIDs: {e}")
        sys.exit(1)
    if not pmids:
        print("No articles found for the given query.")
        sys.exit(0)
    try:
        xmls = fetch_article_xml(pmids, debug=debug)
        parsed = parse_articles(xmls, debug=debug)
    except Exception as e:
        print(f"Error fetching or parsing articles: {e}")
        sys.exit(1)
    if not parsed:
        print("No matching articles with pharma/biotech affiliations found.")
        sys.exit(0)
    df = pd.DataFrame(parsed)
    df = df.fillna("")   # Cleaner: replaces NaN with empty string
    if out_file:
        df.to_csv(out_file, index=False)
        print(f"\nResults saved to {out_file}")
    else:
        # Print as a nicely formatted table
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df.to_string(index=False))

if __name__ == "__main__":
    main()
