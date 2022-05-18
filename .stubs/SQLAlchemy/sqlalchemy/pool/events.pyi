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

from .. import event

class PoolEvents(event.Events):
    def connect(self, dbapi_connection, connection_record) -> None: ...
    def first_connect(self, dbapi_connection, connection_record) -> None: ...
    def checkout(self, dbapi_connection, connection_record, connection_proxy) -> None: ...
    def checkin(self, dbapi_connection, connection_record) -> None: ...
    def reset(self, dbapi_connection, connection_record) -> None: ...
    def invalidate(self, dbapi_connection, connection_record, exception) -> None: ...
    def soft_invalidate(self, dbapi_connection, connection_record, exception) -> None: ...
    def close(self, dbapi_connection, connection_record) -> None: ...
    def detach(self, dbapi_connection, connection_record) -> None: ...
    def close_detached(self, dbapi_connection) -> None: ...
