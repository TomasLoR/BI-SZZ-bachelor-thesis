import re
from license_checker.parameters import CC_VERSIONS, CC_TYPES, CC_TYPE_MAP, LICENSE_PATTERNS

class LicenseIdentifier:
    """
    This class provides functionality to detect Creative Commons licenses
    and extract license mentions from text.
    """
    
    def determine_cc_license(self, url, text):
        """
        Determine the Creative Commons license from a URL and associated text.
        
        Args:
            url: The URL that might contain license information
            text: The text that might mention a license
            
        Returns:
            A string representing the identified CC license or "Unknown" if not found.
        """
        if not url and not text:
            return "Unknown"

        url_lower = url.lower() if url else ""
        text_lower = text.lower() if text else ""

        cc0_result = self._check_for_cc0(url_lower, text_lower)
        if cc0_result:
            return cc0_result

        specific_license = self._extract_license_from_url(url_lower)
        if specific_license:
            return specific_license

        extracted_license = self._extract_license_from_text(text_lower)
        if extracted_license:
            return extracted_license

        return "Unknown"
        
    def _check_for_cc0(self, url_lower, text_lower):
        """
        Check if the URL or text indicates a CC0/Public Domain license.
        
        Args:
            url_lower: Lowercase URL
            text_lower: Lowercase text
            
        Returns:
            "CC0" if found, None otherwise
        """
        if "publicdomain/zero" in url_lower or "cc0" in text_lower or "creative commons zero" in text_lower:
            return "CC0"
        return None
        
    def _extract_license_from_url(self, url_lower):
        """
        Extract specific CC license information from URL.
        
        Args:
            url_lower: Lowercase URL to analyze
            
        Returns:
            License string if found, None otherwise
        """
        for version in CC_VERSIONS:
            for cc_type in CC_TYPES:
                cc_pattern_url = f"licenses/{cc_type.lower()}/{version}"
                if cc_pattern_url in url_lower:
                    return f"CC-{cc_type}-{version}"
        return None
    
    def _extract_license_from_text(self, text_lower):
        """
        Extract license information from text using regex patterns.
        
        Args:
            text_lower: Lowercase text to analyze
            
        Returns:
            License string if found, None otherwise
        """
        try:
            cc_pattern = LICENSE_PATTERNS["Creative Commons (CC)"]
            match = cc_pattern.search(text_lower)

            if match:
                matched_text = match.group(0)
                cc_type = self._process_cc_type_text(matched_text)
                if not cc_type:
                    return None
                return f"CC-{cc_type}"
        except Exception:
            pass
        return None

    def _process_cc_type_text(self, type_str):
        """
        Process Creative Commons license type text into standardized format.
        
        Args:
            type_str: The string containing CC license type information
            
        Returns:
            A standardized string representation of the CC license type
        """
        if not type_str:
            return ""
        
        type_str = type_str.lower().replace('-', ' ')
        words = type_str.split()
        mapped_words = []
        
        for word in words:
            if word in CC_TYPE_MAP:
                mapped_words.append(CC_TYPE_MAP[word])
                has_cc_type = True
            elif word in CC_VERSIONS:
                mapped_words.append(word)
        
        return '-'.join(mapped_words)

    def extract_licenses(self, text):
        """
        Extract license mentions from text using predefined patterns.
        
        Args:
            text: The text to search for license mentions
            
        Returns:
            A list of license names found in the text
        """
        if not text:
            return []
            
        licenses = set()
        try:
            for pattern_name, pattern in LICENSE_PATTERNS.items():
                if pattern.search(text):
                    licenses.add(pattern_name)
        except Exception:
            pass
            
        return list(licenses)