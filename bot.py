import discord
from discord import Option
from discord.ext import commands
from pyexpat.errors import messages

import embeds
from casino import *
from config import *
from database import *
from enums import *

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

create_table()
create_daily_bonus_table()
create_donations_table()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

async def log_to_channel(title, message, colour): # логгер
    log_channel = bot.get_channel(LOGS_CHANNEL_ID)
    if log_channel is not None:
        await log_channel.send(embed=embeds.logs(title, message, colour))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/slots"))
    log_message = f'{bot.user} запущен и готов к работе!'
    await log_to_channel("Запуск бота",log_message, discord.Color.yellow())
    logging.info(log_message)
    print(f'{bot.user} запущен и готов к работе!')

@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id not in BOT_CHANNEL_ID:
        return
    log_message = (f"Удаление сообщения от <@{message.author.id}> в канале <#{message.channel.id}>")
    await log_to_channel("Удаление сообщения", log_message, discord.Color.yellow())
    logging.info(log_message)
    await message.delete()
    await bot.process_commands(message)

@bot.slash_command(name="stats", description='Статистика (Баланс, сколько пожертвовал)', guild_ids=GUILD_IDS)
async def stats(ctx):
    user_id = ctx.author.id
    balance = get_balance(user_id)
    donation = get_user_donation_amount(user_id)
    log_message = (
        f"""Пользователь <@{ctx.author.id}> проверил свою статистику:
            `Баланс: {balance} {CURRENCY1}`
            `Благотворительность: {donation} {CURRENCY1}`""")
    await log_to_channel("/stats", log_message, discord.Color.orange())
    logging.info(log_message)
    await ctx.respond(embed=embeds.stats(balance, donation, CURRENCY1, ctx.author.name, ctx.author.avatar.url), ephemeral=True)

@bot.slash_command(name="check_stats", description='Проверить статистику другого пользователя', guild_ids=GUILD_IDS)
async def check(ctx, user: discord.Option(discord.SlashCommandOptionType.mentionable, name="user", description="Укажите пользователя", required=True)):
    # Проверка на роль
    if isinstance(user, discord.Role):
        log_message = f"Пользователь <@{ctx.author.id}> указал роль вместо пользователя"
        await log_to_channel("/check_stats", log_message, discord.Color.red())
        logging.debug(log_message)
        await ctx.respond(embed=embeds.contra("oralcumshot", ctx.author.name, ctx.author.avatar.url), ephemeral=True)
        return

    # Проверка на бота
    if isinstance(user, discord.Member) and user.bot:
        log_message = f"Пользователь <@{ctx.author.id}> указал бота вместо пользователя"
        await log_to_channel("/check_stats", log_message, discord.Color.red())
        logging.debug(log_message)
        await ctx.respond(embed=embeds.contra("25549895998", ctx.author.name, ctx.author.avatar.url), ephemeral=True)
        return

    user_id = user.id
    balance = get_balance(user_id)
    donation = get_user_donation_amount(user_id)
    log_message = (
        f"""Пользователь <@{ctx.author.id}> проверил статистику пользователя <@{user.id}>:
        `Баланс: {balance} {CURRENCY1}`
        `Благотворительность: {donation} {CURRENCY1}`""")
    await log_to_channel("/check", log_message, discord.Color.orange())
    logging.info(log_message)
    user_info = await bot.fetch_user(user_id)
    await ctx.respond(embed=embeds.check_stats(user_id, balance, donation, CURRENCY1, user_info.name, user_info.avatar.url, ctx.author.name, ctx.author.avatar.url), ephemeral=True)

class ConfirmTransferView(discord.ui.View):
    def __init__(self, sender_id, amount, comment,  mentioned_user_id):
        super().__init__()
        self.sender_id = sender_id
        self.amount = amount
        self.comment = comment
        self.mentioned_user_id = mentioned_user_id

    @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.sender_id:
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            # Здесь выполняется логика перевода
            update_balance(self.sender_id, -self.amount)
            update_balance(self.mentioned_user_id, self.amount)
            log_message = (f"Пользователь <@{interaction.user.id}> перевел `{self.amount} {CURRENCY1}` пользователю <@{self.mentioned_user_id}>. \n Комментарий к переводу: `{self.comment}`.")
            await log_to_channel("/transfer", log_message, discord.Color.green())
            logging.info(log_message)
            mentioned_user = await bot.fetch_user(self.mentioned_user_id)
            await mentioned_user.send(embed=embeds.transfer(f'Вы получили `{self.amount} {CURRENCY1}` от пользователя <@{self.sender_id}>. \n Комментарий к переводу: `{self.comment}`.', interaction.user.name, interaction.user.avatar.url, mentioned_user.name, mentioned_user.avatar.url))
            await interaction.followup.send(embed=embeds.default("Перевод", f'Перевод успешен! Вы перевели `{self.amount} {CURRENCY1}` <@{self.mentioned_user_id}> с комментарием к переводу `{self.comment}`.', interaction.user.name, interaction.user.avatar.url))
            # Прерываем выполнение функции после успешного подтверждения перевода
            return

    @discord.ui.button(label="❎", style=discord.ButtonStyle.red)
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.sender_id:
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            log_message = (f"Пользователь <@{interaction.user.id}> отменил перевод пользователю <@{self.mentioned_user_id}>")
            await log_to_channel("/transfer", log_message, discord.Color.red())
            logging.info(log_message)
            await interaction.followup.send(embed=embeds.default("Перевод", 'Перевод отменен.', interaction.user.name, interaction.user.avatar.url))
            # Прерываем выполнение функции после отмены перевода
            return


@bot.slash_command(name='transfer', description=f'Перевести {CURRENCY2} другому пользователю', guild_ids=GUILD_IDS)
async def transfer(ctx,
                   user: Option(discord.SlashCommandOptionType.mentionable, name="user", description="Укажите пользователя", required=True),
                   amount: Option(int, description="Сумма перевода", required=True, min_value=1),
                   comment: Option(str, description="Комментарий к переводу", required=False)):

    # Проверка на роль
    if isinstance(user, discord.Role):
        log_message = f"Пользователь <@{ctx.author.id}> указал роль вместо пользователя"
        await log_to_channel("/transfer", log_message, discord.Color.red())
        logging.debug(log_message)
        await ctx.respond(embed=embeds.contra("oralcumshot", ctx.author.name, ctx.author.avatar.url), ephemeral=True)
        return

        # Проверка на бота
    if user.bot:
        log_message = f"Пользователь <@{ctx.author.id}> указал бота вместо пользователя"
        await log_to_channel("/transfer", log_message, discord.Color.red())
        logging.debug(log_message)
        await ctx.respond(embed=embeds.contra("25549895998", ctx.author.name, ctx.author.avatar.url), ephemeral=True)
        return

    if comment  == None:
        comment = "Отсутствует"
    else:
        comment = comment

    sender_id = ctx.author.id
    mentioned_user_id = user.id
    sender_balance = get_balance(sender_id)
    title = "Перевод"
    if sender_balance < amount:
        log_message = (f"Пользователь <@{ctx.author.id}> не смог перевести `{amount} {CURRENCY1}` из-за недостатка средств")
        await log_to_channel("/transfer", log_message, discord.Color.red())
        await ctx.respond(embed=embeds.default(title, f'У вас недостаточно {CURRENCY1} для перевода!', ctx.author.name, ctx.author.avatar.url), ephemeral=True)
        return

    view = ConfirmTransferView(sender_id, amount, comment, mentioned_user_id)
    transfer_user = await bot.fetch_user(mentioned_user_id)
    await ctx.author.send(embed=embeds.transfer(f"Вы собираетесь перевести `{amount} {CURRENCY1}` пользователю <@{mentioned_user_id}> с комментарием к переводу: `{comment}`. Подтвердите/Отмените перевод, нажав на кнопки ниже.", transfer_user.name, transfer_user.avatar.url, ctx.author.name, ctx.author.avatar.url), view=view)
    await ctx.respond(embed=embeds.default(title, "Сообщение о подтверждении перевода было отправлено в ЛС", ctx.author.name, ctx.author.avatar.url), ephemeral=True)

@bot.slash_command(name='charity', description=f'Закинуть {CURRENCY2} в благотворительный фонд', guild_ids=GUILD_IDS)
async def donate(ctx, amount: Option(int, description="Сумма пожертвования", required=True, min_value=1)):
    deduct_donation(ctx.author.id, amount)
    update_donation_amount(ctx.author.id, amount)
    log_message = f"Пользователь <@{ctx.author.id}> сделал пожертвование в размере `{amount} {CURRENCY1}`"
    await log_to_channel("/donate", log_message, discord.Color.orange())
    logging.info(log_message)
    await ctx.respond(embed=embeds.default("Благотворительность", f'Вы сделали пожертвование в размере `{amount} {CURRENCY1}`. Спасибо огромное!', ctx.author.name, ctx.author.avatar.url), ephemeral=True)

@bot.slash_command(name='daily', description='Получить ежедневный бонус', guild_ids=GUILD_IDS)
async def daily(ctx):
    user_id = ctx.author.id
    if daily_bonus(user_id):
        log_message = f"Пользователь <@{ctx.author.id}> получил ежедневный бонус в `100 {CURRENCY1}`"
        await log_to_channel("/daily", log_message, discord.Color.orange())
        logging.info(log_message)
        await ctx.respond(embed=embeds.default("Ежедневка", f'Вы получили ежедневный бонус в `100 {CURRENCY1}`!', ctx.author.name, ctx.author.avatar.url), ephemeral=True)
    else:
        log_message = (f"Пользователь <@{ctx.author.id}> уже получал ежедневный бонус сегодня")
        await log_to_channel("/daily", log_message, discord.Color.orange())
        logging.info(log_message)
        await ctx.respond(embed=embeds.default("Ежедневка", 'Вы уже получали ежедневный бонус сегодня!', ctx.author.name, ctx.author.avatar.url), ephemeral=True)

@bot.slash_command(name='leaders', description=f'Показать топ-10 магнатов {CURRENCY1}', guild_ids=GUILD_IDS)
async def leaders(ctx):
    log_message = f"Пользователь <@{ctx.author.id}> посмотрел таблицу лидеров по кол-ву {CURRENCY1}"
    await log_to_channel("/leaders", log_message, discord.Color.orange())
    logging.info(log_message)
    leaders = get_leaders()
    leaderboard = discord.Embed(title="Топ-10 пользователей", color=discord.Color.blue())
    for rank, (user_id, balance) in enumerate(leaders, start=1):
        user = await bot.fetch_user(user_id)
        # Добавляем пользователя в встраиваемое сообщение с упоминанием
        leaderboard.add_field(name=f"{rank}. {user.name}", value=f"""
         {user.mention}: `{balance} {CURRENCY1}`""", inline=False)
    await ctx.respond(embed=leaderboard, ephemeral=True)

@bot.slash_command(name='donation_leaders', description='Показать топ-10 пользователей по сумме пожертвований', guild_ids=GUILD_IDS)
async def donation_leaders(ctx):
    log_message = f"Пользователь <@{ctx.author.id}> посмотрел таблицу лидеров по кол-ву {CURRENCY1}, закинутых в благотворительный фонд"
    await log_to_channel("/donation_leaders", log_message, discord.Color.orange())
    logging.info(log_message)
    leaders = get_donation_leaders()
    leaderboard = discord.Embed(title="Топ-10 пожертвователей", color=discord.Color.blue())
    for rank, (user_id, total_donation) in enumerate(leaders, start=1):
        user = await bot.fetch_user(user_id)
        leaderboard.add_field(name=f"{rank}. <@!{user}>", value=f"""
                 {user.mention}: `{total_donation} {CURRENCY1}`""", inline=False)

    await ctx.respond(embed=leaderboard, ephemeral=True)

@bot.slash_command(name='slots', description='Кручишь слоты в казино', guild_ids=GUILD_IDS)
async def __slots(
        ctx,
        bet: Option(int, description="Сколько вы готовы поставить", required=True, min_value=1),
        number_of_games: Option(int, description="Сколько раз готовы сыграть", required=False, min_value=1, max_value=3, default=1)
        ):
    user_id = ctx.author.id
    current_balance = get_balance(user_id)
    total_cost = bet * number_of_games
    # Если пользователь впервые входит в игру, установите ему начальный баланс
    if current_balance == 0:
        set_initial_balance(user_id)
        current_balance = 500
    if current_balance < total_cost:
        await ctx.respond(f'У вас недостаточно {CURRENCY1} для этой ставки!', ephemeral=True)
        log_message = f"Пользователь <@{ctx.author.id}> не смог играть в слоты из-за недостатка средств"
        await log_to_channel("/slots", log_message, discord.Color.red())
        logging.info(log_message)
        return
    # Проверка входных данных
    if bet is None or bet <= 0:
        await ctx.respond('Укажите корректную ставку, на которую хотите играть!', ephemeral=True)
    else:
        data = await Casino(number_of_games).start()
        win = True if data.multiplier > 0 else False
        to_footer = "Emoji\tCount\tPoints\n"

        for emoji, count in data.emoji_stats.items():
            to_footer += f"{ScoreUnicode[emoji].value}\t\t:\t" \
                         f"{count}\t:\t" \
                         f"{int(ScoreChances[emoji]) // 2}\n"

        win = True if data.multiplier > 0 else False

        # Определяем, какой баланс обновить в зависимости от результата
        if win:
            # Если пользователь выиграл, увеличиваем его баланс на выигрышную сумму
            amount = bet * data.multiplier * number_of_games  # Учитываем количество игр
        else:
            # Если пользователь проиграл, уменьшаем его баланс на сумму ставки
            amount = -bet * number_of_games  # Учитываем количество игр

        # Обновляем баланс пользователя
        update_balance(user_id, amount)

        embed = discord.Embed(
            title=f'Общее количество очков: {data.total_points}. ' + (
                f'Вы выиграли `{bet * data.multiplier * number_of_games} {CURRENCY1}`.' if win
                else f'Вы проиграли `{bet * number_of_games} {CURRENCY1}`.'
            ),
            description="\n".join(data.board),
            color=discord.Color.green() if win else discord.Color.red()
        ).set_footer(
            text=to_footer,
            icon_url=ctx.author.avatar.url
        ).add_field(
            name=f'Для коэффициента x2 вам нужно набрать `<= {data.required_points[1]}` '
                 f'очков, чтобы проиграть `>= {data.required_points[0]}.`',
            value=f'**У тебя есть:** `{data.total_points}`'
        )
        log_message = f"Пользователь <@{ctx.author.id}> играл в слоты на `{amount} {CURRENCY1}`, выиграл: `{win}`"
        if win:
            color = discord.Color.green()
        else:
            color = discord.Color.red()
        await log_to_channel("/slots", log_message, color)
        logging.info(log_message)
        await ctx.respond(embed=embed, ephemeral=True)

# запускаем бота
bot.run(TOKEN)
