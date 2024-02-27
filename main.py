from fastapi import FastAPI, Query
from typing import Annotated
import uvicorn
import numpy_financial as npf


app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Entra en /docs para ver la documentación y tener un uso interactivo de la API"
    }


@app.get("/mortgage")
async def mortgage_calculator(
    cash: Annotated[float, Query(description="Dinero que tienes en el banco [€]", ge=0, example=50000)],
    housing_price: Annotated[float, Query(description="Precio de la vivienda [€]", ge=0, example=350000)],
    inmobilaria_pertcentage_fee: float = Query(0, description="\\% de comisión inmobiliaria", ge=0, le=100),
    housing_tasation: float = Query(0, description="Valor de tasación, si es igual que el valor del inmueble dejar a 0 [€]", ge=0),
    main_house: bool = Query(True, description="Casa principal 4% ITP / Segunda vivienda 6% ITP"),
    second_hand: bool = Query(True, description="Segunda mano para usar ITP, si no, 10% IVA en vez de ITP"),
    notaria_fees: float = Query(700.0, description="Gastos de notaría [€]", ge=0),
    registro_fees: float = Query(420.0, description="Gastos de registro [€]", ge=0),
    tasation_fees: float = Query(335.0, description="Gastos de tasación [€]", ge=0),
    gestoria_fees: float = Query(375.0, description="Gastos de gestoría [€]", ge=0),
    mortgage_years: int = Query(30, description="Años de hipoteca", ge=0),
    interest_rate: float = Query(2.5, description="\\% interés hipoteca (TIN)"),
):
    """
    Method to calculate the cost of a house
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
    gastos_agencia = inmobilaria_pertcentage_fee / 100 * housing_price
    total_gastos = gastos_derivados + gastos_agencia
    cash_entrada_efectivo = cash - total_gastos
    financiacion_necesaria = housing_price - cash_entrada_efectivo
    financiacion_necesaria_percent = (financiacion_necesaria / housing_price) * 100
    prestamo_80percent_tasation = housing_tasation * 0.80
    if cash_entrada_efectivo > 0:
        if housing_tasation != housing_price:
            cuota = -npf.pmt(rate=interest_rate /100 / 12, nper=mortgage_years * 12,  pv=prestamo_80percent_tasation)
            total_ammount_end_of_mortgage = cuota * mortgage_years * 12
            intereses_totales = total_ammount_end_of_mortgage - prestamo_80percent_tasation
            return {
                "gastos_derivados": gastos_derivados,
                "gastos_agencia": gastos_agencia,
                "total_gastos": total_gastos,
                "cash_entrada_efectivo": cash_entrada_efectivo,
                "financiacion_necesaria": financiacion_necesaria,
                "financiacion_necesaria_percent": financiacion_necesaria_percent,
                "prestamo_80percent_tasation": prestamo_80percent_tasation,
                "cuota":cuota,
                "total_ammount_end_of_mortgage": total_ammount_end_of_mortgage,
                "intereses_totales" : intereses_totales,
            }
        else:
            cuota = -npf.pmt(interest_rate/100 / 12, mortgage_years * 12,  financiacion_necesaria)
            total_ammount_end_of_mortgage = cuota * mortgage_years * 12
            intereses_totales = total_ammount_end_of_mortgage - financiacion_necesaria
            return {
                "gastos_derivados": gastos_derivados,
                "gastos_agencia": gastos_agencia,
                "total_gastos": total_gastos,
                "cash_entrada_efectivo": cash_entrada_efectivo,
                "financiacion_necesaria": financiacion_necesaria,
                "financiacion_necesaria_percent": financiacion_necesaria_percent,
                "cuota":cuota,
                "total_ammount_end_of_mortgage": total_ammount_end_of_mortgage,
                "intereses_totales" : intereses_totales,
            }
    else:
        return {
            "error": f"Error, no tienes el efectivo necesario ({cash} €) para pagar los gastos derivados ({total_gastos} €)"
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
