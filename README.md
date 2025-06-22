Vellum: Development Roadmap (To-Do List)
This roadmap is divided into phases. Each phase builds upon the previous one, ensuring a stable foundation before adding more advanced features.

Phase 0: Project Setup & Initial Core (Foundation)
Goal: Establish the project structure, basic Pydantic-MongoDB mapping, and core repository functions.
Estimated Time: 1-2 Weeks

Task 0.1: Project Initialization
Create a new GitHub repository: your-org/vellum
Initialize a Python project structure (src/vellum/__init__.py, src/vellum/model.py, src/vellum/repository.py, src/vellum/query.py, etc.)
Set up pyproject.toml (or setup.py) with motor, pydantic, pymongo as dependencies.
Create README.md with the description we agreed upon.
Add .gitignore, LICENSE (e.g., MIT).
Task 0.2: Testing Framework Setup
Configure pytest and pytest-asyncio.
Set up a docker-compose.yml for a test MongoDB instance.
Implement initial basic tests for connection and CRUD.
Task 0.3: VellumBaseModel (Our equivalent of MongoModel)
Define VellumBaseModel inheriting from pydantic.BaseModel.
Include id: UUID = Field(alias="_id"), created_at, updated_at.
Implement Settings inner class for collection_name and indexes.
Ensure proper model_dump(by_alias=True) behavior.
Task 0.4: VellumRepository (Basic CRUD)
Implement __init__ to link VellumBaseModel to motor.motor_asyncio.AsyncIOMotorCollection.
Implement create(doc: VellumBaseModel) -> VellumBaseModel with auto-timestamping.
Implement get(doc_id: UUID) -> Optional[VellumBaseModel] with Pydantic validation on fetch.
Implement find(filter: Dict, skip, limit, sort) -> List[VellumBaseModel] with Pydantic validation.
Implement update(doc_id: UUID, update_data: Union[BaseModel, Dict]) -> Optional[VellumBaseModel].
Implement delete(doc_id: UUID) -> bool.
Implement count(filter: Dict) -> int.
Task 0.5: Basic Index Management
Implement create_index method in VellumRepository (like your initial example) to create/ensure indexes based on VellumBaseModel.Settings.indexes.
Consider adding a drop_indexes helper for testing.
Task 0.6: Connection Management Utilities
init_db_client function to create AsyncIOMotorClient.
Basic on_startup/on_shutdown pattern for FastAPI.
Phase 1: Core Type-Safe Querying & Aggregation (Differentiator 1: Q-Objects)
Goal: Implement the highly type-safe Vellum.Q query builder and foundational aggregation pipeline.
Estimated Time: 2-3 Weeks

Task 1.1: QueryExpression & Vellum.Q (Basic Operators)
Define QueryExpression class for field access (__eq__, __ne__, __lt__, __le__, __gt__, __ge__).
Add common operators: In, Nin, Exists, Regex, Contains (for array/string).
Implement the Q(model) factory to dynamically create the Vellum.Q object on VellumRepository instance.
Ensure Q-Objects properly handle Field(alias="...").
Integrate Q-Objects into VellumRepository.find filter arguments.
Task 1.2: Basic Aggregation Pipeline Builder (Vellum.aggregate_pipeline())
Define AggregationPipeline class with an internal list of stages.
Implement fluent methods: match(query: Dict), project(projection: Dict), group(group_id: Dict, **accumulators: Any).
Implement sort, limit, skip.
execute() method to run the pipeline and return List[Dict[str, Any]] initially.
Task 1.3: Advanced Pydantic Type Mapping
Ensure seamless handling of Decimal128 (if Pydantic supports it or with custom validators).
Investigate and implement robust ObjectId and UUID conversion for non-_id fields.
Consider built-in support for Pydantic's datetime with timezone awareness for MongoDB.
Phase 2: Advanced Features & Enhanced Type Safety (Differentiator 2: Aggregation Output, Hooks, OCC)
Goal: Elevate Vellum beyond basic features with sophisticated type-mapping for aggregation results, robust lifecycle hooks, and optimistic concurrency.
Estimated Time: 3-4 Weeks

Task 2.1: Type-Safe Aggregation Output Models
Refine AggregationPipeline.project(projection: Dict, output_model: Optional[Type[OutputModelType]] = None) to genuinely return List[OutputModelType] validated by the provided model.
This might require the AggregationPipeline instance itself to track its "current" output schema type.
Implement methods for group that can take an output_model for the grouped results.
Task 2.2: Comprehensive Asynchronous Lifecycle Hooks
Design and implement a decorator-based system for before_insert, after_insert, before_update, after_update, before_delete, after_delete on VellumBaseModel methods.
Ensure hooks are async compatible and can modify the document or raise exceptions.
Task 2.3: Optimistic Concurrency Control (OCC)
Add a version: int = 1 field to VellumBaseModel (or a Mixin).
Modify create to set version, and update to increment version and use $inc with the old version in the query.
Implement a custom exception for OptimisticLockError.
Task 2.4: Built-in Soft Delete Mechanism
Add deleted_at: Optional[datetime] = None to VellumBaseModel (or a Mixin).
Implement soft_delete() and restore() methods on the model/repository.
Modify find, get, count to implicitly exclude soft-deleted documents by default, with an option to include them.
Task 2.5: Advanced Aggregation Stages
Implement unwind, lookup, addFields, set, replaceRoot methods in AggregationPipeline.
Focus on providing type hints for $lookup outputs, possibly requiring explicit join models.
Phase 3: Advanced MongoDB Features & Ecosystem Integration (Polish & Reach)
Goal: Add high-level MongoDB features, migration tools, and deepen FastAPI integration.
Estimated Time: 2-3 Weeks

Task 3.1: Transaction Management
Implement a context manager for MongoDB multi-document transactions using MotorClient.start_session() and session.with_transaction().
Integrate session into VellumRepository methods.
Task 3.2: Relationship Management (Optional, Major Feature)
Decision Point: Decide on a strategy (e.g., Beanie's Link concept, or a simpler Reference model with fetch_related method).
Implement definition and loading of referenced documents (one-to-one, one-to-many).
Consider lazy vs. eager loading options.
Task 3.3: Schema Evolution / Migration Helpers
Explore and outline a strategy for handling Pydantic model changes (e.g., field renames, type changes) and applying them to existing MongoDB documents. This is a complex area, potentially involving CLI tools or helper functions.
Task 3.4: FastAPI Integration Utilities
Create FastAPI Depends functions for injecting VellumRepository instances.
Provide examples of Vellum usage within FastAPI routes.
Task 3.5: Comprehensive Documentation
Write clear, concise documentation (e.g., using MkDocs or Sphinx) for all features, with examples.
Include a "Migration from Beanie" guide if applicable.
Task 3.6: Performance Optimization & Benchmarking
Identify potential bottlenecks and optimize queries.
Create benchmarks to compare Vellum's performance against direct Motor usage and other ODMs (e.g., Beanie).
