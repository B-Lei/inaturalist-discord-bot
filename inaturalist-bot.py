import os
import threading
import discord
from discord.ext import commands
from pyinaturalist import get_observations
from datetime import timedelta, datetime

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

observation_cache = set()   # Cache to avoid returning the same observation
taxon_cache = set()         # Cache to avoid returning the same taxa
hide_names = False
taxon_whitelist = {  # Avoid blacklisting major taxa
    'Aves': 3,
    'Fungi': 47170,
    'Amphibia': 20978,
    'Reptilia': 26036,
    'Mammalia': 40151,
    'Plantae': 47126,
    'Insecta': 47158,
    'Mollusca': 47115,
    'Actinopterygii': 47178,
}

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command.\nPlease run '&help' for a list of commands.")

def clear_caches():  # Every 24 hours, clear all caches
    global observation_cache, taxon_cache
    observation_cache = set()
    taxon_cache = set()
    threading.Timer(86400, clear_caches).start()  

def get_observation(taxa, query=None):
    not_ids = list(observation_cache)
    not_taxons = list(taxon_cache)
    whitelist = list(taxon_whitelist.values())
    observations = get_observations(
        place_id='any',
        iconic_taxa=taxa,
        photos=True,
        identified=True,
        page=1,
        per_page=1,
        not_id=not_ids,
        without_taxon_id=not_taxons,
        q=query,
    )
    if not observations['results']:
        return None
    observation = observations['results'][0]
    observation_cache.add(observation['id'])
    if observation['taxon']['id'] not in whitelist and not query:
        taxon_cache.add(observation['taxon']['id'])
    details = {
        'scientific_name': observation['taxon']['name'],
        'wikipedia_url': observation['taxon'].get('wikipedia_url', 'N/A'),
        'preferred_common_name': observation['taxon'].get('preferred_common_name', 'N/A'),
        'photo_url': observation['photos'][0]['url'].replace('square', 'original'),
        'uri': observation['uri'],
    }
    return details

@bot.command(brief="Bird pics", description="")
async def birdpic(ctx, *args):
    await send_observation_message("Aves", ctx, " ".join(args))

@bot.command(brief="Fungus pics", description="")
async def mushpic(ctx, *args):
    await send_observation_message("Fungi", ctx, " ".join(args))

@bot.command(brief="Amphibian pics", description="")
async def ampic(ctx, *args):
    await send_observation_message("Amphibia", ctx, " ".join(args))

@bot.command(brief="Reptile pics", description="")
async def reppic(ctx, *args):
    await send_observation_message("Reptilia", ctx, " ".join(args))

@bot.command(brief="Mammal pics", description="")
async def mampic(ctx, *args):
    await send_observation_message("Mammalia", ctx, " ".join(args))

@bot.command(brief="Plant pics", description="")
async def plantpic(ctx, *args):
    await send_observation_message("Plantae", ctx, " ".join(args))

@bot.command(brief="Insect pics", description="")
async def bugpic(ctx, *args):
    await send_observation_message("Insecta", ctx, " ".join(args))

@bot.command(brief="Mollusk pics", description="")
async def molpic(ctx, *args):
    await send_observation_message("Mollusca", ctx, " ".join(args))

@bot.command(brief="Fish pics", description="")
async def fishpic(ctx, *args):
    await send_observation_message("Actinopterygii", ctx, " ".join(args))

@bot.command(brief="Clear repetition blacklist", description="")
async def clearcache(ctx):
    clear_caches()
    await ctx.send('The repetition cache has been cleared, and timer has been reset to 24 hours.')

@bot.command(brief="Hide names using spoiler tags", description="")
async def namehide(ctx):
    global hide_names
    hide_names = True
    await ctx.send('Names will now be hidden using spoiler tags.', description="")

@bot.command(brief="Show names", description="")
async def nameshow(ctx):
    global hide_names
    hide_names = False
    await ctx.send('Names will now be displayed without spoiler tags.')

async def send_observation_message(taxa, ctx, query):
    try:
        observation = get_observation(taxa, query)
        if not observation:
            await ctx.send('No results found.')
            return
        if hide_names:
            title = f"Common Name: ||{observation['preferred_common_name']}||" if observation['preferred_common_name'] != 'N/A' else f"Scientific Name: ||{observation['scientific_name']}||"
        else:
            title = f"Common Name: {observation['preferred_common_name']}" if observation['preferred_common_name'] != 'N/A' else f"Scientific Name: {observation['scientific_name']}"
        embed = discord.Embed(title=title)
        embed.set_image(url=observation['photo_url'])
        fields = {
            'Common Name': observation['preferred_common_name'] if observation['preferred_common_name'] not in title else '',
            'Scientific Name': observation['scientific_name'] if observation['scientific_name'] not in title else '',
            'Wikipedia Link': observation['wikipedia_url'],
            'iNaturalist Link': observation['uri'],
        }
        for name, value in fields.items():
            if value:
                if hide_names and name != 'iNaturalist Link':
                    embed.add_field(name=name, value=f"||{value}||")  # Add spoiler tags
                else:
                    embed.add_field(name=name, value=value)
        await ctx.send(embed=embed)
    except Exception as e:
        print('Error occurred:', e)
        await ctx.send("Sorry, I had trouble retrieving an image.")

clear_caches()  # Start the cache clearing timer
bot.run(os.environ["DISCORD_TOKEN"])