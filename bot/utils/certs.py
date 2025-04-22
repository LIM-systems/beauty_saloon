from io import BytesIO
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
            qr_size = int(background.width * 0.15)
            qr_img = qr_img.resize((qr_size, qr_size))

            # Позиция QR-кода
            qr_position = (
                background.width - qr_img.width - 50,
                background.height - qr_img.height - 50
            )

            background.paste(qr_img, qr_position)

            # Рисуем текст
            draw = ImageDraw.Draw(background)

            # Загружаем шрифт
            try:
                font_path = os.path.join(
                    settings.MEDIA_ROOT, 'fonts', 'arial.ttf')
                # размер шрифта можно увеличить
                font = ImageFont.truetype(font_path, size=100)
            except IOError:
                font = ImageFont.load_default()

            # Подготовка текста
            price_text = f"{sum} рублей"

            # Получаем размер текста
            bbox = draw.textbbox((0, 0), price_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Позиция текста (левее и выше от QR)
            text_width, _ = draw.textbbox((0, 0), price_text, font=font)[2:]
            x_center = (background.width - text_width) // 2
            text_position = (x_center, 300)

            # Цвет текста можно изменить тут
            # тёмно-синий (можно 'red', '#FF0000', и т.д.)
            text_color = "#000000"

            draw.text(text_position, price_text, fill=text_color, font=font)

            # Сохраняем в память
            output_buffer = BytesIO()
            background.save(output_buffer, format="PNG")
            output_buffer.seek(0)

            return output_buffer
    return None
