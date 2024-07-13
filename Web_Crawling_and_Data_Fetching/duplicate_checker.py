import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Directory containing the .txt files
directory = "../Data/Raw_Data"

# Function to read the content of a .txt file
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# List to store the content of each file
texts = []
file_names = []

# Read the content of each .txt file in the directory
for file_name in os.listdir(directory):
    if file_name.endswith(".txt"):
        file_path = os.path.join(directory, file_name)
        texts.append(read_text_file(file_path))
        file_names.append(file_name)

# Create a TF-IDF vectorizer and transform the texts
vectorizer = TfidfVectorizer().fit_transform(texts)
vectors = vectorizer.toarray()

# Calculate cosine similarity between all pairs of texts
cosine_similarities = cosine_similarity(vectors)

# Find duplicate pairs based on a similarity threshold
threshold = 0.9
duplicate_pairs = []

for i in range(len(file_names)):
    for j in range(i+1, len(file_names)):
        if cosine_similarities[i][j] > threshold:
            duplicate_pairs.append((file_names[i], file_names[j]))

# Print the duplicate pairs
if duplicate_pairs:
    print("Duplicate pairs:")
    for pair in duplicate_pairs:
        print(pair)
else:
    print("No duplicate pairs found.")
