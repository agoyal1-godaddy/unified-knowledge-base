# Confluence Search POC (Python + Streamlit)

A minimal Streamlit app to search Confluence Cloud using keywords via the REST API (CQL).

## Features
- Keyword search over Confluence content (CQL `text ~ "..."`)
- Optional filters: Space key, content types (page, blogpost), updated-after date
- Pagination controls
- Clickable titles + excerpts

## Prerequisites
- Confluence Cloud site (e.g., `https://your-domain.atlassian.net`)
- An Atlassian API token for your account: https://id.atlassian.com/manage-profile/security/api-tokens
- Your Atlassian account email address

## Setup

1. **Create a virtual environment and install deps**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Streamlit secrets**
   Create the file `.streamlit/secrets.toml` with your values:
   ```toml
   ATLASSIAN_BASE_URL = "https://your-domain.atlassian.net"
   ATLASSIAN_EMAIL = "you@example.com"
   ATLASSIAN_API_TOKEN = "YOUR_API_TOKEN"
   DEFAULT_SPACE = ""          # optional, e.g. "ENG"
   DEFAULT_CONTENT_TYPES = "page,blogpost"
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Notes
- The app uses Basic Auth with email + API token. For production, prefer OAuth 2.0 (3LO) and least-privilege scopes.
- The search uses the Confluence REST endpoint `/wiki/rest/api/search` with CQL and supports pagination.
- If your site uses a different base path, adjust the `build_confluence_link` helper accordingly.
