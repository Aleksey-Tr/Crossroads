from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator

class CharacterShortModel(BaseModel):
    id: int
    title: str

class CharacterFullModel(CharacterShortModel):
    bookId: int
    content: str

class BooksSortFields(Enum):
    date = "date"
    name = "name"

    @classmethod
    def default(cls):
        return cls.name

class BookModel(BaseModel):
    id: int
    authorId: int
    title: str
    description: str
    authorName: str

    @model_validator(mode='before')
    def getAuthorAnime(data):
        if data.author:
            data.authorName = data.author.nickname
        else:
            data.authorName = '-'        
        return data
    
    model_config = ConfigDict(from_attributes=True)