from typing import TYPE_CHECKING, Dict, Generic, List, Protocol, TypeVar

if TYPE_CHECKING:
    from .core import AutoReact

_T = TypeVar("_T", bound="AutoReact")


class CacheProtocol(Protocol):
    def __init__(self, cog: "AutoReact") -> None: ...

    async def initialize(self) -> None: ...


class Cache(CacheProtocol, Generic[_T]):
    def __init__(self, cog: "AutoReact") -> None:
        self.cog: "AutoReact" = cog
        self.autoreact: Dict[int, Dict[str, List[str]]] = {}
        self.event: Dict[int, Dict[str, List[str]]] = {}

    async def initialize(self) -> None:
        autoreact: Dict[int, Dict[str, Dict[str, List[str]]]] = await self.cog.config.all_guilds()
        for guild_id, guild_data in autoreact.items():
            self.autoreact[guild_id] = guild_data.get("reaction", {})
            self.event[guild_id] = guild_data.get("event", {})
