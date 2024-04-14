import os
import threading
import discord
from discord.ext import commands
from discord.ext.commands import Context, errors
from pyinaturalist import get_observations, get_taxa

# -------------------------------------
# Discord Bot Initialization
# -------------------------------------
help_command = commands.DefaultHelpCommand(
    no_category='Commands',
    show_parameter_descriptions=False,
)
intents = discord.Intents.default()
intents.message_content = True
description = (
    "Hi! I'm a bot that grabs pictures from iNaturalist. Don't forget to add "
    "the prefix '&' in front of each command, e.g. \"&birdpic\".\n\n"
    "After all \"pic\" commands, you can optionally add search terms to "
    "narrow the picture selection, e.g. \"&birdpic canada goose\"."
)
bot = commands.Bot(
    intents=intents,
    description=description,
    command_prefix='&',
    help_command=help_command
)

# -------------------------------------
# Global Variables
# -------------------------------------
observation_cache = set()   # Cache to avoid returning the same observation
taxon_cache = set()         # Cache to avoid returning the same taxon
saved_taxa = dict()         # Cache of taxon_ids to reduce API calls
hide_names = False


# -------------------------------------
# Function Definitions
# -------------------------------------
def handle_spoiler(input: str) -> str:
    if input and hide_names:
        return f"||{input}||"
    else:
        return input


def get_taxon_id(taxon: str) -> int:
    if taxon in saved_taxa.keys():
        return saved_taxa[taxon]
    else:
        taxon_resp = get_taxa(
            page=1,
            per_page=1,
            q=taxon,
        )
        if (not taxon_resp) or (not taxon_resp['results']):
            return None
        taxon_id = taxon_resp['results'][0]['id']
        saved_taxa[taxon] = taxon_id
        return taxon_id


def get_observation(taxon: str, query: str = None) -> dict:
    not_ids = list(observation_cache)
    not_taxons = list(taxon_cache)
    taxon_id = get_taxon_id(taxon)
    observations = get_observations(
        taxon_id=taxon_id,
        taxon_name=query,
        rank='species',
        photos=True,
        identified=True,
        page=1,
        per_page=1,
        not_id=not_ids,
        without_taxon_id=not_taxons,
    )
    if (not observations) or (not observations['results']):
        return None
    observation = observations['results'][0]
    observation_cache.add(observation['id'])
    if not query:
        taxon_cache.add(observation['taxon']['id'])
    details = {
        'scientific_name': observation['taxon']['name'],
        'wikipedia_url': observation['taxon']['wikipedia_url'],
        'preferred_common_name': observation['taxon'].get(
            'preferred_common_name', None),
        'photo_url': observation['photos'][0]['url'].replace(
            'square', 'original'),
        'uri': observation['uri'],
    }
    return details


async def send_observation_message(
        ctx: Context, taxon: str, query: str) -> None:
    try:
        observation = get_observation(taxon, query)
        if not observation:
            await ctx.send("No results found.")
            return
        common_name = handle_spoiler(observation['preferred_common_name'])
        sci_name = handle_spoiler(observation['scientific_name'])
        wiki_link = handle_spoiler(observation['wikipedia_url'])
        title = f'{common_name}' if common_name else f'{sci_name}'
        embed = discord.Embed(title=title)
        embed.set_image(url=observation['photo_url'])
        fields = dict()
        if sci_name and sci_name not in title:
            fields["Scientific Name"] = sci_name
        if common_name and common_name not in title:
            fields["Common Name"] = common_name
        fields["Wikipedia Link"] = wiki_link
        fields["iNaturalist Link"] = observation['uri']
        for name, value in fields.items():
            if value:
                embed.add_field(name=name, value=value)
        await ctx.send(embed=embed)
    except Exception as e:
        print("Error occurred:", e)
        await ctx.send("Sorry, I had trouble retrieving an image.")


def clear_caches() -> None:  # Every 24 hours, clear all caches
    global observation_cache, taxon_cache
    observation_cache = set()
    taxon_cache = set()
    SECONDS_IN_ONE_DAY = 86400
    threading.Timer(SECONDS_IN_ONE_DAY, clear_caches).start()


# -------------------------------------
# Discord Bot Event Handling
# -------------------------------------
@bot.event
async def on_ready() -> None:
    print("Logged in as {0.user}".format(bot))


@bot.event
async def on_command_error(ctx: Context, error: errors) -> None:
    if isinstance(error, errors.CommandNotFound):
        await ctx.send(
            "Unknown command.\nPlease run '&help' for a list of commands.")


# -------------------------------------
# Discord Bot Command Definitions
# -------------------------------------
@bot.command(brief="Bird pics")
async def birdpic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Aves', ' '.join(args))


@bot.command(brief="Fungus pics")
async def mushpic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Fungi', ' '.join(args))


@bot.command(brief="Amphibian pics")
async def ampic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Amphibia', ' '.join(args))


@bot.command(brief="Reptile pics")
async def reppic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Reptilia',  ' '.join(args))


@bot.command(brief="Mammal pics")
async def mampic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Mammalia', ' '.join(args))


@bot.command(brief="Plant pics")
async def plantpic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Plantae', ' '.join(args))


@bot.command(brief="Insect pics")
async def bugpic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Insecta', ' '.join(args))


@bot.command(brief="Mollusk pics")
async def molpic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Mollusca', ' '.join(args))


@bot.command(brief="Fish pics")
async def fishpic(ctx: Context, *args: str) -> None:
    await send_observation_message(ctx, 'Actinopterygii', ' '.join(args))


@bot.command(brief="Search using a query")
async def search(ctx: Context, *args: str) -> None:
    if len(args) == 0:
        await ctx.send(
            "Please include a search query.\nUsage: &search [query]")
    else:
        await send_observation_message(ctx, None, ' '.join(args))


@bot.command(brief="Clear memory")
async def clearcache(ctx: Context) -> None:
    clear_caches()
    await ctx.send(
        "Memory has been cleared, and timer has been reset to 24 hours.")


@bot.command(brief="Hide names using spoiler tags")
async def namehide(ctx: Context) -> None:
    global hide_names
    hide_names = True
    await ctx.send("Names will now be hidden using spoiler tags.")


@bot.command(brief="Show names")
async def nameshow(ctx: Context) -> None:
    global hide_names
    hide_names = False
    await ctx.send("Names will now be displayed without spoiler tags.")


# -------------------------------------
# Main Execution
# -------------------------------------
def main() -> None:
    clear_caches()  # Start the cache clearing timer
    bot.run(os.environ['DISCORD_TOKEN'])


if __name__ == '__main__':
    main()
