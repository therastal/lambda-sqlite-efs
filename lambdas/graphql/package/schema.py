from datetime import datetime
from decimal import Decimal
from typing import Optional

import strawberry

from . import datastore


# region Types
@strawberry.interface
class Node:
    id: strawberry.ID


@strawberry.type
class Transaction(Node):
    @strawberry.field
    async def financial_transaction_identifier(self) -> str:
        return await datastore.get_str("transaction_identifier", self.id)

    @strawberry.field
    async def timestamp(self) -> datetime:
        return await datastore.get_dt("transaction_timestamp", self.id)

    @strawberry.field
    async def claim(self) -> "Claim":
        return await datastore.get_ref("transaction_claim", self.id, Claim)

    @strawberry.field
    async def amount(self) -> Decimal:
        return await datastore.get_dec("transaction_amount", self.id)

    @strawberry.field
    async def source_system_code(self) -> Optional[str]:
        return await datastore.get_str("transaction_source_system_code", self.id)

    @strawberry.field
    async def service_type_code(self) -> Optional[str]:
        return await datastore.get_str("transaction_service_type_code", self.id)


@strawberry.type
class Claim(Node):
    @strawberry.field
    async def claim_identifier(self) -> int:
        return await datastore.get_int("claim_identifier", self.id)

    @strawberry.field
    async def claim_type_code(self) -> str:
        return await datastore.get_str("claim_type_code", self.id)

    @strawberry.field
    async def timestamp(self) -> datetime:
        return await datastore.get_dt("claim_timestamp", self.id)

    @strawberry.field
    async def transactions(self) -> Optional[list[Optional[Transaction]]]:
        return await datastore.get_refs("claim_transactions", self.id, Transaction)

    @strawberry.field
    async def parties(self) -> Optional[list[Optional["Party"]]]:
        return await datastore.get_refs("claim_parties", self.id, Party)


@strawberry.type
class Party(Node):
    @strawberry.field
    async def party_identifier(self) -> int:
        return await datastore.get_int("party_identifier", self.id)

    @strawberry.field
    async def timestamp(self) -> datetime:
        return await datastore.get_dt("party_timestamp", self.id)

    @strawberry.field
    async def claims(self) -> Optional[list[Optional[Claim]]]:
        return await datastore.get_refs("party_claims", self.id, Claim)


# endregion


# region Queries
@strawberry.type
class Query:
    @strawberry.field
    def claim(self, id: strawberry.ID) -> Claim:
        return Claim(id=id)

    @strawberry.field
    def party(self, id: strawberry.ID) -> Party:
        return Party(id=id)

    @strawberry.field
    def transaction(self, id: strawberry.ID) -> Transaction:
        return Transaction(id=id)


# endregion
