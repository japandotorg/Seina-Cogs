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
    BFILE as BFILE,
    BINARY_DOUBLE as BINARY_DOUBLE,
    BINARY_FLOAT as BINARY_FLOAT,
    BLOB as BLOB,
    CHAR as CHAR,
    CLOB as CLOB,
    DATE as DATE,
    DOUBLE_PRECISION as DOUBLE_PRECISION,
    FLOAT as FLOAT,
    INTERVAL as INTERVAL,
    LONG as LONG,
    NCHAR as NCHAR,
    NCLOB as NCLOB,
    NUMBER as NUMBER,
    NVARCHAR as NVARCHAR,
    NVARCHAR2 as NVARCHAR2,
    RAW as RAW,
    ROWID as ROWID,
    TIMESTAMP as TIMESTAMP,
    VARCHAR as VARCHAR,
    VARCHAR2 as VARCHAR2,
)

__all__ = (
    "VARCHAR",
    "NVARCHAR",
    "CHAR",
    "NCHAR",
    "DATE",
    "NUMBER",
    "BLOB",
    "BFILE",
    "CLOB",
    "NCLOB",
    "TIMESTAMP",
    "RAW",
    "FLOAT",
    "DOUBLE_PRECISION",
    "BINARY_DOUBLE",
    "BINARY_FLOAT",
    "LONG",
    "dialect",
    "INTERVAL",
    "VARCHAR2",
    "NVARCHAR2",
    "ROWID",
)

dialect: Any
