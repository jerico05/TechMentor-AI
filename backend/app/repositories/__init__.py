"""Repositories - async data-access layer.

Each repository wraps SQLAlchemy queries for one aggregate, keeping services
thin and testable. Inject a session, get back ORM objects.
"""

from app.repositories.user_repository import UserRepository
from app.repositories.student_profile_repository import StudentProfileRepository

__all__ = ["UserRepository", "StudentProfileRepository"]
