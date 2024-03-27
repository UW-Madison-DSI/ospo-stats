from concurrent.futures import ThreadPoolExecutor

from anthropic import Anthropic
from sqlalchemy.orm import Session
from tqdm import tqdm

from ospo_stats.db import ENGINE, Repo
from ospo_stats.llm import get_category


def update_repo(repo: Repo, llm_client: Anthropic, overwrite: bool = False) -> Repo:
    print(repo.url)

    # Determine if repo is active
    if repo.crawl_at and repo.last_pushed_at:
        days_since_last_pushed = (repo.crawl_at - repo.last_pushed_at).days
        if days_since_last_pushed > 365:
            repo.is_active = False
        else:
            repo.is_active = True

    # Exit if category already exists and not overwrite
    if not overwrite and repo.category:
        return repo

    # Update category
    text = repo.name
    if repo.description:
        text += " " + repo.description
    if repo.readme:
        text += " " + repo.readme
    repo.category = get_category(text, client=llm_client, sleep=1)
    return repo


def update_in_batch(
    batch_size: int, llm_client: Anthropic, overwrite: bool = False
) -> None:
    """Update repo in batch.

    Note. Due to rate limit, probably should use batch_size=1 for now.
    """
    with Session(ENGINE).no_autoflush as session:
        total = session.query(Repo).count()
        batches = total // batch_size + (1 if total % batch_size > 0 else 0)

        for batch in tqdm(range(batches)):
            repos = session.query(Repo).offset(batch * batch_size).limit(batch_size)

            # Parallelize llm execution (useless due to rate limit)
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [
                    executor.submit(update_repo, repo, llm_client, overwrite)
                    for repo in repos
                ]
                repos = [future.result() for future in futures]

            # Update change to database
            for repo in repos:
                session.merge(repo)
            session.flush()
            session.commit()


def main():
    anthropic_client = Anthropic()
    update_in_batch(batch_size=1, llm_client=anthropic_client, overwrite=False)


if __name__ == "__main__":
    main()
