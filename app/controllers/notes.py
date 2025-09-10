from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from bson import ObjectId

from app.models.notes import NoteCreate, NoteResponse, NoteUpdate
from app.models.users import UserResponse
from app.utils.database import get_db
from app.utils.logger import logger


class NotesController:
    async def create_note(self, note: NoteCreate, current_user: UserResponse) -> NoteResponse:
        """Create a new note"""
        logger.info(f"[Controller] Create note: user={current_user.email}, data={note.dict()}")
        db = await get_db()
        note_dict = {
            "title": note.title,
            "description": note.description,
            "user_id": current_user.id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.notes.insert_one(note_dict)
        note_dict["_id"] = result.inserted_id
        return NoteResponse(**note_dict)

    async def get_user_notes(self, current_user: UserResponse) -> List[NoteResponse]:
        """Get all notes for current user"""
        logger.info(f"[Controller] Get notes: user={current_user.email}")
        db = await get_db()
        cursor = db.notes.find({"user_id": current_user.id}).sort("created_at", -1)
        notes = await cursor.to_list(length=None)
        return [NoteResponse(**note) for note in notes]

    async def get_note_by_id(self, note_id: str, current_user: UserResponse) -> NoteResponse:
        """Get a specific note by ID"""
        logger.info(f"[Controller] Get note by ID: user={current_user.email}, note_id={note_id}")
        db = await get_db()
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID"
            )
        note = await db.notes.find_one({
            "_id": ObjectId(note_id),
            "user_id": current_user.id
        })
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        return NoteResponse(**note)

    async def update_note(self, note_id: str, note_update: NoteUpdate, current_user: UserResponse) -> NoteResponse:
        """Update a note"""
        logger.info(f"[Controller] Update note: user={current_user.email}, note_id={note_id}, data={note_update.dict()}")
        db = await get_db()
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID"
            )
        # Check if note exists and belongs to user
        existing_note = await db.notes.find_one({
            "_id": ObjectId(note_id),
            "user_id": current_user.id
        })
        if not existing_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        # Build update dictionary
        update_dict = {"updated_at": datetime.utcnow()}
        if note_update.title is not None:
            update_dict["title"] = note_update.title
        if note_update.description is not None:
            update_dict["description"] = note_update.description
        # Update note
        await db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_dict}
        )
        # Return updated note
        updated_note = await db.notes.find_one({"_id": ObjectId(note_id)})
        return NoteResponse(**updated_note)

    async def delete_note(self, note_id: str, current_user: UserResponse) -> dict:
        """Delete a note"""
        logger.warning(f"[Controller] Delete note: user={current_user.email}, note_id={note_id}")
        db = await get_db()
        if not ObjectId.is_valid(note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID" 
            )
        # Check if note exists and belongs to user
        result = await db.notes.delete_one({
            "_id": ObjectId(note_id),
            "user_id": current_user.id
        })
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        return {"message": "Note deleted successfully"}

notes_controller = NotesController()