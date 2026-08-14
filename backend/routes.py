from fastapi import FastAPI, HTTPException, status, Query
from models import BookModel, BooksSortFields, ChapterFullModel, ChapterShortModel, RegisterForm, LoginForm, GenreModel
from repository import repo
from auth import password_to_hash, verify_password

router = FastAPI()

@router.post('/auth/login',responses={401: {'description': 'Неверный логин или пароль'}})
def login(form: LoginForm):
    user = repo.get_user_by_login(form.login)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный логин или пароль')

    if verify_password(form.password, user.hashed_password):
        return 'успешный логин' #добавить токен

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный логин или пароль')

@router.post('/auth/register', responses={409: {'description': 'Данный логин занят'}})
def register(form: RegisterForm):
    is_user_exists = repo.get_user_by_login(form.login)
    if is_user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Данный логин занят')

    new_user = repo.create_user(form.login, password_to_hash(form.raw_password))
    return f"Пользователь с логином {new_user.login} создан"

@router.post('/books')
def create_book():
    ...

@router.get('/books')
def get_books(search: str = "", genres: list[int] = Query(default=[]), sort_by: BooksSortFields = BooksSortFields.default) -> list[BookModel]:
    books_orm = repo.get_books(search, genres, sort_by)
    books = [BookModel.model_validate(book_orm) for book_orm in books_orm]
        
    return books

@router.get('/books/{id}', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_book_by_id(id: int) -> BookModel:
    book_orm = repo.get_book_by_id(id)

    if not book_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
        
    return BookModel.model_validate(book_orm)

@router.get('/genres')
def get_genres() -> list[GenreModel]:
    genres_orm = repo.get_genres()
    genres = [GenreModel.model_validate(genre_orm) for genre_orm in genres_orm]

    return genres

@router.post('/books/{book_id}/chapters')
def create_chapter():
    ...

@router.get('/books/{book_id}/chapters', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_chapters(book_id: int) -> list[ChapterShortModel]:
    book = repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    chapters_orm = repo.get_chapters(book_id)
    chapters = [ChapterShortModel.model_validate(chapter_orm) for chapter_orm in chapters_orm]

    return chapters

@router.get('/books/{book_id}/chapters/{chapter_id}', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_chapter(book_id: int, chapter_id: int) -> ChapterFullModel:
    book = repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    chapter_orm = repo.get_chapter_by_id(book_id, chapter_id)
    if not chapter_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава не найдена')

    chapter = ChapterFullModel.model_validate(chapter_orm)
    return chapter