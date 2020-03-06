import discord

from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role(519325622162423809, 519921688511512578, 529928293680545802)
    async def say(self, ctx, *, content: str):
        await ctx.send(content)

    @commands.command(aliases=['saye'])
    @commands.has_any_role(519325622162423809, 519921688511512578, 529928293680545802)
    async def say_embed(self, ctx, title: str, *, content: str):
        embed = discord.Embed(title=title, colour=discord.Colour(
            0x32ad5a), description=content)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
