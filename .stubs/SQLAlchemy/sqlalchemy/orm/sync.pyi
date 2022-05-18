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

def populate(source, source_mapper, dest, dest_mapper, synchronize_pairs, uowcommit, flag_cascaded_pks) -> None: ...
def bulk_populate_inherit_keys(source_dict, source_mapper, synchronize_pairs) -> None: ...
def clear(dest, dest_mapper, synchronize_pairs) -> None: ...
def update(source, source_mapper, dest, old_prefix, synchronize_pairs) -> None: ...
def populate_dict(source, source_mapper, dict_, synchronize_pairs) -> None: ...
def source_modified(uowcommit, source, source_mapper, synchronize_pairs): ...
