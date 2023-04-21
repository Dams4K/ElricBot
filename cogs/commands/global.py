from discord import *
from discord.ext.pages import Paginator
from data_management import *
from utils.bot_embeds import *
from utils.bot_autocompletes import *
from utils.bot_commands import *
from operator import attrgetter

class GlobalCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    about = BotSlashCommandGroup("about")
    list_grp = BotSlashCommandGroup("list")

    @about.command(name="object")
    @option("object", type=GuildObjectConverter, required=True, autocomplete=get_objects)
    async def about_object(self, ctx, object: GuildObject):
        if object is None:
            await ctx.respond(text_key="OBJECT_DOES_NOT_EXIST")
            return
        
        articles = [article for article in GuildArticle.list_articles(ctx.guild.id) if article.has_object(object)]
        description = [ctx.translate("WHERE_TO_BUY_TEMPLATE", article=article.name, unit_price=round(article.price/article.get_quantity(object), 2)) for article in articles]

        embed = NormalEmbed(ctx.guild_config, title=object.name, description=object.description)
        embed.add_field(name=ctx.translate("WHERE_TO_BUY"), value="\n".join(description))
        await ctx.respond(embed=embed)

    @about.command(name="article")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    async def about_article(self, ctx, article: GuildArticle):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return
        
        embed = NormalEmbed(ctx.guild_config, title=article.name, description=f"prix: {article.price}")

        roles = [ctx.guild.get_role(role_id).mention for role_id in article.role_ids]
        if roles != []:
            embed.add_field(name="Roles", value="\n".join(roles))
        
        objects = [f"{GuildObject(object_id, ctx.guild.id).name} | {amount}" for object_id, amount in article.object_ids.items()]
        if objects != []:
            embed.add_field(name="Objects", value="\n".join(objects))
        
        await ctx.respond(embed=embed)

    @list_grp.command(name="objects")
    async def list_objects(self, ctx):
        objects = GuildObject.list_objects(ctx.guild.id)
        sorted_objects = sorted(objects, key=attrgetter("_object_id"))

        embed_pages = []
        object_descriptions = []
        for i in range(len(sorted_objects)):
            obj = sorted_objects[i]
            object_descriptions.append(f"{obj.name} ({obj._object_id})")

            if (i+1) % 20 == 0 or i+1 == len(sorted_objects):
                embed = NormalEmbed(ctx.guild_config, title="Objects")
                embed.description = "\n".join(object_descriptions)
                embed_pages.append(embed)
                object_descriptions.clear()
        
        if embed_pages == []:
            embed = WarningEmbed(ctx.guild_config, title=ctx.translate("NO_OBJECTS_EXISTS"))
            await ctx.respond(embed=embed)
            return
            
        paginator = Paginator(pages=embed_pages)
        await paginator.respond(ctx.interaction)

    @list_grp.command(name="articles")
    async def list_articles(self, ctx):
        articles = GuildArticle.list_articles(ctx.guild.id)
        sorted_articles = sorted(articles, key=attrgetter("_article_id"))

        embed_pages = []
        articles_description = []
        for i in range(len(sorted_articles)):
            article = sorted_articles[i]
            articles_description.append(f"{article.name} ({article._article_id})")

            if (i+1) % 20 == 0 or i+1 == len(sorted_articles):
                embed = NormalEmbed(ctx.guild_config, title="Articles")
                embed.description = "\n".join(articles_description)
                embed_pages.append(embed)
                articles_description.clear()
        
        if embed_pages == []:
            embed = WarningEmbed(ctx.guild_config, title=ctx.translate("NO_ARTICLES_EXISTS"))
            await ctx.respond(embed=embed)
            return
        
        paginator = Paginator(pages=embed_pages)
        await paginator.respond(ctx.interaction)

    @list_grp.command(name="salaries")
    async def list_salaries(self, ctx):
        salaries = GuildSalaries(ctx.guild.id).salaries

        embeds = []
        description = []
        for i in range(len(salaries)):
            role_id = list(salaries.keys())[i]
            role = ctx.guild.get_role(int(role_id))
            pay = salaries[role_id]

            if not role is None:
                role = role.mention
            
            description.append(f"{role} : {pay}")
            if len(description) >= 20 or i+1 == len(salaries):
                embed = NormalEmbed(ctx.guild_config, title="Salaries")
                embed.description = "\n".join(description)
                embeds.append(embed)
                description.clear()

        if embeds == []:
            embed = WarningEmbed(ctx.guild_config, title=ctx.translate("NO_SALARIES_EXISTS"))
            await ctx.respond(embed=embed)
            return
            
        paginator = Paginator(pages=embeds)
        await paginator.respond(ctx.interaction)


    @bot_slash_command(name="profil")
    @option("member", type=Member, required=False, default=None)
    async def slash_profil(self, ctx, member = None):
        member = ctx.author if member == None else member
        await self.show_profil(ctx, member)
    
    @bot_user_command(name="profil")
    async def user_profil(self, ctx, member: Member):
        await self.show_profil(ctx, member, ephemeral=True)
    
    async def show_profil(self, ctx, member: Member, ephemeral=False):
        member_data = MemberData(member.id, ctx.guild.id)

        xp_goal = member_data.get_xp_goal(ctx.guild_config.leveling_formula)
        embed = NormalEmbed(ctx.guild_config, title=ctx.translate("PROFIL_OF", member=member))
        embed.add_field(name=ctx.translate("LEVEL").capitalize(), value=str(member_data.level))
        embed.add_field(name=ctx.translate("XP").capitalize(), value=f"{member_data.xp}/{xp_goal}")
        embed.add_field(name=ctx.translate("MONEY").capitalize(), value=str(member_data.money))
        
        await ctx.respond(embed=embed, ephemeral=ephemeral)


#     @bridge.bridge_command(name="utip")
#     async def utip(self, ctx):
#         embed = NormalEmbed(ctx.guild_config, title="UTIP")
#         embed.description = """
# [INSERER TEXT COOL]

# [INSERER LIEN UTIP]
# """

#         await ctx.respond(embed=embed)


    @slash_command(name="say")
    async def say(self, ctx, *, message: str):
        if ctx.is_app:
            await ctx.respond("message sent", ephemeral=True)
        else:
            await ctx.message.delete()
        
        await ctx.send(message)


    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        leveling_config = GuildLevelingData(ctx.guild.id)

        if not ctx.command is None:
            return
        if not leveling_config.enabled:
            return
        if leveling_config.is_channel_ban(ctx.channel):
            return
        if leveling_config.is_member_ban(message.author):
            return

        level_before = ctx.author_data.level
        ctx.author_data.add_xp(len(message.content))
        level_after = ctx.author_data.refresh_level(ctx.guild_config.leveling_formula)

        if level_before < level_after:
            await ctx.send(ctx.guild_config.send_level_up_message(ctx.author, level_before, level_after))

def setup(bot):
    bot.add_cog(GlobalCog(bot))