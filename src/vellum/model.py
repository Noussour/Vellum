import datetime
from typing import Any, Dict, Optional, TypeVar
from uuid import UUID, uuid4
import uuid
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import PydanticUndefined
from vellum.hooks import _register_hook
import inspect


T_VellumBaseModel = TypeVar('T_VellumBaseModel', bound='VellumBaseModel')
class VellumBaseModel(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)) 
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)) 
    model_config = ConfigDict(
        populate_by_name=True,  
        json_encoders={
            UUID: str,          
            datetime: lambda dt: dt.isoformat(),
        },
        arbitrary_types_allowed=True,
        extra='ignore', 
        from_attributes=True,
        protected_namespaces=(), 
    )
    def __init__(self,**data:Any):
        if "_id" in data and "id" not in data:
            data["id"]=uuid4()
        if "created_at" not in data:
            data["created_at"] = datetime.datetime.now(datetime.timezone.utc)
        if "updated_at" not in data:
            data["updated_at"] = datetime.datetime.now(datetime.timezone.utc)
        super().__init__(**data)

    class Settings:      
     collection_name: Optional[str] =None
    @classmethod
    def get_collection_name(cls)-> str:
        if cls.Settings.collection_name:
            return cls.Settings.collection_name
        return cls.__name__.lower() 
    def to_mongo(self) -> Dict[str, object]:
        data=self.model_dump(by_alias=True,exclude_none=True)
        if '_id' in data and isinstance(data['_id'], UUID):
            from bson import ObjectId # type: ignore
            data['_id'] = ObjectId(str(data['_id']))
        return data
    @classmethod
    def from_mongo(cls:type[T_VellumBaseModel], data: Dict[str, object]={}) -> T_VellumBaseModel:
        if '_id' in data and isinstance(data['_id'], str):
            from bson import ObjectId # type: ignore
            data['_id'] = ObjectId(data['_id'])
        return cls.model_validate(data)
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('model_')or name in ['created_at', 'updated_at', '_sa_instance_state']:
            super().__setattr__(name, value)
        
        current_value=getattr(self, name, PydanticUndefined)
        if current_value is not PydanticUndefined and current_value!=value:
            super().__setattr__('updated_at', datetime.datetime.now(datetime.timezone.utc))
        super().__setattr__(name, value) 
        
    def __init_subclass__(cls, **kwargs): # type: ignore
        super().__init_subclass__(**kwargs)
        for _, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_vellum_hook_event'): # type: ignore
                event = getattr(method, '_vellum_hook_event') # type: ignore
                _register_hook(cls, event, method)        # type: ignore
            
        
        
            
      
            
        