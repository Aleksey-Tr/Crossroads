from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator, Field


class BooksSortFields(Enum):
    date = "date"
    name = "name"

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str = Field(max_length=16)
    login: str = Field(max_length=32)
    nickname: str = Field(max_length=32)

class RegisterForm(BaseModel):
    login: str = Field(max_length=32)
    nickname: str = Field(max_length=32)
    raw_password: str = Field(max_length=16)

class LoginForm(BaseModel):
    login: str
    password: str

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
    author_id: int|None = None
    genres: list[GenreModel]
    tags: list[TagModel]
    published_at: datetime

    author_name: str
    @model_validator(mode="before")
    def getAuthorAnime(data):
        if data.author:
            data.author_name = data.author.nickname
        else:
            data.author_name = "-"
        return data
    
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