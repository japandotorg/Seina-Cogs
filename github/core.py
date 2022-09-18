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

import logging
import re
import typing as t
from dataclasses import dataclass

import discord
from aiohttp import ClientResponse, ClientSession
from redbot.core import Config, commands  # type: ignore
from redbot.core.bot import Red  # type: ignore

log: logging.Logger = logging.getLogger("red.seinacogs.gihtub.core")

GITHUB_API_URL = "https://api.github.com"

REQUEST_HEADERS = {"Accept": "application/vnd.github.v3+json"}

REPOSITORY_ENDPOINT = "https://api.github.com/orgs/{org}/repos?per_page=100&type=public"
ISSUE_ENDPOINT = "https://api.github.com/repos/{user}/{repository}/issues/{number}"
PR_ENDPOINT = "https://api.github.com/repos/{user}/{repository}/pulls/{number}"

CODE_BLOCK_RE = re.compile(r"^`([^`\n]+)`" r"|```(.+?)```", re.DOTALL | re.MULTILINE)

MAXIMUM_ISSUES = 5

AUTOMATIC_RE = re.compile(
    r"((?P<org>[a-zA-Z0-9][a-zA-Z0-9\-]{1,39})\/)?(?P<repo>[\w\-\.]{1,100})#(?P<number>[0-9]+)"
)


@dataclass(eq=True, frozen=True)
class FoundIssue:
    """
    Dataclass representing an issue found by the regex.
    """

    organization: t.Optional[str]
    repository: str
    number: str


@dataclass(eq=True, frozen=True)
class FetchError:
    """
    Dataclass representing an error while fetching an issue.
    """

    return_code: int
    message: str


@dataclass(eq=True, frozen=True)
class IssueState:
    """
    Dataclass representing the state of an issue.
    """

    repository: str
    number: int
    url: str
    title: str
    emoji: str


class Github(commands.Cog):
    """
    A cog that fetches information from Github.
    """

    def __init__(self, bot: Red):
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=666, force_registration=True)

        self.session: ClientSession = ClientSession()

        self.repos = []

        default_guild = {"toggle": False}
        self.config.register_guild(**default_guild)

    @staticmethod
    def remove_codeblocks(message: str) -> str:
        """
        Removes any codeblock in a message.
        """
        return CODE_BLOCK_RE.sub("", message)

    async def fetch_issue(
        self, number: int, repository: str, user: str
    ) -> t.Union[IssueState, FetchError]:
        """
        Fetch an issue from a Github repository.

        Returns
        -------
        IssueState on succes.
        FetchError on failure.
        """
        url = ISSUE_ENDPOINT.format(user=user, repository=repository, number=number)

        pulls_url = PR_ENDPOINT.format(user=user, repository=repository, number=number)

        json_data, r = await self.fetch_data(url)

        if r.status == 403:
            if r.headers.get("X-RateLimit-Remaining") == "0":
                log.exception(f"Ratelimit reached while fetching {url}")
                return FetchError(403, "Ratelimit reached, please retry in a few minutes.")

            return FetchError(403, "Cannot access issue.")

        elif r.status in (404, 410):
            return FetchError(r.status, "Issue not found.")

        elif r.status != 200:
            return FetchError(r.status, "Error while fetching issue.")

        if "issues" in json_data["html_url"]:
            if json_data.get("state") == "open":
                emoji = "\N{LARGE GREEN CIRCLE}"
            else:
                emoji = "\N{LARGE RED CIRCLE}"

        else:
            pull_data, _ = await self.fetch_data(pulls_url)
            if pull_data["draft"]:
                emoji = "\N{MEDIUM BLACK CIRCLE}"
            elif pull_data["state"] == "open":
                emoji = "\N{LARGE GREEN CIRCLE}"
            elif pull_data["merged_at"] is not None:
                emoji = "\N{LARGE PURPLE CIRCLE}"
            else:
                emoji = "\N{LARGE RED CIRCLE}"

        issue_url = json_data.get("html_url")

        return IssueState(repository, number, issue_url, json_data.get("title", ""), emoji)

    @staticmethod
    async def format_embed(results: t.List[t.Union[IssueState, FetchError]]) -> discord.Embed:
        """
        Take a list of IssueState of FetchError and format a Discord Embed for them.
        """
        description_list = []

        for result in results:
            if isinstance(result, IssueState):
                description_list.append(
                    f"{result.emoji} [[{result.repository}] #{result.number} {result.title}]({result.url})"
                )
            elif isinstance(result, FetchError):
                description_list.append(f"[{result.return_code}] {result.message}")

        resp: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description="\n".join(description_list),
        )
        resp.set_author(name="Github")
        return resp

    async def fetch_data(self, url: str) -> tuple[dict[str], ClientResponse]:
        """
        Retrieve data as a dictionary and the response in a tuple.
        """
        keys = await self.bot.get_shared_api_tokens("github")
        token = keys.get("api_key")

        if token is not None:
            REQUEST_HEADERS["Authorization"] = f"token {token}"

        async with self.session.get(url, headers=REQUEST_HEADERS) as response:
            return await response.json(), response

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Automatic issue linking.

        Listener to retrieve issue(s) from a Github repository
        using automatic linking if matching <org>/<repo>#<issue>
        """
        if message.author.bot:
            return

        if not (await self.config.guild(message.guild).toggle()):
            return

        issues = [
            FoundIssue(*match.group("org", "repo", "number"))
            for match in AUTOMATIC_RE.finditer(self.remove_codeblocks(message.content))
        ]
        links = []

        if issues:
            if not message.guild:
                return

            issues = list(dict.fromkeys(issues))

            if len(issues) > MAXIMUM_ISSUES:
                embed: discord.Embed = discord.Embed(
                    color=await ctx.embed_color(),
                    description=f"Too many issues/PRs! (maximum of {MAXIMUM_ISSUES})",
                )
                await message.channel.send(embed=embed, delete_after=5)
                return

            for repo_issue in issues:
                result = await self.fetch_issue(
                    int(repo_issue.number),
                    repo_issue.repository,
                    repo_issue.organization or "japandotorg",
                )
                if isinstance(result, IssueState):
                    links.append(result)

        if not links:
            return
        
        resp = await self.format_embed(links)
        await message.channel.send(embed=resp)

    @commands.group(name="githubset", aliases=["ghset"])
    @commands.guildowner_or_permissions(administrator=True)
    async def _githubset(self, ctx: commands.Context):
        """
        Commands for the Github configuration settings.
        """
        if ctx.invoked_subcommand is None:
            pass

    @_githubset.command(name="toggle", aliases=["t"])
    @commands.guildowner_or_permissions(administrator=True)
    async def _toggle(self, ctx: commands.Context, true_or_false: bool):
        """
        Toggle the github auto linking module.
        """
        await self.config.guild(ctx.guild).toggle.set(true_or_false)
        return await ctx.tick()
