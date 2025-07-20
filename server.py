from typing import Any
from logging import Logger
import urllib.parse
import json
import httpx
from mcp.server.fastmcp import FastMCP
logger = Logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("OpenAlex")

# Constants
OPENALEX_WORKS_BASE = "https://api.openalex.org/works"
USER_AGENT = "openalex-unofficial-mcp/1.0"

async def make_request(url: str) -> dict[str, Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def search_works(query: str) -> str:
    """Search for scholarly documents with titles and/or abstracts that match que user's query.
    
    Args:
        query: A text to search for in the OpenAlex catalogue (e.g. "Exponential Random graphs", "Quantile regression methods in Economics")
    """
    
    encoded_query = urllib.parse.quote(query)
    fields = [
        "id",
        "title",
        "publication_year",
        "type",
        "authorships",
    ]

    filter=f"filter=title_and_abstract.search:{encoded_query}"
    select=f"select={','.join(fields)}"

    url = f"{OPENALEX_WORKS_BASE}?{filter}&{select}&per-page=5"
    response = await make_request(url)
    return json.dumps(response,separators=(',',':'), ensure_ascii=False)

@mcp.tool()
async def get_paper(openalex_id: str) -> str:
    """Obtain detailed information about a particular scholarly document.
    
    Args:
        openalex_id: The OpenAlex ID of the work (e.g. W4287168995, W2800811598) 
    """

    fields = [
        "id",
        "title",
        "publication_date",
        "type",
        "authorships",
        "referenced_works",

    ]
    select = f"select={','.join(fields)}"

    url = f"{OPENALEX_WORKS_BASE}/{openalex_id}?{select}"
    response = await make_request(url)
    return json.dumps(response,separators=(',',':'), ensure_ascii=False)
    

if __name__ == "__main__":
    # Initialize and run the server
    logger.info("Server started")
    mcp.run(transport='stdio')
