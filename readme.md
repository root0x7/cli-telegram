# 📱 Telegram TUI Client

Bu loyiha **Telethon** va **Rich** kutubxonalaridan foydalanib, terminalda ishlaydigan oddiy Telegram TUI (Text User Interface) mijozidir.  

## 🔧 O‘rnatish

### 1. Python versiyasi
Loyihani ishga tushirish uchun **Python 3.9+** kerak bo‘ladi.  
Python versiyasini tekshirish:
```bash
python3 --version
```

### 2. Virtual environment yaratish (ixtiyoriy, lekin tavsiya etiladi)
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Kutubxonalarni o‘rnatish
Loyihada `requirements.txt` fayli bor, shuning uchun quyidagilarni bajarish kifoya:
```bash
pip install -r requirements.txt
```

Agar qo‘lda o‘rnatmoqchi bo‘lsangiz:
```bash
pip install telethon rich python-dotenv
```

### 4. Telegram API kalitlarini sozlash
Telegram API kalitlarini olish uchun: [https://my.telegram.org](https://my.telegram.org) → **API Development Tools**

Keyin `.env` fayl yarating va quyidagilarni kiriting:
```env
API_ID=123456
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+998901234567
```

### 5. Loyihani ishga tushirish
```bash
python main.py
```

## 📦 Kutubxonalar
- [Telethon](https://github.com/LonamiWebs/Telethon) – Telegram API uchun Python kutubxonasi  
- [Rich](https://github.com/Textualize/rich) – Terminalda chiroyli interfeys yaratish uchun kutubxona  
- [python-dotenv](https://github.com/theskumar/python-dotenv) – `.env` fayldan konfiguratsiya yuklash  

## ⚡ Foydalanish
- Birinchi marta ishga tushirganda, sizdan SMS orqali **Telegram tasdiqlash kodi** so‘raladi.  
- Keyinchalik avtomatik login ishlatiladi.  

---

👨‍💻 Endi loyiha ishga tushirishga tayyor! 🚀