import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pandas as pd
from joblib import load
from preprocess import synergy, add_heroes_attributes


A_team = ['hero_1_A', 'hero_2_A', 'hero_3_A', 'hero_4_A', 'hero_5_A', 'hero_6_A']
B_team = ['hero_1_B', 'hero_2_B', 'hero_3_B', 'hero_4_B', 'hero_5_B', 'hero_6_B']
heroes_stats_df = pd.read_csv('data/heroes_stats.csv')
heroes = [x.lower() for x in heroes_stats_df['localized_name']]
scaler = load('data/joblib/scaler.joblib')

bot = Bot(token='')
dp = Dispatcher()
router = Router()
dp.include_router(router)

def predict(heroes_A, heroes_B):
    test_match = pd.read_csv('data/blank_sample.csv')
    for i in range(1, 7):
        test_match[f'hero_{i}_A'] = heroes_A[i - 1]
    for i in range(1, 7):
        test_match[f'hero_{i}_B'] = heroes_B[i - 1]

    test_match['A'] = test_match[A_team].values.tolist()
    test_match['B'] = test_match[B_team].values.tolist()
    for ch in ('A', 'B'):
        for i in range(1, 7):
            test_match.drop(f'hero_{i}_{ch}', axis=1, inplace=True)
            
    test_match['A_synergy'] = test_match['A'].apply(synergy)
    test_match['B_synergy'] = test_match['B'].apply(synergy)

    test_match[A_team] = test_match['A'].tolist()
    test_match[B_team] = test_match['B'].tolist()
    test_match.drop(['A', 'B'], axis=1, inplace=True)

    for hero in heroes:
        test_match[hero] = 0
        test_match[hero] -= (test_match[A_team] == hero).any(axis=1)
        test_match[hero] += (test_match[B_team] == hero).any(axis=1)

    for ch in ('A', 'B'):
        for i in range(1, 7):
            test_match.drop(f'hero_{i}_{ch}', axis=1, inplace=True)

    for ch in ('A', 'B'):
        for col in heroes_stats_df.columns[1:]:
            test_match[f'{ch}_total_{col}'] = 0

    add_heroes_attributes(test_match)
    
    logreg = load('data/joblib/logistic_regression_model.joblib')
    test_match_scaled = scaler.transform(test_match)
    pred_class = logreg.predict(test_match_scaled)
    probability = logreg.predict_proba(test_match_scaled) 

    return pred_class, probability

# MESSAGE FOR COMMAND /start
@router.message(Command('start'))
async def start_command(message: types.Message):
    user_id = message.chat.id
    await message.answer('Deadlock team win prediction, based on teams picks.', reply_markup=get_predict_new_keyboard(user_id))

@router.message(Command('predict'))
async def predict_command(message: types.Message):
    user_id = message.chat.id
    await bot.send_message(user_id, 'Enter 1 amber hero: ', reply_markup=get_cancel_keyboard(user_id))
    users_picks[user_id] = []

# KEYBOARD FOR START
def get_predict_edit_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Predict', callback_data='predict_edit'))
    return builder.as_markup()

# KEYBOARD FOR START
def get_predict_new_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='New prediction', callback_data='predict_new'))
    return builder.as_markup()

# MESSAGE PICKS
@router.callback_query(F.data == 'predict_edit')
async def predict_message_edit(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    await bot.edit_message_text('Enter 1 amber hero: ',chat_id=user_id, message_id=callback_query.message.message_id, 
                                reply_markup=get_cancel_keyboard(user_id))
    users_picks[user_id] = []

# MESSAGE PICKS
@router.callback_query(F.data == 'predict_new')
async def predict_message_new(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    await bot.send_message(user_id, 'Enter 1 amber hero: ', reply_markup=get_cancel_keyboard(user_id))
    users_picks[user_id] = []
    
users_picks = {}

# KEYBOARD FOR START
def get_cancel_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    return builder.as_markup()

@router.callback_query(F.data == 'cancel')
async def cancel_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    users_picks.pop(user_id, None)
    await bot.edit_message_text('Prediction canceled.',chat_id=user_id, message_id=callback_query.message.message_id,
                                reply_markup=get_predict_edit_keyboard(user_id))

# MESSAGE FOR HERO PICK
@router.message(F.chat.id.in_(users_picks.keys()))
async def get_picks(message: types.Message):
    user_id = message.chat.id
    hero = message.text.lower().strip()

    if hero not in heroes:
        await bot.send_message(user_id, "Invalid hero name. Please enter a valid hero.")
        return
    elif hero in users_picks[user_id]:
        await bot.send_message(user_id, "Hero already used. Please enter another hero.")
        return
    
    users_picks[user_id].append(hero)

    if len(users_picks[user_id]) < 12:
        if len(users_picks[user_id]) < 6:
            await bot.send_message(user_id,f'Enter {len(users_picks[user_id]) + 1} hero amber: ', reply_markup=get_cancel_keyboard(user_id))
        else:
            await bot.send_message(user_id, f'Enter {-5 + len(users_picks[user_id])} hero sapphire: ', reply_markup=get_cancel_keyboard(user_id))

    elif len(users_picks[user_id]) == 12:
        heroes_A = users_picks[user_id][:6]
        heroes_B = users_picks[user_id][6:]

        await bot.send_message(user_id, f'The Amber Hand: {', '.join([x.capitalize() for x in heroes_A])}')
        await bot.send_message(user_id, f'The Sapphire Flame: {', '.join([x.capitalize() for x in heroes_B])}')

        await bot.send_message(user_id, 'Predicting the winner...')
        pred_class, probability = predict(heroes_A, heroes_B)
        await bot.edit_message_text(f'Predicted winner: {'The Amber Hand' if pred_class == 0 else 'The Sapphire Flame'} {probability[0][pred_class][0] * 100:.1f}%', 
                                    chat_id=user_id, message_id=message.message_id + 3, reply_markup=get_predict_new_keyboard(user_id))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())