from ads.libraries import Library
from ads.search import SearchQuery
import os
import subprocess
import sys

# Set your ADS token
os.environ["ADS_DEV_KEY"] = "Cvl4e84W1MgDL4xl06EJoVsMb8x2OcWhX9B6eUdj"

# Replace with your ADS library ID (from the URL)
LIBRARY_ID = "rBhHJF5MTWqIJuR0n-PNKA"

# Output file
BIB_FILE = "ferguson_publications.bib"

def export_bib_from_ads(library_id, output_file):
    lib = Library(id=library_id)
    papers = list(lib.get_documents())

    with open(output_file, "w") as fout:
        for paper in papers:
            bib = paper.bibtex
            fout.write(bib + "\n\n")

    print(f"✅ Saved {len(papers)} entries to {output_file}")
    return len(papers)

def generate_latex_publications():
    """Generate the LaTeX publications file after creating BibTeX."""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "generate_publications_tex.py")
        if os.path.exists(script_path):
            print("\n🔄 Generating LaTeX publications file...")
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, cwd="..")
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠️  Warning: Error generating LaTeX file: {result.stderr}")
        else:
            print(f"⚠️  Warning: {script_path} not found. LaTeX file not generated.")
    except Exception as e:
        print(f"⚠️  Warning: Error running LaTeX generator: {e}")

if __name__ == "__main__":
    # Generate BibTeX file
    num_papers = export_bib_from_ads(LIBRARY_ID, BIB_FILE)
    
    # Generate LaTeX publications file