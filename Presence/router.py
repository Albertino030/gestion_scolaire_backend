from fastapi import APIRouter, Query
from . import service

router = APIRouter(prefix="/presence", tags=["Presence"])


@router.get("/")
def get_all(id_annee: int = Query(None, description="ID de l'année scolaire")):
    return service.get_presences(id_annee)


@router.post("/")
def add(data: dict):
    return service.add_presence(data)


@router.put("/{id}")
def update(id: int, data: dict):
    return service.update_presence(id, data)


@router.delete("/{id}")
def delete(id: int):
    return service.delete_presence(id)