"""Mostly a port of https://github.com/Mediagone/small-uid"""

import random
import time
from typing import Optional

MAX_20BIT_INT = 524288
MAX_CHARS_IN_RANDINT = 6


class UID:
    _uid: int

    def __init__(
        self, int: Optional[int] = None, existing: Optional[set["UID"]] = None
    ):
        if existing is None:
            existing = set()
        self._initialize(int)
        while self in existing:
            self._initialize(int)

    def __repr__(self) -> str:
        return str(self._uid)

    def __str__(self) -> str:
        return str(self._uid)

    def __eq__(self, __o: "UID") -> bool:
        return self._uid == __o._uid

    def __hash__(self) -> int:
        return self._uid

    @property
    def int(self):
        return self._uid

    @property
    def hex(self):
        return hex(self._uid)

    def _initialize(self, i: Optional["int"] = None):
        if i is None:
            time_ms = int(time.time() * 1000)
            rand = random.randrange(MAX_20BIT_INT)
            uidstr = str(time_ms) + str(rand).rjust(MAX_CHARS_IN_RANDINT, "0")
            self._uid = int(uidstr)
        else:
            self._uid = i
