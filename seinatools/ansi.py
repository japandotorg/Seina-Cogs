# Shamelessly stolen from https://github.com/Drapersniper/PyLav/blob/master/pylav/utils/theme.py

from __future__ import annotations


class EightBitANSI:
    escape = "\u001b["
    white = "37"
    red = "31"
    bold = "1"
    italic = "3"
    underline = "4"
    reset = "0"

    @classmethod
    def colorize(
        cls,
        text: str,
        color: str,
        bold: bool = False,
        underline: bool = False,
        italic: bool = False,
    ) -> str:
        color = [getattr(cls, color, "39")]
        if bold:
            color.append(cls.bold)
        if italic:
            color.append(cls.italic)
        if underline:
            color.append(cls.underline)

        color_code = f"{cls.escape}{';'.join(color)}m"
        color_reset = f"{cls.escape}{cls.reset}m"
        text = f"{text}".replace("\n", f"{color_reset}\n{color_code}")

        return f"{color_code}{text}{color_reset}"

    @classmethod
    def paint_red(
        cls, text: str, bold: bool = False, underline: bool = False, italic: bool = False
    ) -> str:
        return cls.colorize(text, "red", bold, underline, italic)

    @classmethod
    def paint_white(
        cls, text: str, bold: bool = False, underline: bool = False, italic: bool = False
    ) -> str:
        return cls.colorize(text, "white", bold, underline, italic)
