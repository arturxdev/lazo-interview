import requests
class GithubService:
    def __init__(self,token: str):
        self.token = token
    def create_issue(self, title: str, body: str, labels: list[str] = ["audit"]):
        print(f"🔍 Creating issue: {title}")
        try:
            url = "https://api.github.com/repos/arturxdev/lazo-interview/issues"

            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            payload = {
                "title": title,
                "body": body,
                "assignees": ["arturxdev"],
                "labels": labels
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 201:
                raise Exception(f"Error creating issue: {response.status_code} {response.text}")
            return response.json()
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None