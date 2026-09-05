from fastapi import APIRouter, HTTPException, status, Query, Depends, Request, Response, UploadFile, File
from fastapi.responses import FileResponse
from models import *
from repos import *
from orm import *
from auth import verify_password, create_jwt, password_to_hash, verify_jwt
import anyio
from pathlib import Path

router = APIRouter()
dir_path = anyio.Path("./covers")#env
dir_path.mkdir(exist_ok=True)

def get_user_by_token(request: Request) -> UserModel:
    token = request.cookies.get('access_token')
    if token:
        user = verify_jwt(token)
        if user:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь не авторизирован')

async def ensure_book_author(sess, book_id: int, user: UserModel) -> BookORM:
    book = await sess.get(BookORM, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
    if book.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
    return book

@router.post('/register')
async def register(form: RegisterForm) -> UserModel:
    async with session_fabric() as sess:
        repo = UserRepo(sess)
        is_exist = await repo.get_by_login_or_nickname(form.login, form.nickname)
        if is_exist:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Данное имя занято')

        hashed_pass = password_to_hash(form.raw_password)
        new_user = await repo.create_user(form.login, form.nickname, hashed_pass)

        await sess.commit()
        await sess.refresh(new_user)
        return new_user

@router.post('/login')
async def login(form: LoginFormModel, response: Response):
    async with session_fabric() as sess:
        user = await UserRepo(sess).get_user_by_login(form.login)

        if user and verify_password(form.password, user.hashed_password):
            jwt_token = create_jwt(UserModel.model_validate(user))
            response.set_cookie(key='access_token', value=jwt_token, httponly=True, secure=True, samesite='strict', max_age=30*24*60*60)
            return {'detail': 'Успешный вход'}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный логин или пароль')

@router.get('/users/me')
async def get_me(user: UserModel = Depends(get_user_by_token)) -> UserModel:
    return user

@router.get('/users/{user_id}')
async def get_user(user_id: int) -> UserModel:
    async with session_fabric() as sess:
        user = UserRepo(sess).get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        return user

@router.get('/users/{user_id}/books')
async def get_user_books(user_id: int) -> list[BookModel]:
    async with session_fabric() as sess:
        user = await UserRepo(sess).get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')

        books = await BookRepo(sess).get_user_books(user.id)
        return books

@router.post('/logout')
async def logout(response: Response, user = Depends(get_user_by_token)):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="strict"
    )
    return {'detail': 'Выход выполнен'}

@router.get('/genres')
async def get_genres() -> list[GenreModel]:
        async with session_fabric() as sess:
            genres = await BookRepo(sess).get_genres()
            return genres

@router.post('/genres')
async def create_genre(genre_name: str, user: UserModel = Depends(get_user_by_token)) -> GenreModel:
    async with session_fabric() as sess:
        repo = BookRepo(sess)
        if user.role == 'admin':
            genre = await repo.get_genre_by_name(genre_name)
            if genre:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Такой жанр уже существует')
            
            new_genre = await repo.create_genre(genre_name)
            await sess.commit()
            await sess.refresh(new_genre)

            return new_genre
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

@router.get('/tags')
async def get_tags() -> list[TagModel]:
        async with session_fabric() as sess:
            tags = await BookRepo(sess).get_tags()
            return tags

@router.post('/tags')
async def create_tag(tag_name: str, user: UserModel = Depends(get_user_by_token)) -> TagModel:
    async with session_fabric() as sess:
        repo = BookRepo(sess)
        if user.role == 'admin':
            tag = await repo.get_tag_by_name(tag_name)
            if tag:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Такой тег уже существует')
            
            new_tag = await repo.create_tag(tag_name)
            await sess.commit()
            await sess.refresh(new_tag)

            return new_tag
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

@router.get('/books')
async def get_books(search: str|None = None, genres: list[int] = Query(default=[]),
              tags: list[int] = Query(default=[]), sort_by: BooksSortFields|None = None) -> list[BookModel]:
    async with session_fabric() as sess:
        books = await BookRepo(sess).get_books(search=search, genre_ids=genres, tag_ids=tags, sort_by=sort_by)        
        return books

@router.get('/books/{id}')
async def get_book_by_id(id: int) -> BookModel:
    async with session_fabric() as sess:
        book = await BookRepo(sess).get_book_by_id(id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
        return book

@router.post('/books')
async def create_book(form: BookCreateForm, user: UserModel = Depends(get_user_by_token)) -> BookModel:
    async with session_fabric() as sess:
        repo = BookRepo(sess)
        new_book = await repo.create_book(user.id, **form.model_dump())

        await sess.flush()
        await sess.commit()
        
        return await repo.get_book_by_id(new_book.id)

@router.patch('/books/{book_id}')
async def update_book(book_id: int, form: BookUpdateForm, user: UserModel = Depends(get_user_by_token)) -> BookModel:
        async with session_fabric() as sess:
            repo = BookRepo(sess)
            book = await repo.get_book_by_id(book_id)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
            if book.author_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')
        
            updated_book = await repo.update_book(book, **form.model_dump(exclude_unset=True))

            await sess.commit()
            await sess.refresh(updated_book)

            return updated_book

@router.delete('/books/{book_id}')
async def delete_book(book_id: int, user: UserModel = Depends(get_user_by_token)):
        async with session_fabric() as sess:
            repo = BookRepo(sess)
            book = await repo.get_book_by_id(book_id)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
            if book.author_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

            await repo.delete_book(book)
            await sess.commit()

        return {'detail': 'Книга успешно удалена'}

@router.put('/books/{book_id}/cover')
async def load_book_cover(book_id: int, file: UploadFile = File(...)):
    async with session_fabric() as sess:
        book = await sess.get(BookORM, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    suffix = Path(file.filename).suffix.lower()
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}#env
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"Разрешены форматы: {ALLOWED_EXTENSIONS}")

    async for f in dir_path.glob(str(book_id)+".*"):
        await f.unlink()

    file_path = dir_path.joinpath(str(book_id)+Path(file.filename).suffix)
    content = await file.read()
    await file_path.write_bytes(content)

    return {"filename": str(file_path)}

@router.get('/books/{book_id}/cover')
async def get_book_cover(book_id: int):
    async with session_fabric() as sess:
        book = await sess.get(BookORM, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    cover = None
    async for file in dir_path.glob(str(book_id)+".*"):
        cover = file
        break

    if not cover:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Обложка не найдена')

    return FileResponse(Path(cover))

@router.delete('/books/{book_id}/cover')
async def delete_book_cover(book_id: int):
    async with session_fabric() as sess:
            book = await sess.get(BookORM, book_id)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

    async for file in dir_path.glob(str(book_id)+".*"):
        await file.unlink()

    return {'detail': 'Обложка успешно удалена'}

@router.get('/books/{book_id}/first-sections')
async def get_book_first_section(book_id: int) -> list[SectionPreviewModel]:
    async with session_fabric() as sess:
        book = await sess.get(BookORM, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')

        sections = await SectionRepo(sess).get_book_first_sections(book.id)
        return sections

@router.get('/sections/{section_id}')
async def get_section_by_id(section_id: int) -> SectionModel:
    async with session_fabric() as sess:
        section = await SectionRepo(sess).get_section_by_id(section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')
        return section

@router.post('/sections/first')
async def create_section_first(form: FirstSectionCreateForm, user: UserModel = Depends(get_user_by_token)) -> SectionPreviewModel:
    async with session_fabric() as sess:
        book = await sess.get(BookORM, form.book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга не найдена')
        if book.author_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

        new_section = await SectionRepo(sess).create_first_section(book.id, form.name)
        await sess.commit()

        await sess.refresh(new_section)
        return new_section

@router.post('/sections/after')
async def create_section_after(form: MiddleSectionCreateForm, user: UserModel = Depends(get_user_by_token)) -> SectionPreviewModel:
    async with session_fabric() as sess:
        book = await sess.get(BookORM, form.book_id)
        section = await sess.get(SectionORM, form.after_section_id)
        if not (book and section):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Книга или часть книги с указанным ID не найдена')
        if book.id != section.book_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Указанная часть книги ей не принадлежит')
        if book.author_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')

        new_section = await SectionRepo(sess).create_middle_section(**form.model_dump())
        await sess.commit()

        await sess.refresh(new_section)
        return new_section

@router.get('/sections/{section_id}/next')
async def get_next_sections(section_id: int) -> list[SectionPreviewModel]:
    async with session_fabric() as sess:
        section = await sess.get(SectionORM, section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')

        next_sections = await SectionRepo(sess).get_next_sections(section_id)
        return next_sections

@router.get("/sections/{section_id}")
async def get_section_chapters(section_id: int) -> list[ChapterPreviewModel]:
    async with session_fabric() as sess:
        section = await sess.get(SectionORM, section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')

        chapters = await SectionRepo(sess).get_section_chapters(section_id)
        return chapters

@router.get('/chapters/{chapter_id}')
async def get_chapter_by_id(chapter_id: int) -> ChapterModel:
    async with session_fabric() as sess:
        chapter = await SectionRepo(sess).get_chapter_by_id(chapter_id)
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава с указанным ID не найдена')
        return chapter

@router.post("/chapters/after")
async def create_middle_chapter(form: MiddleChapterCreateForm, user: UserModel = Depends(get_user_by_token)) -> ChapterPreviewModel:
    async with session_fabric() as sess:
        prev_chapter = await sess.get(ChapterORM, form.previous_chapter_id)
        if not prev_chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава с указанным ID не найдена')

        new_chapter = await SectionRepo(sess).create_middle_chapter(form.title, prev_chapter)
        await sess.commit()
        return ChapterPreviewModel.model_validate(new_chapter)

@router.post("/chapters/first")
async def create_first_chapter(form: FirstChapterCreateForm, user: UserModel = Depends(get_user_by_token)) -> ChapterPreviewModel:
    async with session_fabric() as sess:
        section = await sess.get(SectionORM, form.section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')

        new_chapter = await SectionRepo(sess).create_first_chapter(form.section_id, form.title)
        await sess.commit()
        return ChapterPreviewModel.model_validate(new_chapter)

@router.patch("/chapters/{chapter_id}")
async def update_chapter(chapter_id: int, form: ChapterUpdateForm, user: UserModel = Depends(get_user_by_token)) -> ChapterModel:
    async with session_fabric() as sess:
        repo = SectionRepo(sess)
        chapter = await repo.get_chapter_by_id(chapter_id)
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава с указанным ID не найдена')

        section = await sess.get(SectionORM, chapter.section_id)
        await ensure_book_author(sess, section.book_id, user)

        updated = await repo.update_chapter(chapter, form.content)
        await sess.commit()
        return ChapterModel.model_validate(updated)

@router.delete("/chapters/{chapter_id}")
async def delete_chapter(chapter_id: int, user: UserModel = Depends(get_user_by_token)):
    async with session_fabric() as sess:
        repo = SectionRepo(sess)
        chapter = await repo.get_chapter_by_id(chapter_id)
        if not chapter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Глава с указанным ID не найдена')

        section = await sess.get(SectionORM, chapter.section_id)
        await ensure_book_author(sess, section.book_id, user)

        await repo.delete_chapter(chapter)
        await sess.commit()
        return {'detail': 'Глава успешно удалена'}

@router.delete("/sections/{section_id}")
async def delete_section(section_id: int, user: UserModel = Depends(get_user_by_token)):
    async with session_fabric() as sess:
        repo = SectionRepo(sess)
        section = await repo.get_section_by_id(section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Часть книги не найдена')

        await ensure_book_author(sess, section.book_id, user)
        await repo.delete_section(section)
        await sess.commit()
        return {'detail': 'Часть книги успешно удалена'}