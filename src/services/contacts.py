from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactBase, ContactUpdate
from src.database.models import User

class ContactService:
    """
    Service for handling contact-related operations.

    Methods:
    - create_contact(body: ContactBase, user: User): Create a new contact.
    - get_contacts(skip: int, limit: int, query: str | None, user: User): Get a list of contacts.
    - get_upcoming_birthdays(user: User): Get upcoming birthdays from contacts.
    - get_contact(contact_id: int, user: User): Get a specific contact by ID.
    - update_contact(contact_id: int, body: ContactUpdate, user: User): Update a contact.
    - remove_contact(contact_id: int, user: User): Remove a contact.
    """
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, query: str | None, user: User):
        return await self.contact_repository.get_contacts(skip, limit, query, user)
    
    async def get_upcoming_birthdays(self, user: User):
        return await self.contact_repository.get_upcoming_birthdays(user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)
