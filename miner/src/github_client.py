import os
import requests
from dotenv import load_dotenv

ruta_actual = os.path.dirname(__file__)
ruta_env = os.path.join(ruta_actual, '..', '.env')
load_dotenv(ruta_env)


class GithubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        token_crudo = os.getenv("GITHUB_TOKEN")
        self.token = token_crudo.strip() if token_crudo else None
        
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        else:
            print("No se encontró GITHUB_TOKEN")

    def _check_rate_limit(self, response):
        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining:
            if int(remaining) < 5:
                print(f"Quedan solo {remaining} peticiones a la API")
            elif int(remaining) == 0:
                print("GitHub ha bloqueado por exceso de peticiones")

    def search_popular_repos(self, language: str, page: int = 1, per_page: int = 5) -> list:
       
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": f"language:{language}",
            "sort": "stars",
            "order": "desc",
            "page": page,
            "per_page": per_page
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        self._check_rate_limit(response)
        
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Error al buscar repos: {response.status_code}")
            return []

    def get_files_from_repo(self, owner: str, repo: str, default_branch: str, extensions: tuple) -> list:
        
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        
        response = requests.get(url, headers=self.headers)
        self._check_rate_limit(response)
        
        file_urls = []
        if response.status_code == 200:
            tree = response.json().get("tree", [])
            for item in tree:
                if item["type"] == "blob" and item["path"].endswith(extensions):
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{item['path']}"
                    file_urls.append(raw_url)
        return file_urls

    def download_file_content(self, raw_url: str) -> str:
        response = requests.get(raw_url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        return ""