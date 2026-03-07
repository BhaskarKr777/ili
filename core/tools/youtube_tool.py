"""
YouTube Tool
============
Search YouTube and open the top result in the browser.

Input formats:
  "bubble sort tutorial"              — search and open top result
  "search | python for beginners"     — explicit search
  "open | https://youtube.com/..."    — open a direct URL
"""

import re
import webbrowser
from urllib.parse import quote_plus
from .base_tool import BaseTool


class YouTubeTool(BaseTool):
    name = "youtube"
    description = (
        "Search YouTube and open a video in the browser. "
        "Input: 'your search query' e.g. 'bubble sort tutorial' or "
        "'open | https://youtube.com/watch?v=...' to open a direct link."
    )

    def run(self, input_text: str) -> str:
        # Clean LLM junk
        inp = re.sub(r'\s*[\(\[].*', '', input_text).strip()

        if not inp:
            return "What should I search on YouTube? Provide a search query."

        # ── OPEN DIRECT URL ───────────────────────────────────────────────────
        if inp.lower().startswith("open |") or inp.lower().startswith("http"):
            url = inp.split("|", 1)[-1].strip()
            if not url.startswith("http"):
                url = "https://" + url
            try:
                webbrowser.open(url)
                return f"▶️ Opening YouTube: {url}"
            except Exception as e:
                return f"Error opening URL: {e}"

        # ── SEARCH ────────────────────────────────────────────────────────────
        # Strip "search |" prefix if present
        query = re.sub(r'^search\s*\|\s*', '', inp, flags=re.IGNORECASE).strip()

        if not query:
            return "No search query provided."

        # Try to fetch top result using YouTube's search page
        result = self._fetch_top_result(query)

        if result:
            video_url   = result["url"]
            video_title = result["title"]
            try:
                webbrowser.open(video_url)
                return (
                    f"▶️ Opening: {video_title}\n"
                    f"🔗 {video_url}"
                )
            except Exception as e:
                return f"Found video but couldn't open browser: {e}\nURL: {video_url}"
        else:
            # Fallback: open YouTube search results page
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            try:
                webbrowser.open(search_url)
                return (
                    f"▶️ Opened YouTube search for: '{query}'\n"
                    f"🔗 {search_url}"
                )
            except Exception as e:
                return f"Error opening browser: {e}"

    def _fetch_top_result(self, query: str) -> dict | None:
        """Try to scrape the top YouTube result for a query."""
        try:
            import urllib.request
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            req = urllib.request.Request(
                search_url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode("utf-8", errors="ignore")

            # Extract first video ID from the page
            match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if not match:
                return None

            video_id = match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            # Try to extract title
            title_match = re.search(
                r'"title":\{"runs":\[\{"text":"([^"]+)"', html
            )
            title = title_match.group(1) if title_match else query

            return {"url": video_url, "title": title}

        except Exception:
            return None