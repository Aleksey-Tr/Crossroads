from models import BooksSortFields, CharacterShortModel
from sqlalchemy import create_engine, ForeignKey, String, select, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker, joinedload, relationship

class Base(DeclarativeBase):
    pass

class UserBase(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(16) ,default='user')
    nickname: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

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

    def get_book_by_id(self, id: int) -> BookBase:
        with self.session() as sess:
            sql = select(BookBase).where(BookBase.id == id).options(joinedload(BookBase.author))
            result = sess.scalars(sql).one()
        return result

    def get_characters(self, book_id: int) -> list[CharacterBase]:
        with self.session() as sess:
            sql = select(CharacterBase).where(CharacterBase.book_id == book_id)
            result = sess.scalars(sql).all()

        return result
    

repo = Repository()