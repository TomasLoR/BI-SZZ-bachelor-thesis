import re

# Default User-Agent
USER_AGENT = "MyCrawler/1.0"

# Regex patterns for license detection
LICENSE_PATTERNS = {
    "MIT License": re.compile(
        # Match 'MIT' at word boundary followed by space or hyphen
        r'\bMIT[-\s]+'
        # Allow up to 3 words between MIT and License/Variant
        r'(?:\w+\s+){0,3}'
        # Match either 'License' or 'Variant'
        r'(?:License|Variant)',
        re.IGNORECASE
    ),
    "Apache License": re.compile(
        # Match 'Apache' at word boundary followed by space or hyphen
        r'\bApache[-\s]+'
        # Non-capturing group for license format variations
        r'(?:'
            # Match 'License' with optional version number
            r'License[-\s]*'
            r'(?:v?\d+(?:\.\d+)?)?'
            r'|'
            # OR direct version number
            r'(?:v?\d+(?:\.\d+)?)'
        r')\b',
        re.IGNORECASE 
    ),
    "Creative Commons (CC)": re.compile(
        r'\b(?:'
            # First try to match 'CC' followed by attributes and optional version
            r'CC'
            # Mandatory space or hyphen separator
            r'[\s-]+'
            # Match attributes (one or more), with optional separators
            r'(?:'
                # Full or abbreviated attribute names
                r'(?:BY|Attribution|SA|Share[\s-]?Alike|NC|Non[\s-]?Commercial|ND|No[\s-]?Derivatives)'
                # Optional space or hyphen after each attribute
                r'[\s-]?'
            r')+'
            # Optional single version number (e.g., 4.0)
            r'(?:\d\.\d)?'
            r'|'
            # Then try to match 'Creative Commons' followed by attributes
            r'Creative[\s-]+Commons'
            # Optional space between CC and attributes
            r'[\s-]*'
            # Match optional attributes
            r'(?:'
                # Full or abbreviated attribute names
                r'(?:Attribution|Share[\s-]?Alike|Non[\s-]?Commercial|No[\s-]?Derivatives|'
                r'BY|SA|NC|ND)'
                # Optional space or hyphen after each attribute
                r'[\s-]*'
            r')*'
            # Optional version
            r'(?:\d\.\d)?'
            r'|'
            # Last, match simple 'CC0' as standalone
            r'CC0'
        r')\b',
        re.IGNORECASE
    ),

    "GNU GPL": re.compile(
        # Match at word boundary
        r'\b'
        # Non-capturing group for variations
        r'(?:'
            # 'GNU' followed by optional 'A' or 'L', then 'GPL'
            r'GNU[\s-]+(?:A|L)?GPL'
            r'|'
            # OR standalone GPL with optional 'A' or 'L' prefix
            r'(?:A|L)?GPL[\s-]*'
            # Direct version number (v2.0, 3)
            r'(?:v?\d+(?:\.\d+)?)'
            r'|'
            # OR full spelled out name
            r'General\s+Public\s+License'
        r')\b',
        re.IGNORECASE
    ),

    "BSD License": re.compile(
        # Match 'BSD' at word boundary followed by space or hyphen
        r'\bBSD[\s-]+'
        # Non-capturing group for either clause number or License
        r'(?:'
            # Match digits followed by space or hyphen and 'Clause'
            r'\d+[\s-]Clause'
            # OR
            r'|'
            # Match 'License'
            r'License'
        r')\b',
        re.IGNORECASE
    ),
}

# Versions of CC licenses
CC_VERSIONS = ['1.0', '2.0', '2.5', '3.0', '4.0']

# Types of CC licenses
CC_TYPES = [
    'BY',
    'BY-SA',
    'BY-ND',
    'BY-NC',
    'BY-NC-SA',
    'BY-NC-ND',
]

# Mapping of CC license types
CC_TYPE_MAP = {
    'attribution': 'BY',
    'by': 'BY',
    'noncommercial': 'NC',
    'non-commercial': 'NC',
    'nc': 'NC',
    'sharealike': 'SA',
    'share-alike': 'SA',
    'sa': 'SA',
    'noderivatives': 'ND',
    'no-derivatives': 'ND',
    'nd': 'ND',
}

# Relevant links based on keywords
RELEVANT_LINKS_KEYWORDS = [
    "terms",
    "legal",
    "license",
    "licensing"
    "use",
    "policy",
    "copyright",
]

# Keywords for content analysis
RELEVANT_TEXT_KEYWORDS = [
    "intellectual property",
    "right",
    "authorised",
    "commercial use",
    "non-commercial use",
    "fair use",
    "license",
    "copyright",
    "creative commons",
    "cc by",
    "gpl",
    "apache",
    "mit",
    "bsd",
]