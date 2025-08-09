from .base import Base
from .mixins.int_id_pk import IntIdPkMixin
from .mixins.user_id_pk import UserFkId
from sqlalchemy.orm import Mapped , mapped_column
from datetime import datetime
from sqlalchemy import DateTime , String


class UserLog(Base , IntIdPkMixin , UserFkId):
    
    _user_back_populates = "user_logs"
    
    enter_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user_face_path: Mapped[str | None] = mapped_column(String, nullable=True)
    
    

