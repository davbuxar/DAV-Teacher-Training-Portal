from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class TeacherRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    mobile: str
    whatsapp: str | None = None
    school: str = Field(min_length=2, max_length=180)
    subjects: list[str] = Field(min_length=1)
    levels: list[str] = Field(min_length=1)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value):
        value = " ".join(value.split())
        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise ValueError("Name must contain English letters and spaces only.")
        return value.title()

    @field_validator("mobile", "whatsapp")
    @classmethod
    def validate_mobile(cls, value):
        if value is None or value == "":
            return None
        if not re.fullmatch(r"[1-9][0-9]{9}", value):
            raise ValueError("Enter a valid 10-digit mobile number not starting with 0.")
        return value

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    training_date: str
    venue: str | None = None
    subject: str | None = None
    level: str | None = None
