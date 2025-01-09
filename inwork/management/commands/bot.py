import asyncio
from typing import List, Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from django.core.management.base import BaseCommand

from bot.utils.schedule import on_startup
from aiogram import executor
from bot import handlers
from bot.loader import dp


class Command(BaseCommand):
    help = 'Салон красоты'

    def handle(self, *args, **options):
        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
        # executor.start_polling(dp, skip_updates=False)
