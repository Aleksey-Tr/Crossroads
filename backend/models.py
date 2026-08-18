from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator, computed_field, Field


class BooksSortFields(Enum):
    date = "date"
    name = "name"
    default = name

class GenreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(max_length=64)

class TagModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(max_length=64)

class BookModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int|None
    title: str
    description: str|None
    #published_at

    author_name: str
    genres: list[GenreModel] = list()
    tags: list[TagModel] = list()

    @model_validator(mode="before")
    def getAuthorAnime(data):
        if data.author:
            data.author_name = data.author.nickname
        else:
            data.author_name = "-"
        return data

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

class RegisterForm(BaseModel):
    login: str = Field(max_length=32)
    raw_password: str = Field(max_length=16)

class LoginForm(BaseModel):
    login: str
    password: str