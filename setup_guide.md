# 📚 To'liq O'rnatish Qo'llanmasi

## ⚠️ MUHIM ESLATMA

**Vercel'da audio konvertatsiya ISHLAMAYDI!** Chunki Vercel'da FFmpeg yo'q va serverless function'lar cheklangan.

**Tavsiya:** Railway yoki Render platformalaridan foydalaning.

---

## 🎯 Variant 1: Railway (TAVSIYA ETILADI)

Railway - bu bepul hosting platformasi, FFmpeg bilan ishlaydi.

### Bosqichma-bosqich:

#### 1. Bot yaratish (@BotFather)

1. Telegram'da @BotFather ni oching
2. `/newbot` yozing
3. Bot nomini kiriting: `Music Converter Bot`
4. Username kiriting: `your_music_bot` (o'zingizniki)
5. **Token nusxalang** (masalan: `6234567890:AAHdqT...`)

#### 2. GitHub Repository yaratish

1. GitHub'ga kiring: https://github.com
2. **New repository** bosing
3. Repository nomi: `telegram-music-bot`
4. **Public** tanlang
5. **Create repository**

#### 3. Fayllarni tayyorlash

Kompyuteringizda papka yarating:

```bash
mkdir telegram-music-bot
cd telegram-music-bot
```

**4 ta fayl yarating:**

**Fayl 1: `bot.py`** (Birinchi artifact'dagi kodni qo'ying)

**Fayl 2: `requirements.txt`**
```
python-telegram-bot==20.7
pydub==0.25.1
```

**Fayl 3: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

# FFmpeg o'rnatish
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodni nusxalash
COPY . .

# Bot ishga tushirish
CMD ["python", "bot.py"]
```

**Fayl 4: `railway.json`**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 4. GitHub'ga yuklash

```bash
# Git init
git init

# Fayllarni qo'shish
git add .
git commit -m "Initial commit"

# GitHub'ga ulash
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/telegram-music-bot.git
git push -u origin main
```

#### 5. Railway'da deploy qilish

1. **Railway'ga kiring:** https://railway.app
2. **Sign up** qiling (GitHub bilan)
3. **New Project** bosing
4. **Deploy from GitHub repo** tanlang
5. `telegram-music-bot` repository'ni tanlang
6. **Add variables** bosing:
   - Name: `BOT_TOKEN`
   - Value: Sizning bot tokeningiz
7. **Deploy** bosing

#### 6. Bot tokenini sozlash

Railway'da:
1. Project ochilganda, **Variables** tab'ini oching
2. **BOT_TOKEN** ga tokeningizni qo'ying
3. Automatic deploy bo'ladi

#### 7. Ishlatish

1. Telegram'da botingizni oching
2. `/start` bosing
3. `/set_channel @sizning_kanalingiz`
4. Audio/video yuboring!

---

## 🎯 Variant 2: Render.com

Render ham bepul va yaxshi ishlaydi.

### Bosqichlar:

1. **Render'ga kiring:** https://render.com
2. **Sign up** (GitHub bilan)
3. **New +** → **Web Service**
4. Repository tanlang
5. Settings:
   - **Name:** telegram-music-bot
   - **Environment:** Docker
   - **Plan:** Free
6. **Environment Variables:**
   - Key: `BOT_TOKEN`
   - Value: Sizning tokeningiz
7. **Create Web Service**

---

## 🎯 Variant 3: Lokal kompyuter (Test uchun)

Kompyuteringizda test qilish uchun:

```bash
# Virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Requirements o'rnatish
pip install python-telegram-bot pydub

# FFmpeg o'rnatish
# Windows: https://ffmpeg.org/download.html
# Ubuntu: sudo apt install ffmpeg
# Mac: brew install ffmpeg

# Bot tokenini qo'yish
# bot.py faylida TOKEN = "..." ni o'zgartiring

# Ishga tushirish
python bot.py
```

---

## 🔧 Tez-tez so'raladigan savollar

### Q: Vercel'da ishlamayaptimi?
**A:** Ha, Vercel serverless, FFmpeg yo'q. Railway yoki Render ishlatilsin.

### Q: Bot javob bermayapti?
**A:** 
1. Token to'g'rimi?
2. Railway'da bot ishlab turibmikan? (Logs'ga qarang)
3. Internet bormi?

### Q: Kanalga yuborilmayapti?
**A:**
1. Botni kanalga **admin** qilib qo'shdingizmi?
2. Kanal nomi to'g'rimi? (`@kanal_nomi`)
3. Kanal public'mi?

### Q: Fayl katta bo'lsa?
**A:** Railway bepul plan'da:
- 50MB gacha OK
- Kattaroq fayllar uchun premium kerak

### Q: Boshqa muammo?
**A:** Railway Logs'ga qarang:
1. Railway project oching
2. **Deployments** tab
3. **View Logs**

---

## 📊 Platformalar taqqoslash

| Platform | FFmpeg | Narx | Deploy | Qulaylik |
|----------|--------|------|--------|----------|
| **Railway** | ✅ Ha | Bepul | Oson | ⭐⭐⭐⭐⭐ |
| **Render** | ✅ Ha | Bepul | Oson | ⭐⭐⭐⭐ |
| Vercel | ❌ Yo'q | Bepul | Oson | ⭐⭐ |
| Heroku | ✅ Ha | $$ | O'rtacha | ⭐⭐⭐ |

**Xulosa:** Railway ishlatilsin! 🚀

---

## 📞 Yordam kerakmi?

Muammo bo'lsa:
1. Railway Logs tekshiring
2. Bot token to'g'riligini tekshiring
3. GitHub Issue oching

## 🎉 Omad tilayman!

Muvaffaqiyatli deploy qilganingizdan keyin:
- Botni do'stlaringizga ulashing
- Kanal'ga reklama qiling
- Kodingizni GitHub'da public qiling