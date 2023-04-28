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

## Thanks TrustyJAID <https://github.com/TrustyJAID/Trusty-cogs/blob/master/.utils/utils.py>

import glob
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Final, List, Mapping, Optional, Pattern, TextIO, Union, final

import click
import tabulate
from babel.lists import format_list as babel_list
from typing_extensions import Annotated, Self

DEFAULT_INFO: Dict[str, Any] = {
    "author": [],
    "install_msg": "",
    "name": "",
    "disabled": False,
    "short": "",
    "description": "",
    "tags": [],
    "requirements": [],
    "hidden": False,
}

logging.basicConfig(filename="scripts.log", level=logging.INFO)
log: logging.Logger = logging.getLogger(__file__)
handler: logging.StreamHandler[TextIO] = logging.StreamHandler(sys.stdout)
formatter: logging.Formatter = logging.Formatter(
    "[{asctime}] [{levelname}] {name}: {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
)
handler.setFormatter(formatter)
log.addHandler(handler)

ROOT: Path = Path(__file__).parent.resolve().parents[0]

VER_REG: Pattern[str] = re.compile(r"\_\_version\_\_ = \"(\d+\.\d+\.\d+)", flags=re.I)

DEFAULT_AUTHOR: List[str] = ["inthedark.org#0666"]

HEADER: Final[str] = (
    "# Seina-Cogs V3\n"
    "[![Red-DiscordBot](https://img.shields.io/badge/Red--DiscordBot-V3-red.svg)](https://github.com/Cog-Creators/Red-DiscordBot)"
    "[![Discord.py](https://img.shields.io/badge/Discord.py-rewrite-blue.svg)](https://github.com/Rapptz/discord.py/tree/rewrite)\n\n"
    "Lemon's Cogs for [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot/tree/V3/develop)."
    "To add the cogs to your instance please do: `[p]repo add Seina-Cogs https://github.com/japandotorg/Seina-Cogs/`\n"
    "## About Cogs\n"
    "{body}\n\n"
    "Any questions you can find [Melon](https://discord.com/oauth2/authorize?client_id=808706062013825036&scope=bot&permissions=1099511627767%20applications.commands) and myself over on [the support server](https://discord.gg/mXfYuMy92r)\n"
    "## Credits\n"
    "Thank you to everyone in the official [red server](https://discord.gg/red) for always being nice and helpful"
)


@final
@dataclass
class InfoJson:
    author: List[str]
    description: Optional[str] = ""
    install_msg: Optional[str] = "Thanks for installing"
    short: Optional[str] = ""
    name: Optional[str] = ""
    min_bot_version: Optional[str] = "3.3.0"
    max_bot_version: Optional[str] = "0.0.0"
    hidden: Optional[bool] = False
    disabled: Optional[bool] = False
    required_cogs: Mapping = field(default_factory=dict)
    requirements: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    type: Optional[str] = "COG"
    permissions: List[str] = field(default_factory=list)
    min_python_version: Optional[List[int]] = field(default_factory=lambda: [3, 8, 0])
    end_user_data_statement: str = (
        "This cog does not persistently store data or metadata about users."
    )

    @classmethod
    def from_json(cls, data: Dict[Any, Any]) -> Self:
        required_cogs: Mapping = {}
        author = data.get("author", [])
        description = data.get("description", "")
        install_msg = data.get("install_msg", "Thanks for installing")
        short = data.get("short", "Thanks for installing")
        min_bot_version = "3.1.8"
        if "bot_version" in data:
            min_bot_version = data["bot_version"]
            if isinstance(min_bot_version, list):
                min_bot_version = ".".join(str(i) for i in data["bot_version"])
        if "min_bot_version" in data:
            min_bot_version = data["min_bot_version"]
            # min_bot_version = "3.3.0"
        max_bot_version = data.get("max_bot_version", "0.0.0")
        name = data.get("name", "")
        if "required_cogs" in data:
            if isinstance(data["required_cogs"], list):
                required_cogs = {}
            else:
                required_cogs = data["required_cogs"]
        requirements = data.get("requirements", [])
        tags = data.get("tags", [])
        hidden = data.get("hidden", False)
        disabled = data.get("disabled", False)
        type = data.get("type", "COG")
        permissions = data.get("permissions", [])
        min_python_version = data.get("min_python_version", [])
        end_user_data_statement = data.get(
            "end_user_data_statement",
            "This cog does not persistently store data or metadata about users.",
        )

        return cls(
            author,
            description,
            install_msg,
            short,
            name,
            min_bot_version,
            max_bot_version,
            hidden,
            disabled,
            required_cogs,
            requirements,
            tags,
            type,
            permissions,
            min_python_version,
            end_user_data_statement,
        )


def save_json(folder: str, data: Union[MappingProxyType, Any]) -> None:
    with open(folder, "w") as newfile:
        json.dump(data, newfile, indent=4, sort_keys=True, separators=(",", " : "))


@click.group()
def cli() -> None:
    """Utilities for Cog creation!"""


@cli.command()
def mass_fix() -> None:
    """Ensure all info.json files are up-to-date with current standards"""
    for folder in os.listdir(f"{ROOT}/"):
        if folder.startswith("."):
            continue
        try:
            with open(f"{ROOT}/{folder}/info.json", "r") as infile:
                info = InfoJson.from_json(json.load(infile))
            save_json(f"{ROOT}/{folder}/info.json", info.__dict__)
        except Exception:
            log.exception(f"Error reading info.json in {folder}")
            continue


@cli.command()
@click.option(
    "--key",
    prompt="Enter the json key you want to edit.",
    help="Name of the key being edited",
)
@click.option(
    "--value",
    prompt="Enter the value for the key you want changed.",
    help="The value you want the key edited to.",
)
def edit(key: str, value: Annotated[Union[str, int], click.types.STRING, click.types.INT]):
    for folder in os.listdir(f"{ROOT}/"):
        if folder.startswith("."):
            continue
        try:
            with open(f"{ROOT}/{folder}/info.json", "r") as infile:
                info = InfoJson.from_json(json.load(infile))
            setattr(info, key, value)
            save_json(f"{ROOT}/{folder}/info.json", info.__dict__)
        except Exception:
            log.exception(f"Error reading info.json in {folder}")
            continue


@cli.command()
@click.option("--author", default=DEFAULT_AUTHOR, help="Author of the cog", prompt=True)
@click.option("--name", prompt="Enter the name of the cog", help="Name of the cog being added")
@click.option(
    "--description",
    prompt="Enter a longer description for the cog.",
    help="Description about what the cog can do.",
)
@click.option(
    "--install-msg",
    prompt=True,
    default="Thanks for installing!",
    help="Enter the install message you would like. Default is `Thanks for installing!`",
)
@click.option(
    "--short",
    prompt="Enter a short description about the cog.",
    help="Enter a short description about the cog.",
)
@click.option(
    "--min-bot-version",
    default="3.3.0",
    help="This cogs minimum python version requirements.",
    prompt=True,
)
@click.option(
    "--max-bot-version",
    default="0.0.0",
    help="This cogs minimum python version requirements.",
    prompt=True,
)
@click.option(
    "--hidden",
    default=False,
    help="Whether or not the cog is hidden from downloader.",
    prompt=True,
    type=bool,
)
@click.option(
    "--disabled",
    default=False,
    help="Whether or not the cog is disabled in downloader.",
    prompt=True,
    type=bool,
)
@click.option("--required-cogs", default={}, help="Required cogs for this cog to function.")
@click.option("--requirements", prompt=True, default=[], help="Requirements for the cog.")
@click.option(
    "--tags",
    default=[],
    prompt=True,
    help="Any tags to help people find the cog better.",
)
@click.option("--permissions", prompt=True, default=[], help="Any permissions the cog requires.")
@click.option(
    "--min-python-version",
    default=[3, 8, 0],
    help="This cogs minimum python version requirements.",
)
@click.option(
    "--end-user-data-statement",
    prompt=True,
    default="This cog does not persistently store data or metadata about users.",
    help="The end user data statement for this cog.",
)
def make(
    author: list,
    name: str,
    description: str = "",
    install_msg: str = "",
    short: str = "",
    min_bot_version: str = "3.3.0",
    max_bot_version: str = "0.0.0",
    hidden: bool = False,
    disabled: bool = False,
    required_cogs: Mapping[str, str] = {},
    requirements: List[str] = [],
    tags: list = [],
    permissions: list = [],
    min_python_version: list = [3, 8, 0],
    end_user_data_statement: str = "This cog does not persistently store data or metadata about users.",
):
    """Generate a new info.json file for your new cog!"""
    if isinstance(author, str):
        author = [author]
        if ", " in author:
            author = author.split(", ")
    if isinstance(requirements, str):
        requirements = requirements.split(" ")
    if isinstance(permissions, str):
        permissions = permissions.split(" ")
    if isinstance(tags, str):
        tags = tags.split(" ")
    if isinstance(min_python_version, str):
        min_python_version = [int(i) for i in min_python_version.split(".")]
    type = "COG"
    data_obj = InfoJson(
        author,
        description,
        install_msg,
        short,
        name,
        min_bot_version,
        max_bot_version,
        hidden,
        disabled,
        required_cogs,
        requirements,
        tags,
        type,
        permissions,
        min_python_version,
        end_user_data_statement,
    )
    log.debug(data_obj)
    save_json(f"{ROOT}/{name}/info.json", data_obj.__dict__)


@cli.command()
@click.option("--include-hidden", default=False)
@click.option("--include-disabled", default=False)
def countlines(include_hidden: bool = False, include_disabled: bool = False) -> List[Any]:
    """Count the number of lines of .py files in all folders"""
    total = 0
    totals = []
    log.debug(ROOT)
    for folder in os.listdir(ROOT):
        cog_path = ROOT / folder
        cog = 0
        if folder.startswith("."):
            continue
        if not cog_path.is_dir():
            log.debug(f"{cog_path} is not a directory")
            continue
        try:
            with open(cog_path / "info.json", "r") as infile:
                info = InfoJson.from_json(json.load(infile))
        except Exception:
            info = InfoJson(DEFAULT_AUTHOR, hidden=True, disabled=True)
            log.debug(f"Error opening {cog_path} info.json")
        if info.hidden and not include_hidden:
            continue
        if info.disabled and not include_disabled:
            continue
        try:
            for file in os.listdir(cog_path):
                file_path = cog_path / file
                if not file_path.is_file():
                    continue
                if not file.endswith(".py"):
                    continue
                try:
                    with open(file_path, "r") as infile:
                        lines = len(infile.readlines())
                        log.debug(f"{file_path} has {lines} lines of code")
                    cog += lines
                    total += lines
                except Exception:
                    log.exception(f"Error opening {file_path}")
            totals.append((folder, cog))
        except Exception:
            log.exception(f"Error reading {folder}")
    totals = sorted(totals, key=lambda x: x[1], reverse=True)
    totals.insert(0, ("Total", total))
    print(tabulate.tabulate(totals, headers=["Cog", "# of Lines"], tablefmt="pretty"))
    return totals


@cli.command()
@click.option("--include-hidden", default=False)
@click.option("--include-disabled", default=False)
def countchars(include_hidden: bool = False, include_disabled: bool = False) -> List[Any]:
    """Count the number of lines of .py files in all folders"""
    total = 0
    totals = []
    log.info(f"{ROOT}")
    for folder in os.listdir(f"{ROOT}/"):
        cog = 0
        if folder.startswith("."):
            continue
        try:
            with open(f"{ROOT}/{folder}/info.json", "r") as infile:
                info = InfoJson.from_json(json.load(infile))
        except Exception:
            continue
        if info.hidden and not include_hidden:
            continue
        if info.disabled and not include_disabled:
            continue
        try:
            for file in glob.glob(f"{ROOT}/{folder}/*.py"):
                try:
                    with open(file, "r") as infile:
                        lines = len(infile.read())
                    cog += lines
                    total += lines
                except Exception:
                    pass
            totals.append((folder, cog))
        except Exception:
            pass
    totals = sorted(totals, key=lambda x: x[1], reverse=True)
    totals.insert(0, ("Total", total))
    print(tabulate.tabulate(totals, headers=["Cog", "# ofchars"], tablefmt="pretty"))
    return totals


@cli.command()
def makereadme() -> None:
    """Generate README.md from info about all cogs"""
    table_data = []
    for folder in os.listdir(ROOT):
        if folder.startswith(".") or folder.startswith("_"):
            continue
        _version = ""
        info = None
        for file in glob.glob(f"{ROOT}/{folder}/*"):
            if not file.endswith(".py") and not file.endswith("json"):
                continue
            if file.endswith("info.json"):
                try:
                    with open(file) as infile:
                        data = json.loads(infile.read())
                    info = InfoJson.from_json(data)
                except Exception:
                    log.exception(f"Error reading info.json {file}")
            if _version == "":
                with open(file, "r", encoding="utf-8") as infile:
                    data = infile.read()
                    if maybe_version := VER_REG.search(data):
                        _version = maybe_version.group(1)
        if info and not info.disabled and not info.hidden:
            description = f"<details><summary>{info.short}</summary>{info.description}</details>"
            to_append = [
                info.name,
                _version,
                description,
                babel_list(info.author, style="standard", locale="en"),
            ]
            table_data.append(to_append)

    body = tabulate.tabulate(
        table_data,
        headers=[
            "Name",
            "Status/Version",
            "Description (Click to see full status)",
            "Authors",
        ],
        tablefmt="github",
    )
    with open(f"{ROOT}/README.md", "w") as outfile:
        outfile.write(HEADER.format(body=body))


@cli.command()
def makerequirements() -> None:
    """Generate a requirements.txt for all cogs.
    Useful when setting up the bot in a new venv and requirements are missing.
    """
    requirements = set()
    with open(ROOT / "requirements.txt", "r") as infile:
        current_reqs = {_req.strip() for _req in infile.readlines()}
    for folder in os.listdir(ROOT):
        if folder.startswith(".") or folder.startswith("_"):
            continue
        info = None
        for file in glob.glob(f"{ROOT}/{folder}/*"):
            if not file.endswith(".py") and not file.endswith("json"):
                continue
            if file.endswith("info.json"):
                try:
                    with open(file) as infile:
                        data = json.loads(infile.read())
                    info = InfoJson.from_json(data)
                    if info.disabled:
                        continue
                    for req in info.requirements:
                        requirements.add(req)
                except Exception:
                    log.exception(f"Error reading info.json {file}")
    reqs = sorted(requirements)
    if current_reqs == requirements:
        log.info("Same requirements, ignoring")
        return
    requirements_txt = "{reqs}\n".format(reqs="\n".join(reqs))
    with open(ROOT / "requirements.txt", "w") as outfile:
        outfile.write(requirements_txt)


def run_cli() -> None:
    try:
        cli()
    except KeyboardInterrupt:
        log.debug("Exiting.")
    else:
        log.debug("Exiting.")


if __name__ == "__main__":
    run_cli()
