import pandas as pd
import numpy as np

class ValidationService:
    def __init__(self):
        pass

    def validate_pnl_data(self, file_path: str):
        df = pd.read_csv(file_path)
        df_t = df.set_index("Line Item").T
        gp_valid = df_t["Gross Profit"] == (df_t["Revenue"] - df_t["COGS"])
        oi_valid = df_t["Operating Income"] == (df_t["Gross Profit"] - df_t["Operating Expenses"])
        warnings = []
        success = []
        for quarter in df_t.index:
            if not gp_valid[quarter]:
                warnings.append(f"{quarter}: Error en Gross Profit. no cumple con la formula: Revenue - COGS ")
            if not oi_valid[quarter]:
                warnings.append(f"{quarter}: Error en Operating Income. no cumple con la formula: Gross Profit - Operating Expenses ")
            if gp_valid[quarter] and oi_valid[quarter]:
                success.append(f"{quarter}: Todo correcto con los datos de PNL en las columnas Gross Profit y Operating Income")
        return warnings, success
    def validate_balance_data(self, file_path: str):
        # 1. Cargar el archivo CSV
        df = pd.read_csv(file_path)

        # 2. Transponer el DataFrame para tener fechas como índices
        df_t = df.set_index("Line Item").T

        # 3. Inicializar listas de resultados
        errores = []
        warnings = []
        success = []

        # Error 1: Total Assets debe ser la suma de Cash, Accounts Receivable, Inventory y PP&E
        suma_activos = df_t["Cash"] + df_t["Accounts Receivable"] + df_t["Inventory"] + df_t["PP&E"]
        for fecha in df_t.index:
            if not np.isclose(suma_activos[fecha], df_t["Total Assets"][fecha]):
                errores.append(
                    f"{fecha}: Total Assets incorrecto. Esperado {suma_activos[fecha]}, obtenido {df_t['Total Assets'][fecha]}"
                )
            else:
                success.append(f"{fecha}: Total Assets correcto. Esperado {suma_activos[fecha]}, obtenido {df_t['Total Assets'][fecha]}")
            

        # Error 2: Valores negativos en activos clave
        for col in ["Cash", "Accounts Receivable", "Inventory", "PP&E"]:
            negativos = df_t[df_t[col] < 0]
            for fecha in negativos.index:
                errores.append(f"{fecha}: {col} tiene valor negativo ({df_t[col][fecha]})")
            else:
                success.append(f"{fecha}: {col} tiene valor correcto ({df_t[col][fecha]})")

        # Warning 1: Cuentas por cobrar con crecimiento superior al 25%
        accounts = df_t["Accounts Receivable"]
        growth = accounts.pct_change()
        for fecha in growth.index[1:]:
            if growth[fecha] > 0.25:
                warnings.append(f"{fecha}: Cuentas por cobrar crecieron un {growth[fecha]*100:.1f}%")
            else:
                success.append(f"{fecha}: Cuentas por cobrar crecieron un {growth[fecha]*100:.1f}%")

        # Warning 2: PP&E disminuye cada trimestre
        ppe = df_t["PP&E"]
        if all(ppe.iloc[i] > ppe.iloc[i + 1] for i in range(len(ppe) - 1)):
            warnings.append("PP&E disminuyó de forma continua en los 4 trimestres.")
        else:
            success.append("PP&E disminuyó de forma continua en los 4 trimestres.")

        # Warning 3: Caídas de efectivo mayores al 20%
        cash = df_t["Cash"]
        cash_change = cash.pct_change()
        for fecha in cash_change.index[1:]:
            if cash_change[fecha] < -0.2:
                warnings.append(f"{fecha}: El efectivo cayó un {cash_change[fecha]*100:.1f}%")
            else:
                success.append(f"{fecha}: El efectivo cayó un {cash_change[fecha]*100:.1f}%")
        return warnings, success