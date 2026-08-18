from config import database_url
from models import BooksSortFields
from sqlalchemy import desc, asc, create_engine, ForeignKey, String, select, Text, and_, Table, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, joinedload, relationship, undefer
from datetime import datetime

class Base(DeclarativeBase):
    pass

book_to_genre = Table('book_to_genre', Base.metadata,
                      Column('book_id', ForeignKey('books.id')),
                      Column('genre_id', ForeignKey('genres.id')))
book_to_tag = Table('book_to_tag', Base.metadata,
                    Column('book_id', ForeignKey('books.id')),
                    Column('tag_id', ForeignKey('tags.id')))

class UsersRepo(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(16) ,default='user', nullable=False)
    login: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    books = relationship('BooksRepo', back_populates='author')


class BooksRepo(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int|None] = mapped_column(ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str|None] = mapped_column(nullable=True)
    published_at: Mapped[datetime] = mapped_column(nullable=False)

    author: Mapped[UsersRepo] = relationship(back_populates='books')
    genres: Mapped[list['GenresRepo']] = relationship(secondary=book_to_genre, back_populates='books')
    tags: Mapped[list['TagsRepo']] = relationship(secondary=book_to_tag, back_populates='books')
    sections: Mapped['SectionsRepo'] = relationship(back_populates='book')

class GenresRepo(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    books: Mapped[list[BooksRepo]] = relationship(secondary=book_to_genre, back_populates='genres')

class TagsRepo(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    books: Mapped[BooksRepo] = relationship(secondary=book_to_tag, back_populates='tags')

class SectionsRepo(Base):
    __tablename__ = 'sections'

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    is_default: Mapped[bool] = mapped_column(nullable=False, default=False)
    previous_section: Mapped[int|None] = mapped_column(ForeignKey('sections.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)

    book: Mapped[BooksRepo] = relationship(back_populates='sections')
    chapters: Mapped[list['ChaptersRepo']] = relationship(back_populates='section')
    next_sections: Mapped[list['SectionsRepo']] = relationship()

class ChaptersRepo(Base):
    __tablename__ = 'chapters'

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'), nullable=False)
    title: Mapped[str|None] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, deferred=True)

    section: Mapped[SectionsRepo] = relationship(back_populates='chapters')



class Repository():
    def __init__(self):
        self.url = database_url
        engine = create_engine(self.url)
        self.session = sessionmaker(engine)

    def get_books(self, search: str, genres: list[int] = None,
                  tags: list[int] = None, sort_by:BooksSortFields|None = None) -> list[BooksRepo]:

        #добавить другие сортировки
        sort_option = {BooksSortFields.name: asc(BooksRepo.title), BooksSortFields.date: desc(BooksRepo.published_at)}.get(sort_by, desc(BooksRepo.published_at))

        sql = select(BooksRepo).order_by(sort_option).options(
            joinedload(BooksRepo.author), joinedload(BooksRepo.genres), joinedload(BooksRepo.tags))
        if genres:
            genre_conditions = [BooksRepo.genres.any(GenresRepo.id == gid) for gid in genres]
            sql = sql.where(and_(*genre_conditions))
        if tags:
            tags_conditions = [BooksRepo.tags.any(TagsRepo.id == tid) for tid in tags]
            sql = sql.where(and_(*tags_conditions))
        if search:
            sql = sql.where(BooksRepo.title.ilike(f'%{search}%'))

        with self.session() as sess:
            result = sess.scalars(sql).unique().all()
        return result

    def get_book_by_id(self, id: int) -> BooksRepo|None:
        with self.session() as sess:
            sql = select(BooksRepo).where(BooksRepo.id == id).options(
            joinedload(BooksRepo.author), joinedload(BooksRepo.genres), joinedload(BooksRepo.tags))
            result = sess.scalars(sql).unique().one_or_none()
        return result

    def get_genres(self) -> list[GenresRepo]:
        with self.session() as sess:
            sql = select(GenresRepo)
            result = sess.scalars(sql).all()
        return result

    def get_tags(self) -> list[TagsRepo]:
        sql = select(TagsRepo)
        with self.session() as sess:
            result = sess.scalars(sql).all()
        return result

    def get_book_first_sections(self, book_id: int) -> list[SectionsRepo]:
        sql = select(SectionsRepo).where(
            SectionsRepo.book_id == book_id,
            SectionsRepo.previous_section.is_(None)).options(
                joinedload(SectionsRepo.chapters), joinedload(SectionsRepo.next_sections))

        with self.session() as sess:
            result = sess.scalars(sql).unique().all()
        return result

    def get_section_by_id(self, section_id: int) -> SectionsRepo|None:
        sql = select(SectionsRepo).where(SectionsRepo.id == section_id).options(
            joinedload(SectionsRepo.chapters), joinedload(SectionsRepo.next_sections))

        with self.session() as sess:
            result = sess.scalars(sql).unique().one_or_none()
        return result

    def get_chapter_by_id(self, chapter_id: int) -> ChaptersRepo:
        sql = select(ChaptersRepo).where(ChaptersRepo.id == chapter_id).options(undefer(ChaptersRepo.content))
        
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def get_user_by_login(self, login: str) -> UsersRepo|None:
        with self.session() as sess:
            sql = select(UsersRepo).where(UsersRepo.login == login)
            result = sess.scalars(sql).one_or_none()

        return result

    def create_user(self, login: str, hashed_password: str):
        new_user = UsersRepo(login=login, hashed_password=hashed_password, nickname=login)
        with self.session() as sess:
            sess.add(new_user)
            sess.commit()
            sess.refresh(new_user)
        return new_user

    
repo = Repository()