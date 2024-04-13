# inaturalist-discord-bot
A simple Discord bot that returns observations from [iNaturalist](https://www.inaturalist.org/).

![inaturalist-bot-usage-example](https://github.com/B-Lei/inaturalist-discord-bot/assets/15370387/4e645e59-6d2c-445d-a92e-f8ab14c1a559)

Available as a Docker image in [Docker Hub](https://hub.docker.com/r/numactl/inaturalist-bot).

## Running the bot directly
1. Go to [Discord Developer Portal](https://discord.com/developers/applications) and create the Bot via `Applications > New Application`.
2. Go to `OAuth2` and generate a URL with the following permissions:
   * Read Messages/View Channels
   * Send Messages
   * Send Messages in Threads
3. Open the URL and add the bot to your Discord server.
4. Go to `Bot > Token` to get the Token for this bot. Copy and paste this somewhere to save it, you'll need it.
5. Clone this repository to your system - I recommend doing this in [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
6. **[RECOMMENDED]** Create a python virtual environment and activate it. This keeps python dependencies nice and contained.
    ```
    python3 -m venv inaturalist-venv
    source inaturalist-venv/bin/activate
    ```
7. Install python requirements.
    ```
    pip install -r requirements.txt
    ```
8. Run the bot, passing the Token that you saved earlier as an environment variable:
    ```
    DISCORD_TOKEN=<YOUR_TOKEN> python3 ./inaturalist-bot.py
    ```
9. You should be able to use the bot now. In your Discord server, go to one of the channels and type `&help`.

## Running the bot using Docker
1. Go to [Discord Developer Portal](https://discord.com/developers/applications) and create the Bot via `Applications > New Application`.
2. Go to `OAuth2` and generate a URL with the following permissions:
   * Read Messages/View Channels
   * Send Messages
   * Send Messages in Threads
3. Open the URL and add the bot to your Discord server.
4. Go to `Bot > Token` to get the Token for this bot. Copy and paste this somewhere to save it, you'll need it.
5. In Docker, pull the [Docker Hub image](https://hub.docker.com/r/numactl/inaturalist-bot).
    To do this via command line:
    ```
    docker pull numactl/inaturalist-bot
    ```
6. Run the Docker container, passing the Token that you saved earlier as the environment variable `DISCORD_TOKEN`.
    To do this via command line:
    ```
    docker run --rm -e DISCORD_TOKEN=<YOUR_TOKEN> numactl/inaturalist-bot:latest
    ```
7. You should be able to use the bot now. In your Discord server, go to one of the channels and type `&help`.

## Bot Usage
See `&help` text below:
```
Hi! I'm a bot that grabs pictures from iNaturalist. Don't forget to add the prefix '&' in front of each command, e.g. "&birdpic."

After all "pic" commands, you can optionally add search terms to narrow the picture selection, e.g. "&birdpic canada goose."

​Commands:
  ampic      Amphibian pics
  birdpic    Bird pics
  bugpic     Insect pics
  clearcache Clear repetition blacklist
  fishpic    Fish pics
  help       Shows this message
  mampic     Mammal pics
  molpic     Mollusk pics
  mushpic    Fungus pics
  namehide   Hide names using spoiler tags
  nameshow   Show names
  plantpic   Plant pics
  reppic     Reptile pics

Type &help command for more info on a command.
You can also type &help category for more info on a category.
```

Note that by default, when running `&COMMAND` to return a random observation, there is a "repetition blacklist" that prevents the same specific taxa from appearing more than once per 24 hours. For example, if you run `&birdpic` and it returns a Canada Goose, it won't return another Canada Goose via `&birdpic` for the next 24 hours.

This behavior can be ignored by simply specifying the search term (e.g. `&birdpic canada goose`) or clearing the blacklist using `&clearcache`.

## Libraries used:
* https://github.com/pyinat/pyinaturalist
