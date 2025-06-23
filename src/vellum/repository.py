from typing import TypeVar
from vellum.model import VellumBaseModel
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId


T = TypeVar('T', bound=VellumBaseModel)
class VellumRepository:
    def __init__(self,model_cls:type[T],database:AsyncIOMotorDatabase):
        if not issubclass(model_cls, VellumBaseModel):
            raise TypeError(f"model_cls must be a subclass of VellumBaseModel, got {model_cls}")
        
        self.model_cls:Type[T] = model_cls
        self.collection: AsyncIOMotorCollection = database[model_cls.get_collection_name()]
    
    async def create(self,item:T)->T:
        if not isinstance(item, self.model_cls):
            raise TypeError(f"item must be an instance of {self.model_cls}, got {type(item)}")
        doc_data=item.to_mongo()
        result:InsertOneResult=await self.collection.insert_one(doc_data)
        # if result.inserted_id and isinstance(model_instance.id, UUID) and str(model_instance.id) == str(model_instance.id):
        #      # Motor often returns ObjectId, so ensure consistency with model's UUID
        #      # This check `str(model_instance.id) == str(model_instance.id)`
        #      # is a bit redundant, implies the UUID was just generated
        #      # Better check if it's the default generated UUID
        #      pass # The model's default_factory for ID already generates a UUID   
         
