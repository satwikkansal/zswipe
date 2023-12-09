import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status as http_status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import pyotp
import uvicorn


from logger import get_logger
from storage import upload_to_filecoin
from utils import ErrorHandlerRoute

load_dotenv()
logger = get_logger(__name__)

app = FastAPI(
    title='f5 API', description='', version='0.1',
)
app.router.route_class = ErrorHandlerRoute


# TODO: This needs to be tuned
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def send_validation_error(detail):
    logger.error(f"Validation error: {detail}")
    raise HTTPException(status_code=422, detail=detail)


def validate_body(body) -> bool:
    return True


def get_totp():
    return pyotp.TOTP(os.getenv('TOTP_SECRET'))


@app.get('/')
async def status():
    return 'OK'


@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    file_content = await file.read()
    file_url = upload_to_filecoin(file_content, os.environ['NFT_STORAGE_API_KEY'])
    if file_url:
        return {"file_url": file_url}
    else:
        return {"error": "File upload failed"}


@app.on_event('startup')
async def startup():
    pass


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run('main:app', host="0.0.0.0", port=80, reload=True)
