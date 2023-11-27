from django.core.management.base import BaseCommand
import asyncio
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from typing import List, Union
from aiogram import types
from aiogram.dispatcher import FSMContext


class Command(BaseCommand):
    help = 'Салон красоты'

    def handle(self, *args, **options):
        from aiogram import executor
        import bot.handlers
        from bot.loader import dp
        # from bot.utils import main_menu_buttons, main_menu_buttons_handle
    
        # class ClientMenuMiddleware(BaseMiddleware):
        #     async def on_pre_process_message(self, msg: types.Message, data: dict):
        #         if msg.text in main_menu_buttons:
        #             await FSMContext.get_state(msg.from_user.id).reset()
        #             await main_menu_buttons_handle(msg, msg.text)
                    
        
        # dp.middleware.setup(ClientMenuMiddleware())
        executor.start_polling(dp, skip_updates=False)