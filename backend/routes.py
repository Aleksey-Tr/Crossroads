from fastapi import APIRouter, HTTPException, status, Query, Depends, Request, Response, UploadFile, File
from models import BookModel, BooksSortFields, RegisterForm, LoginForm, GenreModel, TagModel, SectionFullModel, ChapterFullModel, UserModel, BookCreateForm, BookUpdateForm, ChoiceModel, SectionCreateFirstForm, SectionCreateAfterForm, SectionShortModel, ChoiceCreateModel
from repository import repo
from auth import password_to_hash, verify_password, create_jwt, verify_jwt
from pathlib import Path
import shutil
from fastapi.responses import FileResponse
from config import COVERS_DIR

router = APIRouter()
dir_path = Path(COVERS_DIR)
dir_path.mkdir(exist_ok=True)

@router.post('/register', responses={409: {'description': 'Данный логин или имя заняты'}})
def register(form: RegisterForm) -> UserModel:
    is_login_exist = repo.get_user_by_login(form.login)
    is_nickname_exist = repo.get_user_by_nickname(form.nickname)
    if is_login_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Данный логин занят')
    if is_nickname_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Данное имя занято')

    hashed_pass = password_to_hash(form.raw_password)
    new_user = repo.create_user(form)
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
    #401: {'description': 'Пользователь не авторизирован'}

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

@router.get('/users/{user_id}', responses={404: {'description': 'Пользователь не найден'}})
def get_user(user_id: int) -> UserModel:
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
    return user

@router.get('/users/{user_id}/books')
def get_user_books(user_id: int) -> list[BookModel]:
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')

    books = repo.get_user_books(user_id)
    return books

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

@router.post('/books', responses={401: {'description': 'Пользователь не авторизирован'},
                                  503: {'description': 'Не удалось обработать запрос'}})
def create_book(form: BookCreateForm, user: UserModel = Depends(get_user_by_token)) -> BookModel:
    new_book = repo.create_book(user_id=user.id, form=form)    
    return new_book

@router.patch('/books/{book_id}', responses={401: {'description': 'Пользователь не авторизирован'},
                                             403: {'description': 'Недостаточно прав'},
                                             404: {'description': 'Книга не найдена'}})
def update_book(book_id: int, form: BookUpdateForm, user: UserModel = Depends(get_user_by_token)) -> BookModel:
    book = repo.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    
    updated_book = repo.update_book(book_id=book_id, form=form)
    return updated_book

@router.delete('/books/{book_id}', responses={401: {'description': 'Пользователь не авторизирован'},
                                              403: {'description': 'Недостаточно прав'},
                                              404: {'description': 'Книга не найдена'}})
def delete_book(book_id: int, user: UserModel = Depends(get_user_by_token)):
    book = repo.get_simple_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

    repo.delete_book(book)
    return {'detail': 'Книга успешно удалена'}

@router.put('/books/{book_id}/cover')
def load_book_cover(book_id: int, file: UploadFile = File(...)):
    book = repo.get_simple_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    is_file_exist = list(dir_path.glob(str(book_id)+".*"))
    for f in is_file_exist:
        f.unlink()

    file_path = dir_path.joinpath(str(book_id)+Path(file.filename).suffix)
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file_path}

@router.get('/books/{book_id}/cover')
def get_book_cover(book_id: int):
    book = repo.get_simple_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    filename = list(dir_path.glob(str(book_id)+".*"))
    if not filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Обложка не найдена')

    return FileResponse(filename[0])

@router.delete('/books/{book_id}/cover')
def delete_book_cover(book_id: int):
    book = repo.get_simple_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    files = list(dir_path.glob(str(book_id)+".*"))
    if not files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Обложка не найдена')
    
    for f in files:
        f.unlink()
    return {'detail': 'Обложка успешно удалена'}

@router.get('/genres')
def get_genres() -> list[GenreModel]:
    genres_orm = repo.get_genres()
    genres = [GenreModel.model_validate(genre_orm) for genre_orm in genres_orm]

    return genres

@router.post('/genres', responses={401: {'description': 'Пользователь не авторизирован'},
                                   403: {'description': 'Недостаточно прав'},
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

@router.post('/tags', responses={401: {'description': 'Пользователь не авторизирован'},
                                 403: {'description': 'Недостаточно прав'},
                                 409: {'description': 'Такой тег уже существует'}})
def create_tag(tag_name: str, user: UserModel = Depends(get_user_by_token)) -> TagModel:
    if user.role == 'admin':
        if repo.get_tag_by_name(tag_name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Такой тег уже существует')
        
        new_tag = repo.create_tag(tag_name)
        return new_tag
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

@router.get('/books/{book_id}/sections')
def get_book_sections(book_id: int, user: UserModel = Depends(get_user_by_token)) -> list[SectionShortModel]:
    book = repo.get_simple_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

    sections = repo.get_book_sections(book_id)
    return sections

@router.get('/books/{book_id}/first-sections', responses={404: {'description': 'Книга с указанным ID не найдена'}})
def get_book_first_section(book_id: int) -> list[SectionShortModel]:
    book_orm = repo.get_book_by_id(book_id)
    if not book_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    sections_orm = repo.get_book_first_sections(book_id)
    return sections_orm

@router.get('/sections/{section_id}', responses={404: {'description': 'Часть книги с указанным ID не найдена'}})
def get_section_by_id(section_id: int) -> SectionFullModel:
    section_orm = repo.get_section_by_id(section_id)
    if not section_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')
    return section_orm

@router.post('/sections/first', responses={403: {'description': 'Недостаточно прав'},
                                           404: {'description': 'Книга с указанным ID не найдена'}})
def create_section_first(form: SectionCreateFirstForm, user: UserModel = Depends(get_user_by_token)) -> SectionShortModel:
    book = repo.get_simple_book(form.book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

    new_section = repo.create_section_first(form)
    return new_section

@router.post('/sections/after', responses={400: {'description': 'Указанная часть книги ей не принадлежит'},
                                           403: {'description': 'Недостаточно прав'},
                                           404: {'description': 'Книга или часть книги с указанным ID не найдена'}})
def create_section_after(form: SectionCreateAfterForm, user: UserModel = Depends(get_user_by_token)) -> SectionShortModel:
    book = repo.get_simple_book(form.book_id)
    section = repo.get_simple_section(form.after_section_id)
    if not (book and section):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга или часть книги с указанным ID не найдена')
    if book.id != section.book_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Указанная часть книги ей не принадлежит')
    if book.author_id != user.id:
        raise HTTPException
    if not repo.get_simple_section(form.after_section_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

    new_section = repo.create_section_after(form)
    return new_section

# @router.post('/choice', responses={400: {'description': 'Указанная часть книги ей не принадлежит'},
#                                     403: {'description': 'Недостаточно прав'},
#                                     404: {'description': 'Книга или часть книги с указанным ID не найдена'}})
# def create_choice(form: ChoiceCreateModel, user: UserModel = Depends(get_user_by_token)) -> ChoiceModel:
#     book = repo.get_simple_book(form.book_id)
#     from_section = repo.get_simple_section(form.from_section_id)
#     to_section = repo.get_simple_section(form.to_section_id)

#     if not (book and from_section and to_section):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга или часть книги с указанным ID не найдена')
#     if book.author_id != user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
#     if book.id != from_section.book_id or book.id != to_section.book_id:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Указанная часть книги ей не принадлежит')

#     new_choice = repo.create_choice(form)
#     return new_choice

@router.delete('/choice')
def delete_choice(choice_id: int, user: UserModel = Depends(get_user_by_token)):
    choice = repo.get_choice(choice_id)
    if not choice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги с указанным ID не найдена')
    
    book = repo.get_book_by_choice(choice_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга с указанным ID не найдена')

    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

    repo.delete_choice(choice_id)
    return {'detail': 'Выбор успешно удалён'}
        
@router.get('/sections/{section_id}/choices', responses={404: {'description': 'Часть книги с указанным ID не найдена'}})
def get_section_choices(section_id: int) -> list[ChoiceModel]:
    section_orm = repo.get_section_by_id(section_id)
    if not section_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')

    choices_orm = repo.get_section_choices(section_id)
    return choices_orm

@router.post('/sections/{section_id}/choices')
def create_section_choice(section_id: int, form: ChoiceCreateModel, user: UserModel = Depends(get_user_by_token)) -> ChoiceModel:
    section = repo.get_simple_section(section_id)
    next_section = repo.get_simple_section(form.to_section_id)
    if not (section and next_section):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги с указанным ID не найдена')

    book = repo.get_simple_book(section.book_id)
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

    return repo.create_choice(section_id, form)



@router.get('/chapters/{chapter_id}', responses={404: {'description': 'Глава с указанным ID не найдена'}})
def get_chapter_by_id(chapter_id: int) -> ChapterFullModel:
    chapter_orm = repo.get_chapter_by_id(chapter_id)
    if not chapter_orm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава с указанным ID не найдена')
    return ChapterFullModel.model_validate(chapter_orm)