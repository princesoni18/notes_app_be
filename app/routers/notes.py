from typing import List
from fastapi import APIRouter, Depends, status
from app.utils.logger import logger

from app.models.notes import NoteCreate, NoteResponse, NoteUpdate
from app.models.users import UserResponse
from app.controllers.notes import notes_controller
from app.controllers.auth import auth_controller

router = APIRouter()

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    current_user: UserResponse = Depends(auth_controller.get_current_user)
):
    logger.info(f"Create Note Request: user={current_user.email}, data={note.dict()}")
    return await notes_controller.create_note(note, current_user)

@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    current_user: UserResponse = Depends(auth_controller.get_current_user)
):
    """Get all notes for current user"""
    return await notes_controller.get_user_notes(current_user)

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: UserResponse = Depends(auth_controller.get_current_user)
):
    """Get a specific note by ID"""
    return await notes_controller.get_note_by_id(note_id, current_user)

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    current_user: UserResponse = Depends(auth_controller.get_current_user)
):
    logger.info(f"Update Note Request: user={current_user.email}, note_id={note_id}, data={note_update.dict()}")
    return await notes_controller.update_note(note_id, note_update, current_user)

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: UserResponse = Depends(auth_controller.get_current_user)
):
    logger.warning(f"Delete Note Request: user={current_user.email}, note_id={note_id}")
    return await notes_controller.delete_note(note_id, current_user)
