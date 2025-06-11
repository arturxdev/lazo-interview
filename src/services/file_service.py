import uuid
import pandas as pd

class FileService:
    def __init__(self):
        pass
    def parse_csv(self, path: str):
        try:
            return pd.read_csv(path)
        except Exception as e:
            return str(e)

    def parse_multiple_csv(self, paths: list[str]):
        errors = []
        for path in paths:
            result = self.parse_csv(path)
            if result:
                errors.append(result)
        return errors

    def download_file(self, url: str, type: str):
        try:
            url = url
            destino = f"./src/data/{type}_2025-{uuid.uuid4()}.csv"
            import requests
            with open(destino, 'wb') as f:
                response=requests.get(url)
                if response.status_code != 200:
                    raise ValueError(f"No se pudo descargar el archivo de {type}. Código: {response.status_code} url: {url}")
                f.write(response.content)
            return {"destino": destino,"status":True,"error":None}
        except Exception as e:
            return {"destino": None,"status":False,"error":str(e)}
    
    def download_multiple_files(self, file_configs):
        errors = []
        for file in file_configs:
            result = self.download_file(file.url, file.type)
            if result["status"]:
                file.local_path = result["destino"]
            else:
                errors.append(result["error"])
        return errors
