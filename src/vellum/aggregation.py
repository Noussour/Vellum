from typing import Any, Dict, List, Generic, Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorCollection
from vellum.model import VellumBaseModel

T = TypeVar('T', bound=VellumBaseModel)

class VellumAggregationPipeline(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection, model_cls: Type[T]): # type: ignore
        self.collection: AsyncIOMotorCollection = collection # type: ignore
        self.model_cls = model_cls
        self.pipeline: List[Dict[str, Any]] = []

    def match(self, query: Dict[str, Any]):
        self.pipeline.append({"$match": query})
        return self 
    
    def project(self, projection: Dict[str, Any]):
        self.pipeline.append({"$project": projection})
        return self

    def group(self, group_id: Dict[str, Any], **accumulators: Any):
        group_stage = {"_id": group_id}
        group_stage.update(accumulators)
        self.pipeline.append({"$group": group_stage})
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

    async def execute(self) -> List[Dict[str, Any]]:
        cursor = self.collection.aggregate(self.pipeline) # type: ignore
        return await cursor.to_list(length=None) # type: ignore