import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import pyotp
import uvicorn

from logger import get_logger
from utils import ErrorHandlerRoute

load_dotenv()
logger = get_logger(__name__)
auth_token = os.environ['AUTH_TOKEN']

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


@app.get('/basic_auth')
async def get_config(token=Depends(HTTPBearer())):
    creds = token.credentials
    if creds != auth_token:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Invalid auth token")
    return 'OK'


@app.post('/basic_auth_and_2fa',)
def update_config_and_save(token=Depends(HTTPBearer()), totp=Depends(get_totp)):
    items = token.credentials.split(':', 1)
    if len(items) < 2:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN,
                            detail=f'Invalid credentials provided : {token.credentials}')
    req_auth_token = items[0]
    otp_code = items[1]

    if req_auth_token != auth_token:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN,
                            detail=f'Invalid auth token : {token.credentials}')

    # verify otp code
    if not totp.verify(otp_code):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN,
                            detail=f'Can not verify otp : {token.credentials}')

    return 'OK'


@app.on_event('startup')
async def startup():
    pass


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run('main:app', host="0.0.0.0", port=80, reload=True)
