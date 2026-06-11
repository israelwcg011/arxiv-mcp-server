# arXiv MCP Server

A Model Context Protocol (MCP) server that exposes the arXiv API as a set of tools and resources for LLMs. It allows an AI assistant (e.g. Claude Desktop) to search arXiv, retrieve paper metadata, fetch PDF links, and generate BibTeX citations directly inside a conversation.

Built with [FastMCP](https://github.com/jlowin/fastmcp) and [httpx](https://www.python-httpx.org/).

---

## Features

### Tools

| Tool | Description |
|---|---|
| `search_papers` | Search arXiv using the full query syntax (field prefixes, boolean operators, date filters, sorting). |
| `get_paper` | Retrieve full metadata for a specific paper by arXiv ID. |
| `get_paper_pdf_url` | Return the direct PDF URL for a given arXiv ID. |
| `create_bibtex_list_from_arxiv_ids` | Generate BibTeX entries for a list of arXiv IDs. |

### Resources

| Resource | Description |
|---|---|
| `docs://arxiv/api` | Full arXiv API documentation (query syntax, field prefixes, operators, subject categories, response format) — exposed so the LLM can construct valid queries on its own. |

---

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/israelwcg011/arxiv-mcp-server.git
cd arxiv-mcp-server
```

### 2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the server

By default, `server.py` runs with the **SSE** transport on port `8080` (or the `PORT` environment variable, if set):

```bash
python server.py
```

You should see:

```
Starting MCP server 'arxiv' with transport 'sse' on http://0.0.0.0:8080/sse
```

If you prefer **stdio** transport (used by Claude Desktop's local-process config or MCP Inspector's default mode), edit the bottom of `server.py`:

```python
if __name__ == "__main__":
    # cloud / remote run
    # mcp.run(transport="sse", host="0.0.0.0", port=port)

    # local run
    mcp.run(transport="stdio")
```

### 4. Test locally with MCP Inspector

For SSE:

```bash
npx @modelcontextprotocol/inspector --transport sse --server-url http://localhost:8080/sse
```

For stdio:

```bash
npx @modelcontextprotocol/inspector python server.py
```

### 5. Connect it to Claude Desktop (local)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop. You should see `search_papers`, `get_paper`, `get_paper_pdf_url`, and `create_bibtex_list_from_arxiv_ids` available as tools.

---

## Example Queries

**Search for recent papers on a topic:**

```
search_papers(query="all:\"large language models\"", sort_by="submittedDate", sort_order="descending", max_results=10)
```

**Field-specific search with boolean operators:**

```
search_papers(query="au:Hinton AND cat:cs.LG")
```

**Get metadata for a specific paper:**

```
get_paper(arxiv_id="1706.03762")
```

**Generate BibTeX for multiple papers:**

```
create_bibtex_list_from_arxiv_ids(arxiv_ids=["1706.03762", "1502.03167"])
```

The `docs://arxiv/api` resource contains the full query syntax reference (field prefixes, boolean operators, date filters, subject category codes) so an LLM can construct advanced queries without external documentation.

---

## Deployment

This server was containerized with Docker and deployed on [Fly.io](https://fly.io) using:

```bash
fly launch
fly deploy
```

`server.py` reads the port from the `PORT` environment variable (Fly.io sets this dynamically) and supports `transport="sse"`, `host="0.0.0.0"` for remote/cloud deployment. The `Dockerfile` and `fly.toml` are included in the repo as a reference for anyone wanting to deploy their own instance.

---

## Notes

- The arXiv API returns Atom/XML; this server parses it into JSON before returning results to the client.
- `max_results` is capped at 100 per the arXiv API's recommended limits.
- This is a read-only integration — no data is written back to arXiv or any external service.

---

## References

- [arXiv API User Manual](https://info.arxiv.org/help/api/index.html)
- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)