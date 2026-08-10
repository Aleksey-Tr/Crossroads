from models import BooksSortFields
from sqlalchemy import create_engine, ForeignKey, String, select, Text, and_
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, joinedload, relationship, undefer
from auth import password_to_hash, verify_password

class Base(DeclarativeBase):
    pass

class UserBase(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(16) ,default='user')
    login: Mapped[str] = mapped_column(String(32), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(32), unique=True)

class BookBase(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str|None] = mapped_column()

    author: Mapped[UserBase] = relationship()

class CharacterBase(Base):
    __tablename__ = 'characters'

    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), primary_key=True)
    character_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text, deferred=True)



class Repository():
    def __init__(self):
        self.url = 'postgresql+psycopg2://postgres:toor@localhost:5432/novels_test_db'
        engine = create_engine(self.url)
        self.session = sessionmaker(engine)

    def get_books(self, search: str, sortBy:BooksSortFields = BooksSortFields.default) -> list[BookBase]:

        #добавить другие сортировки
        sort_column = {BooksSortFields.name: BookBase.title}[sortBy]

        with self.session() as sess:
            sql = select(BookBase).where(BookBase.title.ilike(f'%{search}%')).order_by(sort_column.desc()).options(joinedload(BookBase.author))
            result = sess.scalars(sql).all()
        return result

    def get_book_by_id(self, id: int) -> BookBase|None:
        with self.session() as sess:
            sql = select(BookBase).where(BookBase.id == id).options(joinedload(BookBase.author))
            result = sess.scalars(sql).one_or_none()
        return result

    def get_characters(self, book_id: int) -> list[CharacterBase]:
        with self.session() as sess:
            sql = select(CharacterBase).where(CharacterBase.book_id == book_id)
            result = sess.scalars(sql).all()

        return result

    def get_character_by_id(self, book_id: int, character_id: int) -> CharacterBase:
        with self.session() as sess:
            sql = select(CharacterBase).where(
                and_(CharacterBase.book_id == book_id, CharacterBase.character_id == character_id)
                ).options(undefer(CharacterBase.content))
            result = sess.scalars(sql).one_or_none()

        return result

    def get_user_by_login(self, login: str) -> UserBase|None:
        with self.session() as sess:
            sql = select(UserBase).where(UserBase.login == login)
            result = sess.scalars(sql).one_or_none()

        return result

    def create_user(self, login: str, hashed_password: str):
        new_user = UserBase(login=login, hashed_password=hashed_password, nickname=login)
        with self.session() as sess:
            sess.add(new_user)
            sess.commit()
            sess.refresh(new_user)
        return new_user

    
repo = Repository()