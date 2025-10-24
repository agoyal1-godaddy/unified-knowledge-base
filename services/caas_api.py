import requests
import streamlit as st

AGENT_API_TOKEN = st.secrets.get("GOCAAS_API_TOKEN", "")

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'cookie': f'auth_jomax={AGENT_API_TOKEN}'
}

def send_prompt(message):
    """
    Send `message` to the configured agent and return the API's 'message' field (or full JSON if absent).
    """

    json_data = {
        'prompt': message,
        'provider': 'openai_chat',
        "providerOptions": {
            "model": "gpt-3.5-turbo"
        }
    }

    url = f'https://caas.api.godaddy.com/v1/prompts'
    resp = requests.post(url, headers=headers, json=json_data)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f'API request failed: {e}; status={resp.status_code}; body={resp.text}')

    data = resp.json()
    # print(data.get('value', data))
    return data.get('data', {}).get('value', '')
