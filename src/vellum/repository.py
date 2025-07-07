from typing import Generic, Tuple, TypeVar
from vellum.exceptions import DocumentNotFoundError, OptimisticLockError
from vellum.model import VellumBaseModel
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID
from vellum.aggregation import VellumAggregationPipeline
from motor.motor_asyncio import  AsyncIOMotorDatabase, AsyncIOMotorCollection # type: ignore
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson.objectid import ObjectId
from vellum.hooks import get_hooks_for_model # type: ignore
from vellum.query import QueryExpression # type: ignore


T = TypeVar('T', bound=VellumBaseModel)

class VellumRepository(Generic[T]):
    def __init__(
                  self,model_cls:Type[T]
                 ,database:AsyncIOMotorDatabase # type: ignore
                 ):
        
        self.model_cls:Type[T] = model_cls
        self.collection: AsyncIOMotorCollection[Dict[str, Any]] = database[model_cls.get_collection_name()] # type: ignore
    
    async def create(self,item:T)->T:
        if not isinstance(item, self.model_cls):
            raise TypeError(f"item must be an instance of {self.model_cls}, got {type(item)}")
        for hook in get_hooks_for_model(self.model_cls, "before_insert"):
            await hook(item)
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

    async def update(self, id: Union[UUID, str, ObjectId], item: T) -> T:
        if not isinstance(item, self.model_cls):
           raise TypeError(f"item must be an instance of {self.model_cls}, got {type(item)}")

        for hook in get_hooks_for_model(self.model_cls, "before_update"):
            await hook(item)

        query_id: ObjectId
        if isinstance(id, UUID):
           query_id = ObjectId(str(id))
        elif isinstance(id, str):
            try:
                query_id = ObjectId(id)
            except Exception:
               raise ValueError(f"Invalid ID format for string: {id}")
        elif isinstance(id, ObjectId): # type: ignore
            query_id = id
        else:
           raise TypeError(f"Invalid type for document_id: {type(id)}")

  
        query: Dict[str, Any] = {"_id": query_id, "version": item.version}

        doc_data = item.model_dump(by_alias=True, exclude={"version"})
        update_op = { # type: ignore
        "$set": doc_data,
        "$inc": {"version": 1}
               }
        result: UpdateResult = await self.collection.update_one(query, update_op) # type: ignore
        doc_exists = True
        if result.modified_count == 0:
             doc_exists = await self.collection.count_documents({"_id": query_id}, limit=1)
             if not doc_exists:
                 raise DocumentNotFoundError(doc_id=id)
             else:
                  raise OptimisticLockError(doc_id=id, version=item.version)
        
        item.version += 1
        for hook in get_hooks_for_model(self.model_cls, "after_update"):
            await hook(item)

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
        doc_to_delete = await self.get(id)
        if not doc_to_delete:
            raise DocumentNotFoundError(f"Document with ID {id} not found.")
        for hook in get_hooks_for_model(self.model_cls, "before_delete"):
            await hook(doc_to_delete)
        result: DeleteResult = await self.collection.delete_one({"_id": query_id})
        if result.deleted_count == 0:
            raise DocumentNotFoundError(f"Document with ID {id} not found.")
        for hook in get_hooks_for_model(self.model_cls, "after_delete"):
            await hook(doc_to_delete)
        return True
    
    async def find(
        self,
        query: Union[Dict[str, Any], QueryExpression] = {},
        skip: int = 0,
        limit: int = 0,
        sort: Optional[List[Tuple[str, int]]] = None,
    ) -> List[T]:
        
        mongo_query: Dict[str, Any]
        
        if isinstance(query, QueryExpression):
            mongo_query = query.to_mongo_query()
        else:
            mongo_query = query

        if limit < 0:
            limit = 0
        if skip < 0:
            skip = 0
            
        cursor = self.collection.find(mongo_query).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        documents: List[Dict[str, Any]] = await cursor.to_list(length=limit if limit > 0 else None)
        return [self.model_cls.from_mongo(doc) for doc in documents]
    async def aggregate(self)-> VellumAggregationPipeline[T]:
        return VellumAggregationPipeline(self.collection, self.model_cls)

         
