import qrcode
from PIL import Image
from io import BytesIO

async def create_qr_code_with_logo(url: str, logo_file) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    if logo_file:
        logo_bytes = await logo_file.read()
        logo_img = Image.open(BytesIO(logo_bytes))

        logo_size = 60
        logo_img = logo_img.resize((logo_size, logo_size))

        pos = ((img_qr.size[0] - logo_size) // 2, (img_qr.size[1] - logo_size) // 2)
        img_qr.paste(logo_img, pos)

    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    buf.seek(0)
    return buf
