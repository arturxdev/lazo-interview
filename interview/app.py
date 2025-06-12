from flask import Flask
import asyncio
import threading
from typing import Any
from interview.workflows.financial_audit_workflow import main_workflow
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, Lazo!"

@app.route("/audit")
def audit():
    print("Audit started")
    pnl_path = "https://gist.githubusercontent.com/arturxdev/e3f45f2a4ba49b450ad5361f755a5a74/raw/92b8fc20793d41ff6c98a7d34f6882e8967bba7b/pnl_2025.csv"
    balance_path = "https://gist.githubusercontent.com/arturxdev/2b05e59f4920517537a09fc3fd9c22bd/raw/64c46863e80e87054fc28628f4dba68b75659154/balance_2025.csv"
    
    def background_task():
        asyncio.run(main_workflow(pnl_path, balance_path))
    threading.Thread(target=background_task).start()
    
    return "Audit started in background"

if __name__ == "__main__":
    app.run(debug=True)