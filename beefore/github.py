import importlib
import sys

import github3
from github3.exceptions import GitHubError


def check(check, directory, username, password, repo_path, pull_request, sha):
    try:
        github = github3.login(username, password=password)
    except GitHubError as ghe:
        print(
            '\n'
            'Unable to log into GitHub: %s' % ghe,
            file=sys.stderr
        )
        sys.exit(10)

    try:
        print('Loading repository %s...' % repo_path)
        owner, repo_name = repo_path.split('/')
        repository = github.repository(owner, repo_name)
    except GitHubError as ghe:
        print(
            '\n'
            'Unable to load repository %s: %s' % (repo_path, ghe),
            file=sys.stderr
        )
        sys.exit(11)

    try:
        print('Loading pull request #%s...' % pull_request)
        pull_request = repository.pull_request(pull_request)
    except GitHubError as ghe:
        print(
            '\n'
            'Unable to load pull request %s in %s: %s' % (pull_request, repository, ghe),
            file=sys.stderr
        )
        sys.exit(12)

    try:
        print('Loading commit %s...' % sha)
        commit = repository.commit(sha)
    except GitHubError as ghe:
        print(
            '\n'
            'Unable to load commit %s: %s' % (sha, ghe),
            file=sys.stderr
        )
        sys.exit(13)

    try:
        check_module = importlib.import_module('beefore.checks.%s' % check)
    except ImportError:
        print(
            '\n'
            "Unable to load check module '%s'" % check,
            file=sys.stderr
        )
        sys.exit(20)

    diff_content = pull_request.diff().decode('utf-8').split('\n')

    print("Running Github %s check..." % check)
    print('==========' * 8)
    problems = check_module.check(
        directory=directory,
        diff_content=diff_content,
        commit=commit.commit
    )

    for problem, position in problems:
        # print("ADD COMMENT", problem, position)
        problem.add_comment(pull_request, commit, position)

    print('==========' * 8)
    return not problems
