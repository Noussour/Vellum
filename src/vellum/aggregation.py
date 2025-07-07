from typing import Any, Dict, List, Generic, Type, TypeVar, Optional, Union
from motor.motor_asyncio import AsyncIOMotorCollection
from vellum.model import VellumBaseModel
from pydantic import BaseModel

T = TypeVar('T', bound=VellumBaseModel)
OutputModelType = TypeVar('OutputModelType', bound=BaseModel)

class VellumAggregationPipeline(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection, model_cls: Type[T]): # type: ignore
        self.collection: AsyncIOMotorCollection = collection # type: ignore
        self.model_cls = model_cls
        self.pipeline: List[Dict[str, Any]] = []
        self.output_model: Optional[Type[OutputModelType]] = None # type: ignore

    def match(self, query: Dict[str, Any]):
        self.pipeline.append({"$match": query})
        return self
    
    def project(
        self, 
        projection: Dict[str, Any], 
        output_model: Optional[Type[OutputModelType]] = None
    ):
        self.pipeline.append({"$project": projection})
        if output_model:
            self.output_model = output_model
        return self

    def group(
        self, 
        group_id: Dict[str, Any], 
        output_model: Optional[Type[OutputModelType]] = None,
        **accumulators: Any
    ):
        group_stage = {"_id": group_id}
        group_stage.update(accumulators)
        self.pipeline.append({"$group": group_stage})
        if output_model:
            self.output_model = output_model
        return self

    def sort(self, sort_fields: Dict[str, int]):
        self.pipeline.append({"$sort": sort_fields})
        return self
        
    def skip(self, num_docs: int):
        self.pipeline.append({"$skip": num_docs})
        return self

    def limit(self, num_docs: int):
        self.pipeline.append({"$limit": num_docs})
        return self

    async def execute(self) -> Union[List[OutputModelType], List[Dict[str, Any]]]: # type: ignore
        cursor = self.collection.aggregate(self.pipeline) # type: ignore
        documents = await cursor.to_list(length=None) # type: ignore
        
        if self.output_model:
            return [self.output_model.model_validate(doc) for doc in documents] # type: ignore
        
        return documents # type: ignore