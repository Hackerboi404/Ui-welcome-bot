import logging
import io
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.utils.keyboard import InlineKeyboardBuilder # Re-using builders for simple code
# Pillow library for image generation
from PIL import Image, ImageDraw, ImageFont

# 1. Configuration (Set these as Environment Variables on Render)
import os
API_TOKEN = os.environ.get('BOT_TOKEN') # Use Render Env Var
GROUP_ID = int(os.environ.get('GROUP_ID'))   # Use Render Env Var, must be int
TEMPLATE_PATH = "welcome_template.png"
FONT_PATH = "Arial.ttf"
DEFAULT_PROFILE = "placeholder_profile.png" # Path to default image

# Initialize bot and dispatcher
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 2. Dynamic Image Generation Function
async def generate_welcome_card(user: types.User, chat_title: str):
    """Generates the unique UI card by overlaying user data on the template."""
    try:
        base_img = Image.open(TEMPLATE_PATH).convert("RGBA")
    except FileNotFoundError:
        logging.error("Template image not found!")
        return None

    draw = ImageDraw.Draw(base_img)
    # Positions based on image_4.png
    FONT_BOLD = ImageFont.truetype(FONT_PATH, 48) # Welcome, {name} (Top right)
    FONT_NORMAL = ImageFont.truetype(FONT_PATH, 28) # User Details
    FONT_SMALL = ImageFont.truetype(FONT_PATH, 22) # Bottom Welcome Message

    # (A) Overlay Profile Picture (If available)
    profile_pasted = False
    if user.id:
        try:
            profile_pic = Image.open(DEFAULT_PROFILE).resize((220, 220)) # Size based on template circle
            mask = Image.new('L', profile_pic.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 220, 220), fill=255)
            # Paste in the circle position (Approx x=80, y=100)
            base_img.paste(profile_pic, (80, 100), mask)
            profile_pasted = True
        except FileNotFoundError:
            pass # No default profile found

    # (B) Overlay Dynamic Text (Approximate positions based on template)
    white = (255, 255, 255, 255)
    light_grey = (200, 200, 200, 255)

    # 1. Title: WELCOME, {name}! (Top right)
    draw.text((450, 60), f"WELCOME, {user.full_name}!", font=FONT_BOLD, fill=white)

    # 2. Member Details (Right panel, below icons)
    details_text = f"User ID: {user.id}\n\n" \
                   f"Username: @{user.username if user.username else 'N/A'}\n\n" \
                   f"Group: {chat_title}"
    draw.text((450, 310), details_text, font=FONT_NORMAL, fill=light_grey, spacing=12)

    # 3. Bottom Welcome Message (Bottom section)
    welcome_msg = "Aap is creative ecosystem ka hissa banne ja rahe hain.\n" \
                   "Hum khush hain ki aap humare sath hain!"
    draw.text((380, 680), welcome_msg, font=FONT_SMALL, fill=white, spacing=8)

    # Convert the resulting image to bytes to send via Telegram
    img_byte_arr = io.BytesIO()
    base_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# 3. New Member Detection Handler
@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: types.ChatMemberUpdated):
    """Detects new members, generates, and sends the personalized UI card."""
    if event.chat.id != GROUP_ID:
        return

    new_member = event.new_chat_member.user
    chat_title = event.chat.title

    logging.info(f"New user {new_member.full_name} joined {chat_title}")

    # Step 2: Generate the Dynamic Card
    card_bytes = await generate_welcome_card(new_member, chat_title)

    if card_bytes:
        # Create Inline Buttons
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="📜 Group Rules", url="https://t.me/OG_FRIENDZ"),
            types.InlineKeyboardButton(text="📢 Stay Updated", url="https://t.me/OG_FRIENDZ")
        )
        builder.row(
            types.InlineKeyboardButton(text="❓ About Us", callback_data="about_us")
        )

        # Send the generated image with buttons
        await bot.send_photo(
            chat_id=event.chat.id,
            photo=types.BufferedInputFile(card_bytes.read(), filename="welcome.png"),
            caption=f"Welcome to {chat_title}, {new_member.mention_html()}!",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
      )
