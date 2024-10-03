import discord
from discord.ext import commands
import asyncio

# Set up your bot with a command prefix
bot = commands.Bot(command_prefix="!")

intents = discord.Intents.default()
intents.message_content = True

# Example command that the bot can handle
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# This function handles executing commands from the terminal
async def terminal_input():
    await bot.wait_until_ready()
    print("Terminal command interface is ready. You can type commands.")
    while not bot.is_closed():
        # Get input from the terminal
        user_input = input(">> ")
        if user_input.startswith("!"):  # Check if it's a valid command
            # Create a fake message object to simulate command execution
            ctx = await create_fake_context(user_input)
            await bot.invoke(ctx)

# This function simulates a message to trigger the command invocation
async def create_fake_context(message_content):
    # Pick the guild and channel where you want to execute commands
    guild = bot.guilds[0]  # You can change this to select a specific guild
    channel = guild.text_channels[0]  # Change this to the desired channel
    author = guild.me  # The bot itself will act as the author of the command

    message = discord.Message(
        state=bot._connection,
        channel=channel,
        data={
            'id': 1234,
            'content': message_content,
            'author': {
                'id': author.id,
                'username': author.name,
                'discriminator': author.discriminator,
                'bot': True,
            },
            'guild_id': guild.id,
            'channel_id': channel.id,
        }
    )
    
    # Create context from the message
    return await bot.get_context(message)

# Run the bot
async def main():
    async with bot:
        # Start the bot and terminal input simultaneously
        bot.loop.create_task(terminal_input())
        await bot.start('MTE1NDM1MDIzNzQyMzUyMTg4Mg.Gd77BH.3ayxpbs_OkG_WddxyAy3Qb7rMwpiLI22K80W6I')  # Replace with your bot token

# Run the async main function
asyncio.run(main())
