from io import BytesIO
import base64
import qrcode
from fastapi import FastAPI, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from PIL import Image
from db_connection import SessionLocal, UserAuth, urlShorner, UsersQr
from auth import create_token, verify_token
from validators import Forauth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://127.0.0.1:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# ✅ Register User
# -------------------------------
@app.post('/register')
def registerUser(request: Forauth, db: Session = Depends(get_db)):
    existing = db.query(UserAuth).filter_by(email=request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_password = pass_context.hash(request.password)
    user = UserAuth(email=request.email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'message': "Successfully registered."}


# -------------------------------
# ✅ Login User
# -------------------------------
@app.post('/login')
def loginuser(request: Forauth, db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not pass_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password.")

    token = create_token({'username': user.email, 'user_id': str(user.id)})
    return {'token': token}


# -------------------------------
# ✅ Shorten URL
# -------------------------------
@app.post("/url-short")
def shorten_url(data: dict, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = token["user_id"]
    short_url = data.get("shortenUrl")
    original_url = data.get("originalUrl")

    if not short_url or not original_url:
        raise HTTPException(status_code=400, detail="Missing required URL fields.")

    existing = db.query(urlShorner).filter_by(shortenUrl=short_url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Short URL already exists.")

    url = urlShorner(
        originalUrl=original_url,
        shortenUrl=short_url,
        user_id=user_id,
    )
    db.add(url)
    db.commit()
    db.refresh(url)

    return {"shortenUrl": f"http://127.0.0.1:8000/to/{short_url}"}


# -------------------------------
# ✅ Redirect to original URL
# -------------------------------
@app.get("/to/{shortenUrl}")
def redirectionto(shortenUrl: str, db: Session = Depends(get_db)):
    url = db.query(urlShorner).filter_by(shortenUrl=shortenUrl).first()
    if url:
        url.clicks += 1
        db.commit()
        return RedirectResponse(url.originalUrl)
    raise HTTPException(status_code=404, detail="Short URL not found.")


# -------------------------------
# ✅ Get All URLs for User
# -------------------------------
@app.get("/my-urls")
def get_paginated_urls(
    token: str = Query(...),
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    payload = verify_token(token)
    user = db.query(UserAuth).filter_by(email=payload['username']).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    total = db.query(urlShorner).filter_by(user_id=user.id).count()
    urls = db.query(urlShorner).filter_by(user_id=user.id).offset(offset).limit(limit).all()

    return {
        "total": total,
        "urls": [
            {
                "id": u.id,
                "originalUrl": u.originalUrl,
                "shortenUrl": u.shortenUrl,
                "clicks": u.clicks
            } for u in urls
        ]
    }


# -------------------------------
# ✅ Delete URL
# -------------------------------
@app.delete("/delete-url/{url_id}")
def delete_url(url_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user = db.query(UserAuth).filter_by(email=payload['username']).first()

    url = db.query(urlShorner).filter_by(id=url_id, user_id=user.id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found or unauthorized.")

    db.delete(url)
    db.commit()
    return {"message": "Deleted successfully."}


# -------------------------------
# ✅ Generate QR Code with optional logo
# -------------------------------
@app.post("/generate-qr/")
async def generate_qr(
    url: str = Query(...),
    logo: UploadFile = File(None),
    qr_color: str = Query("#000000"),
    qr_bg: str = Query("#ffffff"),
    qr_size: int = Query(10),
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    payload = verify_token(token)
    user = db.query(UserAuth).filter_by(email=payload['username']).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token.")

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=qr_size,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color=qr_color, back_color=qr_bg).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"QR generation error: {str(e)}")

    logo_name = None
    if logo:
        try:
            logo_bytes = await logo.read()
            logo_img = Image.open(BytesIO(logo_bytes))
            logo_img = logo_img.resize((60, 60))
            pos = ((img_qr.size[0] - 60) // 2, (img_qr.size[1] - 60) // 2)
            img_qr.paste(logo_img, pos)
            logo_name = logo.filename
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid logo file: {str(e)}")

    db.add(UsersQr(qr_url=url, logo_name=logo_name, user_id=user.id))
    db.commit()

    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


# -------------------------------
# ✅ QR History List
# -------------------------------
@app.get("/user-qr-list")
def get_user_qrs(token: str = Query(...), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user = db.query(UserAuth).filter_by(email=payload["username"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user_qrs = db.query(UsersQr).filter_by(user_id=user.id).all()

    result = []
    for qr in user_qrs:
        encoded = ""
        try:
            if qr.logo_name:
                qr_path = f"./qr_storage/{qr.logo_name}"
                with open(qr_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass

        result.append({
            "qr_url": qr.qr_url,
            "qr_base64": encoded,
        })

    return result

# -----------------------------------
# ✅ user Dashboard for analytics
# -----------------------------------

@app.get("/dashboard-stats")
def dashboard_stats(token: str = Query(...), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user = db.query(UserAuth).filter(UserAuth.email == payload["username"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    urls = db.query(urlShorner).filter(urlShorner.user_id == user.id).all()
    total_urls = len(urls)
    total_clicks = sum([u.clicks for u in urls])

    # 👇 In your FastAPI route
    top_urls = db.query(urlShorner).filter_by(user_id=user.id).order_by(urlShorner.clicks.desc()).limit(5).all()

    return {
    "total_urls": total_urls,
    "total_clicks": total_clicks,
    "top_urls": [
        {"short": u.shortenUrl, "clicks": u.clicks}
        for u in top_urls
    ]
}

from fastapi.responses import StreamingResponse
import csv

@app.get("/export-urls")
def export_urls(token: str = Query(...), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user = db.query(UserAuth).filter_by(email=payload['username']).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    urls = db.query(urlShorner).filter_by(user_id=user.id).all()

    def generate():
        yield "ID,Original URL,Short URL,Clicks\n"
        for u in urls:
            row = f"{u.id},{u.originalUrl},{u.shortenUrl},{u.clicks}\n"
            yield row

    return StreamingResponse(generate(), media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=short_urls.csv"
    })


@app.get("/top-urls")
def get_top_urls(token: str = Query(...), db: Session = Depends(get_db)):
    payload = verify_token(token)
    user = db.query(UserAuth).filter_by(email=payload['username']).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    urls = (
        db.query(urlShorner)
        .filter_by(user_id=user.id)
        .order_by(urlShorner.clicks.desc())
        .limit(5)
        .all()
    )

    labels = [u.shortenUrl for u in urls]
    data = [u.clicks for u in urls]

    return {"labels": labels, "data": data}