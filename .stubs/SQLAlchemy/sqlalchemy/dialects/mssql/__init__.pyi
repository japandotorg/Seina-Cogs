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

from .base import (
    BIGINT as BIGINT,
    BINARY as BINARY,
    BIT as BIT,
    CHAR as CHAR,
    DATE as DATE,
    DATETIME as DATETIME,
    DATETIME2 as DATETIME2,
    DATETIMEOFFSET as DATETIMEOFFSET,
    DECIMAL as DECIMAL,
    FLOAT as FLOAT,
    IMAGE as IMAGE,
    INTEGER as INTEGER,
    JSON as JSON,
    MONEY as MONEY,
    NCHAR as NCHAR,
    NTEXT as NTEXT,
    NUMERIC as NUMERIC,
    NVARCHAR as NVARCHAR,
    REAL as REAL,
    ROWVERSION as ROWVERSION,
    SMALLDATETIME as SMALLDATETIME,
    SMALLINT as SMALLINT,
    SMALLMONEY as SMALLMONEY,
    SQL_VARIANT as SQL_VARIANT,
    TEXT as TEXT,
    TIME as TIME,
    TIMESTAMP as TIMESTAMP,
    TINYINT as TINYINT,
    UNIQUEIDENTIFIER as UNIQUEIDENTIFIER,
    VARBINARY as VARBINARY,
    VARCHAR as VARCHAR,
    XML as XML,
    try_cast as try_cast,
)

__all__ = (
    "JSON",
    "INTEGER",
    "BIGINT",
    "SMALLINT",
    "TINYINT",
    "VARCHAR",
    "NVARCHAR",
    "CHAR",
    "NCHAR",
    "TEXT",
    "NTEXT",
    "DECIMAL",
    "NUMERIC",
    "FLOAT",
    "DATETIME",
    "DATETIME2",
    "DATETIMEOFFSET",
    "DATE",
    "TIME",
    "SMALLDATETIME",
    "BINARY",
    "VARBINARY",
    "BIT",
    "REAL",
    "IMAGE",
    "TIMESTAMP",
    "ROWVERSION",
    "MONEY",
    "SMALLMONEY",
    "UNIQUEIDENTIFIER",
    "SQL_VARIANT",
    "XML",
    "dialect",
    "try_cast",
)

dialect: Any
