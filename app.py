import re
import streamlit as st
from services import snow, sharepoint, github, atlassian, utils

# ---------- Config ----------
st.set_page_config(page_title="Unified Knowledge Base", layout="wide")

DEFAULT_SPACE = st.secrets.get("DEFAULT_SPACE", "")
GITHUB_DEFAULT_ORG = st.secrets.get("GITHUB_DEFAULT_ORG", "")

# ---------- Helpers ----------
def strip_html(x: str) -> str:
    return re.sub("<[^<]+?>", "", x or "").strip()

def clear_search_context():
    for k in list(st.session_state.keys()):
        if (
            k.startswith("search_result_")
            or k.startswith("summary_state_")
            or k.startswith("pending_summarize_")
            or k.startswith("cql_results::")
            or k.startswith("jira_results::")
            or k.startswith("github_repo_results::")
            or k.startswith("github_issue_results::")
            or k.startswith("sharepoint_results::")
            or k in ["c_start", "j_page", "j_tokens", "gh_page", "search_submitted", "currently_loading_summary"]
        ):
            del st.session_state[k]
    st.session_state.search_submitted = False

def get_confluence_cache_key(query, start, space):
    return f"cql_results::{query}::{start}::{space}"

def get_jira_cache_key(query, page):
    return f"jira_results::{query}::{page}"

def get_github_repo_cache_key(query, org, page):
    return f"github_repo_results::{query}::{org}::{page}"

def get_github_issue_cache_key(query, org, page):
    return f"github_issue_results::{query}::{org}::{page}"

def get_sharepoint_cache_key(query, site):
    return f"sharepoint_results::{query}::{site}"

st.markdown("""
<style>
/* Make Select/Deselect All label green, bold, and larger */
div[data-testid="stSidebar"] label[for="select_all_knowledge_sources"] {
    background-color: #ffffff;
    color: #24b47e !important;
    font-weight: 800 !important;
    font-size: 1.11em !important;
    background: #e8f9f0 !important;
    border-radius: 7px;
    padding: 0.13em 0.65em;
    margin-bottom: 0.3em;
    margin-top: 0.18em;
    box-shadow: 0 2px 7px -6px #24b47e44;
    letter-spacing: 0.01em;
    display: inline-block;
}
            
[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    background-color: transparent !important;
}

/* Remove default sidebar gradient */
section[data-testid="stSidebar"]::before {
    background-image: none !important;
    background-color: #ffffff !important;
}

/* Clean up sidebar borders */
.css-1d391kg {
    background-color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton > button#search_btn {
    background: linear-gradient(90deg, #36c285 70%, #20b9b6 100%);
    color: #fff;
    font-weight: 800;
    font-size: 1.12em;
    border: none;
    border-radius: 7px;
    padding: 0.72em 2.1em;
    margin-top: 0.6em;
    margin-bottom: 0.8em;
    box-shadow: 0 4px 18px -7px #20b9b655;
    transition: background 0.17s, box-shadow 0.17s;
    letter-spacing: 0.01em;
}
div.stButton > button#search_btn:hover {
    background: linear-gradient(90deg, #20b9b6 60%, #36c285 100%);
    box-shadow: 0 8px 28px -10px #20b9b6bb;
}

div.stButton > button#servicenow_btn {
    background: linear-gradient(90deg, #2b67f6 60%, #4b8aff 100%);
    color: #fff;
    font-weight: 800;
    font-size: 1.09em;
    border: none;
    border-radius: 7px;
    padding: 0.7em 2em;
    margin-top: 0.6em;
    margin-bottom: 0.7em;
    box-shadow: 0 3px 16px -8px #2b67f6cc;
    transition: background 0.17s, box-shadow 0.17s;
    letter-spacing: 0.01em;
}
div.stButton > button#servicenow_btn:hover {
    background: linear-gradient(90deg, #4b8aff 60%, #2b67f6 100%);
    box-shadow: 0 6px 24px -12px #2b67f6bb;
}
</style>
""", unsafe_allow_html=True)

# ---------- Loader & Blur CSS/JS ----------
st.markdown("""
<style>
.loader-overlay {
    position: fixed;
    z-index: 9999;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(3px);
    display: flex;
    align-items: center;
    justify-content: center;
}
body.blur-content > #root {
    filter: blur(2px) grayscale(0.5) brightness(0.8);
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stTabs [role="tablist"] {
    gap: 0.6em !important;
    margin-bottom: 1.1em !important;
}
.stTabs [role="tablist"] button {
    border: 2.2px solid #2b67f6 !important;
    border-radius: 28px 28px 0 0 !important;
    background: #f7fafd !important;
    color: #2b67f6 !important;
    margin-right: 6px !important;
    margin-bottom: 2px !important;
    padding: 0.85em 2.4em !important;
    font-weight: 700;
    font-size: 1.14em;
    letter-spacing: 0.01em;
    transition: background 0.18s, color 0.18s, box-shadow 0.18s;
    box-shadow: 0 2px 10px rgba(43,103,246,0.09);
    min-width: 140px;
    outline: none !important;
    opacity: 0.97;
}
.stTabs [role="tablist"] button[aria-selected="true"] {
    background: linear-gradient(90deg, #2b67f6 88%, #4b8aff 100%) !important;
    color: #fff !important;
    border-bottom: 4px solid #fff !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 28px -7px #2b67f6bb;
    opacity: 1;
}
.stTabs [role="tablist"] button:not([aria-selected="true"]):hover {
    background: #e3eefd !important;
    color: #2b67f6 !important;
    border-color: #2b67f6 !important;
    opacity: 1;
}
.stTabs [role="tablist"] button:focus {
    box-shadow: none !important;
    outline: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.title("🔎 Unified Knowledge Base")

with st.sidebar:
    # --- SECTION 2: ServiceNow (placed second, but checked first for logic) ---
    st.markdown("""
        <div style="
            font-size: 1.42em;
            font-weight: 900;
            color: #24b47e;
            letter-spacing: 0.01em;
            line-height: 1.20;
            margin-top: 0.25em;
            margin-bottom: 0.7em;
            text-shadow: 0 3px 10px #24b47e14;
        ">
            ServiceNow
        </div>
        """, unsafe_allow_html=True
    )
    srvc_now = utils.source_checkbox(
        "ServiceNow", key="source_servicenow", icon_url=utils.ICONS["ServiceNow"],
        help_text="Query ServiceNow only (disables other sources)."
    )
    # --- SECTION 1: Knowledge Sources ---
    st.markdown("""
        <div style="
            font-size: 1.42em;
            font-weight: 900;
            color: #24b47e;
            letter-spacing: 0.01em;
            line-height: 1.20;
            margin-top: 0.25em;
            margin-bottom: 0.7em;
            text-shadow: 0 3px 10px #24b47e14;
        ">
            Knowledge Sources
        </div>
        """, unsafe_allow_html=True
    )

    # Source keys
    all_sources_keys = ["source_confluence", "source_jira", "source_github", "source_sharepoint"]

    # --- Knowledge Sources section disabled if ServiceNow checked ---
    knowledge_disabled = srvc_now

    # Initialize session state for knowledge checkboxes if not present
    for key in all_sources_keys:
        if key not in st.session_state:
            st.session_state[key] = False

    # Compute if "all selected"
    all_selected = all(st.session_state[key] for key in all_sources_keys)
    none_selected = not any(st.session_state[key] for key in all_sources_keys)

    select_all = st.checkbox(
        "✅ Select/Deselect All",
        value=all_selected,
        key="select_all_knowledge_sources",
        help="Select or deselect all knowledge sources.",
        disabled=knowledge_disabled
    )

    # Handle select/deselect all logic
    if not knowledge_disabled:
        if select_all and not all_selected:
            for key in all_sources_keys:
                st.session_state[key] = True
        elif not select_all and all_selected:
            for key in all_sources_keys:
                st.session_state[key] = False

    # Now show individual checkboxes (all disabled if ServiceNow checked)
    conf = utils.source_checkbox("Confluence", key="source_confluence", icon_url=utils.ICONS["Confluence"], disabled=knowledge_disabled)
    jira = utils.source_checkbox("Jira", key="source_jira", icon_url=utils.ICONS["Jira"], disabled=knowledge_disabled)
    gh   = utils.source_checkbox("GitHub", key="source_github", icon_url=utils.ICONS["GitHub"], disabled=knowledge_disabled)
    sp   = utils.source_checkbox("SharePoint", key="source_sharepoint", icon_url=utils.ICONS["SharePoint"], disabled=knowledge_disabled)

    # Only show text input fields if at least one knowledge source is selected (and not disabled)
    if not knowledge_disabled:
        if "c_space" not in st.session_state:
            st.session_state.c_space = DEFAULT_SPACE
        if conf:
            st.text_input(
                "Confluence Space Key (optional)",
                value=st.session_state.c_space,
                key="c_space"
            )
        if "gh_org" not in st.session_state:
            st.session_state.gh_org = GITHUB_DEFAULT_ORG
        if gh:
            st.text_input(
                "GitHub Organization",
                value=st.session_state.gh_org,
                key="gh_org"
            )
        if "sp_site" not in st.session_state:
            st.session_state.sp_site = ""
        if sp:
            st.text_input(
                "SharePoint Site Path (optional)",
                value=st.session_state.sp_site,
                key="sp_site",
                help="e.g., /sites/yoursite"
            )

    st.markdown("""<hr style="margin:1em 0 1em 0; border:0; border-top:1.5px solid #e0e7ef;"/>""", unsafe_allow_html=True)

    # --- Determine selected sources for later use ---
    sources = []
    if srvc_now:
        sources.append("ServiceNow")
    else:
        if jira:
            sources.append("Confluence")
        if conf:
            sources.append("Jira")
        if gh:
            sources.append("GitHub")
        if sp:
            sources.append("SharePoint")

    st.divider()
    if not sources:
        st.warning("Please select at least one source")
        st.stop()

# Main search interface
if "unified_query" not in st.session_state:
    st.session_state.unified_query = ""
if "search_submitted" not in st.session_state:
    st.session_state.search_submitted = False

if "ServiceNow" in sources:
    pass
else:
    st.text_area(
        "Search Keywords",
        height=100,
        key="unified_query",
        placeholder='Enter your search terms...'
    )
    search_button = st.button("🔎 Search All", use_container_width=True, key="search_btn")
    if search_button:
        clear_search_context()
        st.session_state.search_submitted = True
        st.session_state.c_start = 0
        st.session_state.j_page = 0
        st.session_state.gh_page = 1
        st.rerun()

# -------- Loader overlay logic --------
currently_loading = st.session_state.get("currently_loading_summary", None)
if currently_loading:
    st.markdown(
        """
        <div class="loader-overlay">
            <div>
                <div style="font-size:2em; font-weight:600; color:#2b67f6; text-align:center">
                    <span style="font-size:1.3em;">🧠 Summarizing...</span><br/>
                    <svg width="60" height="60" viewBox="0 0 100 100" style="margin:10px auto;display:block;">
                    <circle cx="50" cy="50" r="35" stroke="#2b67f6" stroke-width="8" fill="none" stroke-linecap="round">
                        <animateTransform attributeName="transform" type="rotate" dur="1s" repeatCount="indefinite"
                        from="0 50 50" to="360 50 50"/>
                    </circle>
                    </svg>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        "<style>body{overflow:hidden !important;}</style>",
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <script>
        document.body.classList.add('blur-content');
        </script>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <script>
        document.body.classList.remove('blur-content');
        </script>
        """,
        unsafe_allow_html=True
    )

# -------- ServiceNow --------
if "ServiceNow" in sources:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg,#f8fafb 80%,#e3eefd 100%);
        border-radius: 18px;
        padding: 2.2em 2em 1.2em 2em;
        border: none;
        box-shadow: 0 3px 32px -10px #2b67f61e;
        margin-bottom: 2em;
        margin-top: 0.5em;
    ">
    <div style="display:flex;align-items:center;gap:0.7em;">
        <span style='font-size:2.05em;line-height:1;'>🟦</span>
        <span style="font-size:1.6em;font-weight:800;color:#2151a8;letter-spacing:0.01em;">
        ServiceNow Query
        </span>
    </div>
    """, unsafe_allow_html=True)

    servicenow_message = st.text_area("Enter your message for ServiceNow", height=100, key="servicenow_message")
    submit_sn = st.button("Submit to ServiceNow", use_container_width=True, key="servicenow_btn")

    def linkify_urls(text):
        url_pattern = re.compile(r'(https?://\S+)')
        return url_pattern.sub(r'[\1](\1)', text)

    if submit_sn:
        if not servicenow_message.strip():
            st.warning("Please enter a message for ServiceNow.")
        else:
            with st.spinner("Querying ServiceNow..."):
                try:
                    resp = snow.send_message(servicenow_message)
                    st.success("ServiceNow Response")
                    if isinstance(resp, (dict, list)):
                        st.json(resp)
                    else:
                        st.markdown(linkify_urls(str(resp)))
                except Exception as e:
                    st.error(f"ServiceNow error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# -------- Main Tabs --------
else:
    unified_query = st.session_state.get("unified_query", "")
    c_space = st.session_state.get("c_space", "")
    gh_org = st.session_state.get("gh_org", "")
    sp_site = st.session_state.get("sp_site", "")

    if st.session_state.get("search_submitted", False) and unified_query:
        tabs = st.tabs(sources)
        for tab, source in zip(tabs, sources):
            with tab:
                # -------- Confluence --------
                if source == "Confluence":
                    cql = atlassian.build_cql(unified_query or "", c_space or "")
                    st.code(cql, language="sql")
                    if "c_start" not in st.session_state:
                        st.session_state.c_start = 0

                    col_a, col_b, _ = st.columns([1, 1, 6])
                    prev_clicked = col_a.button("◀ Prev", disabled=st.session_state.c_start == 0, key="c_prev")
                    next_clicked = col_b.button("Next ▶", key="c_next")

                    if next_clicked:
                        st.session_state.c_start += 10
                        st.rerun()
                    elif prev_clicked:
                        st.session_state.c_start = max(0, st.session_state.c_start - 10)
                        st.rerun()

                    cache_key = get_confluence_cache_key(unified_query, st.session_state.c_start, c_space)
                    if cache_key in st.session_state:
                        payload = st.session_state[cache_key]
                    else:
                        with st.spinner("Searching Confluence..."):
                            payload = atlassian.confluence_search(
                                atlassian.BASE_URL, atlassian.AUTH, cql,
                                start=st.session_state.c_start, limit=10
                            )
                            st.session_state[cache_key] = payload

                    results = payload.get("results", [])
                    total_size = payload.get("totalSize", len(results))

                    if not results:
                        st.info("No results.")
                    else:
                        for r in results:
                            title = r.get("title") or "[Untitled]"
                            link = atlassian.build_confluence_link(atlassian.BASE_URL, r)
                            st.markdown(f"**[{title}]({link})**")
                            excerpt = r.get("excerpt", "")
                            excerpt_no_mark = re.sub(r'</?mark.*?>', '', excerpt or '', flags=re.IGNORECASE)
                            if excerpt_no_mark:
                                st.caption(strip_html(excerpt_no_mark))
                            st.markdown("</div>", unsafe_allow_html=True)

                            content_id = (r.get("content", {}) or {}).get("id") or r.get("id")
                            if content_id:
                                sum_state_key = f"summary_state_{content_id}"
                                pending_sum_key = f"pending_summarize_{content_id}"
                                # Show summary if available
                                if st.session_state.get(sum_state_key):
                                    with st.expander("🧾 Summary", expanded=True):
                                        st.write(st.session_state[sum_state_key])
                                else:
                                    if st.button("🧠 Summarize", key=f"sum_btn_{content_id}"):
                                        st.session_state[pending_sum_key] = True
                                        st.session_state.currently_loading_summary = content_id
                                        st.session_state.active_tab = source
                                        st.session_state.scroll_to_card = content_id
                                        st.rerun()
                                # Generate summary if pending, only for correct content_id
                                if (
                                    st.session_state.get(pending_sum_key)
                                    and st.session_state.get("currently_loading_summary") == content_id
                                ):
                                    try:
                                        with st.spinner("Fetching content..."):
                                            page_text = atlassian.fetch_confluence_page_text(
                                                atlassian.BASE_URL, atlassian.AUTH, content_id
                                            )
                                        if page_text.strip():
                                            with st.spinner("Generating summary..."):
                                                summary = atlassian.summarize_text_with_ai(page_text)
                                                if summary:
                                                    st.session_state[sum_state_key] = summary
                                                else:
                                                    st.error("Failed to generate summary")
                                        else:
                                            st.warning("No content found to summarize")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                                    st.session_state[pending_sum_key] = False
                                    st.session_state.currently_loading_summary = None
                                    st.rerun()
                            else:
                                st.write("⚠️ Unable to determine content id for this result.")
                            st.divider()
                    with st.expander("Raw response (debug)"):
                        st.json(payload)

                # -------- Jira --------
                elif source == "Jira":
                    jql = atlassian.build_jql(unified_query or "")
                    st.code(jql, language="sql")
                    if "j_tokens" not in st.session_state:
                        st.session_state.j_tokens = [None]
                    if "j_page" not in st.session_state:
                        st.session_state.j_page = 0

                    col_a, col_b, _ = st.columns([1,1,6])
                    prev_clicked = col_a.button("◀ Prev", disabled=st.session_state.j_page == 0, key="j_prev")
                    next_clicked = col_b.button("Next ▶", key="j_next")

                    page = st.session_state.j_page
                    cache_key = get_jira_cache_key(unified_query, page)
                    if cache_key in st.session_state:
                        payload = st.session_state[cache_key]
                    else:
                        with st.spinner("Searching Jira..."):
                            payload = atlassian.jira_search_new(
                                atlassian.BASE_URL,
                                atlassian.AUTH,
                                jql,
                                next_token=st.session_state.j_tokens[page],
                                limit=10,
                                fields=["summary","status","assignee","updated","issuetype","project","priority"]
                            )
                            st.session_state[cache_key] = payload

                    issues = payload.get("issues", [])
                    is_last = payload.get("isLast", False)
                    next_token = payload.get("nextPageToken")

                    if issues:
                        for i in issues:
                            key = i.get("key")
                            fields = i.get("fields", {}) or {}
                            url = f"{atlassian.BASE_URL}/browse/{key}"
                            summary = fields.get("summary", "")
                            st.markdown(f"**[{key}]({url})** — {summary}")
                            meta = [
                                f"Type: {(fields.get('issuetype') or {}).get('name')}",
                                f"Status: {(fields.get('status') or {}).get('name')}",
                                f"Assignee: {(fields.get('assignee') or {}).get('displayName', 'Unassigned')}",
                                f"Priority: {(fields.get('priority') or {}).get('name')}",
                                f"Updated: {fields.get('updated')}",
                            ]
                            st.caption(" · ".join([m for m in meta if m]))
                            st.divider()
                    else:
                        st.info("No results.")

                    # Update tokens and page index
                    if next_clicked and not is_last and next_token:
                        st.session_state.j_tokens.append(next_token)
                        st.session_state.j_page += 1
                        st.rerun()
                    elif prev_clicked and st.session_state.j_page > 0:
                        st.session_state.j_page -= 1
                        st.rerun()
                    with st.expander("Raw response (debug)"):
                        st.json(payload)

                # -------- GitHub --------
                elif source == "GitHub":
                    if "gh_page" not in st.session_state:
                        st.session_state.gh_page = 1

                    col_a, col_b, _ = st.columns([1,1,6])
                    prev_clicked = col_a.button("◀ Prev", disabled=st.session_state.gh_page <= 1, key="gh_prev")
                    next_clicked = col_b.button("Next ▶", key="gh_next")

                    gh_page = st.session_state.gh_page
                    repo_q = github.compose_github_query(
                        keywords=unified_query,
                        org=gh_org,
                        search_type="repositories"
                    )
                    issue_q = github.compose_github_query(
                        keywords=unified_query,
                        org=gh_org,
                        search_type="issues"
                    )

                    repo_cache_key = get_github_repo_cache_key(unified_query, gh_org, gh_page)
                    issue_cache_key = get_github_issue_cache_key(unified_query, gh_org, gh_page)

                    if repo_cache_key in st.session_state:
                        repo_results = st.session_state[repo_cache_key]
                    else:
                        with st.spinner("Searching GitHub repositories..."):
                            repo_results = github.github_search(
                                search_type="repositories",
                                q=repo_q,
                                page=gh_page,
                                per_page=10,
                                order="desc"
                            )
                            st.session_state[repo_cache_key] = repo_results

                    if issue_cache_key in st.session_state:
                        issue_results = st.session_state[issue_cache_key]
                    else:
                        with st.spinner("Searching GitHub issues..."):
                            issue_results = github.github_search(
                                search_type="issues",
                                q=issue_q,
                                page=gh_page,
                                per_page=10,
                                order="desc"
                            )
                            st.session_state[issue_cache_key] = issue_results

                    st.code(repo_q, language="text")
                    st.caption(f"Page {gh_page}")

                    if not repo_results.get("items") and not issue_results.get("items"):
                        st.info("No GitHub results found.")
                    else:
                        if repo_results.get("items"):
                            st.subheader("Repositories")
                            for repo in repo_results["items"]:
                                name = repo.get("full_name")
                                url = repo.get("html_url")
                                desc = repo.get("description") or ""
                                stars = repo.get("stargazers_count")
                                upd = repo.get("updated_at")
                                st.markdown(f"**[{name}]({url})**  ⭐ {stars}  \n{desc}")
                                st.caption(f"Updated: {upd}")
                                st.divider()
                        if issue_results.get("items"):
                            st.subheader("Issues & Pull Requests")
                            for it in issue_results["items"]:
                                title = it.get("title")
                                url = it.get("html_url")
                                state = it.get("state")
                                upd = it.get("updated_at")
                                repo_url = it.get("repository_url","")
                                repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else ""
                                st.markdown(f"**[{title}]({url})**  \nRepo: `{repo_name}`  ·  State: {state}  ·  Updated: {upd}")
                                st.divider()
                    if next_clicked:
                        st.session_state.gh_page += 1
                        st.rerun()
                    elif prev_clicked:
                        st.session_state.gh_page = max(1, st.session_state.gh_page - 1)
                        st.rerun()
                    with st.expander("Raw response (debug)"):
                        st.json({
                            "repositories": repo_results,
                            "issues": issue_results,
                        })

                # -------- SharePoint --------
                elif source == "SharePoint":
                    cache_key = get_sharepoint_cache_key(unified_query, sp_site)
                    if cache_key in st.session_state:
                        results = st.session_state[cache_key]
                    else:
                        with st.spinner("Searching SharePoint..."):
                            results = sharepoint.search_sharepoint(unified_query)
                            st.session_state[cache_key] = results
                    if not results:
                        st.info("No results found.")
                    else:
                        for hit in results:
                            name = hit.get('Title', 'Untitled')
                            url = hit.get('Path', '')
                            modified = hit.get('LastModifiedTime', '')
                            created_by = hit.get('CreatedBy', {})
                            summary = hit.get('Summary', '')
                            filetype = hit.get('FileType', {})

                            st.markdown(
                                f'<strong><a href="{url}" target="_blank">{name}</a></strong>',
                                unsafe_allow_html=True
                            )

                            cap = []
                            if created_by:
                                cap.append(f"By {created_by}")
                            if modified:
                                cap.append(f"Last modified: {modified[:10]}")
                            if filetype:
                                cap.append(filetype)
                            st.caption(" · ".join(cap))
                            if summary:
                                st.caption(strip_html(summary))
                            st.divider()
