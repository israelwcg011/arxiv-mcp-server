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

## Live Demo

A deployed instance is running on Fly.io:

```
https://arxiv-mcp-server.fly.dev/sse
```

This is a public, read-only MCP server (it only queries the arXiv API — no writes, no authentication required).

### Test it with MCP Inspector

```bash
npx @modelcontextprotocol/inspector --transport sse --server-url https://arxiv-mcp-server.fly.dev/sse
```

This opens a browser-based UI where you can:
- Browse the available tools and their schemas
- Call tools manually with custom arguments
- Inspect the `docs://arxiv/api` resource
- View raw JSON-RPC messages

### Connect it to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arxiv": {
      "url": "https://arxiv-mcp-server.fly.dev/sse"
    }
  }
}
```

Restart Claude Desktop. You should see `search_papers`, `get_paper`, `get_paper_pdf_url`, and `create_bibtex_list_from_arxiv_ids` available as tools.

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
    # ngrok / cloud run
    # mcp.run(transport="sse", host="0.0.0.0", port=port)

    # local run
    mcp.run(transport="stdio")
```
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