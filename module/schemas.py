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


class TargetIPKRequest(BaseModel):
    sks_lalu: int = Field(..., ge=0, description="Total SKS yang sudah diselesaikan")
    ipk_lalu: float = Field(..., ge=0.0, le=4.0, description="IPK saat ini")
    sks_rencana: int = Field(..., gt=0, description="Rencana SKS di semester berikutnya")
    target_ipk: float = Field(..., ge=0.0, le=4.0, description="Target IPK yang ingin diraih")


class TargetIPKResponse(BaseModel):
    sks_total_nanti: int
    ips_dibutuhkan: float
    tercapai: bool
    catatan: str
