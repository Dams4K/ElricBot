from discord import *
from data_management import *
from utils.bot_autocompletes import *

class ObjectCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    objects = SlashCommandGroup("objects", default_member_permissions=Permissions(administrator=True))
    change = objects.create_subgroup("change")

    # @objects.command(name="list")
    # async def list_objects(self, ctx):
    #     objects = GuildObject.list_objects(ctx.guild.id)
    #     sorted_objects = sorted(objects, key=attrgetter("_object_id"))

    #     embed_pages = []
    #     object_descriptions = []
    #     for i in range(len(sorted_objects)):
    #         obj = sorted_objects[i]
    #         object_descriptions.append(f"{obj.name} ({obj._object_id})")
    #         if (i+1) % 20 == 0 or i+1 == len(sorted_objects):
    #             embed = NormalEmbed(ctx.guild_config, title="Objects")
    #             embed.description = "\n".join(object_descriptions)
    #             embed_pages.append(embed)
    #             object_descriptions.clear()
        
    #     if embed_pages == []:
    #         await ctx.respond(text_key="NO_OBJECTS_EXISTS")
    #     else:
    #         paginator = pages.Paginator(pages=embed_pages)
    #         if hasattr(ctx, "interaction"):
    #             await paginator.respond(ctx.interaction)
    #         else:
    #             await paginator.send(ctx)

    @objects.command(name="create")
    @option("name", type=str, max_length=32, required=True)
    @option("description", type=str, max_length=1024, default="")
    async def create_object(self, ctx, name: str, description: str):
        new_object = GuildObject.new(ctx.guild.id, name)
        new_object.set_description(description)
        await ctx.respond("Object created")

    # @objects.command(name="about")
    # @option("obj", type=GuildObjectConverter, autocomplete=get_objects)
    # async def about_object(self, ctx, obj: GuildObject):
    #     if obj is None:
    #         await ctx.respond(text_key="OBJECT_DOES_NOT_EXIST")
    #     else:
    #         embed = NormalEmbed(ctx.guild_config, title=obj.name, description=obj.description)
    #         await ctx.respond(embed=embed)

    @change.command(name="description")
    @option("obj", type=GuildObjectConverter, autocomplete=get_objects)
    @option("description", type=str, max_length=1024)
    async def change_description(self, ctx, obj: GuildObject, description: str):
        before_description = obj.description
        obj.set_description(description)
        await ctx.respond(text_key="OBJECT_DESCRIPTION_CHANGED", text_args={"before": before_description, "after": description})
    
    @change.command(name="name")
    @option("obj", type=GuildObjectConverter, autocomplete=get_objects)
    @option("name", type=str, max_length=32)
    async def change_name(self, ctx, obj: GuildObject, name: str):
        before_name = obj.name
        obj.set_name(name)
        await ctx.respond(text_key="OBJECT_NAME_CHANGED", text_args={"before": before_name, "after": name})

    @objects.command(name="delete")
    @option("obj", type=GuildObjectConverter, required=True, autocomplete=get_objects)
    async def delete_object(self, ctx, obj: GuildObject):
        if obj is None:
            await ctx.respond(text_key="OBJECT_DOES_NOT_EXIST")
        else:
            confirm_view = ConfirmView()
            confirm_embed = DangerEmbed(ctx.guild_config, title=ctx.translate("DELETION"), description=ctx.translate("OBJECT_DELETION_CONFIRMATION", object=obj.name))
            await ctx.respond(embed=confirm_embed, view=confirm_view)
            await confirm_view.wait()
            if confirm_view.confirmed:
                obj.delete()
                await ctx.respond(text_key="OBJECT_DELETION_PERFORMED", text_args={"object": obj.name})
            else:
                await ctx.respond(text_key="DELETION_CANCELLED")

    @objects.command(name="give")
    @default_permissions(administrator=True)
    @option("member", type=Member, description="pick a member", required=True)
    @option("obj", type=GuildObjectConverter, description="pick an object", required=True, autocomplete=get_objects)
    @option("amount", type=int, default=1)
    async def give_object(self, ctx, member: Member, obj: GuildObject, amount: int = 1):
        member_data = MemberData(member.id, ctx.guild.id)
        member_inventory = member_data.get_inventory()

        if obj is None:
            await ctx.respond(text_key="OBJECT_DOES_NOT_EXIST")
        elif member_inventory.is_full():
            await ctx.respond(text_key="INVENTORY_FULL", text_args={"member": member})
        else:
            member_inventory.add_object(obj, amount)
            member_data.set_inventory(member_inventory)

            await ctx.respond(text_key="OBJECT_GIVED", text_args={"object_name": obj.name, "amount": amount, "member": member})

def setup(bot):
    bot.add_cog(ObjectCog(bot))