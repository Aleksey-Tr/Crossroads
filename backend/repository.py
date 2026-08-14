from config import database_url
from models import BooksSortFields
from sqlalchemy import create_engine, ForeignKey, String, select, Text, and_, Table, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, joinedload, relationship, undefer

class Base(DeclarativeBase):
    pass

book_to_genre = Table('book_to_genre', Base.metadata,
                      Column('book_id', ForeignKey('books.id')),
                      Column('genre_id', ForeignKey('genres.id')))
book_to_tag = Table('book_to_tag', Base.metadata,
                    Column('book_id', ForeignKey('books.id')),
                    Column('tag_id', ForeignKey('tags.id')))

class UserRepo(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(16) ,default='user', nullable=False)
    login: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    books = relationship('BookRepo', back_populates='author')


class BookRepo(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str|None] = mapped_column(nullable=True)

    author: Mapped[UserRepo] = relationship(back_populates='books')
    genres: Mapped[list['GenreRepo']] = relationship(secondary=book_to_genre, back_populates='books')
    tags: Mapped[list['TagsRepo']] = relationship(secondary=book_to_tag, back_populates='books')

class GenreRepo(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    books: Mapped[list[BookRepo]] = relationship(secondary=book_to_genre, back_populates='genres')

class TagsRepo(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    books: Mapped[BookRepo] = relationship(secondary=book_to_tag, back_populates='tags')

class ChapterRepo(Base):
    __tablename__ = 'chapters'

    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), primary_key=True)
    chapter_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text, deferred=True, nullable=False)



class Repository():
    def __init__(self):
        self.url = database_url
        engine = create_engine(self.url)
        self.session = sessionmaker(engine)

    def get_books(self, search: str, genres: list[int] = None,
                  tags: list[int] = None, sort_by:BooksSortFields = BooksSortFields.default) -> list[BookRepo]:

        #добавить другие сортировки
        sort_column = {BooksSortFields.name: BookRepo.title}[sort_by]

        sql = select(BookRepo).order_by(sort_column.desc()).options(joinedload(BookRepo.author), joinedload(BookRepo.genres), joinedload(BookRepo.tags))
        if genres:
            genre_conditions = [BookRepo.genres.any(GenreRepo.id == gid) for gid in genres]
            sql = sql.where(and_(*genre_conditions))
        if tags:
            tags_conditions = [BookRepo.tags.any(TagsRepo.id == tid) for tid in tags]
            sql = sql.where(and_(*tags_conditions))
        if search:
            sql = sql.where(BookRepo.title.ilike(f'%{search}%'))

        with self.session() as sess:
            result = sess.scalars(sql).unique().all()
        return result

    def get_book_by_id(self, id: int) -> BookRepo|None:
        with self.session() as sess:
            sql = select(BookRepo).where(BookRepo.id == id).options(joinedload(BookRepo.author))
            result = sess.scalars(sql).one_or_none()
        return result

    def get_genres(self) -> list[GenreRepo]:
        with self.session() as sess:
            sql = select(GenreRepo)
            result = sess.scalars(sql).all()
        return result

    def get_tags(self) -> list[TagsRepo]:
        sql = select(TagsRepo)
        with self.session() as sess:
            result = sess.scalars(sql).all()
        return result

    def get_chapters(self, book_id: int) -> list[ChapterRepo]:
        with self.session() as sess:
            sql = select(ChapterRepo).where(ChapterRepo.book_id == book_id)
            result = sess.scalars(sql).all()

        return result

    def get_chapter_by_id(self, book_id: int, chapter_id: int) -> ChapterRepo:
        with self.session() as sess:
            sql = select(ChapterRepo).where(
                and_(ChapterRepo.book_id == book_id, ChapterRepo.chapter_id == chapter_id)
                ).options(undefer(ChapterRepo.content))
            result = sess.scalars(sql).one_or_none()

        return result

    def get_user_by_login(self, login: str) -> UserRepo|None:
        with self.session() as sess:
            sql = select(UserRepo).where(UserRepo.login == login)
            result = sess.scalars(sql).one_or_none()

        return result

    def create_user(self, login: str, hashed_password: str):
        new_user = UserRepo(login=login, hashed_password=hashed_password, nickname=login)
        with self.session() as sess:
            sess.add(new_user)
            sess.commit()
            sess.refresh(new_user)
        return new_user

    
repo = Repository()