from io import BytesIO
import unicodedata
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings


def create_cert_img(certificate_entry, certificate):
    sum = certificate_entry.sum
    cert_uid = certificate_entry.cert_uid

    if certificate.image:
        # Генерация QR-кода
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2
        )
        qr.add_data(str(cert_uid))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Открываем основное изображение
        with BytesIO(certificate.image.read()) as cert_buffer:
            background = Image.open(cert_buffer).convert("RGBA")

            # Изменяем размер QR-кода
            qr_size = int(background.width * 0.2)
            qr_img = qr_img.resize((qr_size, qr_size))

            # Позиция QR-кода
            qr_position = (
                background.width - qr_img.width - 50,
                background.height - qr_img.height - 50
            )

            background.paste(qr_img, qr_position)

            # Подготовка текста
            price_text = f"{sum} ₽"
            margin = 50
            max_font_size = 350
            min_font_size = 50

            try:
                font_path = os.path.join(
                    settings.MEDIA_ROOT, 'fonts', 'NotoSans-Medium.ttf')
                font_size = max_font_size
                draw_tmp = ImageDraw.Draw(background)

                # Подбор подходящего размера шрифта
                while font_size >= min_font_size:
                    font = ImageFont.truetype(font_path, size=font_size)
                    bbox = draw_tmp.textbbox((0, 0), price_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    if text_width <= (background.width - margin * 2):
                        break
                    font_size -= 10
                else:
                    font = ImageFont.truetype(font_path, size=min_font_size)
                    bbox = draw_tmp.textbbox((0, 0), price_text, font=font)
                    text_width = bbox[2] - bbox[0]

            except IOError:
                font = ImageFont.load_default()
                bbox = draw_tmp.textbbox((0, 0), price_text, font=font)
                text_width = bbox[2] - bbox[0]

            # Центрирование по горизонтали
            x_center = (background.width - text_width) // 2
            text_position = (x_center, 1000)

            # Цвет с прозрачностью
            text_color = (0, 0, 0, 170)

            # Создание слоя для текста
            text_layer = Image.new("RGBA", background.size, (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_layer)
            text_draw.text(text_position, price_text,
                           fill=text_color, font=font)

            # Наложение текста на фон
            background = Image.alpha_composite(background, text_layer)

            # Сохраняем результат в память
            output_buffer = BytesIO()
            background.save(output_buffer, format="PNG")
            output_buffer.seek(0)

            return output_buffer

    return None
