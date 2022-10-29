# Imports
import nextcord
from nextcord.ext import commands
from typing import Optional
import aiohttp
import asyncio
import random
import base64
import re
import argparse
import colorama
import nest_asyncio
# Init colorama
colorama.init()
# Apply nest_asyncio
nest_asyncio.apply()
# Get token from run
parser = argparse.ArgumentParser()
parser.add_argument('token', type=str, help='Token for Discord Bot')
args = parser.parse_args()
if args.token == None:
    args.token = input("Please input your token: ")


bot = commands.Bot()


# Notify when ready
@bot.event
async def on_ready():
    print(f'{bot.user} online')


# Menus
class ImageMenu(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    
    @nextcord.ui.button(label='Upscale', style=nextcord.ButtonStyle.blurple)
    async def upscale(self, button:nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("**Upscaling**")
        self.value = "upscale"
        self.stop()
    
    @nextcord.ui.button(label='Vary', style=nextcord.ButtonStyle.blurple)
    async def vary(self, button:nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("**Varying**")
        self.value = "vary"
        self.stop()
    
    @nextcord.ui.button(label='Redo', style=nextcord.ButtonStyle.blurple)
    async def redo(self, button:nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.send("**Redoing**")
        self.value = "redo"
        self.stop()

async def findStepsNumber(user):
    if str(user) in open('./premiumMembers.txt', 'r').read():
        return 150
    else:
        return 75

async def stableDiffusionVary(interaction, ID, user, prompt, scale, seed, tile, fileLocation):
    # Make vary request
    async with aiohttp.ClientSession() as session:
        # Get image base64
        imageData = "data:image/png;base64," + base64.b64encode(open(fileLocation, "rb").read()).decode()
        async with session.post('http://127.0.0.1:7860/api/predict/', timeout=-1, json={"fn_index":35,"data":[0,f"{prompt}","","None","None",f"{imageData}",None,None,None,"Draw mask",150,"Euler",4,"original",False,False,1,1,7,0.5,-1,-1,0,0,0,False,512,512,"Just resize",False,32,"Inpaint masked","","","None","<ul>\n<li><code>CFG Scale</code> should be 2 or lower.</li>\n</ul>\n",True,True,"","",True,50,True,1,0,False,4,1,"<p style=\"margin-bottom:0.75em\">Recommended settings: Sampling Steps: 80-100, Sampler: Euler a, Denoising strength: 0.8</p>",128,8,["left","right","up","down"],1,0.05,128,4,"fill",["left","right","up","down"],False,False,None,"","<p style=\"margin-bottom:0.75em\">Will upscale the image to twice the dimensions; use width and height sliders to set tile size</p>",64,"None","Seed","","Nothing","",True,False,False,None,"",""],"session_hash":"xwvsrwexi9d"}) as resp:
            response = await resp.json()

    # Send message
    fileLocation = response['data'][0][0]['name']
    file = nextcord.File(fileLocation, filename=f"{ID}.png")
    msg = await interaction.send(file=file, content=f"**{prompt}** by **{user}** (varied)", view=menu)
    
    # Handle buttons
    while True:
        await msg.edit(view = None)
        menu = ImageMenu()
        await msg.edit(view = menu)
        await menu.wait()

        if menu.value == "upscale":
            asyncio.run(stableDiffusionUpscale(interaction, ID, user, prompt, scale, seed, tile, fileLocation))
        elif menu.value == "vary":
            asyncio.run(stableDiffusionVary(interaction, ID, user, prompt, scale, seed, tile, fileLocation))
        elif menu.value == "redo":
            asyncio.run(stableDiffusionGenerate(interaction, ID, user, prompt, scale, seed, tile, fileLocation))

async def stableDiffusionUpscale(interaction, ID, user, prompt, scale, seed, tile, fileLocation):
    # Make upscale request
    async with aiohttp.ClientSession() as session:
        # Get image base64
        imageData = "data:image/png;base64," + base64.b64encode(open(fileLocation, "rb").read()).decode()
        open('./debug.txt', 'w').write(str(imageData))
        async with session.post('http://127.0.0.1:7860/api/predict/', timeout=-1, json={"fn_index":44,"data":[0,0,f"{imageData}",None,"","",True,0,0,0,2,512,512,True,"ScuNET GAN","None",1,False],"session_hash":"xwvsrwexi9d"}) as resp:
            response = await resp.json()
    
    # Send message
    fileLocation = response['data'][0][0]['name']
    file = nextcord.File(fileLocation, filename=f"{ID}.png")
    msg = await interaction.send(file=file, content=f"**{prompt}** by **{user}** (upscaled)")

    # Handle buttons
    while True:
        await msg.edit(view = None)
        menu = ImageMenu()
        await msg.edit(view = menu)
        await menu.wait()

        if menu.value == "upscale":
            asyncio.run(stableDiffusionUpscale(interaction, ID, user, prompt, scale, seed, tile, fileLocation))
        elif menu.value == "vary":
            asyncio.run(stableDiffusionVary(interaction, ID, user, prompt, scale, seed, tile, fileLocation))
        elif menu.value == "redo":
            asyncio.run(stableDiffusionGenerate(interaction, ID, user, prompt, scale, seed, tile, fileLocation))

async def stableDiffusionGenerate(interaction, ID, user, prompt, scale, seed, tile, fileLocation):
    # Get variables
    steps = await findStepsNumber(user)
    if seed != -1:
        seedGiven = True
    else:
        seedGiven = False
    if seed == -1:
        seed = random.randint(10000000000, 99999999999)
    # Make generation requests
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:7860/api/predict/', timeout=-1, json={"fn_index":13,"data":[f"{prompt}","","None","None",steps,"Euler a",False,bool(tile),1,1,int(scale),-1,-1,0,0,0,False,512,512,False,0.7,0,0,"None",False,False,None,"","Seed","","Nothing","",True,False,False,None,"",""],"session_hash":str(ID)}) as resp:
            response = await resp.json()
    # Send message
    fileLocation = response['data'][0][0]['name']
    file = nextcord.File(fileLocation, filename=f"{ID}.png")
    if seedGiven:
        msg = await interaction.send(file=file, content=f"**{prompt}** by **{user}**\n**Seed:** {seed}", view=menu)
    else:
        msg = await interaction.send(file=file, content=f"**{prompt}** by **{user}**")
    
    # Handle buttons
    while True:
        await msg.edit(view = None)
        menu = ImageMenu()
        await msg.edit(view = menu)
        await menu.wait()

        if menu.value == "upscale":
            asyncio.run(stableDiffusionUpscale(interaction, ID, user, prompt, scale, seed, tile, fileLocation))
        elif menu.value == "vary":
            asyncio.run(stableDiffusionVary(interaction, ID, user, prompt, scale, seed, tile, fileLocation))
        elif menu.value == "redo":
            asyncio.run(stableDiffusionGenerate(interaction, ID, user, prompt, scale, seed, tile, fileLocation))

@bot.slash_command(description = "Generate an Image using Stable Diffusion")
async def diffuse(interaction: nextcord.Interaction, prompt: str):
    scale,seed,tile = 7,-1,False

    # Look for args in prompt
    pattern = re.compile(r"--scale+ [0-9]+")
    matches = pattern.finditer(prompt)
    for match in matches:
        scale = (int(match.group(0)[8:]))
        prompt = prompt.replace(" --scale " + str(scale), "")
    pattern = re.compile(r"--seed+ [0-9]+")
    matches = pattern.finditer(prompt)
    for match in matches:
        seed = (int(match.group(0)[7:]))
        prompt = prompt.replace(" --seed " + str(seed), "")
    pattern = re.compile(r"--tile")
    matches = pattern.finditer(prompt)
    for match in matches:
        tile = True
        prompt = prompt.replace(" --tile", "")
    
    # Tell user it is generating
    await interaction.response.send_message(f"**{prompt}** (generating)")
    # Generate
    ID = random.randint(1000000000, 9999999999)
    print(ID)
    user = interaction.user
    asyncio.run(stableDiffusionGenerate(interaction, ID, user, prompt, scale, seed, tile, None))

bot.run(args.token)