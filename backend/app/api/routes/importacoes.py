from fastapi import APIRouter


router = APIRouter(prefix="/importacoes", tags=["importacoes"])


@router.get("/")
def listar_importacoes():
    return {"message": "Rota de importações pronta"}

