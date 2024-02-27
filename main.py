from fastapi import FastAPI
import uvicorn
from enum import Enum


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World cositas"}


@app.get("/mortgage")
async def mortgage_calculator(
    cash: float,
    housing_price: float,
    housing_tasation: float = 0,
    main_house: bool = True,
    second_hand: bool = True,
    notaria_fees: float = 700.0,
    registro_fees: float = 420.0,
    gestoria_fees: float = 375.0,
    tasation_fees: float = 335.0,
    inmobilaria_pertcentage_fee: float = 0.03,
):
    """
    info
    """
    if second_hand:
        if main_house:
            ITP = housing_price * 0.04
        else:
            ITP = housing_price * 0.06
    else:
        ITP = housing_price * 0.10  # IVA
    if housing_tasation == 0:
        housing_tasation = housing_price
    gastos_derivados = (
        ITP + notaria_fees + registro_fees + gestoria_fees + tasation_fees
    )
    gastos_agencia = inmobilaria_pertcentage_fee * housing_price
    total_gastos = gastos_derivados + gastos_agencia
    cash_entrada_efectivo = cash - total_gastos
    financiacion_necesaria = housing_price - cash_entrada_efectivo
    financiacion_necesaria_percent = financiacion_necesaria / housing_price
    prestamo_80percent_tasation = housing_tasation * 0.80
    if cash_entrada_efectivo > 0:
        if housing_tasation != housing_price:
            return {
                "gastos_derivados": gastos_derivados,
                "gastos_agencia": gastos_agencia,
                "total_gastos": total_gastos,
                "cash_entrada_efectivo": cash_entrada_efectivo,
                "financiacion_necesaria": financiacion_necesaria,
                "financiacion_necesaria_percent": financiacion_necesaria_percent,
                "prestamo_80percent_tasation": prestamo_80percent_tasation,
            }
        else:
            return {
                "gastos_derivados": gastos_derivados,
                "gastos_agencia": gastos_agencia,
                "total_gastos": total_gastos,
                "cash_entrada_efectivo": cash_entrada_efectivo,
                "financiacion_necesaria": financiacion_necesaria,
                "financiacion_necesaria_percent": financiacion_necesaria_percent,
            }
    else:
        return {
            "error": f"Error, no tienes el efectivo necesario ({cash} €) para pagar los gastos derivados ({total_gastos} €)"
        }
    
if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)