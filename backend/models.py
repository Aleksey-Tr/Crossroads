from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

__all__ = ["BooksSortFields", "RegisterForm", "LoginFormModel", "UserModel", "GenreModel", "TagModel", "BookCreateForm", "BookModel", "BookUpdateForm",
           "SectionPreviewModel", "SectionModel", "FirstSectionCreateForm", "MiddleSectionCreateForm", "ChapterPreviewModel", "ChapterModel", "FirstChapterCreateForm", "MiddleChapterCreateForm", "ChapterUpdateForm"]

class BooksSortFields(Enum):
    date = "date"
    name = "name"

class ResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class RegisterForm(BaseModel):
    login: str = Field(max_length=32, min_length=4)
    nickname: str = Field(max_length=32, min_length=4)
    raw_password: str = Field(max_length=16, min_length=6)

    @field_validator('login', 'nickname', 'raw_password')
    def check_fields(value: str):
        disallowed_characters = [' ', ':', "'", '"']
        if any((char in value for char in disallowed_characters)):
            raise ValueError("Недопустимые символы: '"+"' '".join(disallowed_characters)+"'")
        return value

class LoginFormModel(BaseModel):
    login: str = Field(max_length=32, min_length=4)
    password: str = Field(max_length=16, min_length=6)

class UserModel(ResponseModel):
    id: int
    role: str
    nickname: str

class GenreModel(ResponseModel):
    id: int
    name: str

class TagModel(ResponseModel):
    id: int
    name: str

class BookCreateForm(BaseModel):
    title: str = Field(max_length=64)
    description: str|None = None
    genres: list[int]|None = None
    tags: list[int]|None = None

class BookModel(BookCreateForm, ResponseModel):
    id: int
    genres: list[GenreModel]
    tags: list[TagModel]
    published_at: datetime

    author: UserModel|None = None

class BookUpdateForm(BaseModel):
    title: str|None = Field(max_length=64, default=None)
    description: str|None = None
    genres: list[int]|None = None
    tags: list[int]|None = None

class FirstSectionCreateForm(BaseModel):
    book_id: int
    name: str = Field(max_length=256)

class MiddleSectionCreateForm(FirstSectionCreateForm):
    after_section_id: int

class SectionPreviewModel(FirstSectionCreateForm, ResponseModel):
    id: int
    previous_section_id: int|None

class SectionModel(SectionPreviewModel):
    chapters: list['ChapterPreviewModel'] = []

class ChapterPreviewModel(ResponseModel):
    id: int
    title: str
    position: int

class ChapterModel(ChapterPreviewModel):
    section_id: int
    previous_chapter_id: int|None
    next_chapter_id: int|None
    content: str

class FirstChapterCreateForm(BaseModel):
    section_id: int
    title: str = Field(max_length=64)

class MiddleChapterCreateForm(BaseModel):
    title: str = Field(max_length=64)
    previous_chapter_id: int

class ChapterUpdateForm(BaseModel):
    content: str