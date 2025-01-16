from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import folium

API_TOKEN="7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



async def display_pickup_points(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    pickup_points_button = InlineKeyboardButton("Show Pickup Points", callback_data='show_pickup_points')
    keyboard.add(pickup_points_button)
    await message.reply("Press the button to view pickup points on the map!", reply_markup=keyboard)


@dp.callback_query_handler(text='show_pickup_points')
async def process_callback_show_pickup_points(callback_query: types.CallbackQuery):
    # Create the map object
    m = folium.Map(location=[55.7522, 37.6155], zoom_start=12)  # Set the initial map coordinates

    # Add markers for pickup points
    pickup_points = {
        "Pickup Point 1": [55.7522, 37.6155],
        "Pickup Point 2": [55.7525, 37.6160]
        # Add other pickup points in a similar manner
    }

    for point_name, coordinates in pickup_points.items():
        folium.Marker(coordinates, popup=point_name).add_to(m)

    # Save the map to a file
    map_file_path = "map.html"
    m.save(map_file_path)

    # Send the map file to the user
    with open(map_file_path, 'rb') as map_file:
        await bot.send_document(callback_query.from_user.id, map_file, caption="Here is the map with pickup points. Please select a pickup point.")


@dp.callback_query_handler(lambda query: query.data.startswith('picked_point_'))
async def process_callback_picked_point(callback_query: types.CallbackQuery):
    point_id = callback_query.data.split('_')[2]
    await bot.send_message(callback_query.from_user.id, f"You've picked the pickup point #{point_id}. Please share your location now.")


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    longitude, latitude = message.location.longitude, message.location.latitude
    await bot.send_message(message.chat.id, f"Thank you for sharing your location. Longitude: {longitude}, Latitude: {latitude}")


async def main():
    dp.register_message_handler(display_pickup_points, commands=['start'])
    await dp.start_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()