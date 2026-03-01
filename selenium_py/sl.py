from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sqlite3
import os

from Config.config import VOTE_URL
from database import db, sql


def get_driver():
    """Chrome webdriver sozlamalari (headless - server uchun)"""
    options = Options()
    options.add_argument("--headless")           # Ekransiz ishlash (server uchun)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # ChromeDriver avtomatik yuklab oladi
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def save_user(phone_number: str, msg, bot) -> bool:
    """
    Foydalanuvchini DB ga saqlash.
    Agar allaqachon saqlangan bo'lsa False qaytaradi.
    """
    telegram_id = msg.chat.id
    first_name = msg.chat.first_name or "Noma'lum"
    username = msg.chat.username or ""

    existing = sql.execute(
        "SELECT id, status FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()

    if existing:
        if existing[1] == 1:
            bot.send_message(telegram_id, "❗ Siz allaqachon ovoz bergansiz!")
            return False
        # Telefon raqamini yangilash
        sql.execute(
            "UPDATE users SET phone_number = ? WHERE telegram_id = ?",
            (phone_number, telegram_id)
        )
        db.commit()
        return True
    else:
        sql.execute(
            "INSERT INTO users(first_name, username, telegram_id, status, phone_number) VALUES(?, ?, ?, 0, ?)",
            (first_name, username, telegram_id, phone_number)
        )
        db.commit()
        return True


def Vote(bot, msg):
    """
    Selenium orqali ovoz berish.
    VOTE_URL - .env faylida ko'rsatilgan saytga kiradi.
    """
    telegram_id = msg.chat.id
    bot.send_message(telegram_id, "⏳ Ovoz berilmoqda, iltimos kuting...")

    # Foydalanuvchi ma'lumotlarini olish
    user = sql.execute(
        "SELECT phone_number FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()

    if not user:
        bot.send_message(telegram_id, "❌ Foydalanuvchi topilmadi!")
        return

    phone_number = user[0]

    driver = None
    try:
        driver = get_driver()
        driver.get(VOTE_URL)

        wait = WebDriverWait(driver, 15)

        # ============================================================
        # ⚠️  BU YERDA SAYTINGIZGA QARAB ELEMENTLARNI O'ZGARTIRING!
        # ============================================================
        # Misol: telefon raqam input topish
        # phone_input = wait.until(EC.presence_of_element_located((By.ID, "phone")))
        # phone_input.clear()
        # phone_input.send_keys("998" + phone_number)
        #
        # Misol: tugmani bosish
        # vote_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Ovoz')]")
        # vote_btn.click()
        #
        # Misol: natijani kutish
        # time.sleep(2)
        # ============================================================

        # Hozircha demo - muvaffaqiyatli deb belgilaydi
        # Siz o'zingizning sayt logikangizni yozing
        time.sleep(2)

        # Ovoz bergan deb belgilash
        sql.execute(
            "UPDATE users SET status = 1 WHERE telegram_id = ?", (telegram_id,)
        )
        db.commit()

        bot.send_message(telegram_id, "✅ Ovoz muvaffaqiyatli berildi!")

    except Exception as e:
        bot.send_message(telegram_id, f"❌ Xatolik yuz berdi: {str(e)}")
        print(f"[Vote Error] {e}")

    finally:
        if driver:
            driver.quit()
