# Unified Knowledge Search POC

A minimal Streamlit app to search across Confluence Cloud, SharePoint, ServiceNow, Jira, and GitHub using keywords via their respective APIs.

## Features
- Keyword search over Confluence content (CQL text ~ "...")
- Optional filters: Space key, content types (page, blogpost), updated-after date
- Pagination controls
- Clickable titles + excerpts
- SharePoint search: Keyword search across SharePoint sites and files
- ServiceNow integration: Submit queries/messages directly to ServiceNow and view responses
- Jira and GitHub: Search issues, repositories, and more
- Multi-source selection: Search any combination of the above sources simultaneously

## Prerequisites
- Confluence Cloud site (e.g., `https://your-domain.atlassian.net`)
- An Atlassian API token for your account: https://id.atlassian.com/manage-profile/security/api-tokens
- Your Atlassian account email address
- (For SharePoint) Microsoft Graph API access and credentials
- (For ServiceNow) ServiceNow instance and API credentials
- (For GitHub) GitHub API token (if required for private repos/orgs)

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
   # Atlassian (Jira/Confluence)
   ATLASSIAN_BASE_URL = "https://your-domain.atlassian.net"
   ATLASSIAN_EMAIL = "you@example.com"
   ATLASSIAN_API_TOKEN = "YOUR_API_TOKEN"
   DEFAULT_SPACE = ""          # optional, e.g. "ENG"
   DEFAULT_CONTENT_TYPES = "page,blogpost"

   # GitHub (optional)
   GITHUB_DEFAULT_ORG = "your-org"
   GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # optional, for higher rate limits/private repos

   # SharePoint (optional, if you want SharePoint search)
   SHAREPOINT_CLIENT_ID = "..."
   SHAREPOINT_CLIENT_SECRET = "..."
   SHAREPOINT_TENANT_ID = "..."
   SHAREPOINT_SITE = "..."  # e.g., /sites/yoursite

   # ServiceNow (optional, if you want ServiceNow integration)
   SERVICENOW_INSTANCE = "..."
   SERVICENOW_USERNAME = "..."
   SERVICENOW_PASSWORD = "..."
   GOCAAS_API_TOKEN = "..."
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Notes
- The app uses Basic Auth with email + API token. For production, prefer OAuth 2.0 (3LO) and least-privilege scopes.
- The search uses the Confluence REST endpoint `/wiki/rest/api/search` with CQL and supports pagination.
- SharePoint integration uses Microsoft Graph API; make sure the app is registered in Azure AD and granted appropriate permissions.
- ServiceNow integration uses REST API with basic authentication.
- If your Confluence site uses a different base path, adjust the build_confluence_link helper accordingly.
- For best results, ensure all required API tokens and credentials are present in your .streamlit/secrets.toml.
