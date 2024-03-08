import discord
from discord.ext import commands
from discord import Option
from database import create_table, create_daily_bonus_table, create_donations_table
from database import get_balance, update_balance, set_initial_balance, daily_bonus, get_leaders, update_donation_amount, deduct_donation, get_donation_leaders

from enums import (
    ScoreChances,
    ScoreUnicode,
)
from casino import (
    Casino,
)

create_table()
create_daily_bonus_table()
create_donations_table()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
	print(f'{bot.user} запущен и готов к работе!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.slash_command(name='balance', description='Проверь свой баланс монет', guild_ids=[1058779670583197756, 1213493135401947136])
async def balance(ctx):
    user_id = ctx.author.id
    current_balance = get_balance(user_id)
    await ctx.respond(f'Твой текущий баланс: {current_balance} монет.')

@bot.slash_command(name='transfer', description='Перевести деньги другому пользователю', guild_ids=[1058779670583197756, 1213493135401947136])
async def transfer(ctx, user_mention: Option(str, description="Укажите пользователя на которого будет произведен перевод", required=True), amount: Option(int, description="Сумма перевода", required=True, min_value=1)):
    sender_id = ctx.author.id
    # Извлекаем ID пользователя из упоминания
    mentioned_user_id = int(user_mention.strip('<@!>'))
    # Проверяем, достаточно ли средств у отправителя
    sender_balance = get_balance(sender_id)
    if sender_balance < amount:
        await ctx.respond('У вас недостаточно средств для перевода!')
        return

    # Обновляем баланс отправителя
    update_balance(sender_id, -amount)
    # Обновляем баланс получателя
    update_balance(mentioned_user_id, amount)

    await ctx.respond(f'Перевод успешен! Вы перевели {amount} монет пользователю <@{mentioned_user_id}>.')


@bot.slash_command(name='donate', description='Закинуть деньги в благотворительный фонд',
                   guild_ids=[1058779670583197756, 1213493135401947136])
async def donate(ctx, amount: Option(int, description="Сумма пожертвования", required=True, min_value=1)):
    # Сначала списываем сумму пожертвования из баланса пользователя
    deduct_donation(ctx.author.id, amount)
    # Теперь обновляем сумму пожертвования в благотворительном фонде
    update_donation_amount(ctx.author.id, amount)
    await ctx.respond(f'Вы сделали пожертвование в размере {amount}  монет. Спасибо огромное!')

@bot.slash_command(name='leaders', description='Показать топ-10 пользователей', guild_ids=[1058779670583197756, 1213493135401947136])
async def leaders(ctx):
    leaders = get_leaders()
    leaderboard = discord.Embed(title="Топ-10 пользователей", color=discord.Color.blue())
    for rank, (user_id, balance) in enumerate(leaders, start=1):
        # Получаем объект пользователя по ID
        user = await bot.fetch_user(user_id)
        # Добавляем пользователя в встраиваемое сообщение с упоминанием
        leaderboard.add_field(name=f"{rank}. {user.name}", value=f"Баланс: {balance} монет", inline=False)
    await ctx.respond(embed=leaderboard)

@bot.slash_command(name='donation_leaders', description='Показать топ-10 пользователей по сумме пожертвований', guild_ids=[1213493135401947136])
async def donation_leaders(ctx):
    leaders = get_donation_leaders()

    leaderboard = discord.Embed(title="Топ-10 пожертвователей", color=discord.Color.blue())
    for rank, (user_id, total_donation) in enumerate(leaders, start=1):
        user = await bot.fetch_user(user_id)
        leaderboard.add_field(name=f"{rank}. {user.name}", value=f"Сумма пожертвований: {total_donation} монет", inline=False)

    await ctx.respond(embed=leaderboard)

@bot.slash_command(name='daily', description='Получить ежедневный бонус', guild_ids=[1058779670583197756, 1213493135401947136])
async def daily(ctx):
    user_id = ctx.author.id
    if daily_bonus(user_id):
        await ctx.respond('Вы получили ежедневный бонус в 100 монет!')
    else:
        await ctx.respond('Вы уже получали ежедневный бонус сегодня!')

@bot.slash_command(name='slots', description='Кручишь слоты в казино', guild_ids=[1058779670583197756, 1213493135401947136])
async def __slots(
        ctx,
        bet: Option(int, description="Сколько вы готовы поставить", required=True, min_value=1),
        number_of_games: Option(int, description="Сколько раз готовы сыграть", required=False, min_value=1, default=1)
        ):
    user_id = ctx.author.id
    current_balance = get_balance(user_id)
    # Если пользователь впервые входит в игру, установите ему начальный баланс
    if current_balance == 0:
        set_initial_balance(user_id)
        current_balance = 500

    if bet > current_balance:
        await ctx.respond('У вас недостаточно монет для этой ставки!')
        return
    # Проверка входных данных
    if bet is None or bet <= 0:
        await ctx.respond('Укажите корректную ставку, на которую хотите играть!')
    elif not 1 <= number_of_games <= 3:
        await ctx.respond('Вы не можете играть в более трех игр и меньше одной!')
    else:
        # Здесь должна быть логика вашей игры, например, вызов функции Casino(number_of_games).start()
        # Предположим, что это уже реализовано и результаты хранятся в переменной data
        data = await Casino(number_of_games).start() # Пример вызова, замените на реальную логику
        win = True if data.multiplier > 0 else False
        to_footer = "Emoji\tCount\tPoints\n"

        for emoji, count in data.emoji_stats.items():
            # Создание статистики эмодзи в подвале
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
                f'Вы выиграли `{bet * data.multiplier * number_of_games}` монет.' if win
                else f'Вы проиграли `{bet * number_of_games}` монет.'
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
        await ctx.respond(embed=embed)

# запускаем бота
bot.run('Ваш токен здесь')
