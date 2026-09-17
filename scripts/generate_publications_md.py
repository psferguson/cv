"""Generate a Markdown publications page (for the Jekyll website) from
publications.yaml + ferguson_publications.bib.

Mirrors the author/journal formatting of generate_publications_tex.py.
"""

import re

import yaml
from pybtex.database import parse_file

MY_NAME = "Ferguson, P. S."
SELF_PATTERNS = (
    "{Ferguson}, P.",
    "{Ferguson}, P. S.",
    "{Ferguson}, Peter S.",
    "{Ferguson}, P.~S.",
    "{Ferguson}, Peter",
)

# LaTeX journal macros (aas_macros.sty) -> display names
JOURNAL_MACROS = {
    r"\apj": "ApJ",
    r"\apjl": "ApJL",
    r"\apjs": "ApJS",
    r"\aj": "AJ",
    r"\mnras": "MNRAS",
    r"\prd": "Phys. Rev. D",
    r"\nat": "Nature",
    r"\aap": "A&A",
    r"\pasp": "PASP",
}

FRONT_MATTER = """---
layout: page
title: Publications
permalink: /publications/
nav_order: 4
---

Auto-generated from my [ADS library](https://ui.adsabs.harvard.edu/public-libraries/rBhHJF5MTWqIJuR0n-PNKA)
(ORCID [0000-0001-6957-1627](https://orcid.org/0000-0001-6957-1627)).
Mentored students are <u>underlined</u>.

"""


def clean_tex(s):
    """Strip the most common BibTeX/LaTeX markup for display in Markdown."""
    s = s.replace("{\\'o}", "ó").replace("{\\'a}", "á").replace("{\\'\\i}", "í")
    s = s.replace('{\\"o}', "ö").replace("{\\c{c}}", "ç").replace("{\\'e}", "é")
    s = re.sub(r"\$\s*\^\{(\d+)\}\s*\$", r"<sup>\1</sup>", s)  # S$^{5}$
    s = s.replace("~", " ")
    s = re.sub(r"[{}]", "", s)
    return s


def format_author(person):
    name = str(person)
    for pat in SELF_PATTERNS:
        if pat in name:
            return f"**{MY_NAME}**", True
    return clean_tex(name), False


def format_entry(bib_entry, student_led):
    authors = bib_entry.persons["author"]
    author_list = []
    found_self = False

    for author in authors[:4]:
        name, is_self = format_author(author)
        if is_self:
            if not found_self:
                author_list.append(name)
                found_self = True
        else:
            author_list.append(name)

    if len(author_list) > 3:
        if found_self and f"**{MY_NAME}**" in author_list[3]:
            author_list = author_list[:4]
        else:
            author_list = author_list[:3]

    if not found_self:
        author_list.append("...")
        author_list.append(f"**{MY_NAME}**")
    if len(authors) > len(author_list):
        author_list.append("et al.")

    if student_led and author_list:
        author_list[0] = f"<u>{author_list[0]}</u>"

    title = clean_tex(bib_entry.fields.get("title", "No Title"))
    year = bib_entry.fields.get("year", "")
    journal = bib_entry.fields.get("journal", "No Journal")
    url = bib_entry.fields.get("adsurl", "")

    if journal == "arXiv e-prints":
        journal = "arXiv:" + bib_entry.fields.get("eprint", "")
    elif journal == "No Journal" and "SPIE" in url:
        journal = "SPIE"
    elif journal == "No Journal" and "DMTN" in bib_entry.fields.get("number", ""):
        journal = "DMTN"
        url = bib_entry.fields.get("url", url)
    journal = JOURNAL_MACROS.get(journal, clean_tex(journal))

    venue = f"[{journal}, {year}]({url})" if url else f"{journal}, {year}"
    return f"- {', '.join(author_list)}, *{title}*, {venue}\n"


def generate_md(yaml_file, bib_file, output_file):
    with open(yaml_file) as yf:
        publications = yaml.safe_load(yf)
    bib_data = parse_file(bib_file)

    with open(output_file, "w") as md:
        md.write(FRONT_MATTER)
        for section, entries in publications.items():
            if not isinstance(entries, list):
                entries = [entries]
            md.write(f"## {section} ({len(entries)})\n\n")
            for entry in entries:
                if isinstance(entry, dict):
                    bibcode = entry["bibcode"]
                    student_led = entry.get("student_led", False)
                else:
                    bibcode, student_led = entry, False
                if bibcode in bib_data.entries:
                    md.write(format_entry(bib_data.entries[bibcode], student_led))
                else:
                    print(f"warning: {bibcode} not found in {bib_file}")
            md.write("\n")


if __name__ == "__main__":
    generate_md(
        yaml_file="./scripts/publications.yaml",
        bib_file="./ferguson_publications.bib",
        output_file="./publications.md",
    )
