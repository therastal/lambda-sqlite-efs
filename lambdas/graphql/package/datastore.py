import asyncio
from datetime import datetime
from decimal import Decimal
import json
from typing import Optional

import strawberry

from .kvstore import sqlite


async def get_dt(field: str, uid: strawberry.ID) -> datetime:
    return await asyncio.to_thread(sqlite.get, field, int(uid))


async def get_dec(field: str, uid: strawberry.ID) -> Decimal:
    amount = await asyncio.to_thread(sqlite.get, field, int(uid))
    return Decimal(amount).quantize(Decimal("1.00"))


async def get_int(field: str, uid: strawberry.ID) -> int:
    return await asyncio.to_thread(sqlite.get, field, int(uid))


async def get_str(field: str, uid: strawberry.ID) -> str:
    return await asyncio.to_thread(sqlite.get, field, int(uid))


async def get_ref(field: str, uid: strawberry.ID, type_: type):
    id = await asyncio.to_thread(sqlite.get, field, int(uid))
    return type_(id=strawberry.ID(id))


async def get_refs(field: str, uid: str, type_: type) -> Optional[list]:
    ids_str = await asyncio.to_thread(sqlite.get, field, int(uid)) or "[]"
    ids = json.loads(ids_str)
    return [type_(id=strawberry.ID(id)) for id in ids] or None
