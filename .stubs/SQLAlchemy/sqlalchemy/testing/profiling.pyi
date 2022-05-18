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

class ProfileStatsFile:
    force_write: Any
    write: Any
    fname: Any
    short_fname: Any
    data: Any
    dump: Any
    sort: Any
    def __init__(self, filename, sort: str = ..., dump: Any | None = ...): ...
    @property
    def platform_key(self): ...
    def has_stats(self): ...
    def result(self, callcount): ...
    def reset_count(self) -> None: ...
    def replace(self, callcount) -> None: ...

def function_call_count(variance: float = ..., times: int = ..., warmup: int = ...): ...
def count_functions(variance: float = ...) -> None: ...
