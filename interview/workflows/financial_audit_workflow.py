from beeai_framework.workflows import Workflow
from pydantic import BaseModel, ConfigDict
from typing import Optional
from interview.services.file_service import FileService
from interview.services.validation_service import ValidationService
from interview.agents.model import Model
from interview.services.github_servide import GithubService
import os
from dotenv import load_dotenv
load_dotenv()

class FileConfig(BaseModel):
    url: Optional[str] = None
    local_path: Optional[str] = None
    type: Optional[str] = None

class ValidateDataState(BaseModel):
    report: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success:Optional[list[str]] = []
    warnings: Optional[list[str]] = []
    errors: Optional[list[str]] = []
    files: Optional[list[FileConfig]] = []

model = Model(is_production=os.getenv("IS_PRODUCTION"))
print(f"Model: {model.get_model()}")

def download_csv(state: ValidateDataState):
    print("📂 Descargando el archivo CSV...")
    file_service = FileService()
    state.errors = file_service.download_multiple_files(file_configs=state.files)
    return "report_errors" if len(state.errors) > 0 else Workflow.NEXT

def parse_csv(state: ValidateDataState):
    print("🔍 Verificando el formato del archivo CSV...")
    file_service = FileService()
    state.errors = file_service.parse_multiple_csv([file.local_path for file in state.files])
    return "report_errors" if len(state.errors) > 0 else Workflow.NEXT

def validate_pnl_data(state: ValidateDataState):
    print("🔍 Validando los datos de PNL...")
    validation_service = ValidationService()
    file = next((x for x in state.files if x.type == "pnl"), None)
    result= validation_service.validate_pnl_data(file.local_path)
    state.warnings += result[0]
    state.success += result[1]
    return Workflow.NEXT

def validate_balance_data(state: ValidateDataState):
    print("🔍 Validando los datos de Balance...")
    validation_service = ValidationService()
    file = next((x for x in state.files if x.type == "balance"), None)
    result= validation_service.validate_balance_data(file.local_path)
    state.warnings += list(result[0])
    state.success += list(result[1])
    return Workflow.NEXT

async def make_report(state: ValidateDataState):
    print("🔍 Haciendo el reporte...")
    print("🔍 Iniciando auditoría del estado de resultados...\n")
    github_service = GithubService(token=os.getenv("GITHUB_TOKEN"))
    
    prompt = f"""
        Act as a professional financial auditor and write a validation report for a business owner who will present these numbers to executives or investors.

        You will receive three lists:
        - `success`: validations that passed correctly.
        - `warnings`: issues that are not critical errors but deserve attention.
        - `errors`: discrepancies that should be fixed before the final report is shared.

        You must structure the report using only the following three sections:

        ✅ What’s Working  
        ⚠️ What Needs Attention  
        ❌ What’s Wrong

        For each section:
        - List the items from the corresponding array.
        - Use clear, business-friendly language that is easy to understand but still professional.
        - Do not add extra sections or change the structure.
        - Keep the tone direct, helpful, and focused on actionable insights.

        Do not include a title, introduction, or summary—just the three sections in that order.

        Here is the data to validate:
        success:
        {", ".join(state.success)}
        warnings:
        {", ".join(state.warnings)}
        errors:
        {", ".join(state.errors)}
    """
    result = await model.create(prompt)
    state.report = result.get_text_content()
    print(state.report)
    print("=======")
    github_service.create_issue(title="Financial Audit Report", body=state.report)
    return Workflow.END

async def report_errors(state: ValidateDataState):
    print("🔍 Reportando errores...")
    github_service = GithubService(token=os.getenv("GITHUB_TOKEN"))
    prompt = f"""
        You are a professional financial auditor. You have received a list of accounting or financial inconsistencies.

        Your task is to write a clear, concise, and professional report that can be easily understood by a business owner who may present this information to executives, investors, or internal stakeholders.

        The report must be structured using exactly **three sections**:

        ---

        ❌ What’s Wrong  
        Clearly and concisely explain what is incorrect or inconsistent in each case. Avoid technical jargon. Use plain business language and bullet points if helpful.

        🛠️ How to Fix It  
        Provide simple, actionable suggestions to address each issue described above. Be brief and direct — your goal is to help the business owner understand what needs to be done and why.

        📊 Proof of Error  
        Present specific data that demonstrates the problem. This could include:
        - Numeric discrepancies (e.g., "Gross Profit = 60,000, but Revenue - COGS = 55,000")
        - Trend anomalies (e.g., "Cash dropped 30% from Q2 to Q3")
        - Mismatches between totals and line items
        - URLs to the file and the line number of the error

        Use this section to back up the issues raised with clear, direct evidence.

        ---

        Here is the data to validate:  
        errors:

        {", ".join(state.errors)}
    """
    result = await model.create(prompt)
    state.report = result.get_text_content()
    print(state.report)
    github_service.create_issue(title="Financial has failed", body=state.report, labels=["invalid"])
    return Workflow.END


async def main_workflow(pnl_url: str,balance_url: str):
    print("Starting workflow...")
    workflow = Workflow(schema=ValidateDataState, name="CleanDataAgent")
    workflow.add_step("download_files", download_csv)
    workflow.add_step("parse_files", parse_csv)
    workflow.add_step("validate_pnl_data", validate_pnl_data)
    workflow.add_step("validate_balance_data", validate_balance_data)
    workflow.add_step("make_report", make_report)
    workflow.add_step("report_errors", report_errors)
    result = await workflow.run(ValidateDataState(files=[FileConfig(url=pnl_url,type="pnl"),FileConfig(url=balance_url,type="balance")]))
    return result

