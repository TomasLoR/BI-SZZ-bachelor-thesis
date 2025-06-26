from license_checker import LicenseDetector, ModelManager

def main():
    """Main function to demonstrate the usage of the license_checker library."""
    
    # Define a list of websites to check
    websites = [
        "https://en.wikipedia.org",
        "https://www.wikiwand.com",
        "invalid_url.com",
    ]

    # Define an API key
    API_KEY = "my_api_key"

    # Define a question to ask the model
    question = "What kind of content can I scrape from this website?"

    
    print(f"Analyzing {len(websites)} websites for license information...\n")
    
    # Create a LicenseDetector instance
    # You can optionally provide a custom user-agent
    detector = LicenseDetector(user_agent="LicenseCheckerExample/1.0")
    
    try:
        # Scan the websites for license information
        results = detector.scan_websites(websites)
        
        # Process and display the results
        print("\nResults:")
        print("========\n")
        
        for result in results:
            website = result.get("website")
            print(f"Website: {website}")
            
            # Check if the URL is invalid
            if result.get("invalidUrl", False):
                print("  Status: Invalid URL")
                print("-" * 50)
                continue
                
            # Check if the website is blocked by robots.txt
            if result.get("blockedByRobotsTxt", False):
                print("  Status: Blocked by robots.txt")
                print("-" * 50)
                continue
                
            # Display license information if available
            license_link = result.get("licenseLink")
            if license_link:
                print(f"  License Link: {license_link}")
                print(f"  License Type: {result.get('licenseType', 'Unknown')}")
            else:
                print("  License Link: Not found")
                
            # Display any relevant links found
            relevant_links = result.get("relevantLinks", [])
            if relevant_links:
                print("  Relevant Links:")
                for link in relevant_links[:5]:  # Limit to first 5 links
                    print(f"    - {link}")
                if len(relevant_links) > 5:
                    print(f"    ... and {len(relevant_links) - 5} more")
                    
            # Display any license mentions found in the content
            license_mentions = result.get("licenseMentions", [])
            if license_mentions:
                print("  License Mentions:")
                for mention in license_mentions:
                    print(f"    - {mention}")
            
            # Display the first few words of the content if available
            content = result.get("content")
            if content:
                # Get first 50 words or fewer if content is shorter
                words = content.split()
                preview_words = words[:50]
                preview = ' '.join(preview_words)
                print("  Content Preview:")
                print(preview)
            
            print("-" * 50)
        
        # Demonstrate ModelManager usage for processing license text
        print("\nDemonstrating ModelManager functionality:")
        
        # Get a result with content
        content_result = next((r for r in results if r.get("content")), None)
        
        if content_result and content_result.get("content"):
            print("\nFound license text content to analyze.")
            
            try:
                model_manager = ModelManager()
                model = model_manager.get_model("googleai", API_KEY)
                result = model.summarize({"website": "example.com", "content": content_result.get("content")})
                print(f"\nSummary using Gemini model:\n{result.get('summary')}")
                
                # Demonstrate question answering using Mistral model
                print("\nDemonstrating Question Answering with Mistral model:")
                
                print(f"\nQuestion: {question}")
                try:
                    answer = model.answer_question(result, question)
                    print(f"Answer: {answer}")
                except Exception as e:
                    print(f"Error getting answer: {e}")
                
            except Exception as e:
                print(f"Error demonstrating models: {e}")
        else:
            print("No license text content found to demonstrate ModelManager functionality.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()