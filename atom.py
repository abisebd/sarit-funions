import requests
from bs4 import BeautifulSoup
from pytube import Search
from collections import defaultdict
import ssl
import certifi
from urllib.parse import urljoin
from flask import Flask, render_template
import json

app = Flask(__name__)

# SSL Configuration
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def normalize_url(url, base_url):
    if not url:
        return None
    if not url.startswith(('http://', 'https://')):
        return urljoin(base_url, url)
    return url

def scrape_website_links(url, keywords):
    try:
        response = requests.get(url, verify=certifi.where())
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        educational_links = []
        
        for link in links:
            href = link['href']
            if any(keyword in href.lower() for keyword in keywords):
                normalized_url = normalize_url(href, url)
                if normalized_url:
                    educational_links.append(normalized_url)
        
        return educational_links
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

def scrape_youtube_links(keywords):
    try:
        educational_links = []
        for keyword in keywords:
            print(f"Searching YouTube for: {keyword}")  # Debug line
            search = Search(keyword)
            for video in search.results[:5]:  # Limit to 5 results per keyword
                educational_links.append({
                    'url': video.watch_url,
                    'title': video.title
                })
        return educational_links
    except Exception as e:
        print(f"Error searching YouTube: {str(e)}")
        return []

def categorize_websites(links, categories):
    categorized_sites = defaultdict(list)
    for link in links:
        url = link['url'] if isinstance(link, dict) else link
        title = link.get('title', '') if isinstance(link, dict) else ''
        
        for category, keywords in categories.items():
            if any(keyword in url.lower() or 
                  (title and keyword in title.lower()) 
                  for keyword in keywords):
                categorized_sites[category].append(url)
    return categorized_sites

@app.route('/')
def index():
    content = {'websites': categorized_websites, 'youtube': categorized_youtube}
    print("Debug - Content:", content)  # Debug line
    return render_template('index.html', content=content)

if __name__ == "__main__":
    website_urls = [
        'https://www.wikipedia.org',
        'https://www.khanacademy.org',
        'https://www.coursera.org',
        'https://www.w3schools.com',
        'https://www.byjus.com',
        'https://www.vedantu.com'
    ]
    
    categories = {
        'Programming': ['python', 'java', 'code', 'programming', 'developer'],
        'Math': ['math', 'calculus', 'algebra', 'geometry'],
        'Science': ['physics', 'chemistry', 'biology', 'science'],
        'General Education': ['learn', 'course', 'education', 'tutorial']
    }
    
    youtube_keywords = ['programming tutorial', 'math course', 'science education']
    

    # Scrape websites
    all_website_links = []
    for url in website_urls:
        links = scrape_website_links(url, [k for keywords in categories.values() for k in keywords])
        all_website_links.extend(links)


    # Categorize links
    categorized_websites = categorize_websites(all_website_links, categories)


    # Print results
    print("\nCategorized Websites:")
    for category, links in categorized_websites.items():
        print(f"\n{category}:")
        for link in links:
            print(f"  - {link}")
    

    youtube_keywords = ['programming tutorial', 'math course', 'science education']

    print("\nFetching YouTube videos...")
    youtube_links = scrape_youtube_links(youtube_keywords)
    
    print(f"\nFound {len(youtube_links)} YouTube videos")
    categorized_youtube = categorize_websites(youtube_links, categories)

    print("\nCategorized YouTube Videos:")
    for category, links in categorized_youtube.items():
        if links:  # Only print categories that have videos
            print(f"\n{category}:")
            for link in links:
                print(f"  - {link}")

    app.run(debug=True, port=5000)

