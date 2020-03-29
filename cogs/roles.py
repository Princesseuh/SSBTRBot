import discord
import json

from discord.ext import commands

ENVIRONNEMENTJSON = 'data/roles_prod.json'


def get_key(mydict, val):
    for key, value in mydict.items():
        if val == value:
            return key

class RolesManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(ENVIRONNEMENTJSON, 'r', encoding='utf-8') as r:
            self.roles_config = json.load(r)


    def role_list(self):
        return {**self.roles_config['regions'], **self.roles_config['other']}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = self.bot.get_user(payload.user_id)

        if user is None or user.bot or payload.message_id != self.roles_config['self_assign_message']:
            return

        server = self.bot.get_guild(payload.guild_id)
        member = server.get_member(payload.user_id)

        role = discord.utils.find(
            lambda r: r.id == self.role_list()[payload.emoji.name], server.roles
        )


        if role is not None:
            if role.id in self.roles_config['regions'].values():
                role_list = [role for role in member.roles if role.id not in self.roles_config['regions'].values()]
            else:
                role_list = member.roles

            role_list.append(role)

            await member.edit(roles=role_list)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = self.bot.get_user(payload.user_id)

        if user is None or user.bot or payload.message_id != self.roles_config['self_assign_message']:
            return

        server = self.bot.get_guild(payload.guild_id)
        member = server.get_member(payload.user_id)

        role = discord.utils.find(
            lambda r: r.id == self.role_list()[payload.emoji.name], server.roles
        )

        if role is not None:
            await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if (before.roles == after.roles):
            return

        # TODO: Simplify these
        before_region_roles = []
        for role in before.roles:
            if role.id in self.roles_config['regions'].values():
                    before_region_roles.append(role.id)


        after_region_roles = []
        for role in after.roles:
            if role.id in self.roles_config['regions'].values():
                    after_region_roles.append(role.id)


        new_roles = set(after_region_roles) - set(before_region_roles)

        if len(new_roles) > 0:
            channel = self.bot.get_channel(self.roles_config['self_assign_message_channel'])

            role_message = await channel.fetch_message(self.roles_config['self_assign_message'])
            member = after.guild.get_member(after.id)

            for role in before_region_roles:
                await role_message.remove_reaction(get_key(self.roles_config['regions'], role), member)

    @commands.command(aliases=["crm"])
    @commands.has_any_role(519325622162423809, 519921688511512578, 529928293680545802)
    async def create_role_message(self, ctx):
        embed, emoji_list = await self.get_role_embed(ctx)

        message = await ctx.send(embed=embed)

        for emoji in emoji_list:
            await message.add_reaction(emoji)


        with open(ENVIRONNEMENTJSON, 'w', encoding='utf-8') as f:
            self.roles_config['self_assign_message'] = message.id
            self.roles_config['self_assign_message_channel'] = message.channel.id
            json.dump(self.roles_config, f)


    @commands.command(aliases=["urm"])
    @commands.has_any_role(519325622162423809, 519921688511512578, 529928293680545802)
    async def update_role_message(self, ctx):
        embed, emoji_list = await self.get_role_embed(ctx)

        channel = self.bot.get_channel(self.roles_config['self_assign_message_channel'])
        message = await channel.fetch_message(self.roles_config['self_assign_message'])

        for emoji in emoji_list:
            await message.add_reaction(emoji)

        await message.edit(embed=embed)


    async def get_role_embed(self, ctx):
        embed = discord.Embed(title="Roles", colour=discord.Colour(
            0x32ad5a), description="Pour vous assigner une région, cliquez simplement sur la reaction avec l'emoji correspondant à la région désirée.\n\nUn rôle {} est également disponible afin de signaler aux autres membres que vous souhaitez jouer en ligne.".format(ctx.guild.get_role(527673156597448714).mention))

        emoji_list = []

        region_list = ""
        for emoji, role_id in self.roles_config['regions'].items():
            role = ctx.guild.get_role(role_id)

            if not role:
                continue

            region_list += "{}: {}\n".format(emoji, role.mention)
            emoji_list.append(emoji)

        embed.add_field(name="Régions", value=region_list)

        other_list = ""
        for emoji, role_id in self.roles_config['other'].items():
            role = ctx.guild.get_role(role_id)

            if not role:
                continue

            other_list += "{} {}\n".format(emoji, role.mention)
            emoji_list.append(emoji)

        embed.add_field(name="Autres", value=other_list)

        return embed, emoji_list

def setup(bot):
    bot.add_cog(RolesManager(bot))
