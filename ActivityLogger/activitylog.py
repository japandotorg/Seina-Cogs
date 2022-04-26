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

import os
import sys
import pytz
import pyodbc
import timeit
import aioodbc
import logging
import textwrap
import warnings
import prettytable

from io import BytesIO
from collections import deque
from datetime import datetime, timedelta
from tsutils.time import DISCORD_DEFAULT_TZ

import discord
from redbot.core.bot import Red
from redbot.core import checks, commands, data_manager
from redbot.core.utils.chat_formatting import box, inline, pagify

warnings.filterwarnings("ignore")
log = logging.getLogger("red.seina-cogs.activitylog")


def mod_help(self, ctx, help_type):
    hs = getattr(self, help_type)
    return self.format_text_for_context(ctx, hs).format(ctx) if hs else hs


commands.Command.format_help_for_context = lambda s, c: mod_help(s, c, "help")
commands.Command.format_shortdoc_for_context = lambda s, c: mod_help(s, c, "short_doc")


def _data_file(file_name: str) -> str:
    return os.path.join(str(data_manager.cog_data_path(raw_name="activitylog")), file_name)


TIMESTAMP_FORMAT = "%Y-%m-%d %X"  # YYYY-MM-DD HH:MM:SS
DB_FILE = _data_file("log.db")

ALL_COLUMNS = [
    ("timestamp", "Time (PT)"),
    ("server_id", "Server"),
    ("channel_id", "Channel"),
    ("user_id", "User"),
    ("msg_type", "Type"),
    ("clean_content", "Message"),
]

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS messages(
    rowid INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    server_id STRING NOT NULL,
    channel_id STRING NOT NULL,
    user_id STRING NOT NULL,
    msg_type STRING NOT NULL,
    content STRING NOT NULL,
    clean_content STRING NOT NULL)
"""

CREATE_INDEX_1 = """
CREATE INDEX IF NOT EXISTS idx_messages_server_id_channel_id_user_id_timestamp
ON messages(server_id, channel_id, user_id, timestamp)
"""

CREATE_INDEX_2 = """
CREATE INDEX IF NOT EXISTS idx_messages_server_id_user_id_timestamp
ON messages(server_id, user_id, timestamp)
"""

CREATE_INDEX_3 = """
CREATE INDEX IF NOT EXISTS idx_messages_server_id_clean_content
ON messages(server_id, clean_content)
"""

CREATE_INDEX_4 = """
CREATE INDEX IF NOT EXISTS idx_messages_server_id_timestamp
ON messages(server_id, timestamp)
"""

CREATE_INDEX_5 = """
CREATE INDEX IF NOT EXISTS idx_messages_server_id_channel_id_timestamp
ON messages(server_id, channel_id, timestamp)
"""

MAX_LOGS = 500

USER_QUERY = """
SELECT * FROM (
    SELECT timestamp, channel_id, msg_type, clean_content
    FROM messages INDEXED BY idx_messages_server_id_user_id_timestamp
    WHERE server_id = ?
        AND user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
)
ORDER BY timestamp ASC
"""

CHANNEL_QUERY = """
SELECT * FROM (
    SELECT timestamp, user_id, msg_type, clean_content
    FROM messages INDEXED BY idx_messages_server_id_channel_id_timestamp
    WHERE server_id = ?
        AND channel_id = ?
        AND user_id <> ?
    ORDER BY timestamp DESC
    LIMIT ?
)
ORDER BY timestamp ASC
"""

USER_CHANNEL_QUERY = """
SELECT * FROM (
    SELECT timestamp, msg_type, clean_content
    FROM messages INDEXED BY idx_messages_server_id_channel_id_user_id_timestamp
    WHERE server_id = ?
        AND user_id = ?
        AND channel_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
)
ORDER BY timestamp ASC
"""

CONTENT_QUERY = """
SELECT * FROM (
    SELECT timestamp, channel_id, user_id, msg_type, clean_content
    FROM messages INDEXED BY idx_messages_server_id_clean_content
    WHERE server_id = ?
        AND lower(clean_content) LIKE lower(?)
        AND user_id <> ?
    ORDER BY timestamp DESC
    LIMIT ?
)
ORDER BY timestamp ASC
"""

DELETE_BEFORE_QUERY = """
DELETE
FROM messages
WHERE timestamp  < ?
"""

GET_USER_DATA_QUERY = """
SELECT * FROM (
    SELECT timestamp, channel_id, msg_type, clean_content
    FROM messages INDEXED BY idx_messages_server_id_user_id_timestamp
    WHERE user_id = ?
    ORDER BY timestamp DESC
)
ORDER BY timestamp ASC
"""

DELETE_USER_DATA_QUERY = """
DELETE
FROM messages
WHERE user_id = ?
"""

async def conn_attributes(conn):
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    conn.setdecoding(pyodbc.SQL_WMETADATA, encoding='utf-16le')
    conn.setencoding(encoding='utf-8')

class ActivityLogger(commands.Cog):
    " Log activity seen by bot "
    
    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.lock = True
        self.insert_timing = deque(maxlen=1000)
        self.db_path = DB_FILE
        self.pool = None

    async def red_get_data_for_user(self, *, user_id):
        """ Get a user's personal data. """
        
        values = [
            user_id,
        ]
        
        column_data = [
            ('timestamp', 'Time (PT)'),
            ('channel_id', 'Channel'),
            ('msg_type', 'Type'),
            ('clean_content', 'Message'),
        ]

        data = (
            "NOTE: Data stored by this cog is essential for moderator use "
            "so data deletion requests can only be made by the bot owner and "
            "Discord itself.  If you need your data deleted, please contact a "
            "bot owner.\n\n\n"
        )
        
        data += await self.query_and_save(None, None, GET_USER_DATA_QUERY, values, column_data)
        
        return {
            "user_data.txt": BytesIO(data.encode())
        }
        
    async def red_delete_data_for_user(self, *, requester, user_id):
        """
        Delete a user's personal data.
        The personal data stored in this cog is for essential moderation use,
        so some data deletion requests can only be made by the bot owner and
        Discord itself.  If this is an issue, please contact a bot owner.
        """
        if requester not in ("discord_deleted_user", "owner"):
            return

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(DELETE_USER_DATA_QUERY, [user_id])
                
    def cog_unload(self):
        log.debug('Seniority: unloading')
        self.lock = True
        if self.pool:
            self.pool.close()
            self.bot.loop.create_task(self.pool.wait_closed())
            self.pool = None
        else:
            log.error('unexpected error: pool was None')
        log.debug('Seniority: unloading complete')
        
    async def init(self):
        log.debug('ActivityLog: init')
        if not self.lock:
            log.info('ActivityLog: bailing on unlock')
            return
        
        if os.name != 'nt' and sys.platform != 'win32':
            dsn = 'Driver=SQLite3;Database=' + self.db_path
        else:
            dsn = 'Driver=SQLite3 ODBC Driver;Database=' + self.db_path
        self.pool = await aioodbc.create_pool(dsn=dsn, autocommit=True, after_created=conn_attributes)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(CREATE_TABLE)
                await cur.execute(CREATE_INDEX_1)
                await cur.execute(CREATE_INDEX_2)
                await cur.execute(CREATE_INDEX_3)
                await cur.execute(CREATE_INDEX_4)
        await self.purge()
        self.lock = False
        
        log.debug('ActivityLog: init complete')
        
    @commands.command()
    @checks.is_owner()
    async def rawquery(self, ctx, *, query: str):
        await self.query_and_show(ctx, ctx.guild, query, {}, {})
        
    @commands.command()
    @checks.is_owner()
    async def inserttiming(self, ctx):
        size = len(self.insert_timing)
        avg_time = round(sum(self.insert_timing) / size, 4)
        max_time = round(max(self.insert_timing), 4)
        min_time = round(min(self.insert_timing), 4)
        await ctx.send(inline('{} inserts, min={} max={} avg={}'.format(size, min_time, max_time, avg_time)))
        
    @commands.command()
    @checks.is_owner()
    async def togglelock(self, ctx):
        """
        Prevents the bot from inserting into the db.
        This is useful if you need to use sqlite3 to access the database for some reason.
        Will keep the bot from locking up trying to insert records.
        """
        self.lock = not self.lock
        await ctx.send(inline('Locked is now {}'.format(self.lock)))

    @commands.group()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_guild=True)
    async def exlog(self, context):
        """
        Extra log querying tools.
        Uses the bot's local SQL message storage to retrieve deleted/edited messages.
        """

    @exlog.command()
    async def user(self, ctx, user: discord.User, count=10):
        """
        exlog user "{0.author.name}" 100
        List of messages for a user across all channels.
        Count is optional, with a low default and a maximum value.
        """
        count = min(count, MAX_LOGS)
        server = ctx.guild
        values = [
            server.id,
            user.id,
            count
        ]
        column_data = [
            ('timestamp', 'Time (PT)'),
            ('channel_id', 'Channel'),
            ('msg_type', 'Type'),
            ('clean_content', 'Message'),
        ]

        await self.query_and_show(ctx, server, USER_QUERY, values, column_data)

    @exlog.command()
    async def channel(self, ctx, channel: discord.TextChannel, count=10):
        """
        exlog channel #general_chat 100
        List of messages in a given channel.
        Count is optional, with a low default and a maximum value.
        The bot is excluded from results.
        """
        count = min(count, MAX_LOGS)
        server = channel.guild
        values = [
            server.id,
            channel.id,
            self.bot.user.id,
            count
        ]
        column_data = [
            ('timestamp', 'Time (PT)'),
            ('user_id', 'User'),
            ('msg_type', 'Type'),
            ('clean_content', 'Message'),
        ]

        await self.query_and_show(ctx, server, CHANNEL_QUERY, values, column_data)

    @exlog.command()
    async def userchannel(self, ctx, user: discord.User, channel: discord.TextChannel, count=10):
        """
        exlog userchannel "{0.author.name}" #general_chat 100
        List of messages from a user in a given channel.
        Count is optional, with a low default and a maximum value.
        """
        count = min(count, MAX_LOGS)
        server = channel.guild
        values = [
            server.id,
            user.id,
            channel.id,
            count
        ]
        column_data = [
            ('timestamp', 'Time (PT)'),
            ('msg_type', 'Type'),
            ('clean_content', 'Message'),
        ]

        await self.query_and_show(ctx, server, USER_CHANNEL_QUERY, values, column_data)

    @exlog.command()
    async def query(self, ctx, query, count=10):
        """exlog query "4 whale" 100
        Case-insensitive search of messages from every user/channel.
        Put the query in quotes if it is more than one word.
        Count is optional, with a low default and a maximum value.
        The bot is excluded from results.
        """
        if query[0] in ('%', '_'):
            await ctx.send('`You cannot start this query with a wildcard`')
            return

        count = min(count, MAX_LOGS)
        server = ctx.guild
        values = [
            server.id,
            query,
            self.bot.user.id,
            count
        ]
        column_data = [
            ('timestamp', 'Time (PT)'),
            ('channel_id', 'Channel'),
            ('user_id', 'User'),
            ('msg_type', 'Type'),
            ('clean_content', 'Message'),
        ]

        await self.query_and_show(ctx, server, CONTENT_QUERY, values, column_data)

    async def query_and_show(self, ctx, server, query, values, column_data, max_rows=MAX_LOGS * 2, verbose=True):
        result_text = await self.query_and_save(ctx, server, query, values, column_data, max_rows, verbose)
        for p in pagify(result_text):
            await ctx.send(box(p))

    async def query_and_save(self, ctx, server, query, values, column_data, max_rows=MAX_LOGS * 2, verbose=True):
        before_time = timeit.default_timer()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, values)
                rows = await cur.fetchall()
                results_columns = [d[0] for d in cur.description]

        execution_time = timeit.default_timer() - before_time

        if len(column_data) == 0:
            column_data = ALL_COLUMNS

        column_data = [r for r in column_data if r[0] in results_columns]
        for missing_col in [col for col in results_columns if col not in [c[0] for c in column_data]]:
            column_data.append((missing_col, missing_col))

        column_names = [c[0] for c in column_data]
        column_headers = [c[1] for c in column_data]

        tbl = prettytable.PrettyTable(column_headers)
        tbl.hrules = prettytable.HEADER
        tbl.vrules = prettytable.NONE
        tbl.align = 'l'

        for idx, row in enumerate(rows):
            if idx > max_rows:
                break

            table_row = list()
            cols = next(zip(*row.cursor_description))

            for col in column_names:
                if col not in cols:
                    table_row.append('')
                    continue
                raw_value = row[cols.index(col)]
                value = str(raw_value)
                if col == 'timestamp':
                    # Assign a UTC timezone to the datetime
                    raw_value = raw_value.replace(tzinfo=pytz.utc)
                    # Change the UTC timezone to PT
                    raw_value = DISCORD_DEFAULT_TZ.normalize(raw_value)
                    value = raw_value.strftime("%F %X")
                if col == 'channel_id':
                    channel = server.get_channel(int(value)) if server else None
                    value = channel.name if channel else value
                if col == 'user_id':
                    member = server.get_member(int(value)) if server else None
                    value = member.name if member else value
                if col == 'server_id':
                    server_obj = self.bot.get_guild(int(value))
                    value = server_obj.name if server_obj else value
                if col == 'clean_content':
                    value = value.replace('```', '~~~')
                    value = value.replace('`', '\\`')
                    value = '\n'.join(textwrap.wrap(value, 60))
                table_row.append(value)

            tbl.add_row(table_row)

        result_text = ""
        if verbose:
            result_text = "{} results fetched in {}s\n{}".format(
                len(rows), round(execution_time, 2), tbl.get_string())
        return result_text

    @commands.Cog.listener("on_message_edit")
    async def on_message_edit(self, before, after):
        await self.log('EDIT', before, after.edited_at)

    @commands.Cog.listener("on_message_delete")
    async def on_message_delete(self, message):
        await self.log('DELETE', message, datetime.utcnow())

    async def log(self, msg_type, message, timestamp):
        if self.lock:
            return

        if message.author.id == self.bot.user.id:
            return

        stmt = '''
            INSERT INTO messages(timestamp, server_id, channel_id, user_id, msg_type, content, clean_content)
            VALUES(?, ?, ?, ?, ?, ?, ?)
        '''
        timestamp = timestamp or datetime.utcnow()
        server_id = message.guild.id if message.guild else -1
        channel_id = message.channel.id if message.channel else -1

        msg_content = message.content
        msg_clean_content = message.clean_content
        if message.attachments:
            extra_txt = '\nattachments: ' + str(message.attachments)
            msg_content = (msg_content + extra_txt).strip()
            msg_clean_content = (msg_clean_content + extra_txt).strip()

        if message.embeds:
            extra_txt = '\nembeds: ' + str(message.embeds)
            msg_content = (msg_content + extra_txt).strip()
            msg_clean_content = (msg_clean_content + extra_txt).strip()

        values = [
            timestamp,
            server_id,
            channel_id,
            message.author.id,
            msg_type,
            msg_content,
            msg_clean_content,
        ]

        before_time = timeit.default_timer()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(stmt, *values)
        execution_time = timeit.default_timer() - before_time
        self.insert_timing.append(execution_time)

    async def purge(self):
        before = datetime.today() - timedelta(days=(7 * 3))
        values = [before]
        log.debug('Purging old logs')
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(DELETE_BEFORE_QUERY, values)
                log.debug('Purged {}'.format(cur.rowcount))
    