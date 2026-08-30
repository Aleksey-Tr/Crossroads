from config import DB_URL
from models import BooksSortFields, BookCreateForm, BookUpdateForm, RegisterForm, SectionCreateAfterForm, SectionCreateFirstForm, ChoiceCreateModel
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
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False, deferred=True)

    books = relationship('BooksRepo', back_populates='author')

class BooksRepo(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int|None] = mapped_column(ForeignKey('users.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str|None] = mapped_column(nullable=True)
    published_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())

    author: Mapped[UsersRepo] = relationship(back_populates='books')
    genres: Mapped[list['GenresRepo']] = relationship(secondary=book_to_genre, back_populates='books')
    tags: Mapped[list['TagsRepo']] = relationship(secondary=book_to_tag, back_populates='books')
    sections: Mapped['SectionsRepo'] = relationship(back_populates='book', passive_deletes=True)

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
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    is_first: Mapped[bool] = mapped_column(nullable=False, default=False)

    book: Mapped[BooksRepo] = relationship(back_populates='sections')
    chapters: Mapped[list["ChaptersRepo"]] = relationship(back_populates='section')

class ChoicesRepo(Base):
    __tablename__ = 'choices'

    id: Mapped[int] = mapped_column(primary_key=True)
    from_section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'), nullable=False)
    to_section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)

    from_section: Mapped[SectionsRepo] = relationship(foreign_keys=from_section_id)
    to_section: Mapped[SectionsRepo] = relationship(foreign_keys=to_section_id)

class ChaptersRepo(Base):
    __tablename__ = 'chapters'

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey('sections.id'), nullable=False)
    title: Mapped[str|None] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, deferred=True)

    section: Mapped[SectionsRepo] = relationship(back_populates='chapters')


class Repository():
    def __init__(self):
        self.url = DB_URL
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
        sql = select(BooksRepo).where(BooksRepo.id == id).options(
        joinedload(BooksRepo.author), joinedload(BooksRepo.genres), joinedload(BooksRepo.tags))
        with self.session() as sess:
            result = sess.scalars(sql).unique().one_or_none()
        return result
    
    def get_simple_book(self, book_id: int) -> BooksRepo|None:
        sql = select(BooksRepo).where(BooksRepo.id == book_id)
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def create_book(self, user_id, form: BookCreateForm) -> BooksRepo:
        new_book = BooksRepo(author_id=user_id, title=form.title, description=form.description)
        with self.session() as sess:
            if form.genres:
                sql = select(GenresRepo).where(GenresRepo.id.in_(form.genres))
                genres = sess.scalars(sql).all()
                new_book.genres.extend(genres)

            if form.tags:
                sql = select(TagsRepo).where(TagsRepo.id.in_(form.tags))
                tags = sess.scalars(sql).all()
                new_book.tags.extend(tags)

            sess.add(new_book)
            sess.commit()
            sess.refresh(new_book)

            sql = select(BooksRepo).where(BooksRepo.id == new_book.id).options(
                joinedload(BooksRepo.author), joinedload(BooksRepo.genres), joinedload(BooksRepo.tags))
            result = sess.scalars(sql).unique().one_or_none()
        return result

    def update_book(self, book_id: int, form: BookUpdateForm) -> BooksRepo|None:
        with self.session() as sess:
            sql = select(BooksRepo).where(BooksRepo.id == book_id).options(
            joinedload(BooksRepo.author), joinedload(BooksRepo.genres), joinedload(BooksRepo.tags))
            book = sess.scalars(sql).unique().one_or_none()
            if not book:
                return None

            book.title = form.title if form.title else book.title
            book.description = form.description if form.description else book.description
            if form.genres:
                sql = select(GenresRepo).where(GenresRepo.id.in_(form.genres))
                genres = sess.scalars(sql).all()
                book.genres = genres
            if form.tags:
                sql = select(TagsRepo).where(TagsRepo.id.in_(form.tags))
                tags = sess.scalars(sql).all()
                book.tags = tags

            sess.commit()
            sess.refresh(book)
        return book

    def delete_book(self, book: BooksRepo):
        with self.session() as sess:
            sess.delete(book)
            sess.commit()

    def get_genres(self) -> list[GenresRepo]:
        with self.session() as sess:
            sql = select(GenresRepo)
            result = sess.scalars(sql).all()
        return result

    def get_genre_by_name(self, genre_name: str) -> GenresRepo|None:
        sql = select(GenresRepo).where(GenresRepo.name == genre_name)
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def create_genre(self, genre_name: str) -> GenresRepo:
        new_genre = GenresRepo(name=genre_name)
        with self.session() as sess:
            sess.add(new_genre)
            sess.commit()
            sess.refresh(new_genre)
        return new_genre

    def get_tags(self) -> list[TagsRepo]:
        sql = select(TagsRepo)
        with self.session() as sess:
            result = sess.scalars(sql).all()
        return result

    def get_tag_by_name(self, tag_name: str) -> TagsRepo|None:
        sql = select(TagsRepo).where(TagsRepo.name == tag_name)
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def create_tag(self, tag_name: str) -> TagsRepo:
        new_tag = TagsRepo(name=tag_name)
        with self.session() as sess:
            sess.add(new_tag)
            sess.commit()
            sess.refresh(new_tag)
        return new_tag

    def get_book_sections(self, book_id: int) -> list[BooksRepo]:
        sql = select(SectionsRepo).where(SectionsRepo.book_id == book_id)
        with self.session() as sess:
            return sess.scalars(sql).all()

    def get_book_first_sections(self, book_id: int) -> list[SectionsRepo]:
        sql = select(SectionsRepo).where(
            SectionsRepo.book_id == book_id,
            SectionsRepo.is_first == True)

        with self.session() as sess:
            result = sess.scalars(sql).all()
        return result

    def get_section_by_id(self, section_id: int) -> SectionsRepo|None:
        sql = select(SectionsRepo).where(SectionsRepo.id == section_id).options(
            joinedload(SectionsRepo.chapters))

        with self.session() as sess:
            result = sess.scalars(sql).unique().one_or_none()
        return result

    def get_simple_section(self, section_id: int) -> SectionsRepo|None:
        sql = select(SectionsRepo).where(SectionsRepo.id == section_id)

        with self.session() as sess:
            result = sess.scalars(sql).unique().one_or_none()
        return result

    def get_section_choices(self, section_id: int) -> list[ChoicesRepo]:
        sql = select(ChoicesRepo).where(ChoicesRepo.from_section_id == section_id).options(
            joinedload(ChoicesRepo.to_section))
        with self.session() as sess:
            result = sess.scalars(sql).all()
        return result

    def create_section_first(self, form: SectionCreateFirstForm) -> SectionsRepo:
        with self.session() as sess:
            new_section = SectionsRepo(book_id=form.book_id, title=form.section_title, is_first=True)
            sess.add(new_section)
            sess.commit()
            sess.refresh(new_section)
        return new_section    

    def create_section_after(self, form: SectionCreateAfterForm) -> SectionsRepo:
        with self.session() as sess:            
            new_section = SectionsRepo(book_id=form.book_id, title=form.section_title)
            sess.add(new_section)
            sess.flush()

            new_choice = ChoicesRepo(from_section_id=form.after_section_id, to_section_id=new_section.id, name=form.choice_name)
            sess.add(new_choice)
            sess.commit()

            sess.refresh(new_section)
        return new_section

    def create_choice(self, from_section_id, form: ChoiceCreateModel) -> ChoicesRepo:
        new_choice = ChoicesRepo(from_section_id=from_section_id, to_section_id=form.to_section_id, name=form.name)
        with self.session() as sess:
            sess.add(new_choice)
            sess.commit()
            sess.refresh(new_choice, attribute_names=['to_section'])
        return new_choice

    def get_choice(self, choice_id: int) -> ChoicesRepo|None:
        sql = select(ChoicesRepo).where(ChoicesRepo.id == choice_id)
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def delete_choice(self, choice_id: int):
        choice = self.get_choice(choice_id)
        with self.session() as sess:
            sess.delete(choice)
            sess.commit()
            

    def get_book_by_choice(self, choice_id: int) -> BooksRepo|None:
        sql = select(BooksRepo).select_from(ChoicesRepo).where(ChoicesRepo.id == choice_id).join(
            SectionsRepo, SectionsRepo.id == ChoicesRepo.to_section_id).join(
                BooksRepo, BooksRepo.id == SectionsRepo.book_id)
        with self.session() as sess:
            result = sess.scalars(sql).first()
        return result

    def get_chapter_by_id(self, chapter_id: int) -> ChaptersRepo:
        sql = select(ChaptersRepo).where(ChaptersRepo.id == chapter_id).options(undefer(ChaptersRepo.content))
        
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def get_user_by_login(self, login: str) -> UsersRepo|None:
        sql = select(UsersRepo).where(UsersRepo.login == login).options(undefer(UsersRepo.hashed_password))
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def get_user_by_nickname(self, nickname: str) -> UsersRepo|None:
        sql = select(UsersRepo).where(UsersRepo.nickname == nickname)
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result        

    def get_user_by_id(self, user_id: int) -> UsersRepo|None:
        sql = select(UsersRepo).where(UsersRepo.id == user_id)
        with self.session() as sess:
            result = sess.scalars(sql).one_or_none()
        return result

    def get_user_books(self, user_id: int):
        sql = select(BooksRepo).where(BooksRepo.author_id == user_id).options(
        joinedload(BooksRepo.author), joinedload(BooksRepo.genres), joinedload(BooksRepo.tags))
        with self.session() as sess:
            result = sess.scalars(sql).unique().all()
        return result
    
    def create_user(self, form: RegisterForm) -> UsersRepo:
        new_user = UsersRepo(login=form.login, hashed_password=form.raw_password, nickname=form.nickname)
        with self.session() as sess:
            sess.add(new_user)
            sess.commit()
            sess.refresh(new_user)
        return new_user

    
repo = Repository()