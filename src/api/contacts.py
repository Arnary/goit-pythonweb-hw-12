from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.services.contacts import ContactService
from src.database.models import User
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0, limit: int = 100, query: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
):
    """
    Get a list of contacts based on skip, limit, and query parameters.

    Parameters:
    - skip (int): Number of items to skip.
    - limit (int): Maximum number of items to return.
    - query (str, optional): Query string to filter contacts.
    - db (AsyncSession): AsyncSession dependency.
    - user (User): User dependency.

    Returns:
    - List[ContactResponse]: List of contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, query, user=user)
    return contacts

@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),):
    """
    Get a list of upcoming birthdays for contacts.

    Parameters:
    - db (AsyncSession): AsyncSession dependency.
    - user (User): User dependency.

    Returns:
    - List[ContactResponse]: List of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(user)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),):
    """
    Get a specific contact by ID.

    Parameters:
    - contact_id (int): ID of the contact to retrieve.
    - db (AsyncSession): AsyncSession dependency.
    - user (User): User dependency.

    Returns:
    - ContactResponse: Details of the requested contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),):
    """
    Create a new contact.

    Parameters:
    - body (ContactBase): Contact data to create.
    - db (AsyncSession): AsyncSession dependency.
    - user (User): User dependency.

    Returns:
    - ContactResponse: Details of the created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate, contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),
):
    """
    Update an existing contact.

    Parameters:
    - body (ContactUpdate): Contact data to update.
    - contact_id (int): ID of the contact to update.
    - db (AsyncSession): AsyncSession dependency.
    - user (User): User dependency.

    Returns:
    - ContactResponse: Details of the updated contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user),):
    """
    Remove a contact by ID.

    Parameters:
    - contact_id (int): ID of the contact to remove.
    - db (AsyncSession): AsyncSession dependency.
    - user (User): User dependency.

    Returns:
    - ContactResponse: Details of the removed contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
