from PIL import Image, ImageDraw, ImageFont
import os

TEMPLATE_PATH = "sertifikat.png"  # Шаблон сертификата
FONT_PATH = "fonts/DejaVuSansCondensed-Bold.ttf"  # Шрифт
OUTPUT_PATH = "generated_certificates/"  # Папка для готовых сертификатов

# Создаем папку для сертификатов, если её нет
os.makedirs(OUTPUT_PATH, exist_ok=True)


# Создаем папку для сертификатов, если её нет
os.makedirs(OUTPUT_PATH, exist_ok=True)

def generate_certificate(user_name, score):
    # Загружаем шаблон
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)

    # Загружаем шрифт
    font_name = ImageFont.truetype(FONT_PATH, 80)  # Увеличим размер для ФИО
    font_score = ImageFont.truetype(FONT_PATH, 50)

    # Размеры изображения
    img_width, img_height = img.size

    # Определяем размеры текста
    name_bbox = draw.textbbox((0, 0), user_name, font=font_name)
    name_width = name_bbox[2] - name_bbox[0]
    name_height = name_bbox[3] - name_bbox[1]

    score_text = f"Баллы: {score}"
    score_bbox = draw.textbbox((0, 0), score_text, font=font_score)
    score_width = score_bbox[2] - score_bbox[0]

    # Вычисляем координаты для центрирования текста
    name_position = ((img_width - name_width) // 2, img_height // 2 + 150)
    score_position = ((img_width - score_width) // 2, img_height // 2 + 300)

    # Добавляем текст
    draw.text(name_position, user_name, font=font_name, fill="black")
    draw.text(score_position, score_text, font=font_score, fill="black")

    # Сохраняем сертификат
    output_file = f"{OUTPUT_PATH}{user_name.replace(' ', '_')}.png"
    img.save(output_file)

    return output_file
