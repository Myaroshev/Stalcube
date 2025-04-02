#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
import discord
import datetime
#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
from discord.ext import commands
from pymongo import MongoClient
from datetime import timedelta
from config import settings
#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
client = commands.Bot(command_prefix = settings['PREFIX'], intents=discord.Intents.all())
cluster = MongoClient("тут данные от БД")
collection = cluster.stalcube_db.users
#——————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————


servers = [1291493323017551882, 626146788591534090, 992742133431803974] #сервера
 

class WarnSystem(commands.Cog):

    def __init__(self, client):
        self.client: commands.Bot = client

    #функция для создания пользователя в БД (MongoDB)
    def add_user(self, member: discord.Member):
        if collection.count_documents({"_id": member.id}) == 0:
            post = {
                "_id": member.id,
                "nick": member.name,
                "warn": 0
            }
            collection.insert_one(post)  



    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    #event() на ошибку использования команды обычным пользователям(не модерации)
    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingAnyRole):
            await interaction.response.send_message("Вы не можете это использовать!", ephemeral=True)
        else:
            return



    #event()-лог на слэш команду /warn
    @commands.Cog.listener()
    async def on_application_command(self, ctx: discord.ApplicationContext):
        if ctx.command.name == 'warn':
            member_id = int(next(option['value'] for option in ctx.interaction.data['options'] if option['name'] == 'member')) #id пользователя из выборки /warn
            member = ctx.guild.get_member(member_id) #сам пользователь(дискриминатор(==#0), id, name, display_name и тому подобное)

            if member == None or member.id == 1354411757606666385:
                return

            log_channel = self.client.get_channel(1354421033062371500) #поменять на лог-канал в самом дискорде сталкуба(это к Роме)
            warn = collection.find_one({"_id": member.id})["warn"]

            embed = discord.Embed(
                title="⚠️ Выдано предупреждение",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(
                name="Модератор",
                value=f"{ctx.author.mention}\n`{ctx.author.id}`",
                inline=True
            )
            embed.add_field(
                name="Нарушитель",
                value=f"{member.mention}\nВарны: `{warn}`",
                inline=True
            )
            embed.set_footer(text = ctx.author.display_name, icon_url = ctx.author.avatar)
            embed.set_thumbnail(url=member.avatar.url)

            if log_channel:
                await log_channel.send(embed=embed)



    #слэш-команда для варна
    @commands.slash_command(name="warn", description="Выдача варна участнику")
    @commands.has_any_role("тут роли модерации")
    async def warn(self, interaction: discord.Interaction, member: discord.Member):

        if member.id == 1354411757606666385:
            await interaction.respond("Нельзя выдать варн боту 0_0", ephemeral=True)
            return
        if member.id == interaction.user.id:
            await interaction.respond("Нельзя выдать варн самому себе О_о", ephemeral=True)
            return


        self.add_user(member)
        duration = timedelta(hours = 1)
        warn = collection.find_one({"_id": member.id})["warn"]

        
        if (warn+1) == 3:
            collection.update_one({"_id": member.id}, {"$inc": {"warn": 1}})

            await member.timeout_for(duration)
            collection.update_one({"_id": member.id}, {"$set": {"warn": 0}})
            await interaction.response.send_message(f"Пользователь **{member.name}** был отправлен __подумать о своем поведении__", ephemeral=True)
        else:
            collection.update_one({"_id": member.id}, {"$inc": {"warn": 1}})
            await interaction.response.send_message(f"Вы выдали варн пользователю **{member.name}**", ephemeral=True)

    

    #слэш-команда для проверки варнов у пользователя и его состояние о тайм-ауте
    @commands.slash_command(name="warncheck", description="Проверка варнов у пользователя")
    async def warn_check(self, ctx: discord.ApplicationContext,
                         member: discord.Member):
        
        role_1 = discord.utils.get(ctx.guild.roles, name="testbot")

        if role_1 not in ctx.author.roles:
            await ctx.respond("У вас нет прав!", ephemeral=True)
            return

        self.add_user(member)
        warn = collection.find_one({"_id": member.id})["warn"]

        embed = discord.Embed(title=f"Информация об пользователе", description="",color=0xd21234, timestamp=datetime.datetime.now())
        embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar)
        embed.set_thumbnail(url=member.avatar.url)

        if member.timed_out:
            embed.add_field(name=f"", value=f"Пользователь: {member.mention}\nВарны: `{warn}`\nТайм-аут: `наказан`", inline=False)
        else:
            embed.add_field(name=f"", value=f"Пользователь: {member.mention}\nВарны: `{warn}`\nТайм-аут: `не наказан`", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


#установка кога
def setup(client: commands.Bot):
    client.add_cog(WarnSystem(client))