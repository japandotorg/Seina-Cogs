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

import typing

from .array import ARRAY as ARRAY, All as All, Any as Any, array as array
from .base import (
    BIGINT as BIGINT,
    BIT as BIT,
    BOOLEAN as BOOLEAN,
    BYTEA as BYTEA,
    CHAR as CHAR,
    CIDR as CIDR,
    DATE as DATE,
    DOUBLE_PRECISION as DOUBLE_PRECISION,
    ENUM as ENUM,
    FLOAT as FLOAT,
    INET as INET,
    INTEGER as INTEGER,
    INTERVAL as INTERVAL,
    MACADDR as MACADDR,
    MONEY as MONEY,
    NUMERIC as NUMERIC,
    OID as OID,
    REAL as REAL,
    REGCLASS as REGCLASS,
    SMALLINT as SMALLINT,
    TEXT as TEXT,
    TIME as TIME,
    TIMESTAMP as TIMESTAMP,
    TSVECTOR as TSVECTOR,
    UUID as UUID,
    VARCHAR as VARCHAR,
    CreateEnumType as CreateEnumType,
    DropEnumType as DropEnumType,
)
from .dml import Insert as Insert, insert as insert
from .ext import ExcludeConstraint as ExcludeConstraint, aggregate_order_by as aggregate_order_by, array_agg as array_agg
from .hstore import HSTORE as HSTORE, hstore as hstore
from .json import JSON as JSON, JSONB as JSONB
from .ranges import (
    DATERANGE as DATERANGE,
    INT4RANGE as INT4RANGE,
    INT8RANGE as INT8RANGE,
    NUMRANGE as NUMRANGE,
    TSRANGE as TSRANGE,
    TSTZRANGE as TSTZRANGE,
)

__all__ = (
    "INTEGER",
    "BIGINT",
    "SMALLINT",
    "VARCHAR",
    "CHAR",
    "TEXT",
    "NUMERIC",
    "FLOAT",
    "REAL",
    "INET",
    "CIDR",
    "UUID",
    "BIT",
    "MACADDR",
    "MONEY",
    "OID",
    "REGCLASS",
    "DOUBLE_PRECISION",
    "TIMESTAMP",
    "TIME",
    "DATE",
    "BYTEA",
    "BOOLEAN",
    "INTERVAL",
    "ARRAY",
    "ENUM",
    "dialect",
    "array",
    "HSTORE",
    "hstore",
    "INT4RANGE",
    "INT8RANGE",
    "NUMRANGE",
    "DATERANGE",
    "TSVECTOR",
    "TSRANGE",
    "TSTZRANGE",
    "JSON",
    "JSONB",
    "Any",
    "All",
    "DropEnumType",
    "CreateEnumType",
    "ExcludeConstraint",
    "aggregate_order_by",
    "array_agg",
    "insert",
    "Insert",
)

dialect: typing.Any
