import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
import os

def parse_html(html):
    """Parse HTML with BeautifulSoup and extract text (removing scripts/styles)."""
    soup = BeautifulSoup(html, 'html.parser')
    for element in soup(['script', 'style']):
        element.decompose()
    return soup.get_text(separator=' ', strip=True)

async def fetch_content(session, url):
    """Fetch page content asynchronously and extract text."""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                return parse_html(html)
            else:
                print(f"Failed to fetch {url}: HTTP {response.status}")
                return ""
    except Exception as e:
        print(f"Exception fetching {url}: {e}")
        return ""

async def update_story(story, session):
    """
    Given a story dictionary, if it has a URL but no content,
    fetch the external page content and update the 'content' field.
    """
    url = story.get("url", "")
    # Only fetch if URL is present and content is empty.
    if url and (not story.get("content") or not story.get("content").strip()):
        print(f"Fetching external content for story {story.get('id')} from {url}")
        story["content"] = await fetch_content(session, url)
    return story

async def update_all_stories(stories):
    """
    Update all stories concurrently by fetching external content for each story
    that has a URL and empty content.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [update_story(story, session) for story in stories]
        updated_stories = await asyncio.gather(*tasks)
        return updated_stories

def main():
    # Change this filename to match the JSON file created earlier.
    filename = "top_100_stories_2025-02-12.json"
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return

    # Load the stories from the JSON file.
    with open(filename, "r", encoding="utf-8") as f:
        stories = json.load(f)

    # Run the asynchronous updates.
    updated_stories = asyncio.run(update_all_stories(stories))

    # Write the updated stories back to the file.
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(updated_stories, f, indent=2, ensure_ascii=False)

    print(f"Updated {len(updated_stories)} stories in {filename}")

if __name__ == "__main__":
    main()
