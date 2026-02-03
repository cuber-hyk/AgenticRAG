import os
import requests
from typing import List, Optional


class AgenticRAGClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def chat(self, session_id: str, query: str) -> dict:
        url = f"{self.base_url}/api/chat"
        resp = requests.post(url, json={"session_id": session_id, "query": query})
        resp.raise_for_status()
        return resp.json()

    def upload(self, file_paths: List[str]) -> dict:
        url = f"{self.base_url}/api/upload"
        files = [("files", (os.path.basename(p), open(p, "rb"))) for p in file_paths]
        try:
            resp = requests.post(url, files=files)
            resp.raise_for_status()
            return resp.json()
        finally:
            for _, (_, f) in files:
                f.close()
