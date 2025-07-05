from base64 import b64encode, b64decode
from PIL import Image
import io
import subprocess
import sys
import mpv
import os
import time
from functools import lru_cache
from datetime import timedelta

def process_base64_image(base64_str, target_size=(300, 300), quality=85, output_format="JPEG"):
    """
    Обрабатывает изображение из base64 с учетом прозрачности
    
    :param base64_str: Исходное изображение в base64
    :param target_size: Кортеж (ширина, высота)
    :param quality: Качество сжатия (1-100)
    :param output_format: Формат вывода ('JPEG', 'PNG', 'WEBP')
    :return: Новое изображение в base64
    """

    try:
        # Декодируем base64
        img_data = b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))

        if img.size[0]-img.size[1] > 100:
            target_size = (target_size[0],int(target_size[1]/1.75))
            fullform=True
        else:
            fullform=False
        
        # Конвертируем RGBA в RGB если сохраняем как JPEG
        if output_format.upper() == "JPEG" and img.mode == "RGBA":
            img = img.convert("RGB")
        
        # Изменяем размер
        img = img.resize(target_size, Image.LANCZOS)
        
        # Сохраняем в буфер
        buf = io.BytesIO()
        img.save(buf, format=output_format, quality=quality)
        
        return (b64encode(buf.getvalue()).decode('utf-8'),fullform)
    
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

def get_cover_base64(file_path):
    """
    Извлекает обложку аудиофайла и возвращает в формате base64
    
    :param file_path: Путь к аудиофайлу (MP3, FLAC, M4A и др.)
    :return: Строка base64 или None, если обложки нет
    """
    try:
        # Запускаем ffmpeg для извлечения обложки в pipe
        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-an',              # Игнорируем аудио
            '-vcodec', 'copy',  # Без перекодировки
            '-f', 'image2pipe', # Вывод в pipe
            '-vframes', '1',    # Только первый кадр
            '-',                # Вывод в stdout
        ]
        
        # Захватываем stdout как бинарные данные
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Кодируем в base64
        return b64encode(result.stdout).decode('utf-8')
    
    except subprocess.CalledProcessError as e:
        print(f"Ошибка FFmpeg: {e.stderr.decode()}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Общая ошибка: {str(e)}", file=sys.stderr)
        return None

class MPVMetadataExtractor:
    def __init__(self):
        self.player = mpv.MPV()
        self.metadata = {}
        self.cover_image = None

    @lru_cache(maxsize=100)
    def get_metadata(self, file_path):
        """Получаем метаданные через mpv"""
        self.player.play(file_path)

        attemp_load_metadata = 0
        
        # Ждем загрузки метаданных
        while not hasattr(self.player, 'metadata') or not self.player.metadata:
            attemp_load_metadata +=1
            print(attemp_load_metadata)
            if attemp_load_metadata >= 120:
                break
            else:
                pass
            time.sleep(0.01)
        
        # Получаем основные метаданные
        try:
            self.metadata = {
                'title': self._get_meta('title'),
                'artist': self._get_meta('artist'),
                'album': self._get_meta('album'),
                'duration': self.player.duration
            }
            
            self._get_cover()

            self.player.stop()
            return self.metadata, self.cover_image
        except:
            self.metadata = {
                'title': 'Unknown',
                'artist': 'Unknown',
                'album': 'Unknown',
                'duration': self.player.duration
            }
            
            self._get_cover()

            self.player.stop()
            return self.metadata, self.cover_image

    def _get_meta(self, tag):
        """Вспомогательная функция для безопасного получения тега"""
        try:
            return self.player.metadata.get(tag) or \
                   self.player.filtered_metadata.get(tag) or \
                   os.path.splitext(os.path.basename(self.player.filename))[0]
        except:
            return "Unknown"
        
    def _get_cover(self):
        print('Обложка загружается')

def format_duration(seconds: float) -> str:
    """
    Форматирует секунды в строку ЧЧ:ММ:СС
    
    :param seconds: Длительность в секундах (float)
    :return: Строка формата "00:00:00" или "00:00" (если часы = 0)
    """
    delta = timedelta(seconds=seconds)
    total_seconds = int(delta.total_seconds())
    
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"