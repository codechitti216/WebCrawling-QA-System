import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_all_hyperlinks(url, parent_number, base_url, max_depth, visited=None, current_depth=1):
    if visited is None:
        visited = set()

    links = []
    k = 0 

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all hyperlinks
        links_in_page = [a['href'] for a in soup.find_all('a', href=True)]
        
        for i in links_in_page:
            # Convert relative URL to absolute URL
            absolute_url = urljoin(base_url, i)

            # Ensure the URL is unique
            if absolute_url in visited:
                continue

            visited.add(absolute_url)
            k += 1
            hierarchical_key = f"{parent_number}.{k}"
            links.append([absolute_url, hierarchical_key])
            
            # Recursively fetch child hyperlinks up to max_depth
            if current_depth < max_depth:
                child_links = get_all_hyperlinks(absolute_url, hierarchical_key, base_url, max_depth, visited, current_depth + 1)
                links.extend(child_links)
        
        return links
    except requests.exceptions.RequestException as e:
        return []

# URL to scrape
web_link = "https://info.cern.ch/hypertext/WWW/TheProject.html"

# Get all hyperlinks with hierarchy and a max depth of 2 for example
hyperlinks = get_all_hyperlinks(web_link, '1', web_link, max_depth=5)

# Print all hyperlinks with hierarchy
for link in hyperlinks:
    print(f"Hierarchy: {link[1]}, URL: {link[0]}")
