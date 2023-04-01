from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()

security_without_auto_error = HTTPBasic(auto_error=False)
