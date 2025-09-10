from app.models.users import PyObjectId
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId



class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    local_id: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    local_id: Optional[str] = None

class NoteResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    user_id: PyObjectId
    created_at: datetime
    updated_at: datetime
    local_id: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class NoteInDB(NoteResponse):
    pass