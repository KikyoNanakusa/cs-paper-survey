import requests
import xml.etree.ElementTree as ET
import os
from openai import OpenAI

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI()

def fetch_arxiv_data(arxiv_id):
    # APIを通じてメタデータを取得
    api_url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    response = requests.get(api_url)
    return response

def parse_arxiv_data(response):
    if response.status_code == 200:
        # XMLレスポンスの解析
        root = ET.fromstring(response.content)
        entry = root.find('{http://www.w3.org/2005/Atom}entry')
        if entry is not None:
            return {
                'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
                'abstract': ' '.join(entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ').split()),
                'authors': [author.find('{http://www.w3.org/2005/Atom}name').text.strip() for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
            }
    return None

def fetch_bibtex(arxiv_id):
    bibtex_url = f'https://arxiv.org/bibtex/{arxiv_id}'
    bibtex_response = requests.get(bibtex_url)
    if bibtex_response.status_code == 200:
        return bibtex_response.text.strip()
    return "BibTeX information could not be fetched."

def print_markdown(arxiv_url, data, bibtex):
    print(f"## 書誌情報")
    print(f"### タイトル\n{data['title']}\n \n ")
    print(f"### URL\n{arxiv_url}\n \n")
    print(f"### 著者\n{', '.join(data['authors'])}\n \n")
    print(f"### 概要\n{data['abstract']}\n")
    print(f"### BibTeX\n```bibtex\n{bibtex}\n```")
    
def summarize_abstract(client, text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the study objectives, methodology, results, and conclusions in Japanese using bullet points from the following . \n{text} ",
            }
        ],
        model="gpt-4",
        temperature=0
    )
    return chat_completion.choices[0].message.content

def main():
    arxiv_link = input("Enter the arXiv link: ")
    arxiv_id = arxiv_link.split('/')[-1]
    response = fetch_arxiv_data(arxiv_id)
    if response is not None:
        data = parse_arxiv_data(response)
        if data:
            bibtex = fetch_bibtex(arxiv_id)
            print_markdown(arxiv_link, data, bibtex)
        else:
            print("Failed to parse data from arXiv.")
    else:
        print("Failed to fetch data from arXiv API.")

if __name__ == "__main__":
    main()