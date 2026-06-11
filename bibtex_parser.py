# function to parse arxiv metadata to bibtex entry
def to_bibtex(paper: dict) -> str:
    """
    This function takes a paper metadata (in dict format) and returns a bibtex entry.
    An example of a bibtext entry, according to bibtex.com is

    @article{nash51,
        author  = "Nash, John",
        title   = "Non-cooperative Games",
        journal = "Annals of Mathematics",
        year    = 1951,
        volume  = "54",
        number  = "2",
        pages   = "286--295"
    }
    """
    first_author = paper["authors"][0] if paper["authors"] else "Unknown"
    last_name = first_author.split()[-1].lower()
    year = paper["published"][:4]
    arxiv_id = paper["id"].split("/abs/")[-1]
    cite_key = f"{last_name}{year}_{arxiv_id}"
    cite_key = cite_key.lower()

    # authors: "Last, First and Last, First"
    authors_bibtex = " and ".join(
        f"{a.split()[-1]}, {' '.join(a.split()[:-1])}" if len(a.split()) > 1 else a
        for a in paper["authors"]
    )

    # month name from published date
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    month = months[paper["published"][5:7]]

    # arxiv id from url
    arxiv_id = paper["id"].split("/abs/")[-1]

    # return bibtex entry
    return f"""@article{{{cite_key},
        title={{{paper["title"]}}},
        url={{{paper["abstract_url"]}}},
        author={{{authors_bibtex}}},
        year={{{year}}},
        month={month},
        eprint={{{arxiv_id}}},
        journal={{arXiv preprint}}
    }}"""