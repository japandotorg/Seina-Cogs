"""
MIT License

Copyright (c) 2024-present japandotorg

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

import atexit
import weakref
from typing import Any

from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.common.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver as _Firefox
from selenium.webdriver.remote.webdriver import WebDriver as _Driver


class Driver(_Driver):
    active: bool

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        def _atexit():
            self.quit()

        def _finalizer(_driver: "Driver"):
            _driver.quit()

        self.active: bool = True
        self.__atexit__: object = atexit.register(_atexit)
        self._finalizer: weakref.finalize = weakref.finalize(self, _finalizer, self)

    def close(self) -> None:
        try:
            super().close()
        except BaseException:
            pass

    def quit(self) -> None:
        try:
            atexit.unregister(self.__atexit__)
        except BaseException:
            pass
        try:
            self.close()
        except BaseException:
            pass
        try:
            super().close()
        except BaseException:
            pass
        self.active: bool = False


class Firefox(Driver, _Firefox):
    def __init__(self, service: Service, options: BaseOptions, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, service=service, options=options, **kwargs)
