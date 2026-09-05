from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Column, Table, Text
from datetime import datetime

__all__ = ["UserORM", "BookORM", "GenreORM", "TagORM", "SectionORM", "ChapterORM"]

class BaseORM(DeclarativeBase):
    pass

book_to_genre = Table('book_to_genre', BaseORM.metadata,
                      Column('book_id', ForeignKey('books.id')),
                      Column('genre_id', ForeignKey('genres.id')))
book_to_tag = Table('book_to_tag', BaseORM.metadata,
                    Column('book_id', ForeignKey('books.id')),
                    Column('tag_id', ForeignKey('tags.id')))

class UserORM(BaseORM):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(16) ,default='user', nullable=False)
    login: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False, deferred=True)

    books: Mapped[list["BookORM"]] = relationship(back_populates='author')

class BookORM(BaseORM):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int|None] = mapped_column(ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str|None] = mapped_column(nullable=True)
    published_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())

    author: Mapped[UserORM] = relationship(back_populates='books')
    genres: Mapped[list['GenreORM']] = relationship(secondary=book_to_genre, back_populates='books')
    tags: Mapped[list['TagORM']] = relationship(secondary=book_to_tag, back_populates='books')
    sections: Mapped[list['SectionORM']] = relationship(back_populates='book', passive_deletes=True)

class GenreORM(BaseORM):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    books: Mapped[list[BookORM]] = relationship(secondary=book_to_genre, back_populates='genres')

class TagORM(BaseORM):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    books: Mapped[BookORM] = relationship(secondary=book_to_tag, back_populates='tags')

class SectionORM(BaseORM):
    __tablename__ = 'sections'

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    previous_section_id: Mapped[int|None] = mapped_column(ForeignKey('sections.id'), nullable=True)

    book: Mapped[BookORM] = relationship(back_populates='sections')
    chapters: Mapped[list["ChapterORM"]] = relationship(back_populates='section')

class ChapterORM(BaseORM):
    __tablename__ = 'chapters'

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, deferred=True)
    previous_chapter_id: Mapped[int|None] = mapped_column(ForeignKey("chapters.id"), nullable=True, default=None)
    next_chapter_id: Mapped[int|None] = mapped_column(ForeignKey("chapters.id"), nullable=True, default=None)
    position: Mapped[int] = mapped_column(nullable=False)

    previous_chapter: Mapped["ChapterORM|None"] = relationship(foreign_keys=[previous_chapter_id], remote_side=[id])
    next_chapter: Mapped["ChapterORM|None"] = relationship(foreign_keys=[next_chapter_id], remote_side=[id])
    section: Mapped[SectionORM] = relationship(back_populates='chapters')