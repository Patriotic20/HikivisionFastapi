from pydantic import BaseModel
from datetime import datetime


class UserLogsBase(BaseModel):
    enter_time: datetime
    exit_time: datetime



class UserLogsCreate(UserLogsBase):
    user_id: int


class UserLogsResponse(UserLogsBase):
    id: int
    user_id: int
    enter_time: datetime
    exit_time: datetime
    
    
class EnterEvent(BaseModel):
    user_id: int
    enter_time: datetime
    

