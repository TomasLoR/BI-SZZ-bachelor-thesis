import validators
from urllib.parse import urlparse
from license_checker.request_manager import RequestManager
from license_checker.data_extractor import DataExtractor
from license_checker.license_identifier import LicenseIdentifier

class LicenseDetector:
    """
    Detects licenses for websites by crawling and analyzing their content.
    
    This class coordinates the process of checking websites for license information,
    examining relevant pages, and identifying license types.
    """
    
    def __init__(self, user_agent=None):
        """
        Initialize the LicenseDetector with optional user agent.
        
        Args:
            user_agent: User agent string to use for HTTP requests
        """
        self.request_manager = RequestManager(user_agent)
        self.data_extractor = DataExtractor(self.request_manager)
        self.license_identifier = LicenseIdentifier()
        self.all_data = []

    def _validate_url(self, url):
        """
        Validate if a URL is properly formatted.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return validators.url(url) if url else False
        
    def _normalize_url(self, url):
        """
        Extract the base domain from a URL.
        
        Args:
            url: URL to normalize
            
        Returns:
            Base URL as scheme://domain
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception as e:
            print(f"Error parsing URL {url}: {e}")
            return url
    
    def _process_website(self, url):
        """
        Process a single website to detect license information.
        
        Args:
            url: The website URL to process
            
        Returns:
            Dictionary containing license detection results
            
        Raises:
            Exception: Any errors that occur during processing
        """
        result = {
            "website": url,
            "invalidUrl": False,
            "blockedByRobotsTxt": False,
            "licenseLink": None,
            "licenseType": None,
            "relevantLinks": [],
            "licenseMentions": [],
            "content": None,
        }

        # Validate the URL format
        if not self._validate_url(url):
            result["invalidUrl"] = True
            return result

        # Normalize URL to base domain
        base_url = self._normalize_url(url)
        print(f"Processing domain: {base_url}")

        # Check robots.txt
        if not self.request_manager.is_allowed_by_robots(base_url):
            result["blockedByRobotsTxt"] = True
            return result

        # Fetch and parse content
        content = self.request_manager.fetch_page(url)
        if not content:
            return result

        soup = self.data_extractor.parse_html(content)
        if not soup:
            return result
            
        # Extract license information
        license_link, license_text, relevant_links = self.data_extractor.extract_footer_links(soup, url)
        license_type = self.license_identifier.determine_cc_license(license_link, license_text)

        # Process any additional license-related links
        content = self.data_extractor.process_relevant_links(relevant_links)
        license_mentions = self.license_identifier.extract_licenses(content)
        if license_type == "Unknown":
            license_type = self.license_identifier.determine_cc_license("", content)

        result["licenseLink"] = license_link
        result["licenseType"] = license_type
        result["relevantLinks"] = relevant_links
        result["content"] = content
        result["licenseMentions"] = license_mentions
        
        return result

    def scan_websites(self, sites):
        """
        Scan a list of websites for license information.
        
        Args:
            sites: List of website URLs to scan
            
        Returns:
            List of dictionaries containing license detection results for each website
        """
        self.all_data = []
        
        if not sites:
            return self.all_data
            
        for url in sites:
            print(f"Crawling: {url}")
            try:
                result = self._process_website(url)
                self.all_data.append(result)
                print(f"{url} processed.")
            except Exception as e:
                print(f"Unexpected error processing {url}: {e}")
                
                self.all_data.append({
                    "website": url,
                    "error": str(e),
                })
                
        print("All websites processed.")
        return self.all_data