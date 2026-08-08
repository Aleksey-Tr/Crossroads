from models.BookModels import BooksSortFields
from sqlalchemy import create_engine, ForeignKey, String, select
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
    authorId: Mapped[int] = mapped_column('author_id', ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str|None] = mapped_column()

    author: Mapped[UserBase] = relationship()

class BooksRepo():
    def __init__(self):
        self.url = 'postgresql+psycopg2://postgres:toor@localhost:5432/novels_test_db'
        engine = create_engine(self.url)
        self.session = sessionmaker(engine)

    def getBooks(self, search: str, sortBy:BooksSortFields = BooksSortFields.default()):

        #добавить другие сортировки
        sortColumn = {BooksSortFields.name: BookBase.title}[sortBy]

        with self.session() as sess:
            sql = select(BookBase).where(BookBase.title.ilike(f'%{search}%')).order_by(sortColumn.desc()).options(joinedload(BookBase.author))
            return sess.scalars(sql).all()
            

bookRepo = BooksRepo()