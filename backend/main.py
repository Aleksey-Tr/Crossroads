from fastapi import FastAPI
from models.BookModels import BooksSortFields, BookModel, CharacterShortModel, CharacterFullModel
from repo.BooksRepo import bookRepo

app = FastAPI()

@app.post('/books')
def createBook():
    ...

@app.get('/books')
def getBooks(search: str = "", sortBy: BooksSortFields = BooksSortFields.default()) -> list[BookModel]:
    booksOrm = bookRepo.getBooks(search, sortBy)
    books = [BookModel.model_validate(bookOrm) for bookOrm in booksOrm]
        
    return books

@app.get('/books/{bookId}')
def getBook(bookId: int) -> BookModel:
    ...

@app.get('/books/{bookId}/characters')
def getCharacters(bookId: int) -> list[CharacterShortModel]:
    ...

@app.get('/books/{bookId}/characters/{characterId}')
def getCharacter(bookId: int, characterId: int) -> CharacterFullModel:
    ...