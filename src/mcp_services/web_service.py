"""
WebService - MCP service for web scraping functionality
"""

import logging
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, NoSuchElementException
import trafilatura

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


class WebExtractionResult(BaseModel):
    """Web extraction result model"""

    url: str
    title: str = ""
    content: str
    length: int
    status: str = "success"
    message: str = ""


class WebService(MCPServiceBase):
    """
    MCP service for web content extraction using headless browser
    """

    def __init__(self, default_wait_time: int = 5):
        super().__init__(name="web_service")
        self.default_wait_time = default_wait_time
        self.chrome_options = self._configure_chrome_options()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _configure_chrome_options(self) -> ChromeOptions:
        """Configure Chrome options for headless execution"""
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return options

    async def initialize(self):
        """Initialize the web service"""
        self.logger.info("WebService initialized")

    async def extract_text(
        self, url: str, wait_time: Optional[int] = None
    ) -> WebExtractionResult:
        """
        Extract text content from a webpage

        Args:
            url: URL of the webpage to extract content from
            wait_time: Seconds to wait for page rendering (optional)

        Returns:
            WebExtractionResult with extracted content
        """
        effective_wait_time = (
            wait_time if wait_time is not None else self.default_wait_time
        )

        self.logger.info(
            f"Extracting content from: {url} (wait: {effective_wait_time}s)"
        )

        driver = None
        try:
            # Setup WebDriver
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)

            # Navigate to URL
            driver.get(url)

            # Wait for potential JS rendering
            time.sleep(effective_wait_time)

            # Get page source
            page_source = driver.page_source
            if not page_source:
                return WebExtractionResult(
                    url=url,
                    content="",
                    length=0,
                    status="error",
                    message="Could not retrieve page source",
                )

            # Extract title
            title = ""
            try:
                title = driver.title
            except Exception:
                pass

            # Extract text using Trafilatura
            extracted_text = trafilatura.extract(
                page_source,
                url=url,
                output_format="txt",
                include_comments=False,
                favor_recall=True,
            )

            if extracted_text:
                content = " ".join(extracted_text.split())
                self.logger.info(
                    f"Successfully extracted {len(content)} characters from {url}"
                )

                return WebExtractionResult(
                    url=url, title=title, content=content, length=len(content)
                )
            else:
                # Fallback: Try body text
                try:
                    body_text = driver.find_element("tag name", "body").text
                    if body_text:
                        content = " ".join(body_text.split())
                        self.logger.info(f"Used fallback extraction for {url}")

                        return WebExtractionResult(
                            url=url,
                            title=title,
                            content=content,
                            length=len(content),
                            message="Used fallback extraction method",
                        )
                except NoSuchElementException:
                    pass

                return WebExtractionResult(
                    url=url,
                    title=title,
                    content="",
                    length=0,
                    status="warning",
                    message="No content could be extracted",
                )

        except WebDriverException as e:
            self.logger.error(f"WebDriver error for {url}: {e}")
            return WebExtractionResult(
                url=url,
                content="",
                length=0,
                status="error",
                message=f"WebDriver error: {str(e)}",
            )
        except Exception as e:
            self.logger.error(f"Unexpected error for {url}: {e}")
            return WebExtractionResult(
                url=url,
                content="",
                length=0,
                status="error",
                message=f"Extraction failed: {str(e)}",
            )
        finally:
            if driver:
                driver.quit()

    async def get_page_info(self, url: str) -> Dict[str, Any]:
        """
        Get basic page information without full content extraction

        Args:
            url: URL of the webpage

        Returns:
            Dictionary with page information
        """
        driver = None
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)

            driver.get(url)
            time.sleep(2)  # Shorter wait for basic info

            info = {
                "url": url,
                "title": driver.title,
                "current_url": driver.current_url,
                "status": "success",
            }

            return info

        except Exception as e:
            self.logger.error(f"Error getting page info for {url}: {e}")
            return {"url": url, "status": "error", "message": str(e)}
        finally:
            if driver:
                driver.quit()

    async def shutdown(self):
        """Shutdown the web service"""
        self.logger.info("WebService shutdown completed")
