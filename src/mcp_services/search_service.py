"""
SearchService - MCP service for web search functionality
"""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel
from ddgs import DDGS

logger = logging.getLogger(__name__)


class MCPServiceBase:
    """Base class for MCP services"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self):
        """Initialize the service"""
        pass

    async def shutdown(self):
        """Shutdown the service"""
        pass


class SearchResult(BaseModel):
    """Single search result model"""

    title: str
    link: str
    snippet: str


class SearchResponse(BaseModel):
    """Search response model"""

    results: List[SearchResult]
    query: str
    total_results: int
    status: str = "success"


class SearchService(MCPServiceBase):
    """
    MCP service for web search using DuckDuckGo
    """

    def __init__(self):
        super().__init__(name="search_service")

    async def initialize(self):
        """Initialize the search service"""
        self.logger.info("SearchService initialized")

    async def search(
        self, query: str, num_results: int = 10, region: str = "de-de"
    ) -> SearchResponse:
        """
        Perform web search using DuckDuckGo

        Args:
            query: Search query string
            num_results: Maximum number of results to return
            region: Search region (default: de-de)

        Returns:
            SearchResponse with results
        """
        try:
            self.logger.info(f"Searching for: '{query}' (max {num_results} results)")

            with DDGS() as ddgs:
                search_results = [
                    r for r in ddgs.text(query, region=region, max_results=num_results)
                ]

            formatted_results = []
            for result in search_results:
                formatted_results.append(
                    SearchResult(
                        title=result.get("title", "No title provided"),
                        link=result.get("href", "No link provided"),
                        snippet=result.get("body", "No description available"),
                    )
                )

            response = SearchResponse(
                results=formatted_results,
                query=query,
                total_results=len(formatted_results),
            )

            self.logger.info(f"Found {len(formatted_results)} results for '{query}'")
            return response

        except Exception as e:
            self.logger.error(f"Search error for query '{query}': {e}")
            return SearchResponse(
                results=[], query=query, total_results=0, status="error"
            )

    async def search_images(
        self, query: str, num_results: int = 10, region: str = "de-de"
    ) -> Dict[str, Any]:
        """
        Search for images using DuckDuckGo

        Args:
            query: Search query string
            num_results: Maximum number of results to return
            region: Search region

        Returns:
            Dictionary with image search results
        """
        try:
            self.logger.info(f"Searching images for: '{query}'")

            with DDGS() as ddgs:
                image_results = [
                    r
                    for r in ddgs.images(query, region=region, max_results=num_results)
                ]

            return {
                "results": image_results,
                "query": query,
                "total_results": len(image_results),
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Image search error for query '{query}': {e}")
            return {
                "results": [],
                "query": query,
                "total_results": 0,
                "status": "error",
            }

    async def search_news(
        self, query: str, num_results: int = 10, region: str = "de-de"
    ) -> Dict[str, Any]:
        """
        Search for news using DuckDuckGo

        Args:
            query: Search query string
            num_results: Maximum number of results to return
            region: Search region

        Returns:
            Dictionary with news search results
        """
        try:
            self.logger.info(f"Searching news for: '{query}'")

            with DDGS() as ddgs:
                news_results = [
                    r for r in ddgs.news(query, region=region, max_results=num_results)
                ]

            return {
                "results": news_results,
                "query": query,
                "total_results": len(news_results),
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"News search error for query '{query}': {e}")
            return {
                "results": [],
                "query": query,
                "total_results": 0,
                "status": "error",
            }

    async def shutdown(self):
        """Shutdown the search service"""
        self.logger.info("SearchService shutdown completed")
