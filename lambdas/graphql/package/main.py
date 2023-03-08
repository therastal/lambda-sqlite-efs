from fastapi import FastAPI
from mangum import Mangum
from strawberry import Schema
from strawberry.extensions import ParserCache, ValidationCache
from strawberry.fastapi import GraphQLRouter

from . import schema

graphql_schema = Schema(schema.Query, extensions=[ParserCache(), ValidationCache()])
graphql_app = GraphQLRouter(graphql_schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

handler = Mangum(app)
