# bot.py (standard Discord bot)
  * `members_only()`: bot-wide limitation


# client.py (Puzzleboss -> Discord local client)
  * `create`: creates channel
  * `message`: messages channel
  * `_new`: announce new puzzle channel
  * `_solve`: announces puzzle solved
  * `_attention`: announces puzzle status (e.g. critical)
  * `_round`: announces new round
  * `stats`: puzzle status stats
  * `cleanup`: delete all puzzle channels & categories


# common.py
  * `build_puzzle_embed(puzzle)`: create discord embed for specific puzzle state
  * `get_round_embed_color(round)`: discord color hash algorithm


# config.py
  * load config.json


# discord_info.py
  * A bunch of server-specific constants (move to JSON!)
  * `get_team_members(guild)`: get verified team members
  * `is_puzzboss(member)`
  * `is_puzzle_channel(channel)`
  * `get_table(member)`: get current voice channel of member (or None)
  * `get_tables(ctx)`: get all voice channel tables


# puzzboss_interface.py
## REST
  * `post`: posts to PB API
## SQL
  * `_get_db_connection()`
  * `get_puzzle_for_channel()`
  * `get_puzzles_for_channels()`
  * `get_puzzle_for_channel_fuzzy()`
  * `get_solved_round_names()`
  * `get_all_puzzles()`
  * `get_hipri_puzzles()`
  * `get_puzzles_at_table()`
  * `get_solver_from_member()`


# extensions/hunt_status.py
  * `!wrapup`: What puzzles you worked on, with links so you can go leave feedback
  * `!status`: Hunt status update
  * `!hipri`: Show hipri puzzles


# extensions/pin_messages.py
  * `handle_reacts()`: 📌 and 🧹 support for pinning/unpinning (**on_raw_reaction_add**)


# extensions/puzzboss.py
  * `!whois`: Looks up a user in Discord and Puzzleboss. (Regex supported)
  * `!newpuzzboss`: [puzzboss only] Designates a new person as Puzzleboss
  * `!newround`: [puzzboss only] Creates a new round
  * `!solvedround`: [puzzboss only] Marks a round as solved
  * `!solved`: [puzzboss only] Mark a puzzle as solved and archive its channel
    * Handle error state here (`solved_error()`)
  * `!unverified`: Lists not-yet-verified team members
  * `!verify`: Verifies a team member with their email
    * Handle error state here (`verify_error()`)
  * `!relinkdoc`: [puzztech only] Emergency relinking of a puzzle to an existing sheet


# extensions/puzzle_status.py
  * `table_report()`, which tables doing which puzzles, auto-updating message every 15 seconds
  * `!puzzle`: Display current state of a puzzle. If no channel is provided, we default to the current puzzle channel.
  * `!tables`: What is happening at each table?
  * `!whereis`: [aka !location] Find where discussion of a puzzle is happening.
  * `!note`: Update a puzzle's comments in Puzzleboss
  * `!mark`: Update a puzzle's state: needs eyes, critical, wtf, unnecessary
    * `!eyes`, `!critical`, `!wtf`, `!unnecessary` all shorthands for this
  * `handle_workingon()`: 🧩 buttons to mark user as working on puzzle (**on_raw_reaction_add**)
  * `!here`: Lets folks know this is the puzzle you're working on now.
  * `!away`: Lets folks know you're taking a break and not working on anything.
  * `!joinus`: Invite folks to work on the puzzle on your voice channel.
  * `!leaveus`: Unmark a channel as being worked anywhere.
  * Auto-leaveus, when associated voice channel becomes empty (**on_voice_state_update**)


# extensions/solving_tools.py
  * `!stuck`: Suggests some tips from the Have You Tried? list
  * `!rot`: Rotates a message through all rot N and displays the permutations
  * `!rot_specific`: Rotates a message just by rotN
    * Supports !rot0, !rot1, etc.
  * `!roll`: Rolls a dice in NdN format.
  * `!nutrimatic`: Queries nutrimatic.org
  * `!abc`: Converts letters A-Z to/from numbers 1-26
  * `!morse`: Convert to/from morse code (/ for word boundaries)
  * `!braille`: Print the braille alphabet


# extensions/toys.py
  * `!isithuntyet`: Is it hunt yet?
  * `fun_replies()` (**on_message**)
    * 50/50, thanks obama, !backsolv
  * `!hooray`: party emojis


# extensions/utils/tables.py (morse code helper)
# extensions/utils/urlhandler.py (HTTP GET, seemingly unused)


=============

# TODO:
* Move constants to JSON
* Move toys
* Move solving_tools
* Move pin_messages
* Add DB SQL connection and library
