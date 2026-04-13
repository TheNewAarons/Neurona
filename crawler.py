# crawler.py
import requests
import json
from config import SEARCH_TIMEOUT

class WebCrawler:
    """
    Web scraper de fuentes técnicas gratuitas (sin autenticación).
    """

    @staticmethod
    def search_topic(query, sources=None):
        """
        Busca un topic en múltiples fuentes y retorna resultados.

        Args:
            query: Término de búsqueda
            sources: Lista de fuentes a buscar

        Returns:
            list: [{"source": "...", "title": "...", "content": "...", "url": "..."}, ...]
        """
        if sources is None:
            sources = ["stackoverflow", "wikipedia", "github"]

        results = []

        if "stackoverflow" in sources:
            results.extend(WebCrawler.fetch_stackoverflow(query))

        if "wikipedia" in sources:
            results.extend(WebCrawler.fetch_wikipedia(query))

        if "github" in sources:
            results.extend(WebCrawler.fetch_github(query))

        if "hackernews" in sources:
            results.extend(WebCrawler.fetch_hackernews(query))

        if "devto" in sources:
            results.extend(WebCrawler.fetch_devto(query))

        return results[:10]  # Top 10 resultados

    @staticmethod
    def fetch_stackoverflow(query, max_results=3):
        """
        Busca en Stack Overflow API.
        """
        try:
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "q": query,
                "site": "stackoverflow",
                "sort": "relevance",
                "pagesize": max_results,
            }
            response = requests.get(url, params=params, timeout=SEARCH_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("items", []):
                results.append({
                    "source": "stackoverflow.com",
                    "title": item.get("title", ""),
                    "content": f"Q: {item.get('title', '')} (upvotes: {item.get('score', 0)})",
                    "url": item.get("link", ""),
                })

            return results
        except Exception as e:
            print(f"Error fetching SO: {e}")
            return []

    @staticmethod
    def fetch_wikipedia(query):
        """
        Busca en Wikipedia API.
        """
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary"
            # Usar el query como page name directo
            page = query.replace(" ", "_")
            full_url = f"{url}/{page}"

            response = requests.get(full_url, timeout=SEARCH_TIMEOUT)
            response.raise_for_status()

            data = response.json()

            if "extract" in data:
                return [{
                    "source": "wikipedia.org",
                    "title": data.get("title", query),
                    "content": data.get("extract", "")[:500],  # Primeros 500 chars
                    "url": data.get("content_urls", {}).get("mobile", {}).get("page", ""),
                }]
            return []
        except Exception as e:
            print(f"Error fetching Wikipedia: {e}")
            return []

    @staticmethod
    def fetch_github(query, max_results=3):
        """
        Busca en GitHub Search API.
        """
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": max_results,
            }
            response = requests.get(url, params=params, timeout=SEARCH_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("items", []):
                results.append({
                    "source": "github.com",
                    "title": item.get("name", ""),
                    "content": item.get("description", "")[:300],
                    "url": item.get("html_url", ""),
                })

            return results
        except Exception as e:
            print(f"Error fetching GitHub: {e}")
            return []

    @staticmethod
    def fetch_hackernews(query, max_results=3):
        """
        Busca en HackerNews Algolia API.
        """
        try:
            url = "https://hn.algolia.com/api/v1/search"
            params = {
                "query": query,
                "tags": "story",
                "hitsPerPage": max_results,
            }
            response = requests.get(url, params=params, timeout=SEARCH_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("hits", []):
                results.append({
                    "source": "news.ycombinator.com",
                    "title": item.get("title", ""),
                    "content": item.get("story_text", "")[:300] or "Discussion thread",
                    "url": item.get("story_url", f"https://news.ycombinator.com/item?id={item.get('objectID')}"),
                })

            return results
        except Exception as e:
            print(f"Error fetching HackerNews: {e}")
            return []

    @staticmethod
    def fetch_devto(query, max_results=3):
        """
        Busca en DEV.to API.
        """
        try:
            url = "https://dev.to/api/articles"
            params = {
                "tag": query.split()[0].lower(),  # Primer palabra como tag
                "per_page": max_results,
            }
            response = requests.get(url, params=params, timeout=SEARCH_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data:
                results.append({
                    "source": "dev.to",
                    "title": item.get("title", ""),
                    "content": item.get("description", "")[:300],
                    "url": item.get("url", ""),
                })

            return results
        except Exception as e:
            print(f"Error fetching DEV.to: {e}")
            return []
