from github import Github
import json

with open("token.json", "r") as file:
    gitToken = json.load(file)["git"]

g = Github(gitToken)
repo = g.get_repo("Manan-200/dcBots")
n = 0

oldCommit = repo.get_commits()[0]
while True:
    if n == 10000:
        n = 0
        newCommit = repo.get_commits()[0]
        if newCommit != oldCommit:
            oldCommit = newCommit
            print(f"Latest commit: {newCommit.commit.message}")
            print(f"Author: {newCommit.commit.author.name}")
    n += 1