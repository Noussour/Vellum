from typing import Generic, Tuple, TypeVar
from vellum.model import VellumBaseModel
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from motor.motor_asyncio import  AsyncIOMotorDatabase, AsyncIOMotorCollection # type: ignore
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson import ObjectId # type: ignore


T = TypeVar('T', bound=VellumBaseModel)
class DocumentNotFoundError(Exception):
    pass
class VellumRepository(Generic[T]):
    def __init__(
                  self,model_cls:Type[T]
                 ,database:AsyncIOMotorDatabase # type: ignore
                 ):
        # The type constraint on T ensures model_cls is a subclass of VellumBaseModel
        
        self.model_cls:Type[T] = model_cls
        self.collection: AsyncIOMotorCollection[Dict[str, Any]] = database[model_cls.get_collection_name()] # type: ignore
    
    async def create(self,item:T)->T:
        if not isinstance(item, self.model_cls):
            raise TypeError(f"item must be an instance of {self.model_cls}, got {type(item)}")
        doc_data=item.to_mongo()
        result:InsertOneResult=await self.collection.insert_one(doc_data)
        if result.inserted_id:
            pass
        return item
    async def get(self, id: Union[UUID, str,ObjectId]) -> Optional[T]:
        if isinstance(id, UUID):
            query_id = ObjectId(str(id))
        elif isinstance(id, str):
            try:
                query_id = ObjectId(id)
            except Exception:
                raise ValueError(f"Invalid ID format: {id}. Must be a valid UUID string or ObjectId string.")
        elif isinstance(id, ObjectId): # type: ignore
            query_id = id
        else:
            raise TypeError(f"Invalid type for document_id: {type(id)}. Expected UUID, str, or ObjectId.")
  
        document_data: Optional[Dict[str, Any]] = await self.collection.find_one({"_id": query_id})
        if document_data is None:
            raise DocumentNotFoundError(f"Document with ID {id} not found.")  
      
        return self.model_cls.from_mongo(document_data)  

    async def update(self, id: Union[UUID, str,ObjectId], item:T) -> Optional[T]:
        if not isinstance(item, self.model_cls):
            raise TypeError(f"item must be an instance of {self.model_cls}, got {type(item)}")
        if isinstance(id, UUID):
            query_id = ObjectId(str(id))
        elif isinstance(id, str):
            try:
                query_id = ObjectId(str(UUID(id)))
            except Exception: 
                raise ValueError(f"Invalid ID format: {id}. Must be a valid UUID string or ObjectId string.")
        elif isinstance(id, ObjectId): # type: ignore
            query_id = id
        else:
            raise TypeError(f"Invalid type for document_id: {type(id)}. Expected UUID, str, or ObjectId.")
        doc_data = item.to_mongo()
        result: UpdateResult = await self.collection.update_one({"_id": query_id}, {"$set": doc_data})
        if result.modified_count == 0:
            raise DocumentNotFoundError(f"Document with ID {id} not found or no changes made.")
        return item
    async def delete(self, id: Union[UUID, str,ObjectId]) -> bool:  
        if isinstance(id, UUID):
            query_id = ObjectId(str(id))
        elif isinstance(id, str):   
            try:
                query_id = ObjectId(id)
            except Exception:
                raise ValueError(f"Invalid ID format: {id}. Must be a valid UUID string or ObjectId string.")
        elif isinstance(id, ObjectId): # type: ignore
            query_id = id
        else:
            raise TypeError(f"Invalid type for document_id: {type(id)}. Expected UUID, str, or ObjectId.")
        result: DeleteResult = await self.collection.delete_one({"_id": query_id})
        if result.deleted_count == 0:
            raise DocumentNotFoundError(f"Document with ID {id} not found.")
        return True
    async def find(
        self,
        query: Dict[str, Any] = {},
        skip: int = 0,
        limit: int = 0,
        sort: Optional[List[Tuple[str, int]]] = None,
    )->List[T]:
        #add type safety for the query and the sort
        processed_query:Dict[str,Any]={}
        for key,value in processed_query:
            if isinstance(value, UUID):
                processed_query[key] = ObjectId(str(value))
            elif isinstance(value, dict): # type: ignore
                    processed_query[key] = value
            else:        
                    processed_query[key] = value
        if limit < 0:
                limit = 0
        if skip < 0:
             skip = 0            
        cursor = self.collection.find(processed_query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        document:List[dict[str,Any]]=await cursor.to_list(length=limit if limit > 0 else None)
        return [self.model_cls.from_mongo(doc) for doc in document]            
       
         
