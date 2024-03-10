from fastapi import HTTPException, APIRouter, Path, Depends, Body
from .models import Client, Transaction
from .database import get_db
from .schemas import Transacao
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

@router.get("/clientes/{client_id}/extrato", response_model=dict)
async def get_statement(
    client_id: int = Path(...),
    db: Session = Depends(get_db),
):

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.client_id == client_id)
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    statement = {
        "saldo": {
            "total": client.saldo,
            "data_extrato": datetime.now(),
            "limite": client.limite,
        },
        "ultimas_transacoes": [
            {
                "valor": transaction.valor,
                "tipo": transaction.tipo,
                "descricao": transaction.descricao,
                "realizada_em": transaction.created_at,
            }
            for transaction in transactions
        ],
    }

    return statement

@router.post("/clientes/{client_id}/transacoes", response_model=dict)
async def create_transaction(
    client_id: int = Path(...),
    transaction_data: Transacao = Body(..., example={"valor": 10000, "tipo": "c", "descricao": "descricao"}),
    db: Session = Depends(get_db),
):

    transaction_data = transaction_data.model_dump()
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente não foi encontrado")

    if not 1 <= len(transaction_data["descricao"]) <= 10:
        raise HTTPException(status_code=422, detail="Transição invalida")

    if transaction_data["tipo"] == "d" and (client.saldo - transaction_data["valor"]) < (-client.limite):
        raise HTTPException(status_code=422, detail="Transação não permitida.")

    transaction = Transaction(**transaction_data, client_id=client_id)
    db.add(transaction)
    db.commit()

    if transaction_data["tipo"] == "c":
        client.saldo += transaction_data["valor"]
    else:
        client.saldo -= transaction_data["valor"]
    
    db.commit()

    return {"limite": client.limite, "saldo": client.saldo}

