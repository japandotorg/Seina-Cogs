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

from io import BytesIO

import discord
from redbot.core import checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, inline, pagify

from .utils.cog_settings import CogSettings


class ModNotes(commands.Cog):
    """Keep tabs on sussy users"""

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.settings = ModNotesSettings("modnotes")

    @commands.group(aliases=["usernote", "modnotes", "modnote"])
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    async def usernotes(self, ctx):
        """
        Moderator notes for users.
        This module allows you to create notes to share between moderators.
        """

    async def red_get_data_for_user(self, *, user_id):
        """Get a user's personal data."""
        data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        return

    @usernotes.command()
    @checks.mod_or_permissions(manage_guild=True)
    async def get(self, ctx, user: discord.User):
        """Sends the notes for a user."""
        notes = self.settings.getNotesForUser(ctx.guild.id, user.id)
        if not notes:
            await ctx.send(box(f"No notes for {user.name}"))
            return

        for idx, note in enumerate(notes):
            await ctx.send(inline(f"Note {idx + 1} of {len(notes)}:"))
            await ctx.send(box(note))

    @usernotes.command()
    @checks.mod_or_permissions(manage_guild=True)
    async def add(self, ctx, user: discord.User, *, note_text: str):
        """Add a note to a user."""
        timestamp = str(ctx.message.created_at)[:-7]
        msg = f"Added by {ctx.author.name} ({timestamp}): {note_text}"
        server_id = ctx.guild.id
        notes = self.settings.addNoteForUser(server_id, user.id, msg)
        await ctx.send(inline(f"Done. User {user.name} now has {len(notes)} notes"))

    @usernotes.command()
    @checks.mod_or_permissions(manage_guild=True)
    async def delete(self, ctx, user: discord.User, note_num: int):
        """Delete a specific note for a user."""
        notes = self.settings.getNotesForUser(ctx.guild.id, user.id)
        if len(notes) < note_num:
            await ctx.send(box(f"Note not found for {user.name}"))
            return

        note = notes[note_num - 1]
        notes.remove(note)
        self.settings.setNotesForUser(ctx.guild.id, user.id, notes)
        await ctx.send(inline(f"Removed note {note_num}. User has {len(notes)} remaining."))

        await ctx.send(box(note))

    @usernotes.command()
    @checks.mod_or_permissions(manage_guild=True)
    async def list(self, ctx):
        """Lists all users and note counts for the server."""
        user_notes = self.settings.getUserNotes(ctx.guild.id)
        msg = f"Notes for {len(user_notes)} users"
        for user_id, notes in user_notes.items():
            user = ctx.guild.get_member(user_id)
            user_text = f"{user.name} ({user.id})" if user else user_id
            msg += "\n\t{} : {}".format(len(notes), user_text)

        for page in pagify(msg):
            await ctx.send(box(page))


class ModNotesSettings(CogSettings):
    def make_default_settings(self):
        return {"servers": {}}

    def servers(self):
        return self.bot_settings["servers"]

    def getServer(self, server_id):
        servers = self.servers()
        if server_id not in servers:
            servers[server_id] = {}
        return servers[server_id]

    def getUserNotes(self, server_id):
        server = self.getServer(server_id)
        key = "user_notes"
        if key not in server:
            server[key] = {}
        return server[key]

    def getNotesForUser(self, server_id, user_id):
        user_notes = self.getUserNotes(server_id)
        return user_notes.get(user_id, [])

    def setNotesForUser(self, server_id, user_id, notes):
        user_notes = self.getUserNotes(server_id)

        if notes:
            user_notes[user_id] = notes
        else:
            user_notes.pop(user_id, None)
        self.save_settings()
        return notes

    def addNoteForUser(self, server_id, user_id, note: str):
        notes = self.getNotesForUser(server_id, user_id)
        notes.append(note)
        self.setNotesForUser(server_id, user_id, notes)
        return notes
