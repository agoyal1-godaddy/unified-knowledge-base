import re
import requests
import streamlit as st
from services import caas_api

BASE_URL = st.secrets.get("ATLASSIAN_BASE_URL", "")
EMAIL = st.secrets.get("ATLASSIAN_EMAIL", "")
API_TOKEN = st.secrets.get("ATLASSIAN_API_TOKEN", "")
AUTH = (EMAIL, API_TOKEN)

def strip_html(x: str) -> str:
    return re.sub("<[^<]+?>", "", x or "").strip()

def build_confluence_link(base: str, obj: dict) -> str:
    """Builds a correct Confluence Cloud URL using _links.webui and content._expandable.space."""
    try:
        content = obj.get("content", {})
        links = content.get("_links", {}) or obj.get("_links", {})
        webui = links.get("webui")
        self_link = links.get("self")
        space_api_path = content.get("_expandable", {}).get("space", "")
        space_key = space_api_path.split("/")[-1] if space_api_path else None
        base = base.rstrip("/")

        if webui:
            webui = webui.strip()
            if not webui.startswith("/"):
                webui = "/" + webui
            if not webui.startswith("/wiki/"):
                webui = f"/wiki{webui}"
            return f"{base}{webui}"

        content_id = content.get("id")
        title = content.get("title", "").replace(" ", "+")
        if space_key and content_id:
            return f"{base}/wiki/spaces/{space_key}/pages/{content_id}/{title}"

        if self_link:
            return self_link if self_link.startswith("http") else f"{base}{self_link}"
    except Exception as e:
        print("build_confluence_link error:", e)
    return f"{base}/wiki"

def confluence_search(base, auth, cql, start=0, limit=10):
    url = f"{base}/wiki/rest/api/search"
    r = requests.get(url, params={"cql": cql, "start": start, "limit": limit}, auth=auth)
    if not r.ok:
        raise RuntimeError(f"Confluence search failed: {r.status_code} {r.text}")
    return r.json()

def fetch_confluence_page_text(base, auth, content_id):
    """Fetch page body.storage.value and return plain text (stripped)."""
    url = f"{base}/wiki/rest/api/content/{content_id}?expand=body.storage"
    r = requests.get(url, auth=auth, timeout=30)
    r.raise_for_status()
    data = r.json()
    html = data.get("body", {}).get("storage", {}).get("value", "") or ""
    return strip_html(html)

def build_cql(q, space_key="", types_str="page,blogpost", updated_after=None, advanced_cql=""):
    if advanced_cql.strip():
        return advanced_cql.strip()
    clauses = []
    if q and q.strip():
        text_q = q.strip()
        if '"' not in text_q and " AND " not in text_q and " OR " not in text_q:
            text_q = f'text ~ "{text_q}"'
        clauses.append(text_q)
    else:
        clauses.append('text ~ "*"')
    if space_key.strip():
        clauses.append(f'space = {space_key.strip()}')
    types = [t.strip() for t in types_str.split(",") if t.strip()]
    if types:
        if len(types) == 1:
            clauses.append(f"type = {types[0]}")
        else:
            clauses.append("(" + " OR ".join([f"type = {t}" for t in types]) + ")")
    if updated_after:
        clauses.append(f'lastmodified >= "{updated_after.isoformat()}"')
    return " AND ".join(clauses) + " ORDER BY lastmodified DESC"

def jira_search_new(base, auth, jql, next_token=None, limit=10, fields=None):
    """Jira Cloud endpoint: /rest/api/3/search/jql"""
    url = f"{base}/rest/api/3/search/jql"
    payload = {"jql": jql, "maxResults": int(limit)}
    if fields:
        payload["fields"] = fields
    if next_token:
        payload["nextPageToken"] = next_token
    r = requests.post(url, json=payload, auth=auth, headers={"Accept": "application/json"})
    if not r.ok:
        raise RuntimeError(f"Jira search failed: {r.status_code} {r.text}")
    return r.json()

def build_jql(prompt, project="", assignee="", statuses="", types="", updated_after="", advanced=""):
    if advanced.strip():
        return advanced.strip()
    clauses = []
    if prompt and prompt.strip():
        p = prompt.strip()
        if '"' not in p and " AND " not in p and " OR " not in p and "~" not in p:
            p = f'text ~ "{p}"'
        clauses.append(p)
    if project.strip():
        clauses.append(f"project = {project.strip()}")
    if assignee.strip():
        if "(" in assignee or ")" in assignee:
            clauses.append(f"assignee = {assignee.strip()}")
        else:
            clauses.append(f'assignee = "{assignee.strip()}"')
    if statuses.strip():
        vals = [s.strip() for s in statuses.split(",") if s.strip()]
        if len(vals) == 1:
            clauses.append(f'status = "{vals[0]}"')
        elif vals:
            clauses.append("status in (" + ", ".join([f'"{v}"' for v in vals]) + ")")
    if types.strip():
        vals = [s.strip() for s in types.split(",") if s.strip()]
        if len(vals) == 1:
            clauses.append(f'issuetype = "{vals[0]}"')
        elif vals:
            clauses.append("issuetype in (" + ", ".join([f'"{v}"' for v in vals]) + ")")
    if updated_after.strip():
        if updated_after.startswith("-") or updated_after.endswith("d"):
            clauses.append(f"updated >= {updated_after}")
        else:
            clauses.append(f'updated >= "{updated_after}"')
    if not clauses:
        clauses.append('text ~ "*"')
    return " AND ".join(clauses) + " ORDER BY updated DESC"

def summarize_text_with_ai(text, max_chars=8000):
    txt = text if len(text) <= max_chars else text[:max_chars] + "\n\n[TRUNCATED]"
    prompt_message = "You are a helpful assistant that writes concise summaries. Please provide a short (3-6 bullet) summary of the following document:\n\n" + txt
    try:
        resp = caas_api.send_prompt(prompt_message)
        if isinstance(resp, (dict, list)):
            st.json(resp)
            return 1
        else:
            st.code(resp)
            return str(resp)
    except Exception as e:
        return f"Failed to generate summary: {str(e)}"
