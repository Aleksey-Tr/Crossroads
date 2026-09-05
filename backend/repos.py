from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import and_, select, desc, asc, or_
from sqlalchemy.orm import joinedload, undefer
from orm import *
from config import DB_URL

__all__ = ["session_fabric", "UserRepo", "BookRepo", "SectionRepo"]

db_url = DB_URL
engine = create_async_engine(db_url)
session_fabric = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class BaseRepo():
    def __init__(self, session: AsyncSession):
        self.session = session

class UserRepo(BaseRepo):
    async def get_user_by_login(self, login: str) -> UserORM|None:
        sql = select(UserORM).where(UserORM.login == login).options(undefer(UserORM.hashed_password))
        result = await self.session.execute(sql)
        return result.scalars().one_or_none()

    async def get_by_login_or_nickname(self, login: str, nickname: str) -> list[UserORM]:
        sql = select(UserORM).where(or_(UserORM.login == login, UserORM.nickname == nickname))
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def create_user(self, login: str, nickname: str, hashed_password: str) -> UserORM:
        new_user = UserORM(login=login, nickname=nickname, hashed_password=hashed_password)
        self.session.add(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> UserORM|None:
        sql = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(sql)
        return result.scalars().one_or_none()
    
class BookRepo(BaseRepo):
    async def get_genres(self) -> list[GenreORM]:
        sql = select(GenreORM)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_genre_by_name(self, genre_name: str) -> GenreORM|None:
        sql = select(GenreORM).where(GenreORM.name == genre_name)
        result = await self.session.execute(sql)
        return result.scalars().one_or_none()

    async def create_genre(self, genre_name: str) -> GenreORM:
        new_genre = GenreORM(name=genre_name)
        self.session.add(new_genre)
        return new_genre

    async def get_tags(self) -> list[TagORM]:
        sql = select(TagORM)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_tag_by_name(self, tag_name: str) -> TagORM|None:
        sql = select(TagORM).where(TagORM.name == tag_name)
        result = await self.session.execute(sql)
        return result.scalars().one_or_none()

    async def create_tag(self, tag_name: str) -> TagORM:
        new_tag = TagORM(name=tag_name)
        self.session.add(new_tag)
        return new_tag

    async def get_books(self, search: str|None = None, genre_ids: list[int] = None,
                  tag_ids: list[int] = None, sort_by: str|None = None) -> list[BookORM]:

        sort_option = {"name": asc(BookORM.title), "date": desc(BookORM.published_at)}.get(sort_by, desc(BookORM.published_at))

        sql = select(BookORM).order_by(sort_option).options(
            joinedload(BookORM.author), joinedload(BookORM.genres), joinedload(BookORM.tags))
        if genre_ids:
            genre_conditions = [BookORM.genres.any(GenreORM.id == gid) for gid in genre_ids]
            sql = sql.where(and_(*genre_conditions))
        if tag_ids:
            tag_conditions = [BookORM.tags.any(TagORM.id == tid) for tid in tag_ids]
            sql = sql.where(and_(*tag_conditions))
        if search:
            sql = sql.where(BookORM.title.ilike(f'%{search}%'))

        result = await self.session.execute(sql)
        return result.scalars().unique().all()

    async def get_book_by_id(self, book_id: int) -> BookORM|None:
        sql = select(BookORM).where(BookORM.id == book_id).options(
                    joinedload(BookORM.author), joinedload(BookORM.genres), joinedload(BookORM.tags))
        result = await self.session.execute(sql)
        return result.scalars().unique().one_or_none()

    async def create_book(self, user_id: int, **kwargs) -> BookORM:
        genre_ids = kwargs.pop("genres", None)
        tag_ids = kwargs.pop("tags", None)

        genres = []
        if genre_ids:
            sql = select(GenreORM).where(GenreORM.id.in_(genre_ids))
            result = await self.session.execute(sql)
            genres = result.scalars().all()

        tags = []
        if tag_ids:
            sql = select(TagORM).where(TagORM.id.in_(tag_ids))
            result = await self.session.execute(sql)
            tags = result.scalars().all()

        new_book = BookORM(author_id=user_id, genres=genres, tags=tags, **kwargs)
        self.session.add(new_book)
        return new_book

    async def update_book(self, book_orm: BookORM, **kwargs) -> BookORM:
        genre_ids = kwargs.pop("genres", None)
        tag_ids = kwargs.pop("tags", None)

        for key, val in kwargs.items():
            setattr(book_orm, key, val)

        genres = []
        if genre_ids:
            sql = select(GenreORM).where(GenreORM.id.in_(genre_ids))
            result = await self.session.execute(sql)
            genres = result.scalars().all()
            book_orm.genres = genres

        tags = []
        if tag_ids:
            sql = select(TagORM).where(TagORM.id.in_(tag_ids))
            result = await self.session.execute(sql)
            tags = result.scalars().all()
            book_orm.tags = tags

        self.session.flush()
        return book_orm
    
    async def delete_book(self, book: BookORM):
        await self.session.delete(book)

    async def get_user_books(self, user_id: int) -> list[BookORM]:
        sql = select(BookORM).where(BookORM.author_id == user_id).options(
        joinedload(BookORM.author), joinedload(BookORM.genres), joinedload(BookORM.tags))
        result = await self.session.execute(sql)
        return result.scalars().unique().all()

class SectionRepo(BaseRepo):
    def __init__(self, session):
        super().__init__(session)
        self.position_step = 10
        
    async def get_book_first_sections(self, book_id: int) -> list[SectionORM]:
        sql = select(SectionORM).where(SectionORM.book_id == book_id, SectionORM.previous_section_id.is_(None))
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_section_by_id(self, section_id: int) -> SectionORM|None:
        sql = select(SectionORM).where(SectionORM.id == section_id).options(
            joinedload(SectionORM.chapters))
        result = await self.session.execute(sql)
        return result.scalars().unique().one_or_none()
    
    async def get_next_sections(self, section_id: int) -> list[SectionORM]:
        sql = select(SectionORM).where(SectionORM.previous_section_id == section_id)
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def create_first_section(self, book_id: int, name: str) -> SectionORM:
        new_section = SectionORM(book_id=book_id, name=name, previous_section_id=None)
        self.session.add(new_section)
        return new_section

    async def create_middle_section(self, book_id: int, after_section_id: int, name: str) -> SectionORM:
        new_section = SectionORM(book_id=book_id, previous_section_id=after_section_id, name=name)
        self.session.add(new_section)
        return new_section

    async def get_section_chapters(self, section_id: int) -> list[ChapterORM]:
        sql = select(ChapterORM).where(ChapterORM.section_id == section_id).order_by(asc(ChapterORM.position))
        result = await self.session.execute(sql)
        return result.scalars().all()

    async def get_chapter_by_id(self, chapter_id: int) -> ChapterORM|None:
        sql = select(ChapterORM).where(ChapterORM.id == chapter_id).options(undefer(ChapterORM.content))
        result = await self.session.execute(sql)
        return result.scalars().one_or_none()

    async def create_first_chapter(self, section_id: int, title: str) -> ChapterORM:
        new_position = self.position_step

        sql = select(ChapterORM).where(and_(ChapterORM.section_id==section_id, ChapterORM.previous_chapter_id.is_(None)))
        result = await self.session.execute(sql)
        next_chapter = result.scalars().one_or_none()
        if next_chapter:
            new_position = next_chapter.position-self.position_step
    
        new_chapter = ChapterORM(section_id=section_id, title=title, content="", previous_chapter_id=None, next_chapter=next_chapter, position=new_position)
        self.session.flush()
        
        if next_chapter:
            next_chapter.previous_chapter = new_chapter
        await self.session.flush()

        return new_chapter

    async def create_middle_chapter(self, title: str, left_chapter: ChapterORM) -> ChapterORM:
        right_chapter = None
        new_position = left_chapter.position+self.position_step

        if left_chapter.next_chapter_id:
            right_chapter = await self.session.get(ChapterORM, left_chapter.next_chapter_id)
            if right_chapter.position-left_chapter.position <= 1:
                self.recalculate_positions(left_chapter.section_id)            
            new_position = int((left_chapter.position+right_chapter.position)/2)

        new_chapter = ChapterORM(section_id=left_chapter.section_id, title=title, position=new_position, left_chapter=left_chapter, right_chapter=right_chapter)
        await self.session.flush()

        left_chapter.next_chapter_id = new_chapter.id
        if right_chapter:
            right_chapter.previous_chapter_id = new_chapter.id

        await self.session.flush()
        return new_chapter

    async def recalculate_positions(self, section_id: int):
        chapters = await self.get_section_chapters(section_id)
        for index, chapter in enumerate(chapters, 1):
            chapter.position = index*self.position_step
        self.session.flush()