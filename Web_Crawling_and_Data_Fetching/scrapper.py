import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_all_hyperlinks(url, base_url, max_depth, visited=None, current_depth=1):
    if visited is None:
        visited = set()

    links = []
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
            links.append(absolute_url)
            
            # Recursively fetch child hyperlinks up to max_depth
            if current_depth < max_depth:
                child_links = get_all_hyperlinks(absolute_url, base_url, max_depth, visited, current_depth + 1)
                links.extend(child_links)
        
        return links
    except requests.exceptions.RequestException:
        return []

def fetch_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except requests.exceptions.RequestException:
        return ""

def remove_duplicates(links):
    texts = [fetch_text(link) for link in links]
    
    vectorizer = TfidfVectorizer().fit_transform(texts)
    vectors = vectorizer.toarray()
    
    cosine_similarities = cosine_similarity(vectors)
    
    threshold = 0.9
    unique_links = []
    unique_texts = []
    seen = set()
    
    for i in range(len(links)):
        if i in seen:
            continue
        is_duplicate = False
        for j in range(i + 1, len(links)):
            if j in seen:
                continue
            if cosine_similarities[i][j] > threshold:
                is_duplicate = True
                seen.add(j)
        if not is_duplicate:
            unique_links.append(links[i])
            unique_texts.append(texts[i])
    
    return unique_links, unique_texts

def save_links_and_content(links, texts):
    hierarchical_links = []
    parent_number = '1'
    k = 0
    for link in links:
        k += 1
        hierarchical_key = f"{parent_number}.{k}"
        hierarchical_links.append((hierarchical_key, link))
    
    if not os.path.exists("Data"):
        os.makedirs("Data")
    
    with open(os.path.join("../Data", "links.txt"), "w") as file:
        for key, link in hierarchical_links:
            file.write(f"{key}, {link}\n")
    
    print("Links saved to Data/links.txt")
    
    folder_name = "..//Data/Raw_Data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    for i, (key, link) in enumerate(hierarchical_links):
        file_name = f"{key}.txt"
        file_path = os.path.join(folder_name, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(texts[i])
            print(f"Text data saved to {file_path}")
        except IOError as e:
            print(f"An error occurred while saving {file_path}: {e}")

# URL to scrape
web_link = "https://info.cern.ch/hypertext/WWW/TheProject.html"

# Get all hyperlinks with a max depth of 1 for example
all_hyperlinks = get_all_hyperlinks(web_link, web_link, max_depth=1)

# Remove duplicates
unique_links, unique_texts = remove_duplicates(all_hyperlinks)

# Save links and content
save_links_and_content(unique_links, unique_texts)
