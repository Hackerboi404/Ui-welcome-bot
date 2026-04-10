import logging
import io
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession # Timeout fix ke liye
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration
API_TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID'))
TEMPLATE_PATH = "welcome_template.png"
FONT_PATH = "Arial.ttf" 
DEFAULT_PROFILE = "placeholder_profile.png"

# Timeout badhane ke liye session use kar rahe hain
session = AiohttpSession(timeout=60) # 60 seconds timeout
bot = Bot(token=API_TOKEN, session=session)
dp = Dispatcher()

async def generate_welcome_card(user: types.User, chat_title: str):
    try:
        # Template ko clean tarike se load karein
        base_img = Image.open(TEMPLATE_PATH).convert("RGBA")
        draw = ImageDraw.Draw(base_img)
        
        # Font sizes adjust karein (Aap apne hisab se chhota-bada kar sakte ho)
        font_title = ImageFont.truetype(FONT_PATH, 45) # Name ke liye
        font_details = ImageFont.truetype(FONT_PATH, 25) # ID/Username ke liye
        font_msg = ImageFont.truetype(FONT_PATH, 22) # Welcome msg ke liye

        # (A) Profile Picture Logic
        try:
            # User ki profile photo nikalne ka logic abhi skip hai simple rakhne ke liye
            # Sidha placeholder lagate hain coordinates check karne ke liye
            profile_pic = Image.open(DEFAULT_PROFILE).resize((210, 210))
            mask = Image.new('L', profile_pic.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 210, 210), fill=255)
            # Circle ki sahi jagah (Template ke hisab se check karein)
            base_img.paste(profile_pic, (85, 105), mask)
        except:
            pass

        # (B) Text Overlay - COORDINATES UPDATED
        white = (255, 255, 255)
        
        # 1. Name Overlay (Template mein jo '[NEW MEMBER NAME]' likha hai uske upar)
        # Coordinates (x=730, y=75) ke aas pass try karo
        draw.text((730, 75), f"{user.full_name[:15]}", font=font_title, fill=white, anchor="mm")

        # 2. Details Overlay (Boxes ke samne)
        # User ID
        draw.text((560, 315), f"{user.id}", font=font_details, fill=white)
        # Username
        draw.text((560, 365), f"@{user.username if user.username else 'None'}", font=font_details, fill=white)
        # Group Name
        draw.text((560, 415), f"{chat_title[:15]}", font=font_details, fill=white)

        # 3. Message Overlay (Niche ki khali jagah)
        msg = "Welcome! Hum khush hain ki aap\nhumare sath hain!"
        draw.text((450, 700), msg, font=font_msg, fill=white, align="center")

        img_byte_arr = io.BytesIO()
        base_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr
    except Exception as e:
        logging.error(f"Image Error: {e}")
        return None

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: types.ChatMemberUpdated):
    if event.chat.id != GROUP_ID:
        return

    new_member = event.new_chat_member.user
    card = await generate_welcome_card(new_member, event.chat.title)

    if card:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📜 Rules", url="https://t.me/example"),
                    types.InlineKeyboardButton(text="📢 Updates", url="https://t.me/example"))
        
        # Send Photo with longer timeout handling
        await bot.send_photo(
            chat_id=event.chat.id,
            photo=types.BufferedInputFile(card.read(), filename="welcome.png"),
            reply_markup=builder.as_markup()
        )
