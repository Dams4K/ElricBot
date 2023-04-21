from discord import *
from data_management import *
from utils.bot_embeds import *
from utils.bot_autocompletes import *
from utils.bot_views import ConfirmView
from utils.bot_commands import BotSlashCommandGroup
from operator import attrgetter

class ArticlesConfigCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    articles = BotSlashCommandGroup("articles", default_member_permissions=Permissions(administrator=True))
    change = articles.create_subgroup("change")
    add = articles.create_subgroup("add")
    remove = articles.create_subgroup("remove")
    
    @articles.command(name="create")
    @option("name", type=str, max_length=32)
    @option("price", type=float)
    @option("description", type=str, max_length=1024, default="*no description*")
    async def article_create(self, ctx, name, price, description):
        article = GuildArticle.new(ctx.guild.id, name).set_price(price).set_description(description)

        title = ctx.translate("ARTICLE_CREATED")
        description = ctx.translate("ARTICLE_CREATED_DESC", article=article.name)
        embed = NormalEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)

    
    @change.command(name="name")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("name", type=str, max_length=32, required=True)
    async def change_name(self, ctx, article: GuildArticle, name: str):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return
        
        old_name = article.name
        article.set_name(name)

        title = ctx.translate("NAME_MODIFIED")
        description = ctx.translate("ARTICLE_NAME_MODIFIED", article=old_name, new_name=name)
        embed = WarningEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)

    @change.command(name="description")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("description", type=str, max_length=1024, required=True)
    async def change_description(self, ctx, article: GuildArticle, description: str):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return
        
        article.set_description(description)

        title = ctx.translate("DESCRIPTION_MODIFIED")
        description = ctx.translate("ARTICLE_DESCRIPTION_MODIFIED", article=article.name, new_description=description)
        embed = WarningEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)
    
    @change.command(name="price")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("price", type=int, required=True)
    async def change_price(self, ctx, article: GuildArticle, price: int):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return
        
        article.set_price(price)

        title = ctx.translate("PRICE_MODIFIED")
        description = ctx.translate("ARTICLE_PRICE_MODIFIED", article=article.name, new_price=price)
        embed = WarningEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)
    
    @add.command(name="object")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("object", type=GuildObjectConverter, required=True, autocomplete=get_objects)
    @option("quantity", type=int, default=1)
    async def add_object(self, ctx, article: GuildArticle, object: GuildObject, quantity):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return

        if object is None:
            await ctx.respond(text_key="OBJECT_DOES_NOT_EXIST")
            return

        article.add_object(object, quantity)

        title = ctx.translate("OBJECT_ADDED")
        description = ctx.translate("ARTICLE_OBJECT_ADDED", quantity=quantity, object=object.name, article=article.name)
        embed = NormalEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)
    
    @remove.command(name="object")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("object", type=GuildObjectConverter, required=True, autocomplete=get_objects)
    @option("quantity", type=int, default=1)
    async def remove_object(self, ctx, article: GuildArticle, object: GuildObject, quantity=1):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return
        if object is None:
            await ctx.respond(text_key="OBJECT_DOES_NOT_EXIST")
            return
        
        article.remove_object(object, quantity)
        
        title = ctx.translate("OBJECT_REMOVED")
        description = ctx.translate("ARTICLE_OBJECT_REMOVED", quantity=quantity, object=object.name, article=article.name)
        embed = DangerEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)

    @add.command(name="role")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("role", type=Role, required=True)
    async def add_role(self, ctx, article: GuildArticle, role: Role):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return
        
        article.add_role(role)

        title = ctx.translate("ROLE_ADDED")
        description = ctx.translate("ARTICLE_ROLE_ADDED", role=role.mention, article=article.name)
        embed = NormalEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)
    
    @remove.command(name="role")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    @option("role", type=Role, required=True)
    async def remove_role(self, ctx, article: GuildArticle, role: Role):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
            return

        article.remove_role(role)

        title = ctx.translate("ROLE_REMOVED")
        description = ctx.translate("ARTICLE_ROLE_REMOVED", role=role.mention, article=article.name)
        embed = DangerEmbed(ctx.guild_config, title=title, description=description)
        await ctx.respond(embed=embed)

    @articles.command(name="delete")
    @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    async def delete_article(self, ctx, article: GuildArticle):
        if article is None:
            await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
        else:
            confirm_view = ConfirmView()
            confirm_embed = DangerEmbed(ctx.guild_config, title=ctx.translate("DELETION"), description=ctx.translate("ARTICLE_DELETION_CONFIRMATION", article=article.name))
            await ctx.respond(embed=confirm_embed, view=confirm_view)
            await confirm_view.wait()
            if confirm_view.confirmed:
                article.delete()
                await ctx.respond(text_key="ARTICLE_DELETION_PERFORMED", text_args={"article": article.name})
            else:
                await ctx.respond(text_key="DELETION_CANCELLED")

    # @articles.command(name="buy")
    # @option("article", type=GuildArticleConverter, required=True, autocomplete=get_articles)
    # async def buy_article(self, ctx, article):
    #     if article is None:
    #         await ctx.respond(text_key="ARTICLE_DOES_NOT_EXIST")
    #     else:
    #         try:
    #             await article.buy(ctx)
    #             await ctx.respond(text_key="ARTICLE_PURCHASED", text_args={"article": article.name})
    #         except NotEnoughMoney:
    #             author_money = ctx.author_data.money

    #             embed = WarningEmbed(ctx.guild_config, title=ctx.translate("E_CANNOT_PURCHASE"))
    #             embed.description = ctx.translate("E_NOT_ENOUGH_MONEY", money_missing=article.price-author_money, author_money=author_money, article_price=article.price)
    #             await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ArticlesConfigCog(bot))