# Closira — Database Models Package
#
# Import all models here so that:
# 1. SQLAlchemy's Base.metadata knows about all tables
# 2. Other modules can do: from app.models import Enquiry, Event
#
# Why import models in __init__.py?
# SQLAlchemy only creates tables for models it has "seen" (imported).
# If we don't import them before calling Base.metadata.create_all(),
# the tables won't be created. This __init__.py ensures all models
# are registered when the package is imported.

from app.models.enquiry import Enquiry, EnquiryStatus, ChannelType  # noqa: F401
from app.models.event import Event  # noqa: F401
