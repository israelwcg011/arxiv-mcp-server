from fastmcp import FastMCP
from typing import Literal
from datetime import datetime
from config import ARXIV_API_BASE_URL
from arxiv_xml_parser import parse_arxiv_xml
from bibtex_parser import to_bibtex

import asyncio
import httpx
import json
import os

mcp = FastMCP("arxiv")

@mcp.tool()
async def search_papers(
    query: str, 
    start_index: int = 0, 
    max_results: int = 10, 
    sort_by: Literal["relevance", "lastUpdatedDate", "submittedDate"] = "relevance",
    sort_order: Literal["ascending", "descending"] = "descending"
    ) -> str:
    """
    Query papers on arxiv from search query string.

    args:
        query: search query string
        start_index: 0-based index of first result
        max_results: maximum number of results
        sort_by: relevance | lastUpdatedDate | submittedDate
        sort_order: ascending | descending
    """

    # check if the user asked for a large number of results
    # max allowed is 100
    if max_results > 100:
        raise ValueError(f"Error max number of results: {max_results}. Max is 100")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{ARXIV_API_BASE_URL}/query",
                params = {
                    "search_query": query,
                    "start": start_index,
                    "max_results": max_results,
                    "sortBy": sort_by,
                    "sortOrder": sort_order
                }
            )
            response.raise_for_status()
            papers = parse_arxiv_xml(response.text)
            return json.dumps(papers, ensure_ascii = False, indent = 2)
    except Exception as e:
        return f"Unexpected error: {e}"

@mcp.tool()
async def get_paper(arxiv_id: str) -> str:
    """
    This tool retrieves full metada from a specific arxiv paper.

    args:
        arxiv_id: arxiv paper id (e.g., 2605.13529)
    """
    try:
        async with httpx.AsyncClient(follow_redirects = True) as client:
            response = await client.get(
                f"{ARXIV_API_BASE_URL}/query",
                params = {
                    "id_list": arxiv_id
                }
            )
            response.raise_for_status()
            paper = parse_arxiv_xml(response.text)
            return json.dumps(paper, ensure_ascii = False, indent = 2)
    except Exception as e:
        return f"Unexpected error: {e}"

@mcp.tool()
async def get_paper_pdf_url(arxiv_id: str) -> str:
    """
    This tool retrieves the pdf url from a specific arxiv paper.

    args:
        arxiv_id: arxiv paper id (e.g., 2605.13529)
    """
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

@mcp.tool()
async def create_bibtex_list_from_arxiv_ids(arxiv_ids: list[str]) -> str:
    """
    This tool takes a list of arxiv ids as argument, create a bibtex entry for each paper, and returns the list of bibtex entries.

    args:
        arxiv_ids: list of arxiv ids (e.g., ["2605.13529"])
    """
    bibtex_entries = []
    try:
        for arxiv_id in arxiv_ids:
            paper = await get_paper(arxiv_id)
            bibtex_entry = to_bibtex(json.loads(paper)[0]) 
            bibtex_entries.append(bibtex_entry)
        return json.dumps(bibtex_entries, ensure_ascii = False, indent = 2)
    except Exception as e:
        return f"Something went wrong while fetching the papers and parsing to bibtex. Error: {e}"

    

@mcp.resource("docs://arxiv/api")
def arxiv_docs() -> str:
    """arXiv API documentation for query construction and results format. This resource can also help the user."""
    
    return """
# arXiv API Documentation

## Base URL
http://export.arxiv.org/api/query

## Response Format
The API returns Atom/XML, not JSON. Results must be parsed as XML.

## Parameters
- search_query: Query string
- id_list: Comma-separated arXiv IDs (preferred over search_query=id:xxx)
- start: Starting index (default: 0)
- max_results: Number of results (default: 10)
- sortBy: relevance | lastUpdatedDate | submittedDate
- sortOrder: ascending | descending

## Field Prefixes
| Prefix | Field              |
|--------|--------------------|
| ti     | Title              |
| au     | Author             |
| abs    | Abstract           |
| co     | Comment            |
| jr     | Journal Reference  |
| cat    | Subject Category   |
| rn     | Report Number      |
| all    | All of the above   |

## Boolean Operators
- AND
- OR
- ANDNOT

## Grouping
- Parentheses: %28 %29
- Phrases: %22 %22 (double quotes)
- Space: + (extends query to multiple fields)

## Date Filter
submittedDate:[YYYYMMDDTTTT+TO+YYYYMMDDTTTT] (GMT, 24h format)

## Query Examples
- au:del_maestro
- au:del_maestro AND ti:checkerboard
- au:del_maestro ANDNOT ti:checkerboard
- au:del_maestro ANDNOT %28ti:checkerboard OR ti:Pyrochlore%29
- au:del_maestro AND ti:%22quantum criticality%22
- au:del_maestro AND submittedDate:[202301010600+TO+202401010600]

## Article Versions
- Latest version: use id_list=cond-mat/0207270
- Specific version: use id_list=cond-mat/0207270v1

## Subject Categories
### Computer Science
- cs.AI    Artificial Intelligence
- cs.CL    Computation and Language
- cs.CV    Computer Vision and Pattern Recognition
- cs.DS    Data Structures and Algorithms
- cs.IR    Information Retrieval
- cs.LG    Machine Learning
- cs.NE    Neural and Evolutionary Computing
- cs.RO    Robotics

### Statistics
- stat.ML  Machine Learning
- stat.AP  Applications
- stat.CO  Computation
- stat.TH  Statistics Theory

### Mathematics
- math.ST  Statistics Theory
- math.PR  Probability
- math.OC  Optimization and Control

### Physics
- physics.comp-ph  Computational Physics
- physics.data-an  Data Analysis, Statistics and Probability
- cond-mat.dis-nn  Disordered Systems and Neural Networks
- quant-ph         Quantum Physics

### Quantitative Biology
- q-bio.NC  Neurons and Cognition
- q-bio.QM  Quantitative Methods

### Economics
- econ.EM  Econometrics

## Returned Atom Feed Elements

### Feed Level
- title: Canonicalized query string
- id: Unique query ID
- updated: Last update (midnight of current day)
- opensearch:totalResults: Total number of results
- opensearch:startIndex: 0-based index of first result
- opensearch:itemsPerPage: Number of results returned

### Entry Level (per article)
- title: Article title
- id: URL in format http://arxiv.org/abs/id
- published: Date version 1 was submitted
- updated: Date retrieved version was submitted
- summary: Abstract
- author: Author name(s)
- category: arXiv / ACM / MSC category
- arxiv:primary_category: Primary arXiv category
- arxiv:comment: Author comment (if present)
- arxiv:journal_ref: Journal reference (if present)
- arxiv:doi: Resolved DOI URL (if present)
"""




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # ngrok run
    mcp.run(transport = "sse", host = "0.0.0.0", port = port)

    # local run
    #mcp.run(transport = "stdio")