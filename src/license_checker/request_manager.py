import requests
from urllib.parse import urljoin
from protego import Protego
from license_checker.parameters import USER_AGENT

class RequestManager:
    """
    This class handles making HTTP requests to websites while respecting robots.txt
    rules and providing user agent management.
    """
    def __init__(self, user_agent):
        """
        Initialize a RequestManager with the specified user agent.
        
        Args:
            user_agent (str): The user agent string to use for requests.
                             If None, the default from config will be used.
        """
        self.session = requests.Session()
        self.user_agent = user_agent or USER_AGENT
        
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch_robots(self, url):
        """
        Fetch the robots.txt file from a given URL.
        
        Args:
            url (str): The base URL to fetch robots.txt from.
            
        Returns:
            Protego: A parsed robots.txt object, or None if not available.
        """
        try:
            response = self.session.get(urljoin(url, "/robots.txt"), timeout=10)
            if response.status_code == 200:
                return Protego.parse(response.text)
        except requests.RequestException as e:
            print(f"Failed to fetch robots.txt for {url}: {e}")
        except Exception as e:
            print(f"Unexpected error fetching robots.txt for {url}: {e}")
        return None

    def is_allowed_by_robots(self, url):
        """
        Check if the URL is allowed to be crawled according to robots.txt.
        
        Args:
            url (str): The URL to check against robots.txt rules.
            
        Returns:
            bool: True if crawling is allowed or no robots.txt exists, False otherwise.
        """
        if not url:
            return False
            
        robots = self.fetch_robots(url)
        return robots.can_fetch(url, self.user_agent) if robots else True

    def fetch_page(self, url):
        """
        Fetch the content of a webpage.
        
        Args:
            url (str): The URL to fetch the content from.
            
        Returns:
            bytes: The content of the page, or None if the fetch failed.
        """
        if not url:
            return None
            
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.content


    def set_user_agent(self, user_agent):
        """
        Update the user agent used for requests.
        
        Args:
            user_agent (str): The new user agent string to use.
        """
        self.user_agent = user_agent
        self.session.headers.update({"User-Agent": self.user_agent})

    def get_user_agent(self):
        """
        Get the current user agent being used for requests.
        
        Returns:
            str: The current user agent string.
        """
        return self.user_agent