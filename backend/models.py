from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BooksSortFields(Enum):
    date = "date"
    name = "name"

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str = Field(max_length=16)
    #login: str = Field(max_length=32)
    nickname: str = Field(max_length=32)

disallowed_characters = [' ', ':', "'", '"']

class RegisterForm(BaseModel):
    login: str = Field(max_length=32, min_length=4)
    nickname: str = Field(max_length=32, min_length=4)
    raw_password: str = Field(max_length=16, min_length=6)

    @field_validator('login', 'nickname', 'raw_password')
    def check_fields(value: str):
        if any((char in value for char in disallowed_characters)):
            raise ValueError("Недопустимые символы: '"+"' '".join(disallowed_characters)+"'")
        return value
    
class LoginForm(BaseModel):
    login: str = Field(max_length=32, min_length=4)
    password: str = Field(max_length=16, min_length=6)

class GenreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(max_length=64)

class TagModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(max_length=64)

class BookCreateForm(BaseModel):
    title: str = Field(max_length=64)
    description: str|None = None
    genres: list[int]
    tags: list[int]

class BookModel(BookCreateForm):
    model_config = ConfigDict(from_attributes=True)
    id: int
    #author_id: int|None = None
    genres: list[GenreModel]
    tags: list[TagModel]
    published_at: datetime

    author: UserModel|None = None
    
class BookUpdateForm(BaseModel):
    title: str|None = Field(max_length=64, default=None)
    description: str|None = None
    genres: list[int]|None = None
    tags: list[int]|None = None

class SectionShortModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_default: bool
    title: str = Field(max_length=256)

    
class SectionFullModel(SectionShortModel):
    chapters: list['ChapterShortModel'] = []
    next_sections: list[SectionShortModel] = []
    book_id: int
    previous_section: int|None = None

class ChapterShortModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str = Field(max_length=64)

class ChapterFullModel(ChapterShortModel):
    section_id: int
    content: str