from pydantic import BaseModel, validator
from fastapi import HTTPException, status

from controllers.mail import is_email_valid


class AccountBase(BaseModel):
    firstName: str
    lastName: str
    email: str

    class Config:
        orm_mode = True



class AccountRegistration(AccountBase):
    password: str

    @validator("firstName", "lastName", "password", pre=True, always=True)
    def validate_attributes(cls, attribute):
        if not attribute or not attribute.strip():
            print(attribute)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return attribute.strip()
    

    @validator("email", pre=True, always=True)
    def validate_email(cls, email):
        if not email or not email.strip() or not is_email_valid(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return email


class AccountOut(AccountBase):
    id: int


class Account(AccountRegistration, AccountOut):
    pass