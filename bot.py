from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import tempfile
from urllib.parse import urlparse
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8508502920:AAHSk3vLTkZ0Kn-L1zglSeh76u2GpOyqHZcv')
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# User data storage (in-memory, faqat demo uchun)
user_channels = {}


class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Health check"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
        return
    
    def do_POST(self):
        """Webhook handler"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Received update: {update}")
            
            # Process update
            self.process_update(update)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
            
        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def process_update(self, update):
        """Update ni qayta ishlash"""
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        
        # Buyruqlarni qayta ishlash
        if 'text' in message:
            text = message['text']
            
            if text.startswith('/start'):
                self.send_message(chat_id, 
                    "🎵 *Musiqani MP3 formatiga o'tkazuvchi bot*\n\n"
                    "Botdan foydalanish:\n"
                    "1. /set_channel @kanal_nomi - Kanalni belgilang\n"
                    "2. Menga audio, video yoki ovozli xabar yuboring\n"
                    "3. Men uni MP3 formatiga o'tkazirib, kanalingizga yuboraman!\n\n"
                    "⚠️ *Muhim:* Botni kanalingizga admin qilib qo'shing!",
                    parse_mode='Markdown')
            
            elif text.startswith('/set_channel'):
                parts = text.split()
                if len(parts) < 2:
                    self.send_message(chat_id, 
                        "❌ Kanal nomini kiriting!\n"
                        "Misol: /set_channel @mening_kanalim")
                    return
                
                channel = parts[1]
                if not channel.startswith('@'):
                    self.send_message(chat_id, 
                        "❌ Kanal nomi @ belgisi bilan boshlanishi kerak!")
                    return
                
                user_channels[user_id] = channel
                self.send_message(chat_id, 
                    f"✅ Kanal belgilandi: {channel}\n\n"
                    "Endi audio/video yuboring!")
            
            elif text.startswith('/help'):
                self.send_message(chat_id,
                    "ℹ️ *Yordam*\n\n"
                    "*Buyruqlar:*\n"
                    "/start - Boshlash\n"
                    "/set_channel @kanal - Kanalni belgilash\n"
                    "/help - Yordam\n\n"
                    "*Qo'llab-quvvatlanadigan formatlar:*\n"
                    "• Audio (MP3, M4A, OGG, WAV, FLAC)\n"
                    "• Video (MP4, MKV, AVI)\n"
                    "• Ovozli xabarlar",
                    parse_mode='Markdown')
        
        # Audio/Video fayllarni qayta ishlash
        elif 'audio' in message or 'voice' in message or 'video' in message or 'document' in message:
            self.handle_media(message, chat_id, user_id)
    
    def handle_media(self, message, chat_id, user_id):
        """Media fayllarni qayta ishlash"""
        # Kanal tekshiruvi
        if user_id not in user_channels:
            self.send_message(chat_id,
                "⚠️ Avval kanalni belgilang!\n"
                "Buyruq: /set_channel @kanal_nomi")
            return
        
        channel = user_channels[user_id]
        
        # Fayl ma'lumotlarini olish
        file_info = None
        file_name = "audio"
        
        if 'audio' in message:
            file_info = message['audio']
            file_name = file_info.get('file_name', 'audio')
        elif 'voice' in message:
            file_info = message['voice']
            file_name = 'voice_message'
        elif 'video' in message:
            file_info = message['video']
            file_name = file_info.get('file_name', 'video')
        elif 'document' in message:
            file_info = message['document']
            file_name = file_info.get('file_name', 'document')
        
        if not file_info:
            return
        
        # Fayl hajmi tekshiruvi (20MB limit - Vercel uchun)
        file_size = file_info.get('file_size', 0)
        if file_size > 20 * 1024 * 1024:
            self.send_message(chat_id,
                "❌ Fayl hajmi juda katta! (maksimal 20MB)\n"
                "Vercel limitation tufayli.")
            return
        
        file_id = file_info['file_id']
        
        # Status xabari
        status = self.send_message(chat_id, "⏳ Fayl yuklanmoqda...")
        status_message_id = status.get('result', {}).get('message_id')
        
        try:
            # Faylni yuklab olish
            file_path = self.download_file(file_id)
            if not file_path:
                self.edit_message(chat_id, status_message_id, "❌ Fayl yuklab olinmadi!")
                return
            
            self.edit_message(chat_id, status_message_id, "🔄 MP3 formatiga o'tkazilmoqda...")
            
            # MP3 ga konvertatsiya
            output_path = self.convert_to_mp3(file_path)
            if not output_path:
                self.edit_message(chat_id, status_message_id, 
                    "❌ Konvertatsiya xatosi!\n"
                    "FFmpeg mavjud emasmi?")
                return
            
            self.edit_message(chat_id, status_message_id, "📤 Kanalga yuklanmoqda...")
            
            # Kanalga yuborish
            base_name = os.path.splitext(file_name)[0]
            mp3_name = f"{base_name}.mp3"
            
            result = self.send_audio_to_channel(channel, output_path, base_name, mp3_name)
            
            if result:
                self.edit_message(chat_id, status_message_id,
                    f"✅ Muvaffaqiyatli yuborildi!\n"
                    f"Kanal: {channel}\n"
                    f"Fayl: {mp3_name}")
            else:
                self.edit_message(chat_id, status_message_id,
                    "❌ Kanalga yuborishda xatolik!\n"
                    "Bot kanalda admin emasmi?")
            
            # Fayllarni o'chirish
            try:
                os.remove(file_path)
                os.remove(output_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Media handling error: {e}")
            if status_message_id:
                self.edit_message(chat_id, status_message_id,
                    f"❌ Xatolik: {str(e)}")
    
    def download_file(self, file_id):
        """Faylni yuklab olish"""
        try:
            # Fayl yo'lini olish
            resp = requests.get(f"{TELEGRAM_API}/getFile?file_id={file_id}")
            data = resp.json()
            
            if not data.get('ok'):
                return None
            
            file_path = data['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            
            # Faylni yuklab olish
            response = requests.get(file_url)
            if response.status_code != 200:
                return None
            
            # Vaqtinchalik faylga saqlash
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_path)[1])
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def convert_to_mp3(self, input_path):
        """MP3 ga konvertatsiya qilish"""
        try:
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
            
            # FFmpeg bilan konvertatsiya
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vn',  # Video yo'q
                '-ar', '44100',  # Sample rate
                '-ac', '2',  # Stereo
                '-b:a', '192k',  # Bitrate
                '-f', 'mp3',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None
    
    def send_audio_to_channel(self, channel, file_path, title, filename):
        """Kanalga audio yuborish"""
        try:
            with open(file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'chat_id': channel,
                    'title': title,
                    'caption': '🎵 Converted to MP3'
                }
                
                response = requests.post(
                    f"{TELEGRAM_API}/sendAudio",
                    files=files,
                    data=data,
                    timeout=120
                )
                
                return response.json().get('ok', False)
                
        except Exception as e:
            logger.error(f"Send audio error: {e}")
            return False
    
    def send_message(self, chat_id, text, parse_mode=None):
        """Xabar yuborish"""
        try:
            data = {
                'chat_id': chat_id,
                'text': text
            }
            if parse_mode:
                data['parse_mode'] = parse_mode
            
            response = requests.post(f"{TELEGRAM_API}/sendMessage", json=data)
            return response.json()
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return {}
    
    def edit_message(self, chat_id, message_id, text):
        """Xabarni tahrirlash"""
        try:
            data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text
            }
            requests.post(f"{TELEGRAM_API}/editMessageText", json=data)
        except Exception as e:
            logger.error(f"Edit message error: {e}")
