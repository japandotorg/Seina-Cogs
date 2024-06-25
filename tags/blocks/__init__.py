"""
MIT License

Copyright (c) 2020-2023 PhenoM4n4n
Copyright (c) 2023-present japandotorg

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

from typing import Tuple

from .allowed_mentions import AllowedMentionsBlock as AllowedMentionsBlock
from .comment import CommentBlock as CommentBlock
from .customcom import ContextVariableBlock as ContextVariableBlock
from .customcom import ConverterBlock as ConverterBlock
from .delete import DeleteBlock as DeleteBlock
from .react import ReactBlock as ReactBlock
from .reply import ReplyBlock as ReplyBlock
from .silent import SilentBlock as SilentBlock

__all__: Tuple[str, ...] = (
    "DeleteBlock",
    "SilentBlock",
    "ReplyBlock",
    "ReactBlock",
    "ContextVariableBlock",
    "ConverterBlock",
    "CommentBlock",
)
