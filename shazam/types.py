"""
MIT License

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

from typing import Dict, Literal

from shazamio.enums import GenreMusic


Genre = Literal[
    "pop",
    "hiphop",
    "dance",
    "electronic",
    "soul",
    "alternative",
    "rock",
    "latin",
    "film",
    "country",
    "afro",
    "worldwide",
    "reggae",
    "house",
    "kpop",
    "french",
    "singer",
    "mexicano",
]


GENRE: Dict[str, GenreMusic] = {
    "pop": GenreMusic.POP,
    "hiphop": GenreMusic.HIP_HOP_RAP,
    "dance": GenreMusic.DANCE,
    "electronic": GenreMusic.ELECTRONIC,
    "soul": GenreMusic.RNB_SOUL,
    "alternative": GenreMusic.ALTERNATIVE,
    "rock": GenreMusic.ROCK,
    "latin": GenreMusic.LATIN,
    "film": GenreMusic.FILM_TV_STAGE,
    "country": GenreMusic.COUNTRY,
    "afro": GenreMusic.AFRO_BEATS,
    "worldwide": GenreMusic.WORLDWIDE,
    "reggae": GenreMusic.REGGAE_DANCE_HALL,
    "house": GenreMusic.HOUSE,
    "kpop": GenreMusic.K_POP,
    "french": GenreMusic.FRENCH_POP,
    "singer": GenreMusic.SINGER_SONGWRITER,
    "mexicano": GenreMusic.REGIONAL_MEXICANO,
}
