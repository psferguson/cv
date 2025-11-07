import requests
import os
import subprocess
import sys

token = "Cvl4e84W1MgDL4xl06EJoVsMb8x2OcWhX9B6eUdj"
LIBRARY_ID = "rBhHJF5MTWqIJuR0n-PNKA"
BIB_FILE = "ferguson_publications.bib"

def get_all_library_documents(library_id, token):
    """Get all documents from the library (handling pagination)."""
    headers = {'Authorization': 'Bearer ' + token}
    
    # Get library metadata to know total count
    response = requests.get(f"https://api.adsabs.harvard.edu/v1/biblib/libraries/{library_id}",
                           headers=headers)
    response.raise_for_status()
    
    library_data = response.json()
    total_docs = library_data['metadata']['num_documents']
    print(f"🔍 Library has {total_docs} total documents")
    
    # Get all documents (ADS default is 20 per page, so we need to paginate)
    all_bibcodes = []
    start = 0
    rows = 50  # Get 50 at a time
    
    while start < total_docs:
        url = f"https://api.adsabs.harvard.edu/v1/biblib/libraries/{library_id}?start={start}&rows={rows}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        bibcodes = data.get('documents', [])
        all_bibcodes.extend(bibcodes)
        
        print(f"   Retrieved {len(bibcodes)} documents (total: {len(all_bibcodes)}/{total_docs})")
        start += rows
    
    return all_bibcodes

def export_bibcodes_to_bibtex(bibcodes, token):
    """Export bibcodes to BibTeX using ADS export API."""
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'bibcode': bibcodes,
        'format': 'bibtex'
    }
    
    response = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex", 
                            headers=headers, json=payload)
    response.raise_for_status()
    
    export_data = response.json()
    return export_data.get('export', '')

def generate_latex_publications():
    """Generate the LaTeX publications file after creating BibTeX."""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "generate_publications_tex.py")
        if os.path.exists(script_path):
            print("\n🔄 Generating LaTeX publications file...")
            result = subprocess.run([sys.executable, "generate_publications_tex.py"], 
                                  capture_output=True, text=True, 
                                  cwd=os.path.dirname(__file__))
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠️  Warning: Error generating LaTeX file: {result.stderr}")
        else:
            print(f"⚠️  Warning: {script_path} not found. LaTeX file not generated.")
    except Exception as e:
        print(f"⚠️  Warning: Error running LaTeX generator: {e}")

if __name__ == "__main__":
    try:
        # Get all documents from the library
        print("🔍 Fetching all documents from ADS library...")
        all_bibcodes = get_all_library_documents(LIBRARY_ID, token)
        
        # Export to BibTeX
        print(f"📝 Exporting {len(all_bibcodes)} documents to BibTeX...")
        bibtex_content = export_bibcodes_to_bibtex(all_bibcodes, token)
        
        # Write to file
        with open(BIB_FILE, "w") as fout:
            fout.write(bibtex_content)
        
        print(f"✅ Saved {len(all_bibcodes)} entries to {BIB_FILE}")
        
        # Append missing_pubs.bib
        missing_bib_file = "missing_pubs.bib"
        if os.path.exists(missing_bib_file):
            with open(missing_bib_file, "r") as fin:
                missing_bib_content = fin.read()
            with open(BIB_FILE, "a") as fout:
                fout.write("\n" + missing_bib_content)
            print(f"✅ Appended content from {missing_bib_file} to {BIB_FILE}")
        else:
            print(f"⚠️  Warning: {missing_bib_file} not found. No additional entries appended.")
        
        # Generate LaTeX publications file
        #generate_latex_publications()
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
        sys.exit(1)