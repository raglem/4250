#-------------------------------------------------------------------------
# AUTHOR: your name
# FILENAME: scraper.py
# SPECIFICATION: description of the program
# FOR: CS 4250 - Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-------------------------------------------------------------------------

# Importing Python libraries
import requests
from bs4 import BeautifulSoup
from collections import deque
import re

# Defining the seed URL
seed = "https://testingurl.dev/scraping/links/circular"
baseURL = "https://testingurl.dev"

# Creating the frontier and seen collections
frontier = deque()
frontier.append(seed)
seen = set()
seen.add(seed)

# Crawling until the frontier is empty
while frontier:

    # Removing the first URL from the frontier
    url = frontier.popleft()

    # Retrieving and parsing the Web page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Printing the text contained in the <h1> element
    print(soup.h1.text)

    # Extracting and processing hyperlinks
    pattern = re.compile(r"^/scraping/links/circular")
    links = soup.find_all('a', href=pattern)
    for link in links:
        completed_link = baseURL + link['href']
        if completed_link in seen:
            continue
        frontier.append(completed_link)
        seen.add(completed_link)

# Printing all URLs in seen
print(seen)