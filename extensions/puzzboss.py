""" Puzzboss-only commands """
import discord
from discord.ext import commands
from discord.ext.commands import guild_only, has_any_role, MemberConverter, errors
import logging
import puzzboss_interface
import re
import typing

from discord_info import *


class Puzzboss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True, usage="[sneaky]")
    async def admin(self, ctx):
        """Administrative commands, mostly puzzboss-only"""
        if ctx.invoked_subcommand:
            return
        await ctx.send("Sneaky things happen here 👀")

    @has_any_role("Role Verifier", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(name="onboard", hidden=True)
    async def onboard_alias(self, ctx, member: discord.Member):
        """Sends a onboarding message to a new member"""
        return await self.onboard(ctx, member=member)

    @has_any_role("Role Verifier", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command(name="onboard")
    async def onboard(self, ctx, member: discord.Member):
        """Sends a onboarding message to a new member"""
        await member.send(
            """
Welcome to **Setec Astronomy Total Landscaping! 🏡** Here's how to get started.

1. Make an account (https://wind-up-birds.org/account), accessing that page with username `fastasyisland` and password `bookstore`. (This account lets our team coordinate who is solving what, generate common spreadsheets, and more.)
2. Ping @Role Verifier on the Discord server with your wind-up-birds.org username, so we can link the two 🔗

**How the Discord server works:**
* We make text channels for each puzzle 🧩
* We have voice channel "tables" where people can work together 🗣
* We've got a trusty bot, puzzbot (that's me!), which helps us connect puzzle channels to the table VCs where people are solving 🤖
* puzzbot's got a lot of commands, but you don't have to learn any more than maybe 3 of them to participate 🙂

Learn more here: https://wind-up-birds.org/wiki/index.php/Hunting_in_Discord:_A_Guide

Thanks, and happy hunting! 🕵️‍♀️🧩
        """
        )

    # @has_any_role("Role Verifier", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(name="whois", aliases=["finduser"], hidden=True)
    async def whois_alias(
        self,
        ctx,
        member: typing.Optional[discord.Member],
        *,
        query: typing.Optional[str],
    ):
        """Looks up a user in Discord and Puzzleboss. (Regex supported)"""
        return await self.whois(ctx, member=member, query=query)

    @has_any_role("Role Verifier", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command(name="whois", aliases=["finduser"])
    async def whois(
        self,
        ctx,
        member: typing.Optional[discord.Member],
        *,
        query: typing.Optional[str],
    ):
        """Looks up a user in Discord and Puzzleboss. (Regex supported)"""
        response = ""
        discord_result = ""
        if member:
            discord_result = self._lookup_discord_user(member)
            response += f"{discord_result}\n\n"
            query = member.display_name

        if not query:
            await ctx.send(response)
            return

        response += "Checking Puzzleboss accounts... "
        try:
            regex = re.compile(query, re.IGNORECASE)
        except Exception as e:
            regex = re.compile(r"^$")
        query = query.lower()

        def solver_matches(name, fullname, discord_name):
            if query in name.lower():
                return True
            if regex.search(name):
                return True
            if query in fullname.lower():
                return True
            if regex.search(fullname):
                return True
            if not discord_name:
                return False
            if query in discord_name.lower():
                return True
            if regex.search(discord_name):
                return True
            return False

        connection = puzzboss_interface.SQL._get_db_connection(bot=self.bot)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    name,
                    fullname,
                    chat_name AS discord_name
                FROM solver_view
                ORDER BY name
                """,
            )
            solvers = cursor.fetchall()
        results = []
        for solver in solvers:
            if solver_matches(**solver):
                solver_tag = "`{name} ({fullname})`".format(**solver)
                if solver["discord_name"]:
                    solver_tag += " [Discord user `{}`]".format(solver["discord_name"])
                results.append(solver_tag)

        if not results:
            response += "0 results found in Puzzleboss for that query."
        elif len(results) == 1:
            response += "1 match found:\n\n{}".format(results[0])
        else:
            response += "{} matches found:\n\n{}".format(
                len(results), "\n".join(results)
            )
        try:
            await ctx.send(response)
        except:
            response = f"{discord_result}\n\nChecking Puzzleboss accounts... Error! 😔\n"
            response += (
                "Sorry, too many matches ({}) found to display in Discord. "
                + "Please narrow your query."
            ).format(len(results))
            await ctx.send(response)

    def _lookup_discord_user(self, member: discord.Member):
        member_tag = (
            "Discord user `{0.display_name} ({0.name}#{0.discriminator})`"
        ).format(member)
        if member.bot:
            return f"{member_tag} is a bot, like me :)"
        connection = puzzboss_interface.SQL._get_db_connection(bot=self.bot)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    name,
                    fullname
                FROM solver_view
                WHERE chat_uid = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (member.id,),
            )
            solver = cursor.fetchone()
            not_found = f"{member_tag} does not seem to be verified yet!"
            if not solver:
                return not_found
            return ("{0} is Puzzleboss user `{1} ({2})`").format(
                member_tag, solver["name"], solver["fullname"]
            )

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(name="newpuzzboss", aliases=["boss"], hidden=True)
    async def newpuzzboss_alias(self, ctx, newboss: discord.Member):
        """[puzzboss only] Designates a new person as Puzzleboss"""
        return await self.newpuzzboss(ctx, newboss)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command(aliases=["boss"])
    async def newpuzzboss(self, ctx, newboss: discord.Member):
        """[puzzboss only] Designates a new person as Puzzleboss"""
        puzzboss_role = ctx.guild.get_role(PUZZBOSS_ROLE)
        current_puzzbosses = puzzboss_role.members
        if newboss in current_puzzbosses:
            await ctx.send("{0.mention} is already Puzzleboss!".format(newboss))
            return
        betaboss_role = ctx.guild.get_role(BETABOSS_ROLE)
        puzztech_role = ctx.guild.get_role(PUZZTECH_ROLE)
        if betaboss_role not in newboss.roles and puzztech_role not in newboss.roles:
            await ctx.send("{0.mention} should be a Beta Boss first!".format(newboss))
            return
        for puzzboss in puzzboss_role.members:
            await puzzboss.remove_roles(puzzboss_role)
        await newboss.add_roles(puzzboss_role)
        await ctx.send(
            (
                "{0.mention} has annointed {1.mention} as the new {2.mention}! "
                + "Use {2.mention} to get their attention."
            ).format(ctx.author, newboss, puzzboss_role)
        )

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @commands.command(name="newround", aliases=["nr"], hidden=True)
    async def newround_alias(self, ctx, *, round_name: str):
        """[puzzboss only] Creates a new round"""
        return await self.newround(ctx, round_name=round_name)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @admin.command(aliases=["nr"])
    async def newround(self, ctx, *, round_name: str):
        """[puzzboss only] Creates a new round"""
        logging.info("{0.command}: Creating a new round: {1}".format(ctx, round_name))
        response = await puzzboss_interface.REST.post(
            "/rounds/", {"name": "{0}".format(round_name)}
        )
        status = response.status
        if status == 200:
            await ctx.send("Round created!")
            return
        if status == 500:
            await ctx.send("Error. This is likely because the round already exists.")
            return
        await ctx.send("Error. Something weird happened, try the PB UI directly.")

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @commands.command(name="solvedround", hidden=True)
    async def solvedround_alias(self, ctx, *, round_name: str):
        """[puzzboss only] Marks a round as solved"""
        return await self.solvedround(ctx, round_name=round_name)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @admin.command()
    async def solvedround(self, ctx, *, round_name: str):
        """[puzzboss only] Marks a round as solved"""
        logging.info(
            "{0.command}: Marking a round as solved: {1}".format(ctx, round_name)
        )
        response = await puzzboss_interface.REST.post(
            "/rounds/{}/round_uri".format(round_name),
            {"data": "https://perpendicular.institute/puzzles#solved"},
        )
        status = response.status
        if status == 200:
            await ctx.send("You solved the meta!! 🎉 🥳")
            return
        if status == 500:
            await ctx.send(
                (
                    "Error. This is likely because the round "
                    + "`{}` doesn't exist with exactly that name. "
                    + "Please try again."
                ).format(round_name)
            )
            return
        await ctx.send("Error. Something weird happened, ping @dannybd")

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(
        name="solved", aliases=["solve", "answer", "answered", "SOLVED"], hidden=True
    )
    async def solved_alias(
        self, ctx, channel: typing.Optional[discord.TextChannel], *, answer: str
    ):
        """[puzzboss only] Mark a puzzle as solved and archive its channel"""
        return await self.solved(ctx, channel=channel, answer=answer)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command(aliases=["solve", "answer", "answered", "SOLVED"])
    async def solved(
        self, ctx, channel: typing.Optional[discord.TextChannel], *, answer: str
    ):
        """[puzzboss only] Mark a puzzle as solved and archive its channel"""
        logging.info(
            "{0.command}: {0.author.name} is marking a puzzle as solved".format(ctx)
        )
        apply_to_self = channel is None
        if apply_to_self:
            channel = ctx.channel
        puzzle = puzzboss_interface.SQL.get_puzzle_for_channel(channel, bot=self.bot)
        if not puzzle:
            await ctx.send(
                "Error: Could not find a puzzle for channel {0.mention}".format(channel)
            )
            await ctx.message.delete()
            return
        response = await puzzboss_interface.REST.post(
            "/puzzles/{id}/answer".format(**puzzle), {"answer": answer.upper()}
        )
        if apply_to_self:
            await ctx.message.delete()

    @solved.error
    @solved_alias.error
    async def solved_error(self, ctx, error):
        puzzboss_role = ctx.guild.get_role(PUZZBOSS_ROLE)
        if isinstance(error, errors.MissingAnyRole):
            await ctx.send(
                (
                    "Only {0.mention} can mark a puzzle as solved. "
                    + "I've just pinged them; they should be here soon "
                    + "to confirm. (You don't need to ping them again.)"
                ).format(puzzboss_role)
            )
            return
        if isinstance(error, errors.MissingRequiredArgument):
            await ctx.send(
                "Usage: `!solved ANSWER`\n"
                + "If you're calling this from a different channel, "
                + "add the mention in there, like "
                + "`!solved #easypuzzle ANSWER`"
            )
            return
        await ctx.send(
            (
                "Error! Something went wrong, please ping @dannybd. "
                + "In the meantime {0.mention} should use the "
                + "web Puzzleboss interface to mark this as solved."
            ).format(puzzboss_role)
        )

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(name="duplicates", hidden=True)
    async def duplicates_alias(self, ctx):
        """Try to find duplicate guild members"""
        return await self.duplicates(ctx)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command()
    async def duplicates(self, ctx):
        """Try to find duplicate guild members"""
        visitor_role = ctx.guild.get_role(VISITOR_ROLE)
        members = [
            member
            for member in ctx.guild.members
            if not member.bot and visitor_role not in member.roles
        ]
        member_names = [member.name for member in members]

        dupe_members = [
            member for member in members if member_names.count(member.name) > 1
        ]
        dupe_members = sorted(dupe_members, key=lambda member: member.name)
        if not dupe_members:
            await ctx.send("Looks like all obvious duplicates have been cleared!")
            return

        member_role = ctx.guild.get_role(HUNT_MEMBER_ROLE)
        lines = [
            "Joined {0.joined_at:%Y-%m-%d %H:%M}: {0.name}#{0.discriminator} ({0.display_name}){1}".format(
                member, "  [Team Member]" if member_role in member.roles else ""
            )
            for member in dupe_members
        ]
        await ctx.send(
            f"Potential dupe members ({len(lines)}):\n"
            + "```\n"
            + "\n".join(lines)
            + "\n```"
        )

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(name="unmatched", hidden=True)
    async def unmatched_alias(self, ctx):
        """Unmatched Puzzleboss accounts w/o Discord accounts yet"""
        return await self.unmatched(ctx)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command()
    async def unmatched(self, ctx):
        """Unmatched Puzzleboss accounts w/o Discord accounts yet"""
        connection = puzzboss_interface.SQL._get_db_connection(bot=self.bot)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    name,
                    fullname
                FROM solver_view
                WHERE
                    chat_uid IS NULL
                    AND name <> 'puzzleboss'
                ORDER BY name
                """,
            )
            unmatched_users = cursor.fetchall()

        if not unmatched_users:
            await ctx.send("Looks like all PB accounts are matched, nice!")
            return

        await ctx.send(
            f"Puzzleboss accounts without matching Discord accounts ({len(unmatched_users)}):\n```"
            + "\n".join(
                [
                    user["name"] + " (" + user["fullname"] + ")"
                    for user in unmatched_users
                ]
            )
            + "\n```"
        )

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @commands.command(name="unverified", hidden=True)
    async def unverified_alias(self, ctx):
        """Lists not-yet-verified team members"""
        return await self.unverified(ctx)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command()
    async def unverified(self, ctx):
        """Lists not-yet-verified team members"""
        connection = puzzboss_interface.SQL._get_db_connection(bot=self.bot)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    DISTINCT chat_uid
                FROM solver_view
                WHERE chat_uid IS NOT NULL
                """,
            )
            verified_discord_ids = [int(row["chat_uid"]) for row in cursor.fetchall()]
        visitor_role = ctx.guild.get_role(VISITOR_ROLE)
        unverified_users = [
            member
            for member in ctx.guild.members
            if visitor_role not in member.roles
            and member.id not in verified_discord_ids
            and not member.bot
        ]
        unverified_users = sorted(unverified_users, key=lambda member: member.joined_at)
        if not unverified_users:
            await ctx.send(
                "Looks like all team members are verified, nice!\n\n"
                + "(If this is unexpected, try adding the Team Member "
                + "role to someone first.)"
            )
            return
        member_role = ctx.guild.get_role(HUNT_MEMBER_ROLE)
        unverified_other = [
            "Joined {0.joined_at:%Y-%m-%d %H:%M}: {0.name}#{0.discriminator} ({0.display_name})".format(
                member
            )
            for member in unverified_users
            if member_role not in member.roles
        ]
        if unverified_other:
            unverified_other = (
                "Folks needing verification ({0}):\n```\n{1}\n```\n".format(
                    len(unverified_other), "\n".join(unverified_other)
                )
            )
        else:
            unverified_other = ""

        unverified_members = [
            "Joined {0.joined_at:%Y-%m-%d %H:%M}: {0.name}#{0.discriminator} ({0.display_name})".format(
                member
            )
            for member in unverified_users
            if member_role in member.roles
        ]
        if unverified_members:
            unverified_members = "Folks needing verification, but already have the Member role ({0}):\n```\n{1}\n```".format(
                len(unverified_members), "\n".join(unverified_members)
            )
        else:
            unverified_members = ""

        await ctx.send(unverified_other + unverified_members)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @commands.command(name="verify", hidden=True)
    async def verify_alias(
        self, ctx, member: typing.Union[discord.Member, str], *, username: str
    ):
        """Verifies a team member with their email
        Usage: !verify @member username[@wind-up-birds.org]
        """
        return await self.verify(ctx, member, username=username)

    @has_any_role("Beta Boss", "Puzzleboss", "Puzztech")
    @guild_only()
    @admin.command()
    async def verify(
        self, ctx, member: typing.Union[discord.Member, str], *, username: str
    ):
        """Verifies a team member with their email
        Usage: !verify @member username[@wind-up-birds.org]
        """
        verifier_role = ctx.guild.get_role(794318951235715113)
        if verifier_role not in ctx.author.roles:
            await ctx.send(
                (
                    "Sorry, only folks with the @{0.name} "
                    + "role can use this command."
                ).format(verifier_role)
            )
            return
        if not isinstance(member, discord.Member) and " " in username:
            # Let's perform some surgery, and stitch the actual member name
            # back together.
            parts = username.split()
            username = parts[-1]
            member = " ".join([member] + parts[:-1])
            try:
                converter = MemberConverter()
                member = await converter.convert(ctx, member)
            except:
                pass

        if not isinstance(member, discord.Member):
            await ctx.send(
                (
                    "Sorry, the Discord name has to be _exact_, "
                    + "otherwise I'll fail. `{}` isn't recognizable to me "
                    + "as a known Discord name.\n\n"
                    + "TIP: If their display name has spaces or symbols in it, "
                    + 'wrap the name in quotes: `!verify "foo bar" FooBar`'
                ).format(member)
            )
            return
        username = username.replace("@wind-up-birds.org", "")
        logging.info(
            "{0.command}: Marking user {1.display_name} as PB user {2}".format(
                ctx, member, username
            )
        )
        connection = puzzboss_interface.SQL._get_db_connection(bot=self.bot)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    fullname
                FROM solver_view
                WHERE name LIKE %s
                LIMIT 1
                """,
                (username,),
            )
            solver = cursor.fetchone()
            if not solver:
                await ctx.send(
                    (
                        "Error: Couldn't find a {0}@wind-up-birds.org, "
                        + "please try again."
                    ).format(username)
                )
                return
            logging.info(
                "{0.command}: Found solver {1}".format(ctx, solver["fullname"])
            )
            print(solver["id"])
            cursor.execute(
                """
                UPDATE solver_view
                SET chat_uid = %s, chat_name = %s
                WHERE id = %s
                """,
                (
                    str(member.id),
                    "{0.name}#{0.discriminator}".format(member),
                    solver["id"],
                ),
            )
            logging.info("{0.command}: Committing row".format(ctx))
            connection.commit()
            logging.info("{0.command}: Committed row successfully!".format(ctx))
        member_role = ctx.guild.get_role(HUNT_MEMBER_ROLE)
        if member_role not in member.roles:
            logging.info("{0.command}: Adding member role!".format(ctx))
            await member.add_roles(member_role)
        await ctx.send(
            "**{0.display_name}** is now verified as **{1}**!".format(
                member, solver["name"]
            )
        )

    @verify.error
    @verify_alias.error
    async def verify_error(self, ctx, error):
        if isinstance(error, errors.MissingRequiredArgument):
            await ctx.send(
                "Usage: `!verify [Discord display name] [Puzzleboss username]`\n"
                + "If the person's display name has spaces or weird symbols "
                + "in it, try wrapping it in quotes, like\n"
                + '`!verify "Fancy Name" FancyPerson`'
            )
            return
        await ctx.send(
            "Error! Something went wrong, please ping @dannybd. "
            + "In the meantime it should be safe to just add this person "
            + "to the server by giving them the Team Member role."
        )
        raise error

    @has_any_role("Puzztech")
    @guild_only()
    @commands.command(name="relinkdoc", aliases=["linkdoc"], hidden=True)
    async def relinkdoc_alias(
        self,
        ctx,
        channel: typing.Optional[discord.TextChannel],
        *,
        sheet_hash: str,
    ):
        """[puzztech only] Emergency relinking of a puzzle to an existing sheet"""
        return await self.relinkdoc(ctx, channel=channel, sheet_hash=sheet_hash)

    @has_any_role("Puzztech")
    @guild_only()
    @admin.command(name="relinkdoc", aliases=["linkdoc"])
    async def relinkdoc(
        self,
        ctx,
        channel: typing.Optional[discord.TextChannel],
        *,
        sheet_hash: str,
    ):
        """[puzztech only] Emergency relinking of a puzzle to an existing sheet"""
        channel = channel or ctx.channel
        puzzle = puzzboss_interface.SQL.get_puzzle_for_channel(channel, bot=self.bot)
        await ctx.send(
            "Relinking sheet `{}` to `{name}`...".format(sheet_hash, **puzzle)
        )
        response = await puzzboss_interface.REST.post(
            "/puzzles/{id}/drive_id".format(**puzzle),
            {"data": sheet_hash},
        )
        if response.status != 200:
            await ctx.send("Error setting drive_id!")
            return

        response = await puzzboss_interface.REST.post(
            "/puzzles/{id}/drive_uri".format(**puzzle),
            {
                "data": f"https://docs.google.com/spreadsheets/d/{sheet_hash}/edit?usp=drivesdk"
            },
        )
        if response.status != 200:
            await ctx.send("Error setting drive_uri!")
            return

        response = await puzzboss_interface.REST.post(
            "/puzzles/{id}/drive_link".format(**puzzle),
            {
                "data": f'<a href="https://docs.google.com/spreadsheets/d/{sheet_hash}/edit?usp=drivesdk">DOC</a>'
            },
        )
        if response.status != 200:
            await ctx.send("Error setting drive_link!")
            return

        await ctx.send("Done. Please run: `!puz {name}`".format(**puzzle))


def setup(bot):
    cog = Puzzboss(bot)
    bot.add_cog(cog)
