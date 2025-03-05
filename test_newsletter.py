import asyncio
import argparse
from dotenv import load_dotenv
from assistant.research_newsletter_runner import NewsletterRunner

# Load environment variables from .env file
load_dotenv()

async def test_newsletter(use_two_phase=True, max_normal_categories=2):
    # Initialize the runner
    runner = NewsletterRunner()
    
    # Define categories (optional - will use defaults if not specified)
    categories = [
        "Big Tech & Startups",
        "Robotics & Autonomous Systems",
        "Blockchain & Decentralized Systems",
        # "Artificial Intelligence & Public Policy",
    ]
    
    print("Generating newsletter...")
    print("This may take a few minutes as it performs searches for each category.")
    
    # Run the newsletter generation
    result = await runner.run(
        categories=categories,
        date="2025-03-04"  # You can change this date
    )
    
    # Print the results
    print("\n=== TLDR Summary ===")
    print(result["tldr_summary"])
    
    print("\n=== Sources ===")
    print("Number of sources gathered:", len(result["sources"]))
    for source in result["sources"][:10]:  # Show first 10 sources
        print(f"- {source}")

if __name__ == "__main__":
    asyncio.run(test_newsletter()) 