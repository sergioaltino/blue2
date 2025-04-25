SUA_CHAVE_SERPAPI = "d355f1960e0f556f58f6f1d86e8253920cc38f2558cc3d7d0189ad65a775d684"
SUA_CHAVE_OPENAI = "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"

# blue_ocean/search.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from serpapi import GoogleSearch
from openai import OpenAI

client = OpenAI(api_key=SUA_CHAVE_OPENAI)

def crawl_website(base_url: str, max_pages=10):
    visited = set()
    to_visit = [base_url]
    content = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                visited.add(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                content.append(soup.get_text())
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if next_url.startswith(base_url) and next_url not in visited:
                        to_visit.append(next_url)
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")
    return "\n".join(content)

def infer_company_name_and_sector(text):
    prompt = f"""
    A partir do seguinte conteúdo extraído de um site institucional, identifique:
    1. O nome da empresa (máximo 5 palavras).
    2. O setor de atuação (ex: saúde, tecnologia educacional, energia renovável, etc).

    Texto:
    {text[:3000]}

    Responda no formato:
    Empresa: <nome>
    Setor: <setor>
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    lines = response.choices[0].message.content.split("\n")
    company = next((line.replace("Empresa:", "").strip() for line in lines if "Empresa:" in line), "Empresa Desconhecida")
    sector = next((line.replace("Setor:", "").strip() for line in lines if "Setor:" in line), "setor indefinido")
    return company, sector

def search_competitors_by_website(url: str, n=10):
    site_text = crawl_website(url)
    company_name, sector = infer_company_name_and_sector(site_text)

    query = f"principais concorrentes no setor de {sector}"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SUA_CHAVE_SERPAPI
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    competitors = {}
    for result in results.get("organic_results", [])[:n]:
        title = result.get("title")
        snippet = result.get("snippet")
        if title and snippet:
            competitors[title] = snippet
    return company_name, site_text, competitors