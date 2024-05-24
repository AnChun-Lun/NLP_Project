import requests
from bs4 import BeautifulSoup
import time
import random

# List of headers to rotate through
headers_list = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'},
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 335) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Mobile Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'},
]

# Calls other functions for links/text
def get_page_content(url, session, max_retries=5):
    for _ in range(max_retries):
        headers = random.choice(headers_list)  # Randomly select a header from the list
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 403:
                print("403 Forbidden - Retrying with a different header")
                print(url)
                continue
            response.raise_for_status()  # HTTP error exception
            return response.content
        except requests.RequestException as e:
            print(f"Failed to retrieve the webpage. Error: {e}")
    print(f"Max retries exceeded for URL: {url}")
    return None

# Get the links of all articles from thehackernews.com
def get_article_links(homepage_url, session):
    all_links = []
    next_page_url = homepage_url
    
    # Loop until no more "Next page" button
    while next_page_url:
        content = get_page_content(next_page_url, session)
        if content is None:
            break

        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find_all('a', class_='story-link')
        links = [article['href'] for article in articles if 'href' in article.attrs]
        all_links.extend(links)

        # Check "Next page" button
        next_page_button = soup.find('a', class_='blog-pager-older-link-mobile')
        next_page_url = next_page_button['href'] if next_page_button else None

    return all_links

# Get title, text, and link of an article
def get_article_details(article_url, session):
    content = get_page_content(article_url, session)
    if content is None:
        return None, None

    soup = BeautifulSoup(content, 'html.parser')
    try:
        title = soup.find('h1', class_='story-title').get_text(strip=True)
        article_body = soup.find('div', class_='articlebody clear cf')
        paragraphs = article_body.find_all('p')
        article_text = "\n".join([para.get_text(strip=True) for para in paragraphs])
        keywords = soup.find('meta', name="keywords")
        keywords = keywords["content"] if keywords else None
        return title, article_text, keywords
    except AttributeError as e:
        print(f"Failed to parse article details. Error: {e}")
        return None, None

# Main
def scrape_hackernews():
    homepage_url = 'https://thehackernews.com/'
    
    with requests.Session() as session:
        article_links = get_article_links(homepage_url, session)
        articles = []

        for link in article_links:
            title, text, keywords = get_article_details(link, session)
            if title and text:
                articles.append({'title': title, 'text': text, 'keywords': keywords, 'link': link})
                print(f"Scraped article: {title}")
            else:
                print(f"Skipping an article due to missing content.")
            time.sleep(random.uniform(2, 4))  # Time between attempts

        return articles

