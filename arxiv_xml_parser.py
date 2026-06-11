import xml.etree.ElementTree as ET

# Namespaces used in the arXiv Atom feed
NAMESPACES = {
    "atom":     "http://www.w3.org/2005/Atom",
    "arxiv":    "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}

def parse_arxiv_xml(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall("atom:entry", NAMESPACES):
        papers.append({
            "id": entry.find("atom:id", NAMESPACES).text.strip(),
            "title": entry.find("atom:title", NAMESPACES).text.strip(),
            "summary": entry.find("atom:summary", NAMESPACES).text.strip(),
            "published": entry.find("atom:published", NAMESPACES).text.strip(),
            "updated": entry.find("atom:updated", NAMESPACES).text.strip(),
            "authors": [author.find("atom:name", NAMESPACES).text.strip() for author in entry.findall("atom:author", NAMESPACES)],
            "pdf_url": next((link.get("href") for link in entry.findall("atom:link", NAMESPACES) if link.get("rel") == "related"), None),
            "abstract_url": next((link.get("href") for link in entry.findall("atom:link", NAMESPACES) if link.get("rel") == "alternate"), None),
        })
    return papers