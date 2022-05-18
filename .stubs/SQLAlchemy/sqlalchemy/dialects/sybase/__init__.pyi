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
    FLOAT as FLOAT,
    IMAGE as IMAGE,
    INT as INT,
    INTEGER as INTEGER,
    MONEY as MONEY,
    NCHAR as NCHAR,
    NUMERIC as NUMERIC,
    NVARCHAR as NVARCHAR,
    SMALLINT as SMALLINT,
    SMALLMONEY as SMALLMONEY,
    TEXT as TEXT,
    TIME as TIME,
    TINYINT as TINYINT,
    UNICHAR as UNICHAR,
    UNITEXT as UNITEXT,
    UNIVARCHAR as UNIVARCHAR,
    VARBINARY as VARBINARY,
    VARCHAR as VARCHAR,
)

__all__ = (
    "CHAR",
    "VARCHAR",
    "TIME",
    "NCHAR",
    "NVARCHAR",
    "TEXT",
    "DATE",
    "DATETIME",
    "FLOAT",
    "NUMERIC",
    "BIGINT",
    "INT",
    "INTEGER",
    "SMALLINT",
    "BINARY",
    "VARBINARY",
    "UNITEXT",
    "UNICHAR",
    "UNIVARCHAR",
    "IMAGE",
    "BIT",
    "MONEY",
    "SMALLMONEY",
    "TINYINT",
    "dialect",
)

dialect: Any
