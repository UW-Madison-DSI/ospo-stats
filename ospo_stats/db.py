import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()
TURSO_DB_URL = os.getenv("TURSO_DB_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
ENGINE = create_engine(
    f"sqlite+{TURSO_DB_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true",
    connect_args={"check_same_thread": False},
    echo=True,
)


class Base(DeclarativeBase):
    pass


class Repo(Base):
    """Repo table ORM definition."""

    __tablename__ = "repo"
    url: Mapped[str] = mapped_column(String(1024), primary_key=True)
    homepage_url: Mapped[Optional[str]] = mapped_column(String(1024))
    crawl_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime)
    last_pushed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    owner: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    license_key: Mapped[Optional[str]] = mapped_column(String(256))
    license_name: Mapped[Optional[str]] = mapped_column(String(256))
    total_stargazer_count: Mapped[int] = mapped_column(Integer)
    total_issues_count: Mapped[int] = mapped_column(Integer)
    total_open_issues_count: Mapped[int] = mapped_column(Integer)
    total_forks_count: Mapped[int] = mapped_column(Integer)
    total_watchers_count: Mapped[int] = mapped_column(Integer)
    readme: Mapped[Optional[str]] = mapped_column(Text)
    readme_has_image: Mapped[bool] = mapped_column(Boolean)


def insert_example_data():
    """Insert example data to the database."""

    with Session(ENGINE) as session:
        repo = Repo(
            url="https://github.com/UW-Madison-DSI/ospo-stats",
            homepage_url="https://datascience.wisc.edu/",
            created_at=datetime.now(),
            last_pushed_at=datetime.now(),
            owner="UW-Madison-DSI",
            name="ospo-stats",
            description="Open Source Program Office (OSPO) Stats",
            license_key="mit",
            license_name="MIT License",
            total_stargazer_count=0,
            total_issues_count=0,
            total_open_issues_count=0,
            total_forks_count=0,
            total_watchers_count=0,
            readme="This is a test readme.",
            readme_has_image=False,
        )

        session.add(repo)
        session.commit()
