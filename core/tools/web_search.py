"""
Web search tool — uses multiple methods with fallbacks.
No API key needed.
"""
import re
import urllib.parse
from core.tools.base_tool import BaseTool


class WebSearchTool(BaseTool):

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for current information. Input: search query string."

    def run(self, query: str) -> str:
        query = query.strip()

        # Try each method in order
        result = self._try_duckduckgo_api(query)
        if result:
            return result

        result = self._try_wikipedia(query)
        if result:
            return result

        return f"Could not search for '{query}'. Check internet connection."

    def _try_duckduckgo_api(self, query: str) -> str:
        """DuckDuckGo Instant Answer API — no scraping, just JSON."""
        try:
            import requests
            encoded = urllib.parse.quote_plus(query)
            resp = requests.get(
                f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1&skip_disambig=1",
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                timeout=10,
            )
            data = resp.json()

            results = []

            if data.get("AbstractText"):
                results.append(data["AbstractText"])
                if data.get("AbstractURL"):
                    results.append(f"Source: {data['AbstractURL']}")

            if data.get("Answer"):
                results.append(f"Answer: {data['Answer']}")

            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(f"• {topic['Text'][:200]}")

            if results:
                return "\n".join(results)

        except Exception:
            pass
        return ""

    def _try_wikipedia(self, query: str) -> str:
        """Wikipedia search API — very reliable."""
        try:
            import requests
            encoded = urllib.parse.quote_plus(query)

            # Search Wikipedia
            search_resp = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action":   "query",
                    "list":     "search",
                    "srsearch": query,
                    "format":   "json",
                    "srlimit":  3,
                },
                headers={"User-Agent": "ili-agent/1.0"},
                timeout=10,
            )
            search_data = search_resp.json()
            hits = search_data.get("query", {}).get("search", [])

            if not hits:
                return ""

            # Get summary of top result
            title = hits[0]["title"]
            summary_resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}",
                headers={"User-Agent": "ili-agent/1.0"},
                timeout=10,
            )
            summary = summary_resp.json()

            result = f"From Wikipedia — {title}:\n{summary.get('extract', '')[:500]}"

            # Add other search hits
            for hit in hits[1:3]:
                snippet = re.sub(r"<[^>]+>", "", hit.get("snippet", ""))
                result += f"\n• {hit['title']}: {snippet}"

            return result

        except Exception as e:
            return ""