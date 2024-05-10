import requests
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET

def create_github_issue(title, body, token, repo):
    """GitHubのIssueを作成する"""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": body
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Issue created successfully.")
        print("Issue URL:", response.json()['html_url'])
    else:
        print("Failed to create issue.")
        print("Response:", response.content)

def fetch_arxiv_data(arxiv_id):
    api_url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    response = requests.get(api_url)
    return response

def fetch_bibtex(arxiv_id):
    bibtex_url = f'https://arxiv.org/bibtex/{arxiv_id}'
    bibtex_response = requests.get(bibtex_url)
    if bibtex_response.status_code == 200:
        return bibtex_response.text.strip()
    return "BibTeX information could not be fetched."

def print_markdown(arxiv_url, data, bibtex, token, repo):
    markdown_content = (
        f"## 書誌情報\n"
        f"### タイトル\n{data['title']}\n \n"
        f"### URL\n{arxiv_url}\n \n"
        f"### 著者\n{', '.join(data['authors'])}\n \n"
        f"### 概要\n{data['abstract']}\n"
        f"### BibTeX\n```bibtex\n{bibtex}\n```"
    )
    create_github_issue(data['title'], markdown_content, token, repo)

def parse_arxiv_data(response):
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        entry = root.find('{http://www.w3.org/2005/Atom}entry')
        if entry is not None:
            return {
                'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
                'abstract': ' '.join(entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ').split()),
                'authors': [author.find('{http://www.w3.org/2005/Atom}name').text.strip() for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
            }
    return None

def main():
    load_dotenv()  # 環境変数のロード
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO")

    if GITHUB_TOKEN and GITHUB_REPO:
        print("GitHub Token and Repository loaded successfully.")
    else:
        print("Failed to load GitHub Token or Repository. Please check your .env file.")
        return  # エラー時に処理を停止

    arxiv_link = input("Enter the arXiv link: ")
    arxiv_id = arxiv_link.split('/')[-1]
    response = fetch_arxiv_data(arxiv_id)
    if response is not None:
        data = parse_arxiv_data(response)
        if data:
            bibtex = fetch_bibtex(arxiv_id)
            print_markdown(arxiv_link, data, bibtex, GITHUB_TOKEN, GITHUB_REPO)
        else:
            print("Failed to parse data from arXiv.")
    else:
        print("Failed to fetch data from arXiv API.")

if __name__ == "__main__":
    main()

