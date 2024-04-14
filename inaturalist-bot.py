import os
import threading
import discord
from discord.ext import commands
from pyinaturalist import get_observations, get_taxa
from datetime import timedelta, datetime

# -------------------------------------
# Discord Bot Initialization
# -------------------------------------
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands',
    show_parameter_descriptions=False,
)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    intents=intents,
    description = "Hi! I'm a bot that grabs pictures from iNaturalist. Don't forget to add the prefix '&' in front of each command, e.g. \"&birdpic.\"\n\nAfter all \"pic\" commands, you can optionally add search terms to narrow the picture selection, e.g. \"&birdpic canada goose.\"",
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
def get_taxon_id(taxon):
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

def get_observation(taxon, query=None):
    not_ids = list(observation_cache)
    not_taxons = list(taxon_cache)
    taxon_id = get_taxon_id(taxon)
    observations = get_observations(
        taxon_id=taxon_id,
        taxon_name=query,
        min_rank='species',
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
        'wikipedia_url': observation['taxon'].get('wikipedia_url', 'N/A'),
        'preferred_common_name': observation['taxon'].get('preferred_common_name', 'N/A'),
        'photo_url': observation['photos'][0]['url'].replace('square', 'original'),
        'uri': observation['uri'],
    }
    return details

async def send_observation_message(ctx, taxon, query):
    try:
        observation = get_observation(taxon, query)
        if not observation:
            await ctx.send("No results found.")
            return
        if hide_names:
            title = f"Common Name: ||{observation['preferred_common_name']}||" if observation['preferred_common_name'] != 'N/A' else f"Scientific Name: ||{observation['scientific_name']}||"
        else:
            title = f"Common Name: {observation['preferred_common_name']}" if observation['preferred_common_name'] != 'N/A' else f"Scientific Name: {observation['scientific_name']}"
        embed = discord.Embed(title=title)
        embed.set_image(url=observation['photo_url'])
        fields = {
            "Common Name": observation['preferred_common_name'] if observation['preferred_common_name'] not in title else '',
            "Scientific Name": observation['scientific_name'] if observation['scientific_name'] not in title else '',
            "Wikipedia Link": observation['wikipedia_url'],
            "iNaturalist Link": observation['uri'],
        }
        for name, value in fields.items():
            if value:
                if hide_names and name != "iNaturalist Link":
                    embed.add_field(name=name, value=f'||{value}||')  # Add spoiler tags
                else:
                    embed.add_field(name=name, value=value)
        await ctx.send(embed=embed)
    except Exception as e:
        print("Error occurred:", e)
        await ctx.send("Sorry, I had trouble retrieving an image.")

def clear_caches():  # Every 24 hours, clear all caches
    global observation_cache, taxon_cache
    observation_cache = set()
    taxon_cache = set()
    SECONDS_IN_ONE_DAY = 86400
    threading.Timer(SECONDS_IN_ONE_DAY, clear_caches).start()

# -------------------------------------
# Discord Bot Event Handling
# -------------------------------------
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command.\nPlease run '&help' for a list of commands.")

# -------------------------------------
# Discord Bot Command Definitions
# -------------------------------------
@bot.command(brief="Bird pics")
async def birdpic(ctx, *args):
    await send_observation_message(ctx, 'Aves', ' '.join(args))

@bot.command(brief="Fungus pics")
async def mushpic(ctx, *args):
    await send_observation_message(ctx, 'Fungi', ' '.join(args))

@bot.command(brief="Amphibian pics")
async def ampic(ctx, *args):
    await send_observation_message(ctx, 'Amphibia', ' '.join(args))

@bot.command(brief="Reptile pics")
async def reppic(ctx, *args):
    await send_observation_message(ctx, 'Reptilia',  ' '.join(args))

@bot.command(brief="Mammal pics")
async def mampic(ctx, *args):
    await send_observation_message(ctx, 'Mammalia', ' '.join(args))

@bot.command(brief="Plant pics")
async def plantpic(ctx, *args):
    await send_observation_message(ctx, 'Plantae', ' '.join(args))

@bot.command(brief="Insect pics")
async def bugpic(ctx, *args):
    await send_observation_message(ctx, 'Insecta', ' '.join(args))

@bot.command(brief="Mollusk pics")
async def molpic(ctx, *args):
    await send_observation_message(ctx, 'Mollusca', ' '.join(args))

@bot.command(brief="Fish pics")
async def fishpic(ctx, *args):
    await send_observation_message(ctx, 'Actinopterygii', ' '.join(args))

@bot.command(brief="Search using a query")
async def search(ctx, *args):
    if len(args) == 0:
        await ctx.send("Please include a search query.\nUsage: &search [query]")
    else:
        await send_observation_message(ctx, None, ' '.join(args))

@bot.command(brief="Clear repetition blacklist")
async def clearcache(ctx):
    clear_caches()
    await ctx.send("The repetition cache has been cleared, and timer has been reset to 24 hours.")

@bot.command(brief="Hide names using spoiler tags")
async def namehide(ctx):
    global hide_names
    hide_names = True
    await ctx.send("Names will now be hidden using spoiler tags.")

@bot.command(brief="Show names")
async def nameshow(ctx):
    global hide_names
    hide_names = False
    await ctx.send("Names will now be displayed without spoiler tags.")

# -------------------------------------
# Main Execution
# -------------------------------------
def main():
    clear_caches()  # Start the cache clearing timer
    bot.run(os.environ['DISCORD_TOKEN'])

if __name__ == '__main__':
    main()
