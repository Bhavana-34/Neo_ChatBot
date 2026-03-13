import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import TAVILY_API_KEY

logger = logging.getLogger(__name__)


def web_search(query, max_results=4):
    """Perform a live web search using Tavily API and return formatted results"""
    if not TAVILY_API_KEY:
        return ""
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=max_results, include_answer=True)

        parts = []
        if response.get("answer"):
            parts.append(f"[Web Summary]\n{response['answer']}")
        for i, r in enumerate(response.get("results", []), 1):
            content = r.get("content", "").strip()
            if content:
                parts.append(f"[Web Result {i}: {r.get('title', '')}]\n{content}")

        return "\n\n---\n\n".join(parts)

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return ""


def should_search(query, has_doc_context):
    """Decide whether to trigger web search based on query and available context"""
    if not TAVILY_API_KEY:
        return False
    if not has_doc_context:
        return True
    # Trigger search for queries about current/live information
    live_keywords = ["latest", "recent", "current", "today", "news", "update", "2024", "2025", "price", "now"]
    return any(kw in query.lower() for kw in live_keywords)
