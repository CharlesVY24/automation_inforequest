from typing import Annotated, Optional
import os
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Column
from sqlalchemy.dialects.postgresql import JSONB

load_dotenv()


DATABASE_URL_POSTGRES = os.environ.get("URL_STRING_CONNECTION")

engine = create_engine(DATABASE_URL_POSTGRES)


class Tenders(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    referencia_del_proceso: str = Field(index=True)
    entidad: str = Field(index=True)
    nombre_del_procedimiento: str = Field(index=True)
    descripci_n_del_procedimiento: str = Field(default=None)
    fase: str = Field(default=None)
    fecha_de_ultima_publicaci: str = Field(default=None)
    precio_base: float = Field(default=None)
    proveedores_invitados: int = Field(default=None)
    proveedores_con_invitacion: int = Field(default=None)
    visualizaciones_del: int = Field(default=None)
    proveedores_que_manifestaron: int = Field(default=None)
    id_estado_del_procedimiento: int = Field(default=None)
    codigo_principal_de_categoria: str = Field(default=None)
    urlproceso: dict  = Field(default=None, sa_column=Column(JSONB)) 
    estado_del_procedimiento: str = Field(default=None)
    adjudicado: str = Field(default=None)
    estado_resumen: str = Field(default=None)
    fecha_adjudicacion: Optional[str] = Field(default=None)
    fecha_de_publicacion: Optional[str] = Field(default=None)
    objeto_del_contrato: Optional[str] = Field(default=None)
    departamento_entidad: Optional[str] = Field(default=None)
    ciudad_entidad: Optional[str] = Field(default=None)
    id_del_proceso: Optional[str] = Field(default=None)
    categorias_adicionales: Optional[str] = Field(default=None)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]