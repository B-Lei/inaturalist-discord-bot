# inaturalist-discord-bot
A fun Discord bot that returns random observations from [iNaturalist](https://www.inaturalist.org/).<br>
Also available as a Docker image in [Docker Hub](https://hub.docker.com/r/numactl/inaturalist-bot).

![inaturalist-bot-usage-example](https://github.com/B-Lei/inaturalist-discord-bot/assets/15370387/4e645e59-6d2c-445d-a92e-f8ab14c1a559)

## Running the Bot

### Create an application in Discord Develper Portal
1. Go to [Discord Developer Portal](https://discord.com/developers/applications) and create the Bot via `Applications > New Application`.
2. Go to the `Bot` page and click `Reset Token`, then copy and paste the token somewhere safe (you'll need this to launch the bot).
3. In the same page, enable `Message Content Intent`.
4. Go to the `OAuth2` page. Under `Scopes`, click `bot`, and then select the following `bot permissions`:
   * Read Messages/View Channels
   * Send Messages
   * Send Messages in Threads
5. Copy and open the OAuth2 URL in a browser, and select the Discord server you want to add the bot to.

### Option #1: Run the bot locally
1. Clone this repository to your system. I recommend doing this in [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
    ```
    git clone https://github.com/B-Lei/inaturalist-discord-bot.git
    ```
2. Navigate to the directory.
    ```
    cd inaturalist-discord-bot
    ```
3. (**OPTIONAL**) Create a python virtual environment and activate it.<br>
    I recommend doing this to keep your python evironment nice and contained.
    ```
    python3 -m venv inaturalist-venv
    source inaturalist-venv/bin/activate
    ```
4. Install python requirements.
    ```
    pip install -r requirements.txt
    ```
5. Run the bot, passing the Token that you saved earlier as the environment variable `DISCORD_TOKEN`:
    ```
    DISCORD_TOKEN=<YOUR_TOKEN> python3 inaturalist-bot.py
    ```
    To quit, you can use `Ctrl+C` (you might need to do it twice).

### Option #2: Run the bot using the Docker image
1. In Docker, pull the [Docker image](https://hub.docker.com/r/numactl/inaturalist-bot). To do this via command line:
    ```
    docker pull numactl/inaturalist-bot
    ```
2. Run the Docker container, passing the Token that you saved earlier as the environment variable `DISCORD_TOKEN`. To do this via command line:
    ```
    docker run --rm -e DISCORD_TOKEN=<YOUR_TOKEN> numactl/inaturalist-bot:latest
    ```
    To quit, you can use `Ctrl+C` (you might need to do it twice).

## Bot Usage
Please refer to the `&help` text below.

```
Hi! I'm a bot that grabs pictures from iNaturalist. Don't forget to add the prefix '&' in front of each command, e.g. "&birdpic".

After all "pic" commands, you can optionally add search terms to narrow the picture selection, e.g. "&birdpic canada goose".

​Commands:
  ampic    Amphibian pics
  birdpic  Bird pics
  bugpic   Insect pics
  clearmem Clear memory
  crustpic Crustacean pics
  fishpic  Fish pics
  help     Shows this message
  isopic   Isopod pics
  mampic   Mammal pics
  molpic   Mollusk pics
  mushpic  Fungus pics
  namehide Hide names using spoilers
  nameshow Show names without spoilers
  plantpic Plant pics
  reppic   Reptile pics
  search   Search using a query

Type &help command for more info on a command.
You can also type &help category for more info on a category.
```

Note that by default, when running `&COMMAND` to return a random observation, there is a "repetition blacklist" that prevents the same specific taxa from appearing more than once per 24 hours. For example, if you run `&birdpic` and it returns a Canada Goose, it won't return another Canada Goose via `&birdpic` for the next 24 hours.<br>

This behavior can be ignored by simply specifying the search term (e.g. `&birdpic canada goose`) or clearing the blacklist using `&clearcache`.

## Libraries used:
* https://github.com/pyinat/pyinaturalist
