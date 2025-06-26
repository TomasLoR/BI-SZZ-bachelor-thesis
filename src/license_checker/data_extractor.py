from bs4 import BeautifulSoup
from urllib.parse import urljoin
from license_checker.parameters import LICENSE_PATTERNS, RELEVANT_LINKS_KEYWORDS, RELEVANT_TEXT_KEYWORDS
import time
import re

class DataExtractor:
    """    
    This class processes HTML content to extract license links, relevant URLs,
    and license-related text content from websites.
    """

    def __init__(self, request_manager, request_delay=1):
        """
        Initialize the DataExtractor.
        
        Args:
            request_manager: Manager for making HTTP requests
            request_delay: Delay in seconds between requests (default: 1)
        """
        self.request_manager = request_manager
        self.request_delay = request_delay

    def parse_html(self, content):
        """
        Parse HTML content into a BeautifulSoup object.
        
        Args:
            content: HTML content to parse
            
        Returns:
            BeautifulSoup object representing the parsed HTML
        """
        if not content:
            return None
            
        return BeautifulSoup(content, "html.parser")

    def extract_footer_links(self, soup, base_url):
        """
        Extract license links from footer sections.
        
        Args:
            soup: BeautifulSoup object containing the parsed HTML
            base_url: Base URL for resolving relative links
            
        Returns:
            Tuple of (license_link, license_text, relevant_links)
        """
        if not soup or not base_url:
            return "", "", []
            
        license_link = ""
        license_text = ""
        relevant_links = set()
        
        footers = soup.find_all("footer")
        for footer in footers:
            for link in footer.find_all("a"):
                href = link.get("href")
                if not href:
                    continue
                absolute_url = urljoin(base_url, href)
                text = link.get_text().strip()

                if not license_link and self._contains_pattern(text, LICENSE_PATTERNS):
                    license_link = absolute_url
                    license_text = text
                    continue

                if self._contains_keyword(text, RELEVANT_LINKS_KEYWORDS):
                    relevant_links.add(absolute_url)
            
        return license_link, license_text, list(relevant_links)

    def extract_relevant_text(self, soup):
        """
        Extract license-relevant text from the HTML content.
        
        Args:
            soup: BeautifulSoup object containing the parsed HTML
            
        Returns:
            String containing relevant text about licensing
        """
        if not soup:
            return ""
            
        elements = soup.find_all(["p", "li", "span"])
        sentences = []
        for element in elements:
            text = element.get_text().strip()
            text_parts = re.split(r'\.(?=\s|$)', text)
            
            for sentence in text_parts:
                sentence = sentence.strip()
                if self._contains_keyword(sentence, RELEVANT_TEXT_KEYWORDS):
                    sentences.append(sentence)
        
        return ". ".join(sentences)


    def process_relevant_links(self, links):
        """
        Process a list of links to extract license-relevant content.
        
        Args:
            links: List of URLs to process
            
        Returns:
            Combined text content from all links
        """
        if not links or not self.request_manager:
            return ""
            
        combined_content = []
        for link in links:
            content = self.request_manager.fetch_page(link)
            if content:
                soup = self.parse_html(content)
                extracted = self.extract_relevant_text(soup)
                if extracted:
                    combined_content.append(extracted)
            time.sleep(self.request_delay)
                
        return " ".join(combined_content)

    def _contains_keyword(self, text, keywords):
        """
        Check if text contains any of the keywords.
        
        Args:
            text: The text to check
            keywords: List of keywords to look for
            
        Returns:
            True if any keyword is found, False otherwise
        """
        if not text or not keywords:
            return False
            
        try:
            text_lower = text.lower()
            return any(keyword.lower() in text_lower for keyword in keywords)
        except Exception:
            return False

    def _contains_pattern(self, text, patterns):
        """
        Check if text matches any of the regex patterns.
        
        Args:
            text: The text to check
            patterns: Dictionary of pattern_name: compiled_pattern
            
        Returns:
            True if any pattern matches, False otherwise
        """
        if not text or not patterns:
            return False
            
        try:
            text_lower = text.lower()
            for pattern_name, pattern in patterns.items():
                if pattern.search(text_lower):
                    match = pattern.search(text_lower)
                    matched_text = match.group(0)
                    return True
        except Exception as e:
            print(f"Error matching pattern: {e}")
            
        return False