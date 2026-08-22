import os
import requests
from flask import current_app

import re

def parse_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    return text

def generate_sales_insights_narrative(trend_data, lang='en'):
    api_key = current_app.config.get('MISTRAL_API_KEY')
    if not api_key:
        return "AI insights unavailable (MISTRAL_API_KEY not configured)."
        
    language_instruction = "Please write the response entirely in French." if lang == 'fr' else "Please write the response entirely in English."
    
    prompt = f"""
Given this shop's sales trend data: {trend_data['trend_data']}
Total profit this month: {trend_data['total_profit_this_month']}
Total profit last month: {trend_data['total_profit_last_month']}

Write a short, plain-language summary highlighting what's improving, what's declining, and any item worth restocking more aggressively based on rising demand. Keep it skimmable and actionable (no more than 1-2 paragraphs).
{language_instruction}
CRITICAL: Render key figures or emphasis using Markdown bold (**text**), and render section headers or specifically flagged important points using HTML underline tags (<u>text</u>).
"""

    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-tiny",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return parse_markdown(content)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 401:
            return "AI insights unavailable (Invalid API key)."
        elif status_code == 429:
            return "AI insights temporarily unavailable (Rate limit exceeded)."
        else:
            current_app.logger.error(f"Mistral API HTTP error {status_code}: {e.response.text}")
            return f"AI insights could not be generated at this time (Error {status_code})."
    except Exception as e:
        current_app.logger.error(f"Mistral API network/unknown error: {e}")
        return "AI insights could not be generated due to a network error."
