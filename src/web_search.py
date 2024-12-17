"""Module for fetching information from gov.uk prison visitor pages."""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from tenacity import retry, wait_exponential, stop_after_attempt
from . import config

class GovUKSearcher:
    """Class to handle searching and fetching content from gov.uk pages."""
    
    def __init__(self):
        """Initialize with gov.uk URLs from config."""
        self.urls = {
            'id': config.GOV_UK_ID_URL,
            'dress_code': config.GOV_UK_DRESS_CODE_URL,
            'base': config.GOV_UK_BASE_URL
        }
        
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10),
           stop=stop_after_attempt(3))
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch content from a gov.uk page with retry logic.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            The page content as text, or None if the fetch fails
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def _parse_content(self, html_content: str) -> str:
        """
        Parse the main content from a gov.uk page.
        
        Args:
            html_content: The HTML content to parse
            
        Returns:
            The extracted main content as text
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the main content div - adjust selectors based on gov.uk structure
        main_content = soup.find('div', {'class': 'govspeak'})
        if not main_content:
            main_content = soup.find('main')
            
        if main_content:
            # Remove any unnecessary elements
            for element in main_content.find_all(['script', 'style']):
                element.decompose()
            
            return main_content.get_text(separator=' ', strip=True)
        return ""

    def get_id_requirements(self) -> Optional[str]:
        """
        Fetch and parse ID requirements for prison visitors.
        
        Returns:
            Parsed content about ID requirements, or None if fetch fails
        """
        content = self._fetch_page(self.urls['id'])
        if content:
            return self._parse_content(content)
        return None

    def get_dress_code(self) -> Optional[str]:
        """
        Fetch and parse dress code information for prison visitors.
        
        Returns:
            Parsed content about dress code, or None if fetch fails
        """
        content = self._fetch_page(self.urls['dress_code'])
        if content:
            return self._parse_content(content)
        return None

    def search_by_topic(self, topic: str) -> Optional[str]:
        """
        Search for specific topic information using predefined URLs.
        
        Args:
            topic: The topic to search for ('id' or 'dress_code')
            
        Returns:
            The relevant content for the topic, or None if not found
        """
        if topic.lower() == 'id':
            return self.get_id_requirements()
        elif topic.lower() == 'dress_code':
            return self.get_dress_code()
        return None

# Example usage
if __name__ == "__main__":
    searcher = GovUKSearcher()
    
    # Test ID requirements fetch
    id_info = searcher.get_id_requirements()
    if id_info:
        print("ID Requirements:", id_info[:200], "...")
        
    # Test dress code fetch
    dress_code = searcher.get_dress_code()
    if dress_code:
        print("\nDress Code:", dress_code[:200], "...")