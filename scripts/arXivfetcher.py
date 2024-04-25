import requests
import xml.etree.ElementTree as ET

def fetch_arxiv_data(arxiv_url):
    # arXivのIDをURLから抽出
    arxiv_id = arxiv_url.split('/')[-1]
    
    # APIを通じてメタデータを取得
    api_url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        # XMLレスポンスの解析
        root = ET.fromstring(response.content)
        
        # エントリーごとに情報を取得
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            authors = [author.find('{http://www.w3.org/2005/Atom}name').text.strip() for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
            
            # abstractの整形
            abstract = ' '.join(abstract.replace('\n', ' ').split())
            
            # BibTeX情報を取得
            bibtex_url = f'https://arxiv.org/bibtex/{arxiv_id}'
            bibtex_response = requests.get(bibtex_url)
            if bibtex_response.status_code == 200:
                bibtex = bibtex_response.text.strip()
            else:
                bibtex = "BibTeX information could not be fetched."
            
            # Markdown形式で出力
            print(f"## 書誌情報")
            print(f"### タイトル\n{title}\n \n ")
            print(f"### URL\n{arxiv_url}\n \n")
            print(f"### 著者\n{', '.join(authors)}\n \n")
            print(f"### 概要\n{abstract}\n")
            print(f"### BibTeX\n```bibtex\n{bibtex}\n```")
    else:
        print("Failed to fetch data from arXiv API.")

# ユーザーからの入力を受け取る
arxiv_link = input("Enter the arXiv link: ")
fetch_arxiv_data(arxiv_link)

