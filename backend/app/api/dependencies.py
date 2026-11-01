from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.relational_db import get_db

# Re-export get_db for route dependencies
__all__ = ["get_db"]

