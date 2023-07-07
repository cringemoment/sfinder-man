import discord
from copy import deepcopy
from discord.ext import commands
import os
from os import path, listdir, makedirs, environ, rmdir, getcwd, remove
from bs4 import BeautifulSoup
from keep_alive import keep_alive
from json import loads
from PIL import Image
import traceback
import io
import math
from py_fumen_util import disassemble, assemble, join, split as fumensplit
from py_fumen_py import decode as pydecode, encode as pyencode, Field, Page
import requests
from datetime import datetime
import asyncio
import json
import re

print("sdsdadasd")

keep_alive()
bot_token = environ["bot_token"]


class sfindercommandtooslow(Exception):
  pass

class commandKilled(Exception):
  pass

running_commands = []


async def system(ctx, command):
  command = ''.join([
    i if not i in "&;" else "" for i in command.splitlines()[0]
  ]).replace("then", "")
  print(command)

  process = await asyncio.create_subprocess_shell(command)
  process_info = {'process': process, 'name': command, 'user': ctx.author.id}
  running_commands.append(
    process_info
  )  # Add the process information to the list of running commands
  try:
    await asyncio.wait_for(process.communicate(), timeout=1000)
  except asyncio.TimeoutError:
    process.kill()
    raise sfindercommandtooslow(
      "System call has lasted longer than 3 minutes.")
  finally:
    try:
      running_commands.remove(
        process_info
      )  # Remove the process information from the list of running commands
    except ValueError:
      raise commandKilled("Someone killed your command already!")

  return process.returncode


intents = discord.Intents.default()
intents.message_content = True
intents.presences = True

prefix = '>'

bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)


@bot.command()
async def help(ctx, command=None):
  if command is None:
    embed = discord.Embed(
      title="Sfinder Bot Help Guide",
      description="This is cringemoment's hacked together sfinder bot.",
      color=0x7289da)
    embed.add_field(
      name="__Sfinder Commands__",
      value=
      "`>sfinder`\n`>getmyfolder`\n`>getoutputfile`\n`>getallsolutions`\n`>uploadfile`\n`>deletefile`",
      inline=True)
    embed.add_field(
      name="__Additional Research__",
      value= "`>chance`\n`>minimals`\n`>special_minimals`\n`>score_minimals`\n`>score`\n`>congruent`\n`>cover`\n`>saves`\n`>parity`\n`>spincover`\n`>setupcover`",
      inline=True)
    embed.add_field(
      name="__Additional tools__",
      value=
      "`>bestsetup`\n`>bestsave`\n`>cat_finder`\n`>dpcfinder`\n`>catimage`\n`>imageofacat`\n`>tofumen`\n`>calibrate`",
      inline=True)
    embed.add_field(name="__Bot tools__",
                    value="`>currentcommands`\n`>killmyprocesses`",
                    inline=True)
    embed.add_field(
      name="",
      value="For additional help with command format, do `>help command_help`",
      inline=True)
  else:
    if command == "sfinder":
      description = "This is the exact same thing as normal sfinder, but instead of using java -jar sfinder.jar just use `>sfinder`. For additional help with sfinder commands, check https://hsterts.github.io/h-docs/sfinder/."
      format = "Command format: `>sfinder`"
      example = "Example: `>sfinder path -t v115@9gC8EeE8DeF8CeG8DeC8JeAgH -p I,*p4`"
    elif command == "getmyfolder":
      description = "This bot creates a folder for you, to save all the sfinder output into. You can look inside your folder here."
      format = "Command format: `>getmyfolder`"
      example = ""
    elif command == "getoutputfile":
      description = "Grab a file from your folder. Just put the folder name, and the bot sends the file to you."
      format = "Command format: `>getoutputfile {file}`"
      example = "Example: `>getoutputfile path_unique.html`"
    elif command == "getallsolutions":
      description = "At the request of swng, provide a file in your folder, and it'll grab the first link, which is usually the all solutions link."
      format = "Command format: `>getallsolutions {file}`"
      example = "Example: `>getallsolutions path_unique.html`"
    elif command == "tofumen":
      description = "Attach a screenshot of a tetris board. Ideally, take a screenshot of the entire 10-wide board, and try to minimize the amount of free space there is. You can optionally add the game the screenshot was taken in as a parameter. The list of accepted games are in `>help calibrate`"
      format = "Command format: `>tofumen {game}`"
      example = "Example: `>tofumen tetrio`"
    elif command == "chance":
      description = "Gets you the chance of solving a setup."
      format = "Command format: `>chance {fumen} {queue} {clear=4}`"
      example = "Example: `>chance v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4`"
    elif command == "minimals":
      description = "Gets you the minimals, or the minimum amount of solutions needed to get a setup to maximum solve rate, in a tinyurl fumen. The saves parameter allows you to get minimal sets for any pieces saved. Put the parameters side by side, seperated with `||`. (For the people who know, it's Marfung's sfinder-saves.py). If you wanted save O, put `O`. If you want save S or save Z, put `S||Z`."
      format = "Command format: `>minimals {fumen} {queue} {clear=4} {saves = all}`"
      example = "Example: `>minimals v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 O`"
    elif command == "score":
      description = "Gets you the average score for a setup. Very clunky, and you have to specify everything in order.\n The intial_b2b tells the bot if you start with b2b (useful for dpc), the b2b_bonus tells the bot how many extra points b2b is effectively worth (if you're going into dpc, set the bonus to 600 as the tsd will be worth 600 more points with b2b). The initial combo gives you "
      format = "Command format: `>score {fumen} {queue} {clear=4} {initial_b2b=false} {b2b_bonus=0} {initial_combo=0}`"
      example = "Example: `>score v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 true 600 0`"
    elif command == "special_minimals":
      description = "Gets you a minimal set for getting a certain type of spin. The default type, tss, gets you the minimum set to maximize tss+ chance."
      format = "Command format: `>special_minimals {fumen} {queue} {clear=4} {minimal_type=tss}`"
      example = "Example: `>special_minimals v115@9gC8EeE8DeF8CeG8DeC8JeAgH I,*p4 4 tetris`"
    elif command == "bestsetup":
      description = "Slightly finnicky. Provide the right amount of pieces, and it will tell you the best setup. This is not great, you have to specify the right amount of pieces, and it does not have most dupe setups.\nData sourced from konbini."
      format = "Command format: `>bestsetup {pc} {queue}`"
      example = "Example: `>bestsetup 7 LSO`"
    elif command == "bestsave":
      description = "Gets the solutions, and sends roughly the best one. The save evaluation function is not perfect and so take it with a grain of salt."
      format = "Command format: `>bestsave {fumen} {queue}`"
      example = "Example: `>bestsave v115@9gC8EeE8DeF8CeG8DeC8JeAgH ITSJL`"
    elif command == "cat_finder":
      description = "Same code as QwQtris. Takes in a queue and finds the best solve. The format is essentially the same as score as the code is the same"
      format = "Command format: `>cat_finder {fumen} {queue} {clear = 4} {initial_b2b = false} {initial_combo = 0} {b2b_bonus = 0}`"
      example = "Example: `>cat_finder v115@9gC8EeE8DeF8CeG8DeC8JeAgH IJTLI 4 true 0 600`"
    elif command == "command_help":
      description = "Sfinder bot provides the commands through help with a consistent format. The first command is specified with a > as that is the command prefix. All parameters are in {curly brackets}. If there's an equal sign, there's a default value and you do not have to specify a value. Otherwise, you do have to provide a value or else it will error. Provide each value in order, without any other text. If you are not sure what a parameter is just set it as the default."
      format = "Command format: `>fakecommand {value1} {value2 = you dont have to specify this}`"
      example = "Example: `>fakecommand 2`"
    elif command == "dpcfinder":
      description = "Similar to bestsetup, but doesn't take a pc number. Takes a queue and finds the optimal dpc, sorted by score. Great when used in conjunction with `cat_finder`."
      format = "Command format: `>dpcfinder {queue}`"
      example = "Example: `>dpcfinder IOSZJLT`"
    elif command == "cover":
      description = "Takes in multiple fumens and a queue, and gets the cover of the setups. Essentially the same as sfinder's cover command"
      format = "Command format: `>cover {fumen} {fumen} {fumen} {queue}`"
      example = "Example: `>cover http://fumen.zui.jp/?v115@BhilFeAtglR4Beg0RpBtR4Ceg0RpAtzhAeh0JeAgWG?AKN8LCvXBAA http://fumen.zui.jp/?v115@BhR4AtFeR4BtBeg0RpilAtCeg0RpglzhAeh0JeAgWG?AqHMMCvCBAA *p7`"
    elif command == "congruent":
      description = "Takes in a fumen and a queue, and finds all the way to build a setup. Optional parameter to treat garbage blocks as pieces. Useful for followups."
      format = "Command format: `>congruent {fumen} {queue} {garbageCongruents = false}`"
      example = "Example: `>congruent v115@9gllDemlCenlBemlMeAgH *p7 false`"
    elif command == "uploadfile":
      description = "Send this command with a file attached. It will then be uploaded to your folder. Note that your folder has a maximum size of 1mb, and you cannot upload a file larger than 500mb."
      format = "Command format: `>uploadfile`"
      example = ""
    elif command == "deletefile":
      description = "Takes in a file name, and deletes that file from your folder. If no file is provided, it will wipe your entire folder."
      format = "Command format: `>deletefile {filename}`"
      example = "Example: `>deletefile path_minimal.html`"
    elif command == "catimage":
      description = "Takes in a fumen and sends a gif of the fumen, using the Jstris cat skin. Pretty much the same thing as any other fumen bot, but worse, because you don't get comments. You can also set the delay between images, in milliseconds."
      format = "Command format: `>catimage {fumen} {delay = 800}`"
      example = "Example: `>catimage v115@vhGT5I/kB5oBqqBdtB2uBUsB 20`"
    elif command == "saves":
      description = "Takes in a fumen and a queue, and gets you the save % chance, using sfinder-saves.py. If saves is left empty, it uses the -a tag, and gets all the saves. Refer to `>help minimals` for saves."
      format = "Command format: `>saves {fumen} {queue} {clear = 4} {saves = all}`"
      example = "Example: `>saves v115@LhB8GeB8DeA8BeD8AeC8JeAgH T,*p7 4 O`"
    elif command == "imageofacat":
      description = ":3"
      format = ":3"
      example = ":3"
    elif command == "score_minimals":
      description = "Exact same parameters as score, except for a new one, called fuzzyness. As some solutions score marginally more than other solves, both of them have to be included. Fuzzyness gives you a little margin, at the cost of the minimals scoring less than the average score. Weights are extra score for better saves. Provide the numbers in order, no spaces, comma seperated, in the order of OSZITLJ. This helps for creating more curated score sets. If you think saving O is worth 300 points over save L, set it like this. As well, you can use DPC as a shorthand, and the weights will be set to take in dpc scoring for consideration"
      format = "Command format: `>score_minimals {fumen} {queue} {clear=4} {initial_b2b=false} {b2b_bonus=0} {initial_combo=0} {fuzzy_margin=200} {weights = None}`"
      example = "Example: `>score_minimals v115@Ehi0HeQ4g0GewwR4FeywQ4JeAgH L,*p7 4 false 600 0 200 10000,0,0,0,0,0,0`"
    elif command == "parity":
      description = "Takes in a fumen, outputs parity and some extra information. Takes in a left bound for the board, useful for LST."
      format = "Command format: `>parity {fumen} {leftBound=0}`"
      example = "Example: `>parity v115@GhC8FeE8DeF8EeB8JeAgH 5`"
    elif command == "calibrate":
      description = "Calibrate `>tofumen` to a game. Current supported games are:\n `tetrio` (default skin)\n`jstris` (flat color skin)\n`jstrisblock` (the bi-color skin)\n`fourdiscord` (four.lol too)\n`fourlight` (output pics)\n`fourblack` (idk but im keeping it)\n`catimage` (>:3))\n`fumen` (fumen, fumen for mobile, harddrop, etc)"
      format = "Command format: `>calibrate {game}`"
      example = "Example: `>calibrate tetrio`"
    elif command == "currentcommands":
      description = "Sends every command that the bot is currently running."
      format = "Command format: `>currentcommands`"
      example = ""
    elif command == "killmyprocesses":
      description = "Kills every command that the command user is running"
      format = "Command format: `>killmyprocesses`"
      example = ""
    elif command == "spincover":
      description = "It's like sfinder-recursive, but! Provided a queue, a fumen, and a type for cover to run on, it'll get the cover data, and then the cover to path minimals. Shares the same limitations as spin. (does not support kicks!!!)"
      format = "Command format: `>spincover {fumen} {queue} {tspin-type=TSS}`"
      example = "Example: `>spincover v115@WhB8BeB8DeB8AeB8JeAgH *p7 TSD`"
    elif command == "setupcover":
      description = "It's like sfinder-recursive, but better! Provided queues for setup and cover along with a fumen, it'll get the cover data, and then the cover to path minimals. You can optionally include --mode for cover, --exclude for cover, the fill color and the margin color."
      format = "Command format: `>setupcover {fumen} {setup_queue} {cover_queue} {minimal_type=normal} {exclude=none} {fill=I} {margin=O}`"
      example = "Example: `>setupcover v115@zgWpBeXpBeVpxhBe2hCe3hAexhJeAgH [IOSZJL]p6, *p7 normal strict-holes I O`"
    else:
      await ctx.send(f"I don't think {command} is a command :3")
      return

    embed = discord.Embed(title=f"Sfinder Bot Help: {command.capitalize()}",
                          description=description,
                          color=0x7289da)
    embed.add_field(name="Command format", value=format, inline=False)
    if (example != ""):
      embed.add_field(name="Example", value=example, inline=False)
  embed.add_field(
    name="",
    value=
    "Check out https://github.com/cringemoment/ezsfinder ! It's like this bot but better!",
    inline=True)
  await ctx.reply(embed=embed)


@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game(name="sfinder.jar"))
  print(f'Logged in as {bot.user.name}')


def get_size(start_path='.'):
  total_size = 0
  for dirpath, dirnames, filenames in os.walk(start_path):
    for f in filenames:
      fp = os.path.join(dirpath, f)
      # skip if it is symbolic link
      if not os.path.islink(fp):
        total_size += os.path.getsize(fp)

  return total_size


@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.reply(
      f"The sfinder command has a cooldown in servers, to prevent spam. There are {round(error.retry_after, 2)} seconds left. If you would like to spam the command do it in dms"
    )
  elif isinstance(error, commands.errors.BadArgument):
    await ctx.reply(
      f"One of the parameters is wrong. A common error is trying to do `clear=4`, when it should be `4`. The bot is trying to convert something to something else and it's breaking. Specifically, {error}"
    )
  elif isinstance(error, commands.errors.CommandNotFound):
    await ctx.reply(f"I don't think {ctx.invoked_with} is a command :3")
  elif hasattr(error, "original") and isinstance(error.original,
                                                 sfindercommandtooslow):
    await ctx.reply(
      "The command has lasted more than 3 minutes. To prevent hogging the cpu, the bot has turned your command off. If you really need to run it and can't run it on a computer, message cringemoment and ill make an exception."
    )
  else:
    if (hasattr(error, "original")):
      await ctx.reply(
        f"Uh oh, an error just occured. pls go and tell cringemoment. The error is: {error.original}"
      )
    else:
      await ctx.reply(
        f"Uh oh, an error just occured. pls go and tell cringemoment. The error is: {type(error)}, {error}"
      )


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if message.author.id == 308779860346798090:
    return
  if message.content.startswith(">") and not message.content[1] == " ":
    folder_path = str(message.author.id)
    if not path.exists(folder_path):
      makedirs(folder_path)
    else:
      # folder_size = get_size(folder_path)
      if False:  # folder_size > 1 * 1024 * 1024:  # 1 MB in bytes
        for file_name in os.listdir(folder_path):
          file_path = os.path.join(folder_path, file_name)
          if os.path.isfile(file_path):
            os.remove(file_path)

    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the command with timestamp in commandlog.txt
    with open("commandlog.txt", "a") as log_file:
      log_file.write(
        f"{current_time} - {message.author.name} ran command: {message.content}\n"
      )

    await message.add_reaction("✅")

  await bot.process_commands(message)


@bot.command()
async def hello(ctx):
  await ctx.reply('Hello!')


@bot.command()
async def shutdown(ctx):
  if ctx.author.id == 696811705619054633 or ctx.author.id == 717451031897833512:
    await ctx.reply('Shutting down...')
    await bot.close()
  else:
    await ctx.reply("You don't have permission to shut down the bot.")


@bot.command()
async def purge_folders(ctx):
  user_id = ctx.author.id

  if user_id == 696811705619054633:
    folder_path = getcwd()
    for folder_name in listdir(folder_path):
      folder_to_delete = path.join(folder_path, folder_name)
      if folder_name.isdigit():
        for file_name in listdir(folder_to_delete):
          file_path = path.join(folder_to_delete, file_name)
          remove(file_path)
        rmdir(folder_to_delete)

    await ctx.reply("Folders purged.")
  else:
    await ctx.reply("You don't have permission to use this command.")


@bot.command()
@commands.cooldown(1, 15,
                   commands.BucketType.guild)  # 15-second cooldown per user
async def sfinder(ctx, command_type=None, *, parameters=None):
  if command_type is None:
    await ctx.reply("Sfinder command is missing, please pick one.")
    bot.get_command("sfinder").reset_cooldown(ctx)
    return
  elif parameters is None:
    await ctx.reply("Parameters are missing, please set some.")
  elif "-o" in parameters:
    bot.get_command("sfinder").reset_cooldown(ctx)
    return
    await ctx.reply(
      "I'm sorry, but the -o flag messes with the bot. Please don't use it.")
    bot.get_command("sfinder").reset_cooldown(ctx)
    return
  else:
    command_type = command_type.replace('>', "")
    parameters = parameters.replace('>', "")
    output_filename = f"{ctx.author.id}_sfinderoutput.txt"
    error_filename = f"{ctx.author.id}_sfindererror.txt"

    if command_type == "percent":
      lastcommand = await system(
        ctx,
        f"java -jar sfinder.jar {command_type} {parameters} > {output_filename} 2> {error_filename}"
      )
    elif command_type == "path":
      lastcommand = await system(
        ctx,
        f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/{command_type} > {output_filename} 2> {error_filename}"
      )
    elif command_type == "setup":
      lastcommand = await system(
        ctx,
        f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/setup.html > {output_filename} 2> {error_filename}"
      )
    elif command_type == "cover":
      lastcommand = await system(
        ctx,
        f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/cover.csv > {output_filename} 2> {error_filename}"
      )
    else:
      lastcommand = await system(
        ctx,
        f"java -jar sfinder.jar {command_type} {parameters} -o __userdata/{ctx.author.id}/ > {output_filename} 2> {error_filename}"
      )

    if (lastcommand != 0):
      await ctx.reply(file=discord.File(error_filename))
      bot.get_command("sfinder").reset_cooldown(ctx)
      return

    # Read the output file
    if (ctx.guild == None):
      sfinder_output = open(output_filename, "r").read()

      segment_length = 1900
      sfinder_output_segments = [
        sfinder_output[i:i + segment_length]
        for i in range(0, len(sfinder_output), segment_length)
      ]

      # Send each segment using ctx.reply
      for segment in sfinder_output_segments:
        await ctx.reply("```" + segment + "```")
    else:
      await ctx.reply(file=discord.File(output_filename))

    # Delete the output file
    remove(output_filename)
    remove(error_filename)

    # Clean up after cooldown period
    if ctx.guild is None:
      bot.get_command("sfinder").reset_cooldown(ctx)


@bot.command()
async def getoutputfile(ctx, *, filename):
  filename = filename.replace("/", "")
  file_path = f"__userdata/{ctx.author.id}/{filename}"

  if path.isfile(file_path):
    with open(file_path, "rb") as file:
      discord_file = discord.File(file)
      await ctx.reply(file=discord_file)
  else:
    await ctx.reply("File not found.")


filesizelimit = 200000


@bot.command()
async def uploadfile(ctx):
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No file attached.")
    return

  file = ctx.message.attachments[0]
  if file.size > filesizelimit:  # 500 KB in bytes
    await ctx.reply(f"File size exceeds the limit of {filesizelimit[:-3]} KB.")
    return

  folder_name = str(ctx.author.id)
  file_path = f"__userdata/{folder_name}/{file.filename}"
  # Download the file to the specified folder
  await file.save(file_path)
  await ctx.reply(f"File '{file.filename}' has been saved successfully.")


@bot.command()
async def deletefile(ctx, name=None):
  folder_name = "__userdata/" + str(ctx.author.id)
  folder_path = folder_name + "/"

  if name is None:
    # Delete all files in the user's folder
    for file_name in os.listdir(folder_path):
      file_path = os.path.join(folder_path, file_name)
      if os.path.isfile(file_path):
        os.remove(file_path)
    await ctx.reply("All files deleted")
    return

  # Ensure that the provided file name is safe
  safe_name = os.path.basename(name)
  if not safe_name or "/" in safe_name or "\\" in safe_name:
    await ctx.reply("Invalid file name.")
    return

  file_path = os.path.join(folder_path, safe_name)

  # Check if the file exists in the user's folder
  if os.path.exists(file_path):
    # Delete the file
    os.remove(file_path)
    await ctx.reply(f"File '{safe_name}' has been deleted successfully.")
  else:
    await ctx.reply(f"File '{safe_name}' does not exist in your folder.")


@bot.command()
async def getmyfolder(ctx):
  user_id = str(ctx.author.id)
  folder_path = f"__userdata/{user_id}"

  if not path.exists(folder_path):
    makedirs(folder_path)
  files = listdir(folder_path)
  if len(files) > 0:
    file_names = "\n".join(files)
    await ctx.reply(f"Files in your folder:\n```\n{file_names}\n```")
  else:
    await ctx.reply("Your folder is currently empty.")


def make_tiny(url):
  import contextlib

  try:
    from urllib.parse import urlencode

  except ImportError:
    from urllib import urlencode
  from urllib.request import urlopen

  request_url = ('http://tinyurl.com/api-create.php?' +
                 urlencode({'url': url}))
  with contextlib.closing(urlopen(request_url)) as response:
    return response.read().decode('utf-8 ')


@bot.command()
async def getallsolutions(ctx, *, file_name):
  file_name = file_name.strip(";/")
  await ctx.reply(
    "Note: This does not work with spin.html, if someone actually used it.")

  file_path = f"__userdata/{ctx.author.id}/{file_name}"

  if not path.isfile(file_path):
    await ctx.reply("File not found.")
  else:
    with open(file_path, "r") as file:
      file_contents = file.read()
      soup = BeautifulSoup(file_contents, 'html.parser')
      link = soup.find('a')
      if link:
        href = link.get('href')
        href = make_tiny(href)
        await ctx.reply(f"Found link: {href}")
      else:
        await ctx.reply("No link found.")


def evaluatesave(save):
  piecessaveindex = {"S": 0, "Z": 0, "O": 3, "J": 1, "L": 1, "I": 4, "T": 6}

  score = 0
  for piece in save:
    score += piecessaveindex[piece]

  if (save.count("J") + save.count("L") % 2 == 0):
    score += 8

  return score


@bot.command(aliases=["best_save"])
async def bestsave(ctx, fumen, allpieces, clear=4):
  allpieces = allpieces.upper()
  await system(
    ctx,
    f"java -jar sfinder.jar path -t {fumen} -p {allpieces} --clear {clear} --split yes --kicks kicks/jstris180.properties -d 180 > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  with open('output/path_unique.html', 'r', encoding="utf-8") as f:
    html = f.read()

  soup = BeautifulSoup(html, 'html.parser')

  solutions = []

  for link in soup.find_all('a')[1:]:
    href = link.get('href')
    if href.startswith('http://fumen.zui.jp/?'):
      pieces = ''.join([i[0] for i in link.get_text().split(' ')])
      solutions.append([href, pieces])

  saves = []

  if (solutions != []):
    for solution in solutions:
      solutionfumen = solution[0]
      piecesused = solution[1]

      solutionallpieces = [char for char in allpieces.replace(",", "")]
      solutionpiecesused = [char for char in piecesused]
      pieceuseddontremove = deepcopy(piecesused)

      for pieceused in pieceuseddontremove:
        solutionpiecesused.remove(pieceused)
        try:
          solutionallpieces.remove(pieceused)
        except ValueError:
          await ctx.reply("Not enough pieces placed")
          return False

      leftover = solutionallpieces
      saves.append([solutionfumen, leftover, evaluatesave(leftover)])

    saves.sort(key=lambda x: int(x[2]) * -1)
    bestsave = ''.join(saves[0][1])
    await ctx.reply(f"Best save: **{bestsave}**\n{unglue(saves[0][0])}",
                    file=toimage(unglue(saves[0][0])))

  else:
    await ctx.reply("There's no solution")


@bot.command()
async def catimage(ctx, fumen=None, delay=800):
  if fumen is None:
    await ctx.reply("Please provide a fumen")
    return

  fumens = []
  gluedfumens = fumensplit([fumen])
  for i in gluedfumens:
    fumens.append(unglue(i))

  allfumenimages = []

  highestheight = 0

  for fumen in fumens:
    board = decode(fumen).splitlines()
    height = len(board)
    if (height > highestheight):
      highestheight = height

  for fumen in fumens:
    fumenimage = Image.new("RGB", (10 * 32, highestheight * 32), "black")
    board = decode(fumen).splitlines()
    if (len(board) > 0):
      board = [[i for i in j] for j in board]
      heightoffset = highestheight - len(board)

      for rownumber, row in enumerate(board):
        for columnnumber, piece in enumerate(row):
          if (not piece == "_"):
            fumenimage.paste(catimages[piece],
                             (columnnumber * 32,
                              (rownumber + heightoffset) * 32))

    allfumenimages.append(fumenimage)

  # Create a byte stream to save the GIF
  gif_byte_stream = io.BytesIO()

  # Save the sequence of fumen images as a GIF
  allfumenimages[0].save(gif_byte_stream,
                         format='GIF',
                         save_all=True,
                         append_images=allfumenimages[1:],
                         optimize=False,
                         duration=delay,
                         loop=0)

  # Reset the byte stream's position to the beginning
  gif_byte_stream.seek(0)

  # Send the GIF as a file attachment in Discord
  await ctx.reply(file=discord.File(gif_byte_stream, filename='catimage.gif'))


allpcdata = {}
for i in range(1, 8):
  allpcdata[i] = {}
  allpcdata[i]["data"] = loads(open(f"konbini/cover{i}.json").read())
  allpcdata[i]["setups"] = open(f"konbini/setups{i}.txt").read().splitlines()
  allpcdata[i]["percent"] = open(f"konbini/percent{i}.txt").read().splitlines()

dpcsetups = open("konbini/dpc.txt").read().splitlines()
dpccover = loads(open("konbini/dpccover.json").read())


def unglue(glued):
  if (type(glued) == type([])):
    return assemble(glued)
  return assemble([glued])[0]


def glue(unglued):
  if (type(unglued) == type([])):
    return disassemble(unglued)
  return disassemble([unglued])[0]


@bot.command(aliases=["best_setup"])
async def bestsetup(ctx, pcnumber=None, allpieces=None):
  if (pcnumber == None or allpieces == None):
    await ctx.reply("You have to specify a pc number and a queue")
    return
  elif (pcnumber not in [str(i) for i in range(1, 8)]):
    await ctx.reply("PC number must be between 1 and 7")
    return
  pcnumber = int(pcnumber)

  allpieces = allpieces.upper()
  allsetups = []

  for piecelength in range(3, len(allpieces) + 2):
    testsetup = allpieces[:piecelength]
    if (testsetup in allpcdata[pcnumber]["data"]):
      workingsetups = allpcdata[pcnumber]["data"][testsetup]
      [allsetups.append(i) for i in workingsetups]

  if (len(allsetups) == 0):
    await ctx.reply(
      "No setups found in database. If you're on third pc, make sure to put the extra piece first. Otherwise, either there is just no setup, or you didn't put enough pieces."
    )
    return

  allsetups.sort()
  await ctx.reply(allpcdata[pcnumber]["percent"][allsetups[0]])
  await ctx.reply(
    file=toimage(unglue(allpcdata[pcnumber]["setups"][allsetups[0]])))
  await ctx.reply(unglue(allpcdata[pcnumber]["setups"][allsetups[0]]))


@bot.command(aliases=["dpc_finder"])
async def dpcfinder(ctx, queue=None):
  if (queue == None):
    await ctx.reply("You have to specify a queue")
    return
  elif (len(queue) < 7):
    await ctx.reply("You have to provide at least 7 pieces.")
    return

  queue = queue.upper()

  if (len(queue) == 7):
    tetrominoes = "IOSZJLT"
    for char in tetrominoes:
      if (not char in queue[1:]):
        queue += char
        break

  pcsetups = dpcsetups
  pcsetupcovers = dpccover

  if (queue in pcsetupcovers):
    await ctx.reply(file=toimage(unglue(pcsetups[pcsetupcovers[queue][0]])))
    await ctx.reply(unglue(pcsetups[pcsetupcovers[queue][0]]))
  else:
    await ctx.reply("No setup found in database")


def hold_reorders(queue):
  if len(queue) <= 1:
    return set(queue)  # base case

  result = set()

  a = hold_reorders(queue[1:])  # use first piece, work on the 2nd-rest
  for part in a:
    result.add(queue[0] + part)

  b = hold_reorders(queue[0] +
                    queue[2:])  # use second piece, work on 1st + 3rd-rest
  for part in b:
    result.add(queue[1] + part)

  return list(result)


@bot.command(aliases=["catfinder"])
async def cat_finder(ctx,
                     fumen=None,
                     allpieces=None,
                     highestvalue=4,
                     fedb2b="false",
                     combo=0,
                     b2bendbonus=0):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
  elif (allpieces == None):
    await ctx.reply("Please provide a queue")

  allpieces = allpieces.upper()

  piecesfile = open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w")
  accum = ""
  for holdqueue in hold_reorders(allpieces):
    accum += holdqueue + "\n"
  piecesfile.write(accum)
  piecesfile.close()

  outputpathfile = f"__userdata/{ctx.author.id}/path.csv"

  await system(
    ctx,
    f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {highestvalue} --hold avoid --split yes -f csv -k pattern -o {outputpathfile} > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  currentpath = open(outputpathfile).read()
  if (not "1" in currentpath):
    await ctx.reply("No solution, sorry")
  else:
    await system(
      ctx,
      f"node best_score.js initialB2B={fedb2b} initialCombo={combo} queue={allpieces} b2bEndBonus={b2bendbonus} fileName={outputpathfile} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
    bestsolve = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
    for i in bestsolve:
      await ctx.reply(i)

    if (len(bestsolve) > 1):
      extras = bestsolve[1]
      await ctx.send(f"The optimal solve is {extras}")
    else:
      await ctx.send("There is no extra scoring")

    solutionfumen = unglue(bestsolve[0])
    await ctx.send(file=toimage(solutionfumen))
    await ctx.send(solutionfumen)


@bot.command(aliases=["percent"])
async def chance(ctx, fumen=None, queue=None, clear=4):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
  elif (queue == None):
    await ctx.reply("Please provide a queue")
  else:
    pathtest = await system(
      ctx,
      f"java -jar sfinder.jar percent --tetfu {fumen} --patterns {queue} --clear {clear} -K kicks/jstris180.properties -d 180 > __userdata/{ctx.author.id}/ezsfinder.txt 2> error.txt"
    )
    if (pathtest != 0):
      await ctx.reply(
        "Something went wrong with the sfinder command. Please check for any typoes you might have had."
      )
      await ctx.reply(file=discord.File("error.txt"))
      bot.get_command("sfinder").reset_cooldown(ctx)
      return
    output = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read()
    solverate = (output[output.find("success"):output.find("success") +
                        20].split()[2])
    await ctx.reply(f"The chance of solving the setup is {solverate}")
    remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")


@bot.command()
async def minimals(ctx, fumen=None, queue=None, clear=4, saves=None):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  if (saves == None or saves.upper() == "ALL"):
    pathtest = await system(
      ctx,
      f"java -jar sfinder.jar path -f csv -k pattern --tetfu {fumen} --patterns {queue} --clear {clear} -K kicks/jstris180.properties -d 180   > __userdata/{ctx.author.id}/ezsfinder.txt 2> error.txt"
    )
    if (pathtest != 0):
      await ctx.reply(
        "Something went wrong with the sfinder command. Please check for any typoes you might have had."
      )
      await ctx.reply(file=discord.File("error.txt"))
      bot.get_command("sfinder").reset_cooldown(ctx)
      return

    await system(
      ctx,
      f"npx sfinder-minimal output/path.csv > __userdata/{ctx.author.id}/ezsfinder.txt")
    await system(ctx,
                 f"python true_minimal.py > __userdata/{ctx.author.id}/ezsfinder.txt")
    minimallink = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()[1]
    await ctx.reply(f"The normal minimals are {minimallink}")
  else:
    pathtest = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -p {queue} -f csv -k pattern -K kicks/jstris180.properties -d 180 --clear {clear} --output __userdata/{ctx.author.id}/path.csv > __userdata/{ctx.author.id}/ezsfinder.txt 2> error.txt"
    )
    if (pathtest != 0):
      await ctx.reply(
        "Something went wrong with the sfinder command. Please check for any typoes you might have had."
      )
      await ctx.reply(file=discord.File("error.txt"))
      bot.get_command("sfinder").reset_cooldown(ctx)
      return
    filtertest = await system(
      ctx,
      f'python sfinder-saves.py filter -w "{saves}" -p {queue} -f __userdata/{ctx.author.id}/path.csv > __userdata/{ctx.author.id}/ezsfinder.txt 2> __userdata/{ctx.author.id}/error.txt'
    )
    if (filtertest != 0):
      await ctx.reply(
        "Something went wrong running sfinder-saves.py. It does not take queue input as liberally as sfinder, so make sure to put commas."
      )
      await ctx.reply(file=discord.file(f"__userdata/{ctx.author.id}/error.txt"))
    pieces = saves.replace("||", "")
    output = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
    await ctx.reply(f"The save {pieces} minimals are {output[-1]}")
  remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")


def resize_image_with_median(image, new_width, new_height):
  # Resize the image to the desired width and height
  resized_image = image.resize((new_width, new_height))

  # Get the size of the resized image
  resized_width, resized_height = resized_image.size

  # Calculate the grid size based on the number of rows and columns
  grid_width = image.width // resized_width
  grid_height = image.height // resized_height

  # Create a new image to store the median RGB values
  median_image = Image.new("RGB", (resized_width, resized_height))

  # Iterate through each pixel in the resized image
  for y in range(resized_height):
    for x in range(resized_width):
      # Calculate the grid boundaries
      left = x * grid_width
      upper = y * grid_height
      right = (x + 1) * grid_width
      lower = (y + 1) * grid_height

      # Get the grid square from the original image
      grid_square = image.crop((left, upper, right, lower))

      # Get the RGB values for each pixel in the grid square
      grid_pixels = list(grid_square.getdata())

      # Calculate the median RGB values
      median_rgb = tuple(
        int(sum(channel) / len(channel)) for channel in zip(*grid_pixels))

      # Assign the median RGB values to the corresponding pixel in the median image
      median_image.putpixel((x, y), median_rgb)

  return median_image


def encode(text):
  text = '\n'.join(text[i:i + 10] for i in range(0, len(text), 10))
  tetrisfield = Field(field=text, garbage="__________")
  page = Page(field=tetrisfield)
  return (pyencode([page]))


def decode(fumen):
  decode_pages = pydecode(fumen)
  return '\n'.join(decode_pages[0].field.string().splitlines()[:-1])


catimages = {}
for i in "IOSZJLTX_":
  catimages[i] = Image.open(f"cat images/cat{i}.png")


def toimage(fumen):
  board = decode(fumen)
  board = [[i for i in j] for j in board.splitlines()]

  fumenimage = Image.new("RGB", (len(board[0]) * 32, len(board) * 32), "black")

  for rownumber, row in enumerate(board):
    for columnnumber, piece in enumerate(row):
      if (not piece == "_"):
        fumenimage.paste(catimages[piece], (columnnumber * 32, rownumber * 32))
  image_buffer = io.BytesIO()
  fumenimage.save(image_buffer, format="PNG")
  image_buffer.seek(0)
  discord_file = discord.File(image_buffer, filename="image.png")

  return discord_file


def create_mode_image(original_image, new_width, new_height):
  # Open the original image

  # Calculate the cell size based on the new resolution
  cell_width = original_image.width // new_width
  cell_height = original_image.height // new_height

  # Create a new image for storing the cell mode RGB values
  new_image = Image.new("RGB", (new_width, new_height))

  # Iterate over each cell in the new image
  for row in range(new_height):
    for col in range(new_width):
      # Define the boundaries of the current cell in the original image
      left = col * cell_width
      upper = row * cell_height
      right = left + cell_width
      lower = upper + cell_height

      # Crop the original image to the current cell
      cell_image = original_image.crop((left, upper, right, lower))

      # Calculate the mode RGB value of the cell
      mode_rgb = cell_image.convert("RGB").getcolors(cell_width * cell_height)
      mode_rgb = max(mode_rgb, key=lambda x: x[0])[1]

      # Set the mode RGB value in the new image
      new_image.putpixel((col, row), mode_rgb)

  return new_image


bot.command()


async def textfumen(ctx, *, textfumen=None):
  if textFumen == None:
    ctx.reply("Attach a text fumen")
  textfumen = textfumen.upper()
  textfumen = textfumen.replace("\n", "")
  textfumen = ''.join([i if i in "IOSZJLTX_" else "" for i in textfumen])
  if (len(textfumen) % 10 != 0):
    await ctx.reply(
      f"Board length must be multiple of 10. The current length is {len(textfumen)}"
    )
  await ctx.reply(encode(textfumen))
  return


def get_closest_piece(rgb_value, preset, pieceSet="normal"):
  closest_piece = None
  closest_distance = float('inf')

  pieces = preset[pieceSet]

  # Iterate through each Tetris piece and its RGB value
  for piece, piece_rgb in pieces.items():
    # Calculate the Euclidean distance between the RGB values
    distance = math.sqrt(
      sum((c1 - c2)**2 for c1, c2 in zip(rgb_value, piece_rgb)))

    # Update the closest piece if the distance is smaller
    # If the piece is void, make the margin slightly smaller
    if piece == '_' or piece == 'X':
      if distance * 1.1 < closest_distance:
        closest_distance = distance * 1.1
        closest_piece = piece
      continue

    if distance < closest_distance:
      closest_distance = distance
      closest_piece = piece

  return closest_piece


@bot.command()
async def tofumen(ctx, preset=None):
  if preset != None:
    folderpath = f"rgbShorthands/{preset.lower()}.json"
    if not path.exists(folderpath):
      await ctx.reply(
        "Preset does not exist (check help for the full list or ping epic to add)\n"
      )
      return
    open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
         'w').write(open(folderpath).read())

  if not path.exists(f"__userdata/{ctx.author.id}/toFumenRGB.json"):
    folderpath = f"rgbShorthands/fumen.json"
    open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
         'w').write(open(folderpath).read())

  # Check if an image is attached
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No image found.")
    return

  # Get the image attachment
  attachment = ctx.message.attachments[0]

  try:
    image_bytes = await attachment.read()
    image_io = io.BytesIO(image_bytes)

    image = Image.open(image_io)
    width, height = image.size
    new_width = 10
    new_height = round(new_width * height / width)

    # Resize the image
    # image = create_mode_image(image, new_width, new_height)
    image = image.resize((new_width, new_height), Image.NEAREST)
    # Convert the image to a Tetris field
    pieces = json.loads(
      open(f"__userdata/{ctx.author.id}/toFumenRGB.json").read())

    field = ''
    for y in range(new_height):
      line = ""
      for x in range(new_width):
        pixel = image.getpixel((x, y))
        closest_piece = get_closest_piece(pixel, pieces)
        line += closest_piece

      if not '_' in line:
        line = ""
        for x in range(new_width):
          pixel = image.getpixel((x, y))
          closest_piece = get_closest_piece(pixel, pieces, "cleared")
          line += closest_piece

      field += line + '\n'

    # Send the field back to the user
    await ctx.reply("```\n" + field + "```" + "\n" +
                    encode(field.replace("\n", "")))

  except Exception:
    await ctx.reply("An error occurred while processing the image.")
    traceback.print_exc()


def remove_duplicates(file_name):
  unique_lines = set()

  # Read file and collect unique lines
  with open(file_name, 'r') as file:
    for line in file:
      line = line.strip()
      if line not in unique_lines:
        unique_lines.add(line)

  # Rewrite unique lines to the file
  with open(file_name, 'w') as file:
    file.write('\n'.join(unique_lines))


def generate_permutations(bag, permutation_length):
  elements = list(bag)

  if elements and elements[0] == '^':
    # Negate the list of elements
    elements = [p for p in "IOSZJLT" if p not in elements[1:]]
  else:
    elements = elements[
      1:-1] if elements[0] == '[' and elements[-1] == ']' else elements

  permutations = [[]]
  result = set()

  # Generate all permutations of the given length
  for i in range(permutation_length):
    permutations = [
      p + [e] for p in permutations for e in elements if e not in p
    ]

  # Convert each permutation back to a string and add to the result set
  for p in permutations:
    result.add(''.join(p))

  # Convert the result set to a list and return it
  return list(result)


def combine_lists(lists):
  if not lists:
    return []

  result = []

  def combine(index, current):
    if index == len(lists):
      result.append(''.join(current))
      return
    for i in range(len(lists[index])):
      combine(index + 1, current + [lists[index][i]])

  combine(0, [])
  return result


def countpieces(string):
  count = 0
  if ("^" in string):
    string = [p for p in "IOSZJLT" if p not in string[string.index("^"):]]
  for char in string:
    if (char in "IOSZJLT"):
      count += 1
  return count


def queuesplit(string):
  bagmode = False
  result = []
  for char in string:
    char = char.upper() if char in "ioszjlt" else char
    if (not bagmode and char in "IOSZJLT"):
      result.append(char)
    if (char == "[" or char == "*"):
      temp = ""
      bagmode = True
    if (bagmode == True):
      temp += char
    if (char == "!" or char in "0123456789"):
      result.append(temp)
      bagmode = False

  result = ','.join(result)
  return result


def sfinder_all_permutations(input_str):
  input_str = queuesplit(input_str)
  inputs = input_str.split(',')

  # Generate all permutations for each input
  permutations = []
  for input_str in inputs:
    input_str = input_str.replace("^", "[^]").replace(
      "!", "p" + str(countpieces(input_str)))
    if (not "p" in input_str):
      input_str += "p1"
    bag_with_brackets, permutation_length = input_str.split('p')
    if not permutation_length:
      permutation_length = 1

    bag = bag_with_brackets.replace('*', '[IOSZJLT]').replace('[', '').replace(
      ']', '').upper()

    permutations.append(generate_permutations(bag, int(permutation_length)))

  return combine_lists(permutations)


def hold_reorders(queue):
  if len(queue) <= 1:
    return set(queue)  # base case

  result = set()

  a = hold_reorders(queue[1:])  # use first piece, work on the 2nd-rest
  for part in a:
    result.add(queue[0] + part)

  b = hold_reorders(queue[0] +
                    queue[2:])  # use second piece, work on 1st + 3rd-rest
  for part in b:
    result.add(queue[1] + part)

  return list(result)


def holdsfinderqueues(queue):
  properhold = set()
  for i in sfinder_all_permutations(queue):
    [properhold.add(j) for j in hold_reorders(i)]

  return (list(properhold))


@bot.command()
async def score(ctx,
                fumen=None,
                queue=None,
                clear=4,
                initial_b2b="false",
                b2b_bonus=0,
                initial_combo=0,
                field_file=None):
  if (fumen == None or queue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  with open(f"__userdata/{ctx.author.id}/queuefeed.txt", "w") as queuefeed:
    accum = ""
    for i in holdsfinderqueues(queue):
      accum += i + "\n"
    queuefeed.write(accum)

  if (not "FILE:" in fumen):
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar path -t {fumen} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/path.csv -K kicks/jstris180.properties -d 180 > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )
  else:
    file = fumen.split("FILE:")[1]
    scorecommand = await system(
      ctx,
      f"java -jar sfinder.jar cover -fp {file} -pp __userdata/{ctx.author.id}/queuefeed.txt --clear {clear} --hold avoid -split yes -f csv -k pattern -o output/cover.csv -K kicks/jstris180.properties -d 180 > __userdata/{ctx.author.id}/ezsfinder.txt 2> scoreerror.txt"
    )

  if (scorecommand != 0):
    await ctx.reply(
      "An error has occured with the sfinder command and the parameters you sent."
    )
    await ctx.reply(file=discord.File("scoreerror.txt"))
    return

  if (not "FILE:" in fumen):
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  else:
    await system(
      ctx,
      f"node avg_score_ezsfinderversion.js queue={queue} initialB2B={initial_b2b} initialCombo={initial_combo} b2bEndBonus={b2b_bonus} fileName=output/cover.csv fileType=cover > __userdata/{ctx.author.id}/ezsfinder.txt"
    )
  score = open(f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()
  printingscores = True

  allspecial = "```\n"

  for v, i in enumerate(score):
    if (i == "{"):
      printingscores = False
    if (printingscores):
      specialcount = int(i.split(": ")[1])
      specialtype = i.split(": ")[0]
      allqueues = int(score[-1])
      allspecial += (
        f"There are {specialcount}/{allqueues} ({round(specialcount/allqueues * 100, 3)}%) queues where {specialtype} is the optimal solve \n"
      )
    if ("average_covered_score" in i):
      if (allspecial != "```\n"):
        allspecial += "\n```"
        await ctx.reply(allspecial)
      else:
        await ctx.reply("There is no extra scoring")

      score_percentage = int(score[v + 1].split(": ")[1][:-1]) / int(
        score[-1]) * 100
      withpcscore = round(float(i.split(": ")[1][:-1]), 2)
      average_score = round(
        withpcscore / int(score[-1]) * int(score[v + 1].split(": ")[1][:-1]),
        2)

      await ctx.send(
        f"**On average, when the setup has a perfect clear, you would score {withpcscore} points.**"
      )
      await ctx.send(
        f"**Factoring in pc chance ({score_percentage}%), the average score is {average_score}**"
      )

      remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
      remove(f"__userdata/{ctx.author.id}/queuefeed.txt")
      break


@bot.command()
async def special_minimals(ctx,
                           fumen=None,
                           queue=None,
                           clear=4,
                           minimal_type="tss"):
  if (fumen == None or queue == None):
    await ctx.reply("You have to specify a fumen and a queue")

  sfindercommand = await system(
    ctx,
    f"java -jar sfinder.jar path -t {fumen} -p {queue} --clear {clear} -K kicks/jstris180.properties --split yes -d 180 -o __userdata/{ctx.author.id}/path > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  if (sfindercommand != 0):
    await ctx.reply(
      "Something went wrong with the sfinder command. Please check for any typoes you might have had."
    )
    remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
    return

  with open(f'__userdata/{ctx.author.id}/path_unique.html', encoding="utf-8") as f:
    html = f.read()

  soup = BeautifulSoup(html, 'html.parser')
  links = []
  for link in soup.findAll('a'):
    links.append(link.get('href'))
    allfumen = links[1:]

  with open(f"__userdata/{ctx.author.id}/coverfield.txt", "w") as file:
    for i in allfumen:
      file.write(i)
      file.write("\n")

  remove_duplicates(f"__userdata/{ctx.author.id}/coverfield.txt")

  covercommand = await system(
    ctx,
    f"java -jar sfinder.jar cover -p {queue} -M {minimal_type} -K kicks/jstris180.properties -d 180 -fp __userdata/{ctx.author.id}/coverfield.txt -o __userdata/{ctx.author.id}/tempcover.csv> __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  if (covercommand != 0):
    await ctx.reply(
      "Something went wrong with the cover command. Check that the minimal type is a valid one"
    )
    remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
    return

  await system(
    ctx,
    f"python cover-to-path.py --csv-path __userdata/{ctx.author.id}/tempcover.csv --unglued-fumen-script-path unglueFumen.js > __userdata/{ctx.author.id}/ezsfinder.txt"
  )

  await system(
    ctx,
    f"npx sfinder-minimal __userdata/{ctx.author.id}/tempcover_to_path.csv > __userdata/{ctx.author.id}/ezsfinder.txt"
  )
  await system(ctx, f"python true_minimal.py > __userdata/{ctx.author.id}/ezsfinder.txt")
  trueminimallink = open(
    f"__userdata/{ctx.author.id}/ezsfinder.txt").read().splitlines()[-1]
  await ctx.reply(f"Your {minimal_type} minimals are {trueminimallink}")

  #remove(f"__userdata/{ctx.author.id}/coverfield.txt")
  #remove(f"__userdata/{ctx.author.id}/ezsfinder.txt")
  #remove(f"__userdata/{ctx.author.id}/tempcover.csv")
  #remove(f"__userdata/{ctx.author.id}/tempcover_to_path.csv")


@bot.command()
async def congruent(ctx, fumen=None, queue=None, blueGarbage=""):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return

  if blueGarbage.upper() == "TRUE":
    await system(
      ctx, f"node convertalltoblue.js {fumen} > __userdata/{ctx.author.id}/tempblued.txt")
  else:
    await system(
      ctx, f"node converttoblue.js {fumen} > __userdata/{ctx.author.id}/tempblued.txt")
  blued = open(f"__userdata/{ctx.author.id}/tempblued.txt").read().replace("\n", "")
  blued = encode(blued)

  await system(
    ctx,
    f"java -jar sfinder.jar setup --fill I --tetfu {blued} --patterns {queue} -d 180 -K kicks/tetrio180.properties -fo csv --output __userdata/{ctx.author.id}/tempsetup.csv > setupoutput.txt 2> __userdata/{ctx.author.id}/error.txt"
  )

  allfumens = [
    i.split(",")[0]
    for i in open(f"__userdata/{ctx.author.id}/tempsetup.csv").read().splitlines()[1:]
  ]

  if(allfumens == []):
    await ctx.reply("Looks like there were no congruents. If all the blocks are garbage, make sure to enable the garbage parameter.")
    return

  allfumens = join(allfumens)[0]
  await ctx.reply(make_tiny("https://fumen.zui.jp/?" + allfumens))
  remove(f"__userdata/{ctx.author.id}/tempblued.txt")
  remove(f"__userdata/{ctx.author.id}/tempsetup.csv")


@bot.command()
async def cover(ctx, *, allstuff=None):
  if (allstuff == None):
    await ctx.reply("Please provide fumens and queues")
    return

  allstuff = allstuff.split()
  fumens = []
  queue = ""
  for arg in allstuff:
    if ("115" in arg):
      fumens.append(arg)
    else:
      queue = arg

  fumens = glue(unglue(fumensplit(fumens)))

  fumens = ' '.join(fumens)

  covercommand = await system(
    ctx,
    f'java -jar sfinder.jar cover -t "{fumens}" -p {queue} -K kicks/jstris180.properties -d 180 --output __userdata/{ctx.author.id}/tempcover.csv > __userdata/{ctx.author.id}/tempcover.txt'
  )

  if (covercommand != 0):
    await ctx.reply(
      "Something went wrong with the cover command. Make sure your parameters are right."
    )
    return

  allqueues = 0
  setupcover = 0
  failqueues = open(f"__userdata/{ctx.author.id}/coverfailqueues.txt", "w")

  coverfile = open(f"__userdata/{ctx.author.id}/tempcover.csv").read().splitlines()[1:]
  for cover in coverfile:
    allqueues += 1
    coverage = cover.split(",")[1:]
    coverqueue = cover.split(",")[0]
    coverage = any([True if i == "O" else False for i in coverage])
    if (coverage):
      setupcover += 1
    else:
      failqueues.write(coverqueue)
      failqueues.write("\n")
  failqueues.close()

  await ctx.reply(f"The coverage is {setupcover}/{allqueues}")
  if (setupcover != allqueues):
    await ctx.send("Fail queues")
    await ctx.send(file=discord.File(f"__userdata/{ctx.author.id}/coverfailqueues.txt"))


@bot.command(aliases=[":3"])
async def imageofacat(ctx):
  response = requests.get("https://api.thecatapi.com/v1/images/search")
  data = response.json()
  image_url = data[0]['url']
  embed = discord.Embed(title="", color=0xFFA500)
  embed.set_image(url=image_url)

  await ctx.reply(embed=embed)


@bot.command()
async def saves(ctx, fumen=None, queue=None, clear=4, *, saves=None):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
  elif (queue == None):
    await ctx.reply("Please provide a queue")

  sfindercommand = await system(
    ctx,
    f"java -jar sfinder.jar path -f csv -k pattern -t {fumen} -p {queue} --clear {clear} -K kicks/jstris180.properties -d 180 --output __userdata/{ctx.author.id}/temppath.csv > ezsfinder.txt 2> __userdata/{ctx.author.id}/error.txt"
  )
  if (sfindercommand != 0):
    await ctx.reply(
      "Something went wrong with the sfinder command. Please check for any typoes you might have had.",
      file=discord.File(f"__userdata/{ctx.author.id}/error.txt"))
    return
  if (saves == None):
    filtertest = await system(
      ctx,
      f"python sfinder-saves.py percent -p {queue} -f __userdata/{ctx.author.id}/temppath.csv -a > __userdata/{ctx.author.id}/tempsaves.txt 2> __userdata/{ctx.author.id}/error.txt"
    )
  else:
    saves = saves.upper()
    filtertest = await system(
      ctx,
      f'python sfinder-saves.py percent -p {queue} -f __userdata/{ctx.author.id}/temppath.csv -w "{saves}" > __userdata/{ctx.author.id}/tempsaves.txt 2> __userdata/{ctx.author.id}/error.txt'
    )

  if (filtertest != 0):
    await ctx.reply(
      "Something went wrong running sfinder-saves.py. It does not take queue input as liberally as sfinder, so make sure to put commas.",
      file=discord.File(f"__userdata/{ctx.author.id}/error.txt"))
    return

  output = open(f"__userdata/{ctx.author.id}/tempsaves.txt").read()
  await ctx.reply(output)


import csv


def convert_csv(input_file, output_file):
  csv_file = open(input_file, 'r')
  csv_data = csv.reader(csv_file)
  rows = list(csv_data)[1:]

  queues_set = set()
  solutions_map = {}
  for row in rows:
    queue = row[0]
    queues_set.add(queue)
    if row[4] == '':
      continue
    solutions = row[4].split(';')
    for solution in solutions:
      if solution not in solutions_map:
        solutions_map[solution] = set([queue])
      else:
        solutions_map[solution].add(queue)

  solutions_list = list(solutions_map.keys())
  data = []
  for queue in queues_set:
    temp = [
      'O'
      if solutions_map[solution] and queue in solutions_map[solution] else 'X'
      for solution in solutions_list
    ]
    temp.insert(0, queue)
    data.append(temp)

  content = "sequence," + ','.join(solutions_list)

  for row in data:
    content += "\n" + ','.join(row)

  with open(output_file, 'w') as file:
    file.write(content)


@bot.command()
async def score_minimals(ctx,
                         testfumen=None,
                         testqueue=None,
                         clear=4,
                         initial_b2b="false",
                         b2bendbonus=0,
                         initial_combo=0,
                         fuzzymargin=200,
                         weights=None):
  if (testfumen == None or testqueue == None):
    await ctx.reply("Please specify a fumen and a queue")
    return

  pathfile = f"__userdata/{ctx.author.id}/path.csv"
  holdoutputfile = f"__userdata/{ctx.author.id}/holdyescover.csv"
  noholdoutputfile = f"__userdata/{ctx.author.id}/holdavoidcover.csv"
  outputfile = f"__userdata/{ctx.author.id}/scorecover.csv"
  outputpathfile = f"__userdata/{ctx.author.id}/scorepath.csv"
  solutionsfeedfile = f"__userdata/{ctx.author.id}/solutionsfeed.txt"
  queuefeedfile = f"__userdata/{ctx.author.id}/holdreorders.txt"
  trueminimallink = f"__userdata/{ctx.author.id}/minimallink.txt"

  await system(
    ctx,
    f"java -jar sfinder.jar path -t {testfumen} -p {testqueue} -K kicks/jstris180.properties -d 180 --split yes --clear {clear} --output {pathfile} -f csv -k pattern > ezsfinder.txt"
  )

  convert_csv(pathfile, holdoutputfile)
  solutions = open(holdoutputfile).read().splitlines()[0].split(",")[1:]

  holddata = holdsfinderqueues(testqueue)

  with open(queuefeedfile, "w") as file:
    for i in holddata:
      file.write(i)
      file.write("\n")

  with open(solutionsfeedfile, "w") as file:
    for i in solutions:
      file.write(i)
      file.write("\n")

  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/jstris180.properties -d 180 -pp {queuefeedfile} --hold avoid -o {noholdoutputfile}> ezsfinder.txt"
  )
  await system(
    ctx,
    f"java -jar sfinder.jar cover -fp {solutionsfeedfile} -K kicks/jstris180.properties -d 180 -p {testqueue} -o {holdoutputfile} > ezsfinder.txt"
  )

  if (weights == None):
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile}"
    )
  elif (weights.upper() == "DPC"):
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights=4726.378,4495.700,4454.710,4454.710,4255.940,4255.940,4135.546"
    )
  else:
    scoretest = await system(
      ctx,
      f"node scoremins.js doholdcover={holdoutputfile} noholdcover={noholdoutputfile} initialCombo={initial_combo} initialB2b={initial_b2b} b2bEndBonus={b2bendbonus} queue={testqueue} fuzzy={fuzzymargin} output={outputfile} save_weights={weights}"
    )

  if (scoretest != 0):
    await ctx.reply(
      "Something went wrong with the score command. Make sure all your parameters (especially the weights) are correct."
    )
    return

  await system(
    ctx,
    f'python cover-to-path.py --csv-path "{outputfile}" --unglued-fumen-script-path unglueFumen.js --output-file-path "{outputpathfile}"'
  )
  await system(ctx, f"npx sfinder-minimal {outputpathfile}")
  await system(ctx, f"python true_minimal.py > {trueminimallink}")
  link = open(trueminimallink).read().splitlines()[-1]
  await ctx.reply(f"Your score minimals is {link}")


def evenchecker(num):
  return "EOvdedn"[num % 2::2]


def pcLine(total, highestPCLine):
  if total % 2 == 1:
    return "N/A"
  elif total % 4 == 0:
    return f"Line {math.ceil(highestPCLine / 2) * 2}"
  else:
    return f"Line {math.ceil((highestPCLine - 1) / 2) * 2 + 1}"


@bot.command()
async def parity(ctx, fumen=None, leftBound=1, rightBound=10):
  if (fumen == None):
    await ctx.reply("Please specify a fumen and a queue")
    return
  if (leftBound < 1 or leftBound >= rightBound or rightBound > 10):
    await ctx.reply("Bad bounds")
    return

  checkerboard = rowparity = columnar = total = 0
  highestPCLine = -1

  fumen = decode(fumen).splitlines()
  for i in range(len(fumen)):
    fumen[i] = fumen[i][leftBound - 1:rightBound]

  for rowindex, row in enumerate(fumen):
    for columnindex, block in enumerate(row,
                                        leftBound + 1):  # +1 for 1-indexed
      if (block != "_"):
        if (columnindex % 2 == 0):
          columnar += 1
        if (rowindex % 2 == 0):
          rowparity += 1
        if ((columnindex + rowindex) % 2 == 0):
          checkerboard += 1
        total += 1
        highestPCLine = rowindex + 1

  await ctx.reply(
    f"``` Total minos: {total}\n Next Available PC: {pcLine(total, highestPCLine)}\n Horizontal parity: {evenchecker(rowparity)}\n Vertical parity: {evenchecker(columnar)}\n Checkerboard parity: {(evenchecker(checkerboard))}```"
  )


#sorry man im testing something


@bot.command()
async def calibrate(ctx, preset=None):
  # Apply preset
  if preset != None:
    folderpath = f"rgbShorthands/{preset.lower()}.json"
    if not path.exists(folderpath):
      await ctx.reply(
        "Game preset does not exist (check help for the full list or ping epic to add)\n"
        + folderpath)
      return

    open(f"__userdata/{ctx.author.id}/toFumenRGB.json",
         'w').write(open(folderpath).read())
    await ctx.reply("Success!")
    return

  # Check if an image is attached
  if len(ctx.message.attachments) == 0:
    await ctx.reply("No image found.")
    return

  # Get the image attachment
  attachment = ctx.message.attachments[0]

  try:
    image_bytes = await attachment.read()
    image_io = io.BytesIO(image_bytes)

    image = Image.open(image_io)
    width, height = image.size
    new_width = 9
    new_height = 2

    # Resize the image
    image = image.resize((new_width, new_height), Image.NEAREST)

    # Add rgb values into dictionary

    pieces = dict()
    order = "SZLJTIOX_"
    for x in range(len(order)):
      pixel = image.getpixel((x, 1))
      pieces[order[x]] = pixel

    clearedPieces = dict()
    order = "SZLJTIOX"
    for x in range(len(order)):
      pixel = image.getpixel((x, 0))
      clearedPieces[order[x]] = pixel

    # Send the values back to the user
    message = "Pieces:\n```\n"
    for key in pieces.keys():
      message += f"{key}: {pieces.get(key)}\n"

    message += "\n```Cleared Line Pieces:\n```\n"
    for key in clearedPieces.keys():
      message += f"{key}: {clearedPieces.get(key)}\n"
    message += "\n```"

    await ctx.reply(message)

    # Write to file
    full = dict()
    full["normal"] = pieces
    full["cleared"] = clearedPieces
    with open(f"__userdata/{ctx.author.id}/toFumenRGB.json", 'w') as convert_file:
      convert_file.write(json.dumps(full))

  except Exception:
    await ctx.reply("An error occurred while processing the image.")
    traceback.print_exc()

  # I did not write a single full line of code here but it works sooooo


@bot.command()
async def currentcommands(ctx):
  if not running_commands:
    await ctx.reply("No commands are running right now")
    return

  message = "```\n"
  for i in running_commands:
    message += f"{i['user']}: " + i["name"] + "\n"
  message += "```"
  await ctx.reply(message)


@bot.command()
async def killmyprocesses(ctx):
  for process in running_commands:
    if (ctx.author.id == process['user']):
      await ctx.send(f"{process['name']} killed")
      try:
        running_commands.remove(process)
      except:
        pass
      process['process'].kill()
  await ctx.reply(
    "All your processes killed. Note that whatever command you were running will probably error."
  )


@bot.command()
async def togray(ctx, fumen):
  fumen = decode(fumen)
  fumen = re.sub("[SZJLTIO]", "X", fumen)
  fumen = re.sub("\n", "", fumen)
  fumen = encode(fumen)
  await ctx.reply(fumen)

tspintypes = {"TSM" : 1, "TSS" : 1, "TSD" : 2, "TST" : 3}

@bot.command()
async def spincover(ctx, fumen = None, queue = None, minimal_type = "TSS"):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a queue")
    return
  elif(not minimal_type.upper() in tspintypes):
    print(minimal_type.upper())
    await ctx.reply("The type must be either TSM, TSS, TSD or TST.")
    return

  spinfile = f"__userdata/{ctx.author.id}/tempspin.csv"
  queuefeedfile = f"__userdata/{ctx.author.id}/tempfield.txt"
  coverfile = f"__userdata/{ctx.author.id}/cover.csv"
  coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
  tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  spincommand = await system(ctx, f"java -jar sfinder.jar spin -t {fumen} -p {queue} --format csv --split yes -o {spinfile} -c {tspintypes[minimal_type.upper()]} > {tempfile} 2> {errorfile}")

  if (spincommand != 0):
    await ctx.reply(
      "An error has occured with the spin command and the parameters you sent."
    )
    await ctx.reply(file=discord.File(errorfile))
    return

  spins = open(spinfile, encoding = "utf-8").read().splitlines()
  allspins = ""
  for spin in spins[1:]:
    spin = spin.split(",")
    allspins += spin[0] + "\n"

  with open(queuefeedfile, "w") as fieldinput:
    fieldinput.write(allspins)

  covercommand = await system(ctx, f"java -jar sfinder.jar cover -fp {spinfile} -p {queue} --kicks kicks/jstris180.properties -d 180 -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}")
  if (covercommand != 0):
    await ctx.reply(
      "An error has occured with the spin command and the parameters you sent."
    )
    await ctx.reply(file=discord.File(errorfile))
    return

  output = ""

  setupandcover = []
  coveroutput = open(coveroutputfile).read().splitlines()
  for i in coveroutput:
    if("fumen.zui.jp" in i):
        coverpercent = float(i.split(" %")[0])
        coverfumen = i.split("fumen.zui.jp/?")[1]
        setupandcover.append([decode(unglue(coverfumen)), coverpercent])
    elif("OR" in i):
        totalcover = i.split(" = ")[1]
        output += f"The total coverage is {totalcover}\n"

  setupandcover.sort(key=lambda x: x[1] * -1)
  #setupandcover = setupandcover[:50]
  outputfumen = []

  for i in setupandcover:
    outputfumen.append(Page(Field(field = i[0], garbage = "__________"), comment = str(i[1])))

  output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" + pyencode(outputfumen)) + "\n"

  await system(ctx, f"python cover-to-path.py --csv-path {coverfile} --output-file-path {covertopathfile} --unglued-fumen-script-path unglueFumen.js  > {tempfile}")
  await system(ctx, f"npx sfinder-minimal {covertopathfile} > {tempfile}")
  await system(ctx, f"python true_minimal.py > {tempfile}")
  outputlink = open(tempfile).read().splitlines()[1]
  output += f"The minimal followup set is {outputlink}"
  await ctx.reply(output)

  remove(spinfile)
  remove(queuefeedfile)
  remove(coverfile)
  remove(coveroutputfile)
  remove(covertopathfile)
  #remove(tempfile)

@bot.command()
async def setupcover(ctx, fumen = None, queue = None, second_queue = None, minimal_type = "normal", exclude = "none", fill = "I", margin = "O"):
  if (fumen == None):
    await ctx.reply("Please provide a fumen")
    return
  elif (queue == None):
    await ctx.reply("Please provide a setup queue")
    return
  elif (second_queue == None):
    await ctx.reply("Please provide a cover queue")
    return

  spinfile = f"__userdata/{ctx.author.id}/tempspin.csv"
  queuefeedfile = f"__userdata/{ctx.author.id}/tempfield.txt"
  coverfile = f"__userdata/{ctx.author.id}/cover.csv"
  coveroutputfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  covertopathfile = f"__userdata/{ctx.author.id}/cover-to-path.csv"
  tempfile = f"__userdata/{ctx.author.id}/ezsfinder.txt"
  errorfile = f"__userdata/{ctx.author.id}/error.txt"

  spincommand = await system(ctx, f"java -jar sfinder.jar setup -t {fumen} -p {queue} --format csv --split yes -o {spinfile} --fill {fill} --margin {margin} --exclude {exclude} > {tempfile} 2> {errorfile} ")
  spins = open(spinfile, encoding = "utf-8").read().splitlines()

  if (spincommand != 0):
    await ctx.reply(
      "An error has occured with the setup command and the parameters you sent."
    )
    await ctx.reply(file=discord.File(errorfile))
    return

  allspins = ""
  for spin in spins[1:]:
    spin = spin.split(",")
    allspins += spin[0] + "\n"

  with open(queuefeedfile, "w") as fieldinput:
    fieldinput.write(allspins)

  covercommand = await system(ctx, f"java -jar sfinder.jar cover -fp {spinfile} -p {second_queue} --kicks kicks/jstris180.properties -d 180 -o {coverfile} -M {minimal_type} > {coveroutputfile} 2> {errorfile}")
  if (covercommand != 0):
    await ctx.reply(
      "An error has occured with the cover command and the parameters you sent."
    )
    await ctx.reply(file=discord.File(errorfile))
    return

  output = ""

  setupandcover = []
  coveroutput = open(coveroutputfile).read().splitlines()
  for i in coveroutput:
    if("fumen.zui.jp" in i):
        coverpercent = float(i.split(" %")[0])
        coverfumen = i.split("fumen.zui.jp/?")[1]
        setupandcover.append([decode(unglue(coverfumen)), coverpercent])
    elif("OR" in i):
        totalcover = i.split(" = ")[1]
        output += f"The total coverage is {totalcover}\n"

  setupandcover.sort(key=lambda x: x[1] * -1)
  #setupandcover = setupandcover[:50]
  outputfumen = []

  for i in setupandcover:
    outputfumen.append(Page(Field(field = i[0], garbage = "__________"), comment = str(i[1])))

  output += "All solutions: " + make_tiny("https://fumen.zui.jp/?" + pyencode(outputfumen)) + "\n"

  await system(ctx, f"python cover-to-path.py --csv-path {coverfile} --output-file-path {covertopathfile} --unglued-fumen-script-path unglueFumen.js  > {tempfile}")
  await system(ctx, f"npx sfinder-minimal {covertopathfile} > {tempfile}")
  await system(ctx, f"python true_minimal.py > {tempfile}")
  outputlink = open(tempfile).read().splitlines()[1]
  output += f"The minimal followup set is {outputlink}"
  await ctx.reply(output)

  remove(spinfile)
  remove(queuefeedfile)
  remove(coverfile)
  remove(coveroutputfile)
  remove(covertopathfile)

@bot.command(aliases=["unglue"]) #unglue is already a command
async def ungluefumen(ctx, fumen):
  await ctx.reply("Please provide a cover queue")
  fumen = unglue(bestsolve[0])

bot.run(bot_token)
