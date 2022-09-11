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

import requests


def _fetch_user(username: str):
    """
    Fetches the username from the maplestory api.
    """
    overall_url = f"https://maplestory.nexon.net/api/ranking?id=overall&id2=legendary&rebootIndex=0&character_name={username}&page_index=1"
    o_response = requests.get(overall_url).json()

    world_url = f"https://maplestory.nexon.net/api/ranking?id=overall&id2=legendary&rebootIndex={(1 if (o_response[0]['WorldID'] == 45 ) else 2)}&character_name={username}&page_index=1"
    w_response = requests.get(world_url).json()

    return [o_response[0], w_response[0]]
