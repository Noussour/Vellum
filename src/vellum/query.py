from typing import Any, Dict, List
from uuid import UUID


MongoFilePath=str
class QueryExpression:
    def to_mongo_query(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method.")
    def __and__(self,other: 'QueryExpression') -> 'And': # type: ignore
        return And(self, other) # type: ignore
    def __or__(self, other: 'QueryExpression') -> 'Or': # type: ignore
        return Or(self, other) # type: ignore
    def __invert__(self) -> 'Nor': # type: ignore
        return Nor(self) # type: ignore
class FieldQueryExpression(QueryExpression):
    def __init__(self, field: MongoFilePath, value: Any | list[Any] | tuple[Any, ...] | set[Any]):
        self.field = field
        self.value = value

    def _convert_value_to_mongo(self, value: Any) -> Any:
 
        if isinstance(value, UUID):
            from bson import ObjectId # type: ignore
            return ObjectId(str(value))

        return value
class Eq(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {self.field: self._convert_value_to_mongo(self.value)}

class Ne(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {self.field: {"$ne": self._convert_value_to_mongo(self.value)}}

class Gt(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {self.field: {"$gt": self._convert_value_to_mongo(self.value)}}

class Gte(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {self.field: {"$gte": self._convert_value_to_mongo(self.value)}}

class Lt(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {self.field: {"$lt": self._convert_value_to_mongo(self.value)}}

class Lte(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {self.field: {"$lte": self._convert_value_to_mongo(self.value)}}

class In(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        if not isinstance(self.value, (list, tuple, set)):
            raise TypeError(f"Value for $in operator must be a list, tuple, or set, got {type(self.value)}")
        converted_values = [self._convert_value_to_mongo(v) for v in self.value] # type: ignore
        return {self.field: {"$in": converted_values}}

class NotIn(FieldQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        if not isinstance(self.value, (list, tuple, set)):
            raise TypeError(f"Value for $nin operator must be a list, tuple, or set, got {type(self.value)}")
        converted_values = [self._convert_value_to_mongo(v) for v in self.value] # type: ignore
        return {self.field: {"$nin": converted_values}}
class LogicalQueryExpression(QueryExpression):
    def __init__(self, *expressions: QueryExpression):
        if not all(isinstance(exp, QueryExpression) for exp in expressions): # type: ignore
            raise TypeError("All arguments must be QueryExpression instances.")
        self.expressions = expressions

class And(LogicalQueryExpression):
    """Represents a logical AND ($and) operation."""
    def to_mongo_query(self) -> Dict[str, Any]:
        return {"$and": [exp.to_mongo_query() for exp in self.expressions]}

class Or(LogicalQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:
        return {"$or": [exp.to_mongo_query() for exp in self.expressions]}

class Nor(LogicalQueryExpression):
    def to_mongo_query(self) -> Dict[str, Any]:

        return {"$nor": [exp.to_mongo_query() for exp in self.expressions]}

# Helper fucntions

def eq(field: MongoFilePath, value: Any) -> Eq:
    return Eq(field, value)

def ne(field: MongoFilePath, value: Any) -> Ne:
    return Ne(field, value)

def gt(field: MongoFilePath, value: Any) -> Gt:
    return Gt(field, value)

def gte(field: MongoFilePath, value: Any) -> Gte:
    return Gte(field, value)

def lt(field: MongoFilePath, value: Any) -> Lt:
    return Lt(field, value)

def lte(field: MongoFilePath, value: Any) -> Lte:
    return Lte(field, value)

def In_(field: MongoFilePath, values: List[Any]) -> In:
    return In(field, values)

def NotIn_(field: MongoFilePath, values: List[Any]) -> NotIn:
    return NotIn(field, values)

def And_(*expressions: QueryExpression) -> And:
    return And(*expressions)

def Or_(*expressions: QueryExpression) -> Or:
    return Or(*expressions)

def Nor_(*expressions: QueryExpression) -> Nor:
    return Nor(*expressions)    