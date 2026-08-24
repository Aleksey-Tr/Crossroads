from fastapi import FastAPI, HTTPException, status, Query, Depends, Request, Response
from models import BookModel, BooksSortFields, RegisterForm, LoginForm, GenreModel, TagModel, SectionFullModel, ChapterFullModel, UserModel, BookCreateForm, BookUpdateForm
from repository import repo
from auth import password_to_hash, verify_password, create_jwt, verify_jwt

router = FastAPI()

@router.post('/register', responses={409: {'description': 'Данный логин занят'}})
def register(form: RegisterForm) -> UserModel:
    is_user_exists = repo.get_user_by_login(form.login)
    if is_user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Данный логин занят')

    hashed_pass = password_to_hash(form.raw_password)
    new_user = repo.create_user(login=form.login, hashed_password=hashed_pass)
    return UserModel.model_validate(new_user)

@router.post('/login', responses={401: {'description': 'Неверный логин или пароль'}})
def login(form: LoginForm, response: Response):
    user = repo.get_user_by_login(form.login)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный логин или пароль')

    if verify_password(form.password, user.hashed_password):
        jwt_token = create_jwt(UserModel.model_validate(user))
        response.set_cookie(key='access_token', value=jwt_token, httponly=True, secure=True, samesite='strict', max_age=30*24*60*60)
        return {'detail': 'Успешный вход'}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный логин или пароль')

def get_user_by_token(request: Request) -> UserModel:
    token = request.cookies.get('access_token')
    if token:
        user = verify_jwt(token)
        if user:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не авторизирован')

@router.post('/logout', responses={401: {'description': 'Пользователь не авторизирован'}})
def logout(response: Response, user = Depends(get_user_by_token)):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="strict"
    )
    return {'detail': 'Выход выполнен'}

@router.get('/users/me', responses={401: {'description': 'Пользователь не авторизирован'}})
def get_me(user: UserModel = Depends(get_user_by_token)) -> UserModel:
    return user

@router.get('/books')
def get_books(search: str = "", genres: list[int] = Query(default=[]),
              tags: list[int] = Query(default=[]), sort_by: BooksSortFields|None = None) -> list[BookModel]:
    books_orm = repo.get_books(search=search, genres=genres, tags=tags, sort_by=sort_by, )
    books = [BookModel.model_validate(book_orm) for book_orm in books_orm]
        
    return books

@router.get('/books/{id}', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_book_by_id(id: int) -> BookModel:
    book_orm = repo.get_book_by_id(id)

    if not book_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
        
    return BookModel.model_validate(book_orm)

@router.post('/books', responses={503: {'description': 'Не удалось обработать запрос'}})
def create_book(form: BookCreateForm, user: UserModel = Depends(get_user_by_token)) -> BookModel:
    new_book = repo.create_book(user_id=user.id, form=form)
    if not new_book:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Не удалось обработать запрос. Попробуйте позже.')
    
    return new_book

@router.patch('/books/{book_id}', responses={404: {'description': 'Книга не найдена'}, 403: {'description': 'Недостаточно прав'}})
def update_book(book_id: int, form: BookUpdateForm, user: UserModel = Depends(get_user_by_token)) -> BookModel:
    book = repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    
    updated_book = repo.update_book(book_id=book_id, form=form)
    return updated_book

@router.get('/genres')
def get_genres() -> list[GenreModel]:
    genres_orm = repo.get_genres()
    genres = [GenreModel.model_validate(genre_orm) for genre_orm in genres_orm]

    return genres

@router.post('/genres', responses={403: {'description': 'Недостаточно прав'},
                                 409: {'description': 'Такой жанр уже существует'}})
def create_genre(genre_name: str, user: UserModel = Depends(get_user_by_token)) -> TagModel:
    if user.role == 'admin':
        if repo.get_genre_by_name(genre_name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Такой жанр уже существует')
        
        new_genre = repo.create_genre(genre_name)
        return new_genre
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

@router.get('/tags')
def get_tags() -> list[TagModel]:
    tags_orm = repo.get_tags()
    tags = [TagModel.model_validate(tag) for tag in tags_orm]

    return tags

@router.post('/tags', responses={403: {'description': 'Недостаточно прав'},
                                 409: {'description': 'Такой тег уже существует'}})
def create_tag(tag_name: str, user: UserModel = Depends(get_user_by_token)) -> TagModel:
    if user.role == 'admin':
        if repo.get_tag_by_name(tag_name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Такой тег уже существует')
        
        new_tag = repo.create_tag(tag_name)
        return new_tag
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

@router.get('/books/{book_id}/first-sections', responses={404: {'description': 'Книга или часть книги с указанным ID не найдена'}})
def get_book_first_section(book_id: int) -> list[SectionFullModel]:
    book_orm = repo.get_book_by_id(book_id)
    if not book_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    sections_orm = repo.get_book_first_sections(book_id)
    if not sections_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')
    return [SectionFullModel.model_validate(section_orm) for section_orm in sections_orm]

@router.get('/sections/{section_id}', responses={404: {'description': 'Часть книги с указанным ID не найдена'}})
def get_section_by_id(section_id: int) -> SectionFullModel:
    section_orm = repo.get_section_by_id(section_id)
    if not section_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')
    return SectionFullModel.model_validate(section_orm)

@router.get('/chapters/{chapter_id}', responses={404: {'description': 'Глава с указанным ID не найдена'}})
def get_chapter_by_id(chapter_id: int) -> ChapterFullModel:
    chapter_orm = repo.get_chapter_by_id(chapter_id)
    if not chapter_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава с указанным ID не найдена')
    return ChapterFullModel.model_validate(chapter_orm)