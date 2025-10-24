import requests
import streamlit as st

AGENT_API_TOKEN = st.secrets.get("AGENT_API_TOKEN", "")
AGENT_CONVERSATION_ID = st.secrets.get("AGENT_CONVERSATION_ID", "")
AGENT_ID = st.secrets.get("AGENT_ID", "")

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'cookie': f'auth_jomax={AGENT_API_TOKEN}'
}

def send_message(message, conversation_id=None, project_id=''):
    """
    Send `message` to the configured agent and return the API's 'message' field (or full JSON if absent).
    """
    if conversation_id is None:
        conversation_id = AGENT_CONVERSATION_ID

    json_data = {
        'conversationId': conversation_id,
        'message': message,
        'projectId': project_id,
        'llm': {
            'options': {},
        },
        'additionalOptions': {
            'similarityScore': 0.3,
            'reasoning': 'rwc',
            'queryRouter': 'hybrid',
            'citations': True,
        },
    }

    url = f'https://agent.api.godaddy.com/v1/agents/{AGENT_ID}/invoke'
    resp = requests.post(url, headers=headers, json=json_data)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f'API request failed: {e}; status={resp.status_code}; body={resp.text}')

    data = resp.json()
    return data.get('message', data)


if __name__ == '__main__':
    # simple demo
    print(send_message('Get me list of live servers'))