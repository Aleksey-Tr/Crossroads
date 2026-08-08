from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator, computed_field, Field


class CharacterShortModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(validation_alias='character_id')
    title: str|None

    @computed_field
    def full_title(self) -> str:
        return f'Глава {self.id}' + (f': {self.title}' if self.title else '')


class CharacterFullModel(CharacterShortModel):
    book_id: int
    content: str


class BooksSortFields(Enum):
    date = "date"
    name = "name"
    default = name


class BookModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    title: str
    description: str
    author_name: str

    @model_validator(mode="before")
    def getAuthorAnime(data):
        if data.author:
            data.author_name = data.author.nickname
        else:
            data.author_name = "-"
        return data