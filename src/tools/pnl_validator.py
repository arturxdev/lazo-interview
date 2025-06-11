import asyncio
import sys
from typing import Any
from pydantic import BaseModel, Field
from beeai_framework.tools import StringToolOutput, Tool, ToolRunOptions
from beeai_framework.context import RunContext
from beeai_framework.emitter import Emitter
from beeai_framework.errors import FrameworkError


class DataPNL(BaseModel):
    revenue: float
    cogs: float
    gross_profit: float

class ValidatorPNLToolInput(BaseModel):
    """Input for the ValidadorPNLTool."""
    pnl_data:DataPNL = Field(
        description="The P&L data to validate.",
        example=DataPNL(revenue=100000, cogs=40000, gross_profit=58000)
    )

class ValidatorPNLTool(Tool[ValidatorPNLToolInput, ToolRunOptions, StringToolOutput]):
    """Tool for validating Profit & Loss statement calculations."""
    
    name = "ValidadorPNLTool"
    description = "Validates that Gross Profit equals Revenue minus COGS in a P&L statement and returns a descriptive message about any inconsistencies."
    input_schema = ValidatorPNLToolInput
    def __init__(self, options: dict[str, Any] | None = None) -> None:
        super().__init__(options)
        self._emitter = self._create_emitter()
        
    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(
            namespace=["tool", "pnl_validator"],
            creator=self,
        )
    
    async def _run(self, input: ValidatorPNLToolInput, options: ToolRunOptions|None, context: RunContext) -> StringToolOutput:
        """
        Validates the P&L statement calculations and returns a descriptive message.
        
        Args:
            pnl_data (Dict[str, Any]): Dictionary containing P&L data with keys:
                - revenue: Total revenue
                - cogs: Cost of Goods Sold
                - gross_profit: Gross Profit
        
        Returns:
            str: A descriptive message about the validation results
        """
        try:
            revenue = input.pnl_data.revenue
            cogs = input.pnl_data.cogs
            actual_gross_profit = input.pnl_data.gross_profit
            
            expected_gross_profit = revenue - cogs
            difference = expected_gross_profit - actual_gross_profit
            if abs(difference) < 0.01:
                return StringToolOutput(
                    result=f"✅ Validación exitosa: El cálculo de Gross Profit es correcto.\n" \
                       f"Revenue: ${revenue:,.2f}\n" \
                       f"COGS: ${cogs:,.2f}\n" \
                       f"Gross Profit: ${actual_gross_profit:,.2f}",
                    
                )
            else:
                return StringToolOutput(
                    result=f"❌ Inconsistencia detectada en el cálculo de Gross Profit:\n" \
                       f"Revenue: ${revenue:,.2f}\n" \
                       f"COGS: ${cogs:,.2f}\n" \
                       f"Gross Profit reportado: ${actual_gross_profit:,.2f}\n" \
                       f"Gross Profit esperado: ${expected_gross_profit:,.2f}\n" \
                       f"Diferencia: ${abs(difference):,.2f}",
                   
                )
        except (ValueError, TypeError) as e:
            return StringToolOutput(
                result=f"❌ Error en los datos: {str(e)}\n" \
                   f"Por favor asegúrese de que todos los valores sean números válidos.",
            )

async def main():
    tool = ValidatorPNLTool()
    input = ValidatorPNLToolInput(pnl_data=DataPNL(revenue=100000, cogs=40000, gross_profit=58000))
    result = await tool.run(input)
    print(result)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except FrameworkError as e:
        sys.exit(e.explain())