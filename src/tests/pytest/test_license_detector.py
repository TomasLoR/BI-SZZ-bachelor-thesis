import pytest
import requests
from license_checker import LicenseDetector
from license_checker.license_identifier import LicenseIdentifier
from test_utils import read_urls
import time

def test_license_detector_implementation():
    """Test that the LicenseDetector correctly processes websites and returns structured results."""
    test_url = "https://en.wikipedia.org/"
    
    detector = LicenseDetector()
    results = detector.scan_websites([test_url])
    
    assert len(results) == 1
    assert results[0]["website"] == test_url
    assert "licenseLink" in results[0]
    assert "licenseType" in results[0]
    assert "relevantLinks" in results[0]
    assert "licenseMentions" in results[0]
    assert "content" in results[0]
    assert "blockedByRobotsTxt" in results[0]
    assert results[0]["blockedByRobotsTxt"] is False

def test_user_agent_set_correctly(requests_mock):
    custom_ua = "TestUserAgent/1.0"
    test_url = "http://example.com"
    
    detector = LicenseDetector(user_agent=custom_ua)
    detector.scan_websites([test_url])
    
    assert requests_mock.last_request.headers["User-Agent"] == custom_ua

def test_blocked_by_robots_txt():
    test_url = "https://en.wikipedia.org/"
    
    detector = LicenseDetector()
    res = detector.scan_websites([test_url])

    detector.set_user_agent("MJ12bot")
    res_blocked = detector.scan_websites([test_url])

    assert res_blocked[0].get("blockedByRobotsTxt") is True
    assert res[0].get("blockedByRobotsTxt") is False

@pytest.mark.parametrize("website_data", read_urls("data/invalid_urls.json"))
def test_invalid_urls(website_data):
    test_url = website_data["website"]

    detector = LicenseDetector()
    res = detector.scan_websites([test_url])

    assert res[0].get("invalidUrl") is True

# AI generated test cases: https://gemini.google.com/app/fd1ab97fa81a4aa9
@pytest.mark.parametrize("license_text, expected_type", [
    # Creative Commons (CC) - Examples showing different versions and types (BY, SA, ND, NC, etc.)
    ("Licensed under Creative Commons Attribution 4.0 International.", "Creative Commons (CC)"),
    ("This work uses assets under CC0 1.0 Universal Public Domain Dedication.", "Creative Commons (CC)"),
    ("Content available under Creative Commons BY-SA 3.0 Unported.", "Creative Commons (CC)"),
    ("Images are CC BY-NC 2.0. Not for commercial use.", "Creative Commons (CC)"),
    ("Documentation is licensed under Creative Commons Attribution-ShareAlike 2.5 Generic.", "Creative Commons (CC)"),
    ("We recommend using the Creative Commons Attribution 4.0 license for maximum reuse.", "Creative Commons (CC)"),
    ("Ensure compliance with the CC BY-NC-ND 4.0 license terms.", "Creative Commons (CC)"),
    ("Based on data released under the Creative Commons Zero v1.0 Universal license.", "Creative Commons (CC)"),
    ("Older materials might be under Creative Commons 2.0 Generic (CC BY 2.0).", "Creative Commons (CC)"),
    ("A comparison between Creative Commons 3.0 and 4.0 versions.", "Creative Commons (CC)"),

    # GNU GPL - Examples showing different versions (v2, v3) and common phrases
("This software is distributed under the GNU General Public License v3.", "GNU GPL"),
    ("Copyright (C) 2023 Free Software Foundation, Inc. Licensed under GPLv2.", "GNU GPL"),
    ("Available under the GNU GPL version 2, or (at your option) any later version.", "GNU GPL"),
    ("Includes components licensed under GNU Lesser General Public License (LGPL) v2.1.", "GNU GPL"), # Note: LGPL is related but distinct. Including for variety.
    ("Code released under the terms of the GNU Affero General Public License v3.", "GNU GPL"), # Note: AGPL is related but distinct. Including for variety.
    ("Dual-licensed under a proprietary license or the GNU GPL v3.", "GNU GPL"),
    ("See COPYING file for the full text of the GNU General Public License version 2.", "GNU GPL"),
    ("Compatibility issues between GPLv1 and later versions were discussed.", "GNU GPL"),
    ("Migrating project from GPLv2 to GNU GPL v3.", "GNU GPL"),
    ("Must comply with the Free Software Definition as per the GNU GPL.", "GNU GPL"), # General mention

    # MIT License - Examples showing common variations in wording
    ("Permission is hereby granted, free of charge... under the MIT License.", "MIT License"),
    ("Licensed under the terms of the MIT License. Copyright (c) 2024 Jane Doe", "MIT License"),
    ("This project uses the MIT license (see LICENSE file).", "MIT License"),
    ("Code provided under the permissive MIT license.", "MIT License"),
    ("Utilizes libraries governed by the MIT style license.", "MIT License"),
    ("The software is licensed under the MIT License (Expat).", "MIT License"), # Expat is a common name for the MIT license
    ("Uses several dependencies, most released under the MIT License.", "MIT License"),
    ("Copyright (c) 2022 The Foo Authors. MIT License.", "MIT License"),
    ("// SPDX-License-Identifier: MIT", "MIT License"), # Common identifier in source code
    ("Choosing between MIT and Apache? The MIT license is simpler.", "MIT License"),

    # Apache License - Examples showing different versions (2.0) and common phrases
    ("Licensed under the Apache License, Version 2.0 (the \"License\");", "Apache License"),
    ("Copyright 2023 The Apache Software Foundation. Apache License 2.0.", "Apache License"),
    ("This project is distributed under the Apache License v2.0.", "Apache License"),
    ("Uses libraries governed by the Apache License, Version 1.1.", "Apache License"),
    ("See NOTICE file for details on Apache License 2.0 compliance.", "Apache License"),
    ("Originally licensed under Apache 1.0, now relicensed to Apache 2.0.", "Apache License"),
    ("// SPDX-License-Identifier: Apache-2.0", "Apache License"), # Common identifier
    ("Requires patent grant as specified in Apache License Version 2.0.", "Apache License"),
    ("Comparing the Apache License 2.0 with the GPLv3.", "Apache License"),
    ("Contributions must be compatible with the Apache 2.0.", "Apache License"),

    # BSD License - Examples showing different clause versions (2-clause, 3-clause)
    ("Redistribution and use... permitted provided that the following conditions are met: (BSD 3-Clause License)", "BSD License"),
    ("Licensed under the Simplified BSD License (2-clause).", "BSD License"),
    ("Uses components under the New BSD License (3-clause).", "BSD License"),
    ("Code originally from Berkeley, subject to the old 4-clause BSD license.", "BSD License"),
    ("See LICENSE file for terms of the BSD 2-Clause License.", "BSD License"),
    ("This is essentially public domain, using the BSD 0-Clause license.", "BSD License"),
    ("// SPDX-License-Identifier: BSD-3-Clause", "BSD License"), # Common identifier
    ("Comparing BSD 3-Clause and MIT licenses.", "BSD License"),
    ("Requires copyright notice preservation under the 2-clause BSD license.", "BSD License"),
    ("Project relicensed from 4-clause BSD to the more common 3-clause BSD license.", "BSD License"),
])
def test_license_identifier_extract_licenses(license_text, expected_type):
    """Test the LicenseIdentifier can correctly extract license mentions from text."""
    identifier = LicenseIdentifier()
    print(f"Testing with text: {license_text}")
    
    license_mentions = identifier.extract_licenses(license_text)
    
    assert isinstance(license_mentions, list)
    assert len(license_mentions) > 0
    
    matched = any(expected_type in mention for mention in license_mentions)
    assert matched, f"Expected to find '{expected_type}' in {license_mentions}"

# AI generated test cases: https://g.co/gemini/share/4d26a9c0cbc8
@pytest.mark.parametrize("license_text, expected_type", [
    # --- Creative Commons (CC) False Positives ---
    ("Join our creative team meeting in the commons area.", "Creative Commons (CC)"),
    ("Please CC the manager on this email thread regarding attribution.", "Creative Commons (CC)"),
    ("Share your ideas freely; we encourage creative input.", "Creative Commons (CC)"),
    ("This public domain photo requires no attribution.", "Creative Commons (CC)"), # Mentions related concepts but not CC license itself
    ("Her work involved noncommercial research into derivatives.", "Creative Commons (CC)"),
    ("He made a creative contribution, alike to previous efforts.", "Creative Commons (CC)"),
    ("The park rules allow sharing picnics in the commons.", "Creative Commons (CC)"),
    ("Attribution of blame is not productive here; let's be creative.", "Creative Commons (CC)"),
    ("We need a common strategy for creative content distribution.", "Creative Commons (CC)"),
    ("Carbon Copy (CC) is an outdated method; use digital sharing.", "Creative Commons (CC)"),

    # --- GNU GPL False Positives ---
    ("The gnu is a fascinating animal found in Africa's general public reserves.", "GNU GPL"),
    ("Check the Gas Pressure Level (GPL) before starting.", "GNU GPL"),
    ("Generally, public distribution requires a specific license.", "GNU GPL"), # Discusses licensing generally
    ("This is free software, but not necessarily under the GNU license.", "GNU GPL"), # Explicitly ambiguous/negative
    ("We need to copyleft alignment on this document.", "GNU GPL"), # Nonsensical use of copyleft
    ("The source code is available upon request for general review.", "GNU GPL"),
    ("Modification is permitted, subject to our internal public rules.", "GNU GPL"),
    ("The Free Software Foundation (FSF) advocates for user freedom, often via GPL.", "GNU GPL"), # Mentions FSF/GPL contextually, not applying it
    ("Version 3 (v3) of the general guidelines is now public.", "GNU GPL"),
    ("Ensure the GNU compiler collection is installed for this project.", "GNU GPL"), # Mentions GNU tool, not license

    # --- MIT License False Positives ---
    ("She received her degree from MIT.", "MIT License"),
    ("Permission is granted, provided you submit the license paperwork.", "MIT License"), # Generic permission/license
    ("Make copies of the software installation guide for the team.", "MIT License"),
    ("Access is free of charge, but usage requires MIT affiliation.", "MIT License"),
    ("Use this software without restriction during the trial period.", "MIT License"),
    ("We need to modify, merge, and publish these findings soon.", "MIT License"),
    ("You can distribute copies, but not sublicense or sell them.", "MIT License"), # Sounds like license terms, but isn't MIT specifically
    ("The copyright notice must remain intact on all copies.", "MIT License"), # Generic requirement
    ("He submitted his work for review at the Massachusetts Institute of Technology.", "MIT License"),
    ("This library offers permissive use, similar to the MIT style.", "MIT License"), # Comparison, not application

    # --- Apache License False Positives ---
    ("Configure the Apache web server settings for version 2.0.", "Apache License"),
    ("The Apache Software Foundation (ASF) hosts many projects.", "Apache License"), # Mentions ASF contextually
    ("This work is based on the original study; see the notice.", "Apache License"),
    ("Any derivative works require permission from the foundation.", "Apache License"), # Ambiguous 'foundation'
    ("Each contributor must sign the patent agreement.", "Apache License"),
    ("The trademark license is pending approval.", "Apache License"), # Different type of license
    ("We received a contribution from the Apache county.", "Apache License"),
    ("This software requires Java version 2.0 or higher.", "Apache License"), # Version number collision
    ("Attach the NOTICE file containing contributor information.", "Apache License"), # Generic file name
    ("His work on the project was a significant contribution.", "Apache License"),

    # --- BSD License False Positives ---
    ("He earned a Bachelor of Science Degree (BSD) in computer science.", "BSD License"),
    ("Redistribution of assets requires board approval.", "BSD License"),
    ("Use of source materials is restricted to authorized personnel.", "BSD License"),
    ("Binary forms of the data are stored separately.", "BSD License"),
    ("Modification requests must follow the 3-clause procedure.", "BSD License"), # Arbitrary clause number
    ("Ensure the copyright notice and list of conditions are clear.", "BSD License"), # Generic terms
    ("Read the disclaimer before using the equipment.", "BSD License"), # Generic term
    ("This is a simplified version, not the new BSD model.", "BSD License"), # Vague comparison
    ("Source code access is granted under specific conditions.", "BSD License"),
    ("The Berkeley Software Distribution influenced many systems.", "BSD License"), # Historical/contextual mention
])
def test_license_identifier_false_positives(license_text, expected_type):
    """Test the LicenseIdentifier does not incorrectly identify false positives."""
    identifier = LicenseIdentifier()
    print(f"Testing with text: {license_text}")
    
    license_mentions = identifier.extract_licenses(license_text)
    
    assert isinstance(license_mentions, list)
    assert len(license_mentions) == 0, f"Expected no license mentions, but found: {license_mentions}"

@pytest.mark.parametrize("website_data", read_urls("data/direct_license_websites.json"))
def test_direct_license_detection(website_data):
    test_url = website_data["website"]
    expected_license_link = website_data["expected"]

    detector = LicenseDetector()
    res = detector.scan_websites([test_url])

    assert res[0].get("licenseLink") == expected_license_link[0], "License link mismatch"
    assert res[0].get("licenseType") == expected_license_link[1], "License type mismatch"

@pytest.mark.parametrize("website_data", read_urls("data/license_mentions_websites.json"))
def test_license_mentions_in_text(website_data):
    _test_website_data(website_data, "licenseMentions")

@pytest.mark.parametrize("website_data", read_urls("data/license_types_websites.json"))
def test_license_types_in_text(website_data):
    _test_website_data(website_data, "licenseType")

def _test_website_data(website_data, result_key):
    test_url = website_data["website"]
    expected_items = website_data["expected"]

    detector = LicenseDetector()
    result = detector.scan_websites([test_url])
    actual_items = result[0].get(result_key)
    if isinstance(actual_items, str):
        actual_items = [actual_items]

    assert len(actual_items) == len(set(actual_items)), "Duplicate items found"
    assert set(actual_items) == set(expected_items), "Mismatch between actual and expected items"



def test_processing_time_performance():
    """Test that the average processing time of websites is less than or equal to 5 seconds."""
    direct_license_sites = read_urls("data/direct_license_websites.json")
    license_mentions_sites = read_urls("data/license_mentions_websites.json")
    
    all_sites = direct_license_sites + license_mentions_sites
    
    detector = LicenseDetector()
    
    urls = [site["website"] for site in all_sites]
    
    start_time = time.time()
    detector.scan_websites(urls)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time_per_site = total_time / len(urls)
    
    print(f"Average processing time per site: {avg_time_per_site:.2f} seconds")
    print(f"Total time for {len(urls)} sites: {total_time:.2f} seconds")
    
    assert avg_time_per_site <= 5, f"Average processing time per site ({avg_time_per_site:.2f}s) exceeds 5 seconds"