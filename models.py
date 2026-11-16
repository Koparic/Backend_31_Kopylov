from enum import Enum
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, Any, Tuple

class Status(str, Enum):
    IN_SHELTER = "в приюте"
    ADOPTED = "пристроено"


class AnimalBase(BaseModel):
    name: str = Field(..., min_length=1, description="Кличка животного")
    species: str = Field(..., min_length=1, description="Вид (собака, кошка, хомяк и т.д.)")
    age: int = Field(..., ge=0, description="Возраст (полных лет или месяцев)")
    status: Status = Field(..., description="Текущий статус")

    @validator("name", "species")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("field cannot be empty or whitespace")
        return v


class AnimalCreate(AnimalBase):
    """Поля для создания ресурса"""
    pass


class AnimalUpdate(BaseModel):
    """Поля для частичного обновления (PATCH)"""
    name: Optional[str] = None
    species: Optional[str] = None
    age: Optional[int] = None
    status: Optional[Status] = None


class AnimalOut(AnimalBase):
    """То, что возвращается клиенту"""
    id: int
