import os
import re
import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv


load_dotenv()
PAT = os.getenv("PAT")
ORIGIN_REPO = os.getenv("ORIGIN_REPO")

# Session
HEADERS = {
    "Authorization": 'token ' + PAT
}
session = requests.session()
session.mount("https://", HTTPAdapter())
session.headers.update(HEADERS)
md = session.get(ORIGIN_REPO)
if int(md.headers['Content-Length']) <= 35:
    ORIGIN_REPO = re.sub('readme', 'README', ORIGIN_REPO)
    md = session.get(ORIGIN_REPO)

md = md.content.decode("utf-8")


externalLinks = "(?:[^\!]|^)\[([^\[\]]+)\]\((?!https://github.com/|#)([^()]+)\)"
internalGithubRepos = "(?:[^\!]|^)\[([^\[\]]+)\]\((?=https://github.com/)([^()]+)\)"



def grabStats(repo):
    head, sep, tail = repo.group(2).partition('/tree/')
    repoUrl = re.sub('https://github.com', 'https://api.github.com/repos', head)

    r = session.get(repoUrl)
    data = r.json()
    repoStars = str(data['stargazers_count'] if 'stargazers_count' in data else '?')
    repoForks = str(data['forks'] if 'forks' in data else '?')
    
    for n in range(6-len(repoStars)):
        repoStars = '&nbsp;' + repoStars

    for n in range(6-len(repoForks)):
        repoForks = '&nbsp;' + repoForks
        
    repoStars = '<b><code>' + repoStars + '⭐</code></b>'
    repoForks = '<b><code>' + repoForks + '🍴</code></b>'

    return f' {repoStars} {repoForks} [' + repo.group(1) + '](' + repo.group(2) + ')'


# curl requests with github matches
md = re.sub(externalLinks, r""" 🌎 [\1](\2)""", md)
md = re.sub(internalGithubRepos, grabStats, md)


# Write users to be followed to file
filename = './results/readme.md'
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w+", encoding='utf-8') as f:
    f.write(md)