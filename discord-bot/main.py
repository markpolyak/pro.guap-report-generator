import json
import os

import discord
from discord.ext import commands
import requests, shutil

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents)

DISCORD_TOKEN = os.environ['TOKEN_BOT']
REPORT_GENERATOR_HOST = f"http://{os.environ['REPORT_GENERATOR_HOST']}"

@bot.command()
async def helps(ctx):
    await ctx.send(
                    '''
                   Команды бота:        
                   auth login pass # авторизация 
                   semesters user-id # получение списка семестров по user-id
                   subs_id user-id semester_id # получение списка предметов по semester_id
                   subs_name user-id semester_name # получение списка предметов по semester_name
                   tasks_id user-id subject_id # получение списка задач по subject_id
                   tasks_name user-id subject_name # получение списка задач по subject_name
                   rep_id user-id task_id #получение файла отчета по task_id
                   rep_name user-id task_name #получение файла отчета по task_name
                   '''
                   )

@bot.command()
async def auth(ctx, arg1, arg2):
    req = requests.post(f'{REPORT_GENERATOR_HOST}/authorize',json={
            "auth_form": {
            "login_pass": {
            "login": arg1,
            "password": arg2
    }
    }
    })
    gs =json.loads(req.text)
    await ctx.send('Ваш user-id: ' + gs['Authorize'])

@bot.command()
async def semesters(ctx, arg):
    req = requests.get(f'{REPORT_GENERATOR_HOST}/get-all-semesters',
                       headers= {'user-id':arg})
    await ctx.send(req.text)

@bot.command()
async def subs_id(ctx, arg1, arg2):
        req = requests.get(f'{REPORT_GENERATOR_HOST}/get-subjects',
                           headers={'user-id': arg1},
                           params={'semester_id': arg2})
        await ctx.send(req.json())

@bot.command()
async def subs_name(ctx, arg1, arg2):
        req = requests.get(f'{REPORT_GENERATOR_HOST}/get-subjects',
                           headers={'user-id': arg1},
                           params={'semester_name': arg2})
        await ctx.send(req.json())

@bot.command()
async def tasks_id(ctx, arg1, arg2):
    req = requests.get(f'{REPORT_GENERATOR_HOST}/get-tasks',
                       headers={'user-id': arg1},
                       params={'subject_id': arg2})
    await ctx.send(req.json())

@bot.command()
async def tasks_name(ctx, arg1, arg2):
    req = requests.get(f'{REPORT_GENERATOR_HOST}/get-tasks',
                       headers={'user-id': arg1},
                       params={'subject_name': arg2})
    await ctx.send(req.json())

@bot.command()
async def rep_id(ctx, arg1, arg2):
    req = requests.get(
        f'{REPORT_GENERATOR_HOST}/get-task-report',
        headers={'user-id': arg1},
        params={'task_id': arg2},
        stream=True,
    )
    with open('1337.doc', 'wb') as f:
        shutil.copyfileobj(req.raw, f)
    await ctx.send(file=discord.File('1337.doc'))

@bot.command()
async def rep_name(ctx, arg1, arg2):
    req = requests.get(
        f'{REPORT_GENERATOR_HOST}/get-task-report',
        headers={'user-id': arg1},
        params={'task_name': arg2},
        stream=True,
    )
    with open('Отчет.doc', 'wb') as f:
        shutil.copyfileobj(req.raw, f)
    await ctx.send(file=discord.File('Отчет.doc'))

bot.run(DISCORD_TOKEN)
