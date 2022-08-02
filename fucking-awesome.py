import os
import re
import time
import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv


load_dotenv()
PAT = os.getenv("PAT")
ORIGIN_OWNER = os.getenv("ORIGIN_OWNER")
ORIGIN_REPO = os.getenv("ORIGIN_REPO")
originRepoURL = f'https://raw.githubusercontent.com/correia-jpv/fucking-{ORIGIN_REPO}/main/readme.md'
# Session
HEADERS = {
    "Authorization": 'token ' + PAT
}
session = requests.session()
session.mount("https://", HTTPAdapter())
session.headers.update(HEADERS)
md = session.get(originRepoURL)
if int(md.headers['Content-Length']) <= 35:
    originRepoURL = re.sub('readme', 'README', originRepoURL)
    md = session.get(originRepoURL)

md = md.content.decode("utf-8")


# Match original repo links
originalRepoLinks = f'(https:\/\/github\.com\/)([^\/]*)\/({ORIGIN_REPO}[\/\)\&])'

md = re.sub(originalRepoLinks, r"""\1correia-jpv/fucking-\3""", md)


md += f'\r\n## Source\r\n[{ORIGIN_OWNER}/{ORIGIN_REPO}](https://github.com/{ORIGIN_OWNER}/{ORIGIN_REPO})'

# Match all markdown links that are not from github
externalLinks = "([^!])\[([^\[\]]+)\]\(https:\/\/(?!github\.com\/|#)([^()]+)\)"

md = re.sub(externalLinks, r""" 🌎 [\2](\3)""", md)


# Match all anchor links that are not from github
externalLinksAnchors = '<a.+?\s*href\s*=\s*["\']?((?:(?!https:\/\/github\.com\/))https:\/\/[^"\'\s>]+)["\']?>((?:(?!<img).)*)(?=<\/a>)'

md = re.sub(externalLinksAnchors, r"""<a href="\1">🌎 \2""", md)



# Match all markdown GitHub links not to own repository
internalGithubRepos = f"([^!])\[([^\[\]]+)\]\((?:(?!https:\/\/github\.com\/correia-jpv\/fucking-{ORIGIN_REPO}))(?=https:\/\/github.com\/[^()]+\/)([^()]+)"

def grabStats(repo):
    repoUrl = repo.group(3)
    head, sep, tail = repoUrl.partition('/tree/')
    repoUrl = head
    head, sep, tail = repoUrl.partition('/labels/')
    repoUrl = head
    head, sep, tail = repoUrl.partition('/blob/')
    repoUrl = head
    repoUrl = re.sub('https://github.com', 'https://api.github.com/repos', repoUrl)

    r = session.get(repoUrl)
    while (r.status_code == 403):
        print('waiting')
        for second in range(0, 600):
            time.sleep(1)
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

    return f'{repo.group(1)}{repoStars} {repoForks} [' + repo.group(2) + '](' + repo.group(3) + ')'

md = re.sub(internalGithubRepos, grabStats, md)


# Match all anchor GitHub links not to own repository or with images
internalGithubReposAnchors = f'<a.+?\s*href\s*=\s*["\']?((?:(?!https:\/\/github\.com\/correia-jpv\/fucking-{ORIGIN_REPO}))https:\/\/github.com\/[^"\'\s>]+\/[^"\'\s>]+)["\']?>((?:(?!<img).)*)(?=<\/a>)'

def grabStatsAnchors(repo):
    repoUrl = repo.group(1)
    head, sep, tail = repoUrl.partition('/tree/')
    repoUrl = head
    head, sep, tail = repoUrl.partition('/labels/')
    repoUrl = head
    head, sep, tail = repoUrl.partition('/blob/')
    repoUrl = head
    repoUrl = re.sub('https://github.com', 'https://api.github.com/repos', repoUrl)

    r = session.get(repoUrl)
    while (r.status_code == 403):
        print('waiting')
        for second in range(0, 600):
            time.sleep(1)
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

    return f' {repoStars} {repoForks} <a href="{repo.group(1)}">{repo.group(2)}</a>'

md = re.sub(internalGithubReposAnchors, grabStatsAnchors, md)


filename = f'./results/readme-{ORIGIN_REPO}.md'
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w+", encoding='utf-8') as f:
    f.write(md)