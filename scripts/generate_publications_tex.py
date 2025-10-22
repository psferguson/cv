import yaml
from pybtex.database import parse_file

def generate_tex(yaml_file, bib_file, output_file):
    # Load YAML file
    with open(yaml_file, 'r') as yf:
        publications = yaml.safe_load(yf)
    # Parse BibTeX file
    bib_data = parse_file(bib_file)

    # Start writing the LaTeX file
    my_name = "Ferguson, P. S." 
    with open(output_file, 'w') as tex_file:
        tex_file.write("% Generated Publications\n")
        tex_file.write("\\renewcommand{\\labelitemi}{$$}\n")

        for title in publications.keys():
            subsection_string = "\\subsection{" + f"{title}" +  f"  ({len(publications[title])})"+"}\n"
            tex_file.write(subsection_string)
            tex_file.write("\\begin{itemize}[itemsep=1pt]\n")
            # Write section title
            entries = publications[title]
            if not isinstance(entries, list):
                entries = [entries]
            # Modify how the author list is displayed
            for entry in entries:
                # Handle both string entries and dictionary entries
                if isinstance(entry, dict):
                    bibcode = entry['bibcode']
                    student_led = entry.get('student_led', False)
                else:
                    bibcode = entry
                    student_led = False
                
                if bibcode in bib_data.entries:
                    bib_entry = bib_data.entries[bibcode]
                    authors = bib_entry.persons['author']
                    author_list = []
                    found_self = False

                    # Adjust logic to ensure exactly 3 authors are shown, with the user's name bolded if present
                    for i, author in enumerate(authors[:4]):
                        author_name = str(author)
                        if "{Ferguson}, P." in author_name or "{Ferguson}, P. S." in author_name or "{Ferguson}, Peter S." in author_name or "{Ferguson}, P.~S." in author_name or "{Ferguson}, Peter" in author_name:
                            if not found_self:  # Ensure the user's name is added only once
                                author_list.append(f"\\textbf{{{my_name}}}")
                                found_self = True
                        else:
                            author_list.append(author_name)


                    # Adjust logic to keep the first 4 authors if the user's name is the 4th author
                    if len(author_list) > 3:
                        #print(bib_entry.fields.get('title', 'No Title'))
                        #import pdb; pdb.set_trace()
                        if found_self and len(author_list) > 3 and my_name in author_list[3]:
                            author_list = author_list[:4]  # Keep the first 4 authors if user's name is the 4th
                        else:
                            author_list = author_list[:3]  # Otherwise, truncate to 3 authors
                        
                    
                    if not found_self:  # If user's name wasn't found, add it at the end
                        author_list.append("...")
                        author_list.append(f"\\textbf{{{my_name}}}")
                    if len(authors) > len(author_list):  # If more authors exist, add "et al."
                        author_list.append("et al.")

                    formatted_authors = ', '.join(author_list)
                    title = bib_entry.fields.get('title', 'No Title')
                    year = bib_entry.fields.get('year', 'No Year')
                    journal = bib_entry.fields.get('journal', 'No Journal')
                    
                    url = bib_entry.fields.get('adsurl', '')
                    if journal == 'arXiv e-prints':
                        journal = 'arXiv/' + bib_entry.fields.get('eprint', '')  # Keep only the arXiv ID part
                    elif (journal == 'No Journal') & ("SPIE" in url):
                        journal = "SPIE" 
                    elif (journal == 'No Journal') & ("DMTN" in bib_entry.fields.get('number', '')):
                        journal = "DMTN"
                        url = bib_entry.fields.get('url', url)  # Use 'url' field if available
                    
                    # Add asterisk for student-led papers
                    prefix = "*" if student_led else ""
                    tex_file.write(f"    \\item {prefix}{formatted_authors}, \\textit{{{title}}}, \\href{{{url}}}{{\\textbf{{{journal}}}, {year}}}\n")
            tex_file.write("\\end{itemize}\n")

if __name__ == "__main__":
    generate_tex(
        yaml_file="./scripts/publications.yaml",
        bib_file="./ferguson_publications.bib",
        output_file="./auto_pubs.tex"
    )
