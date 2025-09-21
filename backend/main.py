from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from . import models, database, auth, utils
import shutil, os, jwt, json
from typing import List

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "backend/uploads"
OUTPUT_DIR = "backend/uploads/annotated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def decode_token(token: str):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

@app.post("/signup")
def signup(fullname: str, username: str, password: str, confirm_password: str, db: Session = Depends(get_db)):
    if not fullname or not username or not password:
        raise HTTPException(status_code=400, detail="All fields required")
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if auth.signup_user(db, fullname, username, password):
        return {"message": "Signup successful"}
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, username, password)
    if user:
        token = auth.create_access_token({"sub": username, "user_id": user.id})
        return {"access_token": token, "fullname": user.fullname}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/uploadimage")
def upload_image(file: UploadFile = File(...), token: str = "", conf: float = 0.5, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    username = payload.get("sub")
    user_id = payload.get("user_id")

    # save original
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # avoid overwriting: append timestamp if exists
    if os.path.exists(file_path):
        base, ext = os.path.splitext(file.filename)
        import time
        file_path = os.path.join(UPLOAD_DIR, f"{base}_{int(time.time())}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # prepare output path
    out_filename = os.path.splitext(os.path.basename(file_path))[0] + "_annotated.jpg"
    output_path = os.path.join(OUTPUT_DIR, out_filename)

    # run detection (stronger settings)
    detections, avg_conf = utils.predict_and_annotate(file_path, output_path,
                                                     conf_threshold=conf, iou_threshold=0.45, imgsz=1280)

    # Save record to DB
    record = models.UploadedImage(
        filename=os.path.basename(file_path),
        output_path=output_path,
        detections_json=json.dumps(detections),
        avg_confidence=avg_conf,
        user_id=user_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"id": record.id, "detections": detections, "output_image_endpoint": f"/output/{record.id}"}

@app.get("/output/{image_id}")
def get_output_image(image_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.UploadedImage).filter_by(id=image_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(rec.output_path, media_type="image/jpeg")

@app.get("/history")
def get_history(token: str = "", db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    records = db.query(models.UploadedImage).filter_by(user_id=user_id).order_by(models.UploadedImage.uploaded_at.desc()).all()
    out = []
    for r in records:
        out.append({
            "id": r.id,
            "filename": r.filename,
            "output_path": r.output_path,
            "avg_confidence": r.avg_confidence,
            "uploaded_at": r.uploaded_at.isoformat(),
            "detections": json.loads(r.detections_json)
        })
    return JSONResponse(out)
