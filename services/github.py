import requests
import streamlit as st

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")

def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def github_search(search_type, q, page=1, per_page=10, sort=None, order="desc"):
    """
    search_type: 'repositories' | 'issues' | 'code'
    q: fully composed query string with qualifiers (org:, repo:, language:, etc.)
    """
    base = "https://api.github.com"
    if search_type == "repositories":
        url = f"{base}/search/repositories"
        params = {"q": q, "page": page, "per_page": per_page, "order": order}
        if sort: params["sort"] = sort  # 'stars' | 'forks' | 'updated'
    elif search_type == "issues":
        url = f"{base}/search/issues"
        params = {"q": q, "page": page, "per_page": per_page, "order": order, "sort": sort or "updated"}
    elif search_type == "code":
        url = f"{base}/search/code"
        params = {"q": q, "page": page, "per_page": per_page, "order": order, "sort": sort or "indexed"}
    else:
        raise ValueError("Invalid search type")

    r = requests.get(url, headers=gh_headers(), params=params)
    if not r.ok:
        raise RuntimeError(f"GitHub search failed: {r.status_code} {r.text}")
    return r.json()

def compose_github_query(keywords, org="", repo="", language="", in_fields=None, search_type="repositories"):
    """
    Compose a GitHub search query with qualifiers.
    in_fields: list like ['title','body'] (for issues) or ['file','path'] (for code). Optional.
    """
    parts = []

    if search_type == "issues":
        parts.append("is:issue is:pr")
    if keywords:
        # Wrap in quotes if it has spaces and not already quoted
        k = keywords.strip()
        if " " in k and '"' not in k:
            k = f'"{k}"'
        parts.append(k)
    if org.strip():
        parts.append(f"org:{org.strip()}")
    if repo.strip():
        parts.append(f"repo:{repo.strip()}")
    if language.strip():
        parts.append(f"language:{language.strip()}")
    if in_fields:
        parts.append("in:" + ",".join(in_fields))
    return " ".join(parts).strip() or "*"
