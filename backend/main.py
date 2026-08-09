from fastapi import FastAPI, HTTPException, status
from models import BookModel, BooksSortFields, CharacterFullModel, CharacterShortModel
from repository import repo

app = FastAPI()

@app.post('/auth/login')
def login():
    ...

@app.post('/auth/register')
def register():
    ...

@app.post('/books')
def create_book():
    ...

@app.get('/books')
def get_books(search: str = "", sort_by: BooksSortFields = BooksSortFields.default) -> list[BookModel]:
    books_orm = repo.get_books(search, sort_by)
    books = [BookModel.model_validate(book_orm) for book_orm in books_orm]
        
    return books

@app.get('/books/{book_id}', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_book_by_id(id: int) -> BookModel:
    book_orm = repo.get_book_by_id(id)

    if not book_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
        
    return BookModel.model_validate(book_orm)

@app.post('/books/{book_id}/characters')
def create_character():
    ...

@app.get('/books/{book_id}/characters', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_characters(book_id: int) -> list[CharacterShortModel]:
    book = repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    characters_orm = repo.get_characters(book_id)
    characters = [CharacterShortModel.model_validate(character_orm) for character_orm in characters_orm]

    return characters

@app.get('/books/{book_id}/characters/{characterId}', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_character(book_id: int, character_id: int) -> CharacterFullModel:
    book = repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    character_orm = repo.get_character_by_id(book_id, character_id)
    if not character_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава не найдена')

    character = CharacterFullModel.model_validate(character_orm)
    return character