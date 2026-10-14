"""
models/__init__.py – Model Package Initializer
==============================================
Importing all models here ensures SQLAlchemy's Base.metadata
is populated before create_all() is called during startup.
"""

from models.user import User
from models.application import Application, ApplicationStatus, PaymentStatus
from models.scheme import Scheme

__all__ = ["User", "Application", "ApplicationStatus", "PaymentStatus", "Scheme"]
