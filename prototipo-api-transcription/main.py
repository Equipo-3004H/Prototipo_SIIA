from unittest import result

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import whisper
import shutil

app = FastAPI()
model = whisper.load_model("tiny")

# Manejadores de excepciones personalizados
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
     return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"detail": exc.detail, "body": exc.body}),
    )

# Manejador de excepciones para errores de validación con detalles en formato JSON
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

# Manejador de excepciones para errores no controlados con un mensaje genérico
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )

# Endpoint de ejemplo para levantar una excepción personalizada
@app.get("/levantar-excepcion/")
async def raise_error():
    raise HTTPException(status_code=400, detail="Este es un error de ejemplo.")

# Endpoint de ejemplo para subir un archivo y mostrar su nombre y tipo de contenido
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = model.transcribe(file_location)
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "transcription": result["text"]
        }
