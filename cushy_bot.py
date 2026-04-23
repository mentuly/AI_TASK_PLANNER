import sys
from aiogram.fsm.context import FSMContext
import logging
import asyncio
from aiogram.fsm.state import State, StatesGroup
from enum import Enum
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import ( 
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    ReactionTypeEmoji
)
users = {}

class ChatAction(str, Enum):
    """
    This object represents bot actions.

    Choose one, depending on what the user is about to receive:

    - typing for text messages,
    - upload_photo for photos,
    - record_video or upload_video for videos,
    - record_voice or upload_voice for voice notes,
    - upload_document for general files,
    - choose_sticker for stickers,
    - find_location for location data,
    - record_video_note or upload_video_note for video notes.

    Source: https://core.telegram.org/bots/api#sendchataction
    """

    TYPING = "typing"
    UPLOAD_PHOTO = "upload_photo"
    RECORD_VIDEO = "record_video"
    UPLOAD_VIDEO = "upload_video"
    RECORD_VOICE = "record_voice"
    UPLOAD_VOICE = "upload_voice"
    UPLOAD_DOCUMENT = "upload_document"
    CHOOSE_STICKER = "choose_sticker"
    FIND_LOCATION = "find_location"
    RECORD_VIDEO_NOTE = "record_video_note"
    UPLOAD_VIDEO_NOTE = "upload_video_note"

fruits = {"apple" : {"name" : "apple",
                       "count" : 1,
                       "price" : 5},
          "kiwi" : {"name" : "kiwi",
                       "count" : 13,
                       "price" : 21},
          "banana" : {"name" : "banana",
                       "count" : 49,
                       "price" : 8},    
          "pineapple" : {"name" : "pineapple",
                           "count" : 7,
                           "price" : 35},
          "dragonfruit" : {"name" : "dragonfruit",
                           "count" : 3,
                           "price" : 100},
          "grape" : {"name" : "grape",
                           "count" : 45,
                           "price" : 25},
          "melon" : {"name" : "melon",
                           "count" : 3,
                           "price" : 43},
          "watermelon" : {"name" : "watermelon",
                           "count" : 3,
                           "price" : 35},
          "orange" : {"name" : "orange",
                           "count" : 3,
                           "price" : 5},
          "lemon" : {"name" : "lemon",
                           "count" : 3,
                           "price" : 9},
          "mango" : {"name" : "mango",
                           "count" : 3,
                           "price" : 89},
          "pear" : {"name" : "pear",
                           "count" : 3,
                           "price" : 10},
          "peach" : {"name" : "peach",
                           "count" : 70,
                           "price" : 11},
          "cherry" : {"name" : "cherry",
                           "count" : 115,
                           "price" : 6},
          "strawberry" : {"name" : "strawberry",
                           "count" : 125,
                           "price" : 6}
            }

vegetables = {"cucumber" : {"name" : "cucumber",
                            "count" : 76,
                            "price" : 11},
              "potato" : {"name" : "potato",
                          "count" : 156,
                          "price" : 3},
              "tomato" : {"name" : "tomato",
                       "count" : 56,
                       "price" : 4},    
              "carrot" : {"name" : "carrot",
                        "count" : 98,
                        "price" : 5},
              "cabbage" : {"name" : "cabbage",
                           "count" : 56,
                           "price" : 25},
              "broccoli" : {"name" : "broccoli",
                           "count" : 56,
                           "price" : 12},
              "garlic" : {"name" : "garlic",
                           "count" : 56,
                           "price" : 13},
              "onion" : {"name" : "onion",
                           "count" : 56,
                           "price" : 16},
              "sweet potato" : {"name" : "sweet potato",
                           "count" : 56,
                           "price" : 25},
              "corn" : {"name" : "corn",
                           "count" : 56,
                           "price" : 26},
              "chili pepper" : {"name" : "chili pepper",
                           "count" : 56,
                           "price" : 30},
              "mushroom" : {"name" : "mushroom",
                           "count" : 56,
                           "price" : 15}
            }

eggs = {  "chicken eggs" : {"name" : "chicken eggs",
                     "count" : 120,
                     "price" : 5},
          "quail eggs" : {"name" : "quail eggs",
                       "count" : 80,
                       "price" : 8}
            }

meat_and_sea = {  "bacon" : {"name" : "bacon",
                     "count" : 120,
                     "price" : 15},
          "mutton" : {"name" : "mutton",
                       "count" : 80,
                       "price" : 9},
          "shin" : {"name" : "shin",
                     "count" : 120,
                     "price" : 16},
          "steak" : {"name" : "steak",
                       "count" : 80,
                       "price" : 30},
          "shrimp" : {"name" : "shrimp",
                     "count" : 120,
                     "price" : 25},
          "oyster" : {"name" : "oyster",
                       "count" : 80,
                       "price" : 35}
            }

nuts = {  "peanut" : {"name" : "peanut",
                     "count" : 120,
                     "price" : 15},
          "hazelnut" : {"name" : "hazelnut",
                       "count" : 80,
                       "price" : 16},
          "coconut" : {"name" : "coconut",
                     "count" : 120,
                     "price" : 34}
        }

dairy_products = {
          "cheese" : {"name" : "cheese",
                     "count" : 120,
                     "price" : 20},
          "butter" : {"name" : "butter",
                       "count" : 80,
                       "price" : 19},
          "ice cream" : {"name" : "ice cream",
                     "count" : 120,
                     "price" : 25},
          "milk" : {"name" : "milk",
                       "count" : 80,
                       "price" : 8}
            }

sweets = {
          "ice cream" : {"name" : "ice cream",
                     "count" : 120,
                     "price" : 25},
          "bar of chocolate" : {"name" : "bar of chocolate",
                     "count" : 120,
                     "price" : 15},
          "candy" : {"name" : "candy",
                       "count" : 80,
                       "price" : 18},
          "lollipop" : {"name" : "lollipop",
                     "count" : 120,
                     "price" : 19},
          "donut" : {"name" : "donut",
                       "count" : 80,
                       "price" : 25},
          "cookies" : {"name" : "cookies",
                     "count" : 120,
                     "price" : 15},
          "cake" : {"name" : "cake",
                       "count" : 80,
                       "price" : 25},
          "pudding" : {"name" : "pudding",
                     "count" : 120,
                     "price" : 12},
          "honey" : {"name" : "honey",
                       "count" : 80,
                       "price" : 45},
          "pie" : {"name" : "pie",
                     "count" : 120,
                     "price" : 23}
            }

baking = {
          "waffles" : {"name" : "waffles",
                 "count" : 120,
                 "price" : 5},
          "pancakes" : {"name" : "pancakes",
                   "count" : 80,
                   "price" : 8},
          "toaster bread" : {"name" : "toaster bread",
                 "count" : 120,
                 "price" : 9},
          "croissant" : {"name" : "croissant",
                   "count" : 80,
                   "price" : 15},
          "loaf" : {"name" : "loaf",
                 "count" : 120,
                 "price" : 19},
          "pie" : {"name" : "pie",
                   "count" : 80,
                   "price" : 23},
          "cookies" : {"name" : "cookies",
                     "count" : 120,
                     "price" : 15},
          "donut" : {"name" : "donut",
                       "count" : 80,
                       "price" : 25},
          "cake" : {"name" : "cake",
                     "count" : 120,
                     "price" : 25}
            }

drinks = {"water" : {"name" : "water",
                     "count" : 76,
                     "price" : 10},
          "pepsi" : {"name" : "pepsi",
                       "count" : 156,
                       "price" : 30},
          "coca-cola" : {"name" : "coca-cola",
                       "count" : 56,
                       "price" : 30},    
          "sprite" : {"name" : "sprite",
                        "count" : 98,
                        "price" : 30},
          "fanta" : {"name" : "fanta",
                        "count" : 130,
                        "price" : 25},
          "juice" : {"name" : "juice",
                        "count" : 50,
                        "price" : 15},
          "milk" : {"name" : "milk",
                        "count" : 45,
                        "price" : 16}
            }

logging.basicConfig(level=logging.INFO)

class Registration(StatesGroup):
    name = State()
    age = State()

bot = Bot(token="6872249572:AAGXQKIMr4cp0PqFFHEcw-EruKOnOxE63jE")
Token="6872249572:AAGXQKIMr4cp0PqFFHEcw-EruKOnOxE63jE"
dp = Dispatcher()

async def send_typing_action(chat_id, duration=5):
    await bot.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(duration)

async def sand_typing_action(chat_id, duration=3):
    await bot.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(duration)

@dp.message(Command('start'))
async def command_start(message: Message):
    chat_id = message.chat.id
    await send_typing_action(chat_id)
    await message.react([ReactionTypeEmoji(emoji = "👍")])
    await message.answer(f"Hello! You are greeted by our bot, where you can purchase something from our range, but before that, you need to go through registration. If you agree, please press /registration.")

@dp.message(Command('stop'))
async def command_stop_shoping(message: Message):
    chat_id = message.chat.id
    await sand_typing_action(chat_id)
    await message.react([ReactionTypeEmoji(emoji = "❤")])
    await message.answer(f"You have ended your shopping!\nPress  /buy to start shopping again")

@dp.message(Command("registration"))
async def bot_register(message: types.Message, state: FSMContext):
    name = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"{message.from_user.first_name}")
            ],
            [
                KeyboardButton(text="Cancel registration.")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.react([ReactionTypeEmoji(emoji = "👍")])
    chat_id = message.chat.id
    await sand_typing_action(chat_id)
    await message.answer(f"Hi!\n"
                         f"Write your name for registration:",
                         reply_markup=name)
    await state.set_state(Registration.name)

@dp.message(Registration.name)
async def get_name (message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    phone = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Cancel registration.")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    chat_id = message.chat.id
    await sand_typing_action(chat_id)
    await message.answer(f"<b>{message.text}</b>, now send here your age.",
                         reply_markup=phone)
    await state.set_state(Registration.age)
     
@dp.message(Registration.age)
async def get_age(message: types.Message, state: FSMContext):
    answer = message.text
    user_id = message.from_user.id
    if answer.isnumeric():
        if int(answer) > 5 :
            if int(answer) < 150 :
                data = await state.update_data(age=answer)
                await state.clear()
                name = data.get('name')
                age = data.get('age')
                chat_id = message.chat.id
                await send_typing_action(chat_id)
                await message.answer(f"Registration succesfully ended.\n"
                                     f"Name: {name}\n"
                                     f"Age: {age}\n\n"
                                     f"To buy a product, please press /buy. Happy shopping! 😉"
                                     )
                users[user_id] = {"Name" : {name},
                                  "Age" : {age},
                                  "Balance" : 1500}
            else:
                chat_id = message.chat.id
                await sand_typing_action(chat_id)
                await message.answer(f'Write right age.')
        else:
            chat_id = message.chat.id
            await sand_typing_action(chat_id)
            await message.answer(f'Sorry you are to young.')
    else:
        chat_id = message.chat.id
        await sand_typing_action(chat_id)
        await message.answer(f'Write right age.')
            
@dp.message(Command("logging"))
async def loging(message: types.Message):
    user_id = message.from_user.id
    if user_id in users:
        chat_id = message.chat.id
        await sand_typing_action(chat_id)
        await message.answer("You are succesfully loged in.")
    else:
        chat_id = message.chat.id
        await sand_typing_action(chat_id)
        await message.answer("You don't have an account.")

@dp.message(Command('receive')) 
async def donate(message: types.Message): 
    user_id = message.from_user.id 

    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[ 
        [types.InlineKeyboardButton(text="100 UAH", callback_data="10_0")], 
        [types.InlineKeyboardButton(text="200 UAH", callback_data="20_0")], 
        [types.InlineKeyboardButton(text="300 UAH", callback_data="30_0")], 
        [types.InlineKeyboardButton(text="500 UAH", callback_data="50_0")], 
        [types.InlineKeyboardButton(text="1000 UAH", callback_data="100_0")], 
        [types.InlineKeyboardButton(text="2000 UAH", callback_data="200_0")], 
        ]) 


    await message.answer("Enter: How much money do you want to receive?", reply_markup=keyboard)  


@dp.callback_query(lambda query: query.data.startswith('10_')) 
async def UAH100(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    user = users.get(user_id) 
    balance = user.get("Balance") 
    balance += 100 
    user.update( {"Balance" : balance } )
    await callback_query.message.answer("You have receive 100 UAH to your balance") 
@dp.callback_query(lambda query: query.data.startswith('20_')) 
async def UAH200(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    user = users.get(user_id) 
    balance = user.get("Balance") 
    balance += 200 
    user.update( {"Balance" : balance } ) 
    await callback_query.message.answer("You have receive 200 UAH to your balance") 
@dp.callback_query(lambda query: query.data.startswith('30_')) 
async def UAH300(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    user = users.get(user_id) 
    balance = user.get("Balance") 
    balance += 300 
    user.update( {"Balance" : balance } ) 
    await callback_query.message.answer("You have receive 300 UAH to your balance") 
@dp.callback_query(lambda query: query.data.startswith('50_')) 
async def UAH500(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    user = users.get(user_id) 
    balance = user.get("Balance") 
    balance += 500 
    user.update( {"Balance" : balance } ) 
    await callback_query.message.answer("You have receive 500 UAH to your balance") 
@dp.callback_query(lambda query: query.data.startswith('100_')) 
async def UAH1000(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    user = users.get(user_id) 
    balance = user.get("Balance") 
    balance += 1000 
    user.update( {"Balance" : balance } ) 
    await callback_query.message.answer("You have receive 1000 UAH to your balance") 
@dp.callback_query(lambda query: query.data.startswith('200_')) 
async def UAH2000(callback_query: types.CallbackQuery): 
    user_id = callback_query.from_user.id 
    user = users.get(user_id) 
    balance = user.get("Balance") 
    balance += 2000 
    user.update( {"Balance" : balance } ) 
    await callback_query.message.answer("You have receive 2000 UAH to your balance")

@dp.message(Command("buy"))
async def show_shop(message: Message, state: FSMContext) -> None:
    await state.set_state()
    chat_id = message.chat.id
    await sand_typing_action(chat_id)     
    await message.answer(
         f"Choose what you want:\n",
         reply_markup=ReplyKeyboardMarkup( 
             keyboard=[ 
                 [ 
                     KeyboardButton(text="/buy"), 
                     KeyboardButton(text="/receive"),
                     KeyboardButton(text="/logging"),
                     KeyboardButton(text="/stop"),
                     KeyboardButton(text="/start")
                 ] 
             ], 
            resize_keyboard=True, 
         ), 
     )
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [types.InlineKeyboardButton(text="Fruits🍎", callback_data="bua_fruits")],
        [types.InlineKeyboardButton(text="Vegetables🥗", callback_data="bub_vegetables")],
        [types.InlineKeyboardButton(text="Eggs🥚", callback_data="buc_eggs")],
        [types.InlineKeyboardButton(text="Meat and sea ​products 🥩", callback_data="bud_meat")],
        [types.InlineKeyboardButton(text="Nuts🌰", callback_data="bue_nuts")],
        [types.InlineKeyboardButton(text="Dairy products🥛", callback_data="buf_dairy_products")],
        [types.InlineKeyboardButton(text="Sweets🧁", callback_data="bug_sweets")],
        [types.InlineKeyboardButton(text="baking🥨", callback_data="bug_sweets")],        
        [types.InlineKeyboardButton(text="Drinks🥤", callback_data="buh_drinks")]
    ])

    await message.reply(reply_markup=keyboard)


@dp.callback_query(lambda query: query.data.startswith('bua_'))
async def fruits_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    balance = users.get(user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
            [types.InlineKeyboardButton(text="🍎Apple - 5 UAH", callback_data="bui_apple")],
            [types.InlineKeyboardButton(text="🍌Banana - 8 UAH", callback_data="bui_banana")],
            [types.InlineKeyboardButton(text="🍍Pineapple - 35 UAH", callback_data="bui_pineapple")],
            [types.InlineKeyboardButton(text="🥝Kiwi - 21 UAH", callback_data="bui_kiwi")],
            [types.InlineKeyboardButton(text="💮Dragonfruit - 100 UAH", callback_data="bui_dragonfruit")],
            [types.InlineKeyboardButton(text="🍇Grape - 25 UAH", callback_data="bui_grape")],
            [types.InlineKeyboardButton(text="🍈Melon - 43 UAH", callback_data="bui_melon")],
            [types.InlineKeyboardButton(text="🍉Watermelon - 35 UAH", callback_data="bui_watermelon")],
            [types.InlineKeyboardButton(text="🍊Orange - 5 UAH", callback_data="bui_orange")],
            [types.InlineKeyboardButton(text="🍋lemon - 9 UAH", callback_data="bui_lemon")],
            [types.InlineKeyboardButton(text="🥭Mango - 89 UAH", callback_data="bui_mango")],
            [types.InlineKeyboardButton(text="🍐Pear - 10 UAH", callback_data="bui_pear")],
            [types.InlineKeyboardButton(text="🍑Peach - 11 UAH", callback_data="bui_peach")],
            [types.InlineKeyboardButton(text="🍒Cherry - 6 UAH", callback_data="bui_cherry")],
            [types.InlineKeyboardButton(text="🍓Strawberry - 6 UAH", callback_data="bui_strawberry")]
        ])
    balance_message = f"Your Balance: {balance.get('Balance')} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)


@dp.callback_query(lambda query: query.data.startswith('bub_'))
async def vegatable_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    balance = users.get(user_id) 
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🥒Cucumber - 11 UAH", callback_data="buj_cucumber")],
        [types.InlineKeyboardButton(text="🥔Potato - 3 UAH", callback_data="buj_potato")],
        [types.InlineKeyboardButton(text="🍅Tomato - 4 UAH", callback_data="buj_tomato")],
        [types.InlineKeyboardButton(text="🥕Carrot - 5 UAH", callback_data="buj_carrot")],
        [types.InlineKeyboardButton(text="🥬Cabbage - 25 UAH", callback_data="buj_cabbage")],
        [types.InlineKeyboardButton(text="🥦Broccoli - 12 UAH", callback_data="buj_broccoli")],
        [types.InlineKeyboardButton(text="🧄Garlic - 13 UAH", callback_data="buj_garlic")],
        [types.InlineKeyboardButton(text="🧅Onion - 16 UAH", callback_data="buj_onion")],
        [types.InlineKeyboardButton(text="🍠Sweet potat - 25 UAH", callback_data="buj_sweet potato")],
        [types.InlineKeyboardButton(text="🌽Corn - 26 UAH", callback_data="buj_corn")],
        [types.InlineKeyboardButton(text="🌶Chili pepper - 30 UAH", callback_data="buj_chili pepper")],
        [types.InlineKeyboardButton(text="🍄Mushroom - 15 UAH", callback_data="buj_mushroom")]
    ])
    balance_message = f"Your Balance: {balance.get('Balance')} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('buc_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🥚Chicken eggs - 5 UAH", callback_data="buk_chicken eggs")],
        [types.InlineKeyboardButton(text="🪺Quail eggs - 8 UAH", callback_data="buk_quail eggs")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('bud_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🥓Bacon - 15 UAH", callback_data="bul_bacon")],
        [types.InlineKeyboardButton(text="🍖Mutton - 9 UAH", callback_data="bul_mutton")],
        [types.InlineKeyboardButton(text="🍗Shin - 16 UAH", callback_data="bul_shin")],
        [types.InlineKeyboardButton(text="🥩Steak - 30 UAH", callback_data="bul_steak")],
        [types.InlineKeyboardButton(text="🍤Shrimp - 25 UAH", callback_data="bul_shrimp")],
        [types.InlineKeyboardButton(text="🦪Oyster - 35 UAH", callback_data="bul_oyster")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('bue_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🥜Peanut - 15 UAH", callback_data="bum_peanut")],
        [types.InlineKeyboardButton(text="🌰Hazelnut - 17 UAH", callback_data="bum_hazelnut")],
        [types.InlineKeyboardButton(text="🥥Coconut - 34 UAH", callback_data="bum_coconut")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('buf_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🧀Cheese - 20 UAH", callback_data="bun_cheese")],
        [types.InlineKeyboardButton(text="🧈Butter - 19 UAH", callback_data="bun_butter")],
        [types.InlineKeyboardButton(text="🍦Ice cream - 25 UAH", callback_data="bun_ice cream")],
        [types.InlineKeyboardButton(text="🥛Milk - 8 UAH", callback_data="bun_milk")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('bug_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🍦Ice cream - 25 UAH", callback_data="buo_ice cream")],
        [types.InlineKeyboardButton(text="🍫Bar of chocolate - 15 UAH", callback_data="buo_bar of chocolate")],
        [types.InlineKeyboardButton(text="🍬Candy - 18 UAH", callback_data="buo_candy")],
        [types.InlineKeyboardButton(text="🍭Lollipop - 19 UAH", callback_data="buo_lollipop")],
        [types.InlineKeyboardButton(text="🍩Donut - 25 UAH", callback_data="buo_donut")],
        [types.InlineKeyboardButton(text="🍪Cookies - 15 UAH", callback_data="buo_cookies")],
        [types.InlineKeyboardButton(text="🍰Cake - 25 UAH", callback_data="buo_cake")],
        [types.InlineKeyboardButton(text="🍮Pudding - 12 UAH", callback_data="buo_pudding")],
        [types.InlineKeyboardButton(text="🍯Honey - 45 UAH", callback_data="buo_honey")],
        [types.InlineKeyboardButton(text="🥧Pie - 23 UAH", callback_data="buo_")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('bup_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🧇Waffles - 5 UAH", callback_data="bur_waffles")],
        [types.InlineKeyboardButton(text="🥞Pancakes - 8 UAH", callback_data="bur_pancakes")],
        [types.InlineKeyboardButton(text="🍞Toaster bread - 9 UAH", callback_data="bur_toaster bread")],
        [types.InlineKeyboardButton(text="🥐Croissant - 15 UAH", callback_data="bur_croissant")],
        [types.InlineKeyboardButton(text="🥖Loaf - 19 UAH", callback_data="bur_loaf")],
        [types.InlineKeyboardButton(text="🥮Pie - 23 UAH", callback_data="bur_pie")],
        [types.InlineKeyboardButton(text="🍪Cookies - 15 UAH", callback_data="bur_cookies")],
        [types.InlineKeyboardButton(text="🍩Donut - 25 UAH", callback_data="bur_donut")],
        [types.InlineKeyboardButton(text="🍰Cake - 25 UAH", callback_data="bur_cake")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('buh_'))
async def drinks_products(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = users.get(user_id)
    balance = user.get("Balance")
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text="🧊Water - 10 UAH", callback_data="buq_water")],
        [types.InlineKeyboardButton(text="🥤Pepsi - 30 UAH", callback_data="buq_pepsi")],
        [types.InlineKeyboardButton(text="🥤Coca-Cola - 30 UAH", callback_data="buq_coca-cola")],
        [types.InlineKeyboardButton(text="🥤Sprite - 30 UAH", callback_data="buq_sprite")],
        [types.InlineKeyboardButton(text="🥤Fanta - 25 UAH", callback_data="buq_fanta")],
        [types.InlineKeyboardButton(text="🧃Juice - 15 UAH", callback_data="buq_juice")],
        [types.InlineKeyboardButton(text="🍶Milk - 16 UAH", callback_data="buq_milk")]
    ])
    balance_message = f"Your Balance: {balance} UAH."
    await callback_query.message.answer(f"Choose Product:\n{balance_message}", reply_markup=keyboard)

@dp.callback_query(lambda query: query.data.startswith('bui_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in fruits:
        product = fruits.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('buj_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in vegetables:
        product = vegetables.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('buk_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in eggs:
        product = eggs.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('bul_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in meat_and_sea:
        product = meat_and_sea.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('bum_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in nuts:
        product = nuts.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('bun_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in dairy_products:
        product = dairy_products.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('buo_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in sweets:
        product = sweets.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('bur_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in baking:
        product = baking.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

@dp.callback_query(lambda query: query.data.startswith('buq_'))
async def process_buy(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    item = callback_query.data.split('_')[1]
    user = users.get(user_id)
    balance = user.get("Balance")
    if item in drinks:
        product = drinks.get(item)
        price = product.get("price")
        count = product.get("count")

        if count > 0:
            if balance >= price:
                balance -= price
                user.update( {"Balance" : balance } )
                logging.info(f"User {user.get('Name')} available balance is {balance} ")
                balance_message = f"Your Balance: {balance} UAH."
                await bot.send_message(user_id, f"You bought {item.capitalize()}.\n{price} UAH were withdrawn from your balance. And you can press /stop if you bought everything you wanted. \nYou have : {balance_message}")
                int(count) - 1
            else:
                await bot.send_message(user_id, "You don't have enough money, please press /receive to have more.")
    else:
        await callback_query.message.answer(f"Sorry, we don't have {item} on our stock")

async def main() -> None:
    bot = Bot(Token, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
