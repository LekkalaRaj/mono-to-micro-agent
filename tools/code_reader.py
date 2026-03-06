"""
tools/code_reader.py
─────────────────────
Tool 1 — CodeReader
Fetches and catalogues Java source files from a GitHub repository.

PRODUCTION WIRING
─────────────────
Replace the stub body with PyGitHub calls:

    from github import Github
    g = Github(settings.github_token)
    repo = g.get_repo(github_url.replace("https://github.com/", ""))
    # walk repo.get_contents("") recursively, collect *.java files

The Pydantic output contract is fixed — downstream agents won't change
when the implementation switches from stub to live.
"""

from __future__ import annotations

from models.schemas import CodeReaderInput, CodeReaderOutput
from utils.logger  import get_logger

logger = get_logger(__name__)


from github import Github, GithubException

def code_reader_tool(github_url: str, file_filter: str = ".java") -> dict:
    """
    Fetch and parse Java source files from a GitHub repository URL.

    Args:
        github_url:  Full GitHub URL  (e.g. https://github.com/org/legacy-app)
        file_filter: File extension filter (default ".java")

    Returns:
        Serialised CodeReaderOutput as a plain dict (ADK requirement).
    """
    _input = CodeReaderInput(github_url=github_url, file_filter=file_filter)
    logger.info("Fetching repository: %s  filter=%s", _input.github_url, _input.file_filter)

    # Clean the GitHub URL to get the repository path (e.g., LekkalaRaj/monolithic_app)
    repo_path = _input.github_url.replace("https://github.com/", "")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    repo_path = repo_path.strip("/")

    from config.settings import get_settings
    settings = get_settings()
    
    auth_kwargs = {}
    if settings.github_token:
        auth_kwargs["login_or_token"] = settings.github_token
    
    try:
        g = Github(**auth_kwargs)
        repo = g.get_repo(repo_path)
    except GithubException as e:
        logger.error(f"Failed to fetch repository {repo_path}: {e}")
        raise ValueError(f"Could not access GitHub repository {_input.github_url}. Ensure it is public or provide a valid GITHUB_TOKEN.")

    file_tree = []
    file_contents = {}
    total_loc = 0

    def process_contents(path: str = ""):
        nonlocal total_loc
        try:
            contents = repo.get_contents(path)
            # If get_contents returns a single file instead of a list, handle it
            if not isinstance(contents, list):
                contents = [contents]
                
            for item in contents:
                if item.type == "dir":
                    process_contents(item.path)
                elif item.type == "file" and item.path.endswith(_input.file_filter):
                    file_tree.append(item.path)
                    try:
                        content_str = item.decoded_content.decode('utf-8')
                        file_contents[item.path] = content_str
                        total_loc += len(content_str.splitlines())
                    except Exception as e:
                        logger.warning("Could not read file %s: %s", item.path, e)
        except GithubException as e:
            logger.warning("Could not list contents for path %s: %s", path, e)

    logger.info("Starting GitHub API traversal for %s...", repo_path)
    process_contents()

    output = CodeReaderOutput(
        repo_name=repo.name,
        total_files=len(file_tree),
        file_tree=file_tree,
        file_contents=file_contents,
        dependencies=[],
        java_version="unknown",
        loc_total=total_loc,
        note="Live fetched via PyGitHub API"
    )

    logger.info("Repository scan complete: %d files, %d LOC", output.total_files, output.loc_total)
    return output.model_dump()