from fastapi import FastAPI
from models import BookModel, BooksSortFields, CharacterFullModel, CharacterShortModel
from repository import repo

app = FastAPI()

@app.post('/books')
def create_book():
    ...

@app.get('/books')
def get_books(search: str = "", sort_by: BooksSortFields = BooksSortFields.default) -> list[BookModel]:
    books_orm = repo.get_books(search, sort_by)
    books = [BookModel.model_validate(book_orm) for book_orm in books_orm]
        
    return books

@app.get('/books/{book_id}')
def get_book_by_id(id: int) -> BookModel:
    book_orm = repo.get_book_by_id(id)
    book = BookModel.model_validate(book_orm)

    return book

@app.get('/books/{book_id}/characters')
def get_characters(book_id: int) -> list[CharacterShortModel]:
    characters_orm = repo.get_characters(book_id)
    characters = [CharacterShortModel.model_validate(character_orm) for character_orm in characters_orm]

    return characters

@app.get('/books/{book_id}/characters/{characterId}')
def get_character(book_id: int, character_id: int) -> CharacterFullModel:
    ...