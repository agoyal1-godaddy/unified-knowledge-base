import streamlit as st
from typing import Optional

# --- Brand icons ---
ICONS = {
    "ServiceNow": "https://cdn.brandfetch.io/idn6njzi5Z/theme/dark/logo.svg?c=1bxid64Mup7aczewSAYMX&t=1677205843183",
    "Jira": "https://cdn.simpleicons.org/jira",
    "Confluence": "https://cdn.simpleicons.org/confluence",
    "GitHub": "https://cdn.simpleicons.org/github",
    "SharePoint": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Microsoft_Office_SharePoint_%282019%E2%80%932025%29.svg",
}

def source_checkbox(label: str, key: str, icon_url: str, disabled: bool = False,
                    help_text: Optional[str] = None, icon_size_px: int = 18) -> bool:
    col_cb, col_ic, col_tx = st.columns([0.08, 0.08, 0.84], vertical_alignment="center")

    with col_cb:
        checked = st.checkbox(
            "", key=key, disabled=disabled, help=help_text, label_visibility="collapsed"
        )

    with col_ic:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;height:1.6rem;">
              <img src="{icon_url}" alt="{label}"
                   style="width:{icon_size_px}px;height:{icon_size_px}px;object-fit:contain;" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Text label (dim it when disabled)
    with col_tx:
        color = "#6c757d" if disabled else "inherit"
        st.markdown(
            f'<div style="line-height:1.6rem;color:{color};font-weight:500;">{label}</div>',
            unsafe_allow_html=True,
        )

    return checked