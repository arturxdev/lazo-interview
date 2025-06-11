# from src.agents.auditor_agent import create_auditor_agent
# from src.tools.pnl_validator import DataPNL
from typing import Any
from src.workflows.financial_audit_workflow import main_workflow


async def main():
    pnl_path = "https://gist.githubusercontent.com/arturxdev/e3f45f2a4ba49b450ad5361f755a5a74/raw/92b8fc20793d41ff6c98a7d34f6882e8967bba7b/pnl_2025.csv"
    balance_path = "https://gist.githubusercontent.com/arturxdev/2b05e59f4920517537a09fc3fd9c22bd/raw/64c46863e80e87054fc28628f4dba68b75659154/balance_2025.csv"
    await main_workflow(pnl_path, balance_path)
