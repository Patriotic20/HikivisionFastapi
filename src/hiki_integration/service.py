from core.basic_service import BasicCrud
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import EnterEvent
from core.models import UserLog

class UserLogsService:
    def __init__(self , db: AsyncSession):
        self.db = db
        self.service = BasicCrud(db)
        
        
    async def create_user_logs(self, user_log: EnterEvent):
        return await self.service.create(model=UserLog , obj_items=user_log)
    
    async def get_user_logs_by_id(self, user_log_id: int):
        return await self.service.get_by_id(model=UserLog , item_id=user_log_id)
    
    async def get_user_logs_by_user_id(self , user_id: int):
        return await self.service.get_by_field(model=UserLog, field_name="user_id" , field_value=user_id)
    
    
    async def update_user_log_by_id(self , user_id: int ,field_name: str ,field_value: str):
        return await self.service.update_by_field(model=UserLog , user_id=user_id , field_name=field_name , field_value=field_value)


    async def delete_by_id(self):
        pass
    

    async def delete_all_user_logs(self):
        pass
