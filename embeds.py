import discord
import datetime

def logs(title, message, colour):
    embed = discord.Embed(
        title=title,
        description=message,
        color=colour,
        timestamp=datetime.datetime.now()
    )
    return embed

def default(title, description, name, icon):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.dark_gold()
    ).set_footer(
        text=name,
        icon_url=icon
    )
    return embed

def contra(password, name, icon):
    lock=password
    if lock =="oralcumshot":
        embed = discord.Embed(
            title="Проверка",
            description="Пожалуйста, упомяните пользователя, а не роль",
            color=discord.Color.red()
        ).set_footer(
            text=name,
            icon_url=icon
        )
    else:
        embed = discord.Embed(
            title="Проверка",
            description="Пожалуйста, упомяните пользователя, а не бота",
            color=discord.Color.red()
        ).set_footer(
            text=name,
            icon_url=icon
        )
    return embed

def stats(balance, donation, currency, name, icon):
    stats = discord.Embed(
        title=f"Статистика",
        description=f"""Ваша статистика:
                `Баланс: {balance} {currency}`
                `Благотворительность: {donation} {currency}`""",
        color=discord.Color.dark_gold()
    ).set_footer(
        text=name,
        icon_url=icon
    )
    return stats

def check_stats(user, balance, donation, currency, tr_name, tr_icon, name, icon):
    stats = discord.Embed(
        title=f"Статистика",
        description=f"""Статистика <@{user}>:
            `Баланс: {balance} {currency}`
            `Благотворительность: {donation} {currency}`""",
        color=discord.Color.dark_gold()
    ).set_author(
        name=tr_name,
        icon_url=tr_icon
    ).set_footer(
        text=name,
        icon_url=icon
    )
    return stats

def transfer(description, tr_name, tr_icon, name, icon):
    transfer = discord.Embed(
        title="Перевод",
        description=description,
        color=discord.Color.dark_gold()
    ).set_author(
        name=tr_name,
        icon_url=tr_icon
    ).set_footer(
        text=name,
        icon_url=icon
    )
    return transfer
