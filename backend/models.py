from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator, computed_field, Field


class ChapterShortModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(validation_alias='chapter_id')
    title: str|None

    @computed_field
    def full_title(self) -> str:
        return f'Глава {self.id}' + (f': {self.title}' if self.title else '')


class ChapterFullModel(ChapterShortModel):
    book_id: int
    content: str


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
    genres: list[GenreModel]
    tags: list[TagModel]

    @model_validator(mode="before")
    def getAuthorAnime(data):
        if data.author:
            data.author_name = data.author.nickname
        else:
            data.author_name = "-"
        return data
    @model_validator(mode='before')
    def getGenres(data):
        if data.genres:
            data.genres = [GenreModel.model_validate(genre) for genre in data.genres]
        else:
            data.genres = None
        return data
    @model_validator(mode='before')
    def getTags(data):
        if data.genres:
            data.tags = [TagModel.model_validate(tag) for tag in data.tags]
        else:
            data.tags = None
        return data


class RegisterForm(BaseModel):
    login: str = Field(max_length=32)
    raw_password: str = Field(max_length=16)

class LoginForm(BaseModel):
    login: str
    password: str