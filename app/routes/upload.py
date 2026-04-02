# from fastapi import APIRouter, UploadFile, File
# import os

# router = APIRouter()

# UPLOAD_DIR = "data/uploads"

# @router.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)

#     with open(file_path, "wb") as f:
#         content = await file.read()
#         f.write(content)

#     return {"filename": file.filename}


from fastapi import APIRouter, UploadFile, File
import os
from app.services.parser import extract_text

router = APIRouter()

UPLOAD_DIR = "data/uploads"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 👇 ADD THIS
    text = extract_text(file_path)

    return {
        "filename": file.filename,
        "text_preview": text[:500]  # show first 500 chars
    }