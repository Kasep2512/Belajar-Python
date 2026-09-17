# module/schemas.py
"""Skema data Pydantic untuk validasi request dan response API."""

from typing import Optional
from pydantic import BaseModel, Field


class MataKuliahBase(BaseModel):
    no: int = Field(..., example=1)
    kode: str = Field(..., example="SI101")
    mata_kuliah: str = Field(..., example="Algoritma & Pemrogarman")
    sks: int = Field(..., ge=1, le=6, example=3)
    nilai: str = Field(..., pattern=r"^[A-Ea-e]$", example="A")
    semester: int = Field(..., ge=1, le=8, example=1)


class MataKuliahResponse(MataKuliahBase):
    id: int
    bobot: float

    class Config:
        from_attributes = True


class UpdateNilaiRequest(BaseModel):
    nilai: str = Field(
        ...,
        pattern=r"^[A-Ea-e]$",
        description="Nilai mutu baru (A, B, C, D, E)",
        example="A",
    )


class ProfilResponse(BaseModel):
    npm: str
    nama: str
    jurusan: str
    ipk_cetak: Optional[str] = None
