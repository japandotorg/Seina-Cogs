"""
MIT License

Copyright (c) 2022-present japandotorg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any

from sqlalchemy.dialects.firebird.base import (
    BIGINT as BIGINT,
    BLOB as BLOB,
    CHAR as CHAR,
    DATE as DATE,
    FLOAT as FLOAT,
    NUMERIC as NUMERIC,
    SMALLINT as SMALLINT,
    TEXT as TEXT,
    TIME as TIME,
    TIMESTAMP as TIMESTAMP,
    VARCHAR as VARCHAR,
)

__all__ = (
    "SMALLINT",
    "BIGINT",
    "FLOAT",
    "FLOAT",
    "DATE",
    "TIME",
    "TEXT",
    "NUMERIC",
    "FLOAT",
    "TIMESTAMP",
    "VARCHAR",
    "CHAR",
    "BLOB",
    "dialect",
)

dialect: Any
