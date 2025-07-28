# restaurant_agent_app.py

import streamlit as st
import json
import datetime
import random
from typing import List, Dict
import requests
import os  # Added for environment variable access

# ------------------- Load Restaurant Data -------------------
st.set_page_config(page_title="Restaurant AI Agent", layout="centered")
@st.cache_data
def load_restaurants() -> List[Dict]:
    with open("restaurants.json", "r") as f:
        return json.load(f)

restaurants = load_restaurants()

# ------------------- Simulated Reservation Store -------------------
reservations = []

# ------------------- Tool Functions -------------------
def search_restaurants(location=None, cuisine=None, num_guests=None):
    results = []
    for r in restaurants:
        if location and location.lower() not in r["location"].lower():
            continue
        if cuisine and cuisine.lower() not in r["cuisine"].lower():
            continue
        if num_guests and num_guests > r["capacity"]:
            continue
        results.append(r)
    return results[:5]

def recommend_restaurants():
    return sorted(restaurants, key=lambda x: x["rating"], reverse=True)[:5]

def make_reservation(restaurant_id, date, time, num_guests, name):
    # Basic input validation
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        datetime.datetime.strptime(time, "%H:%M")
        assert num_guests > 0
    except (ValueError, AssertionError):
        return "Invalid reservation input. Please check date/time/guest count."

    booking_id = f"BOOK{random.randint(1000, 9999)}"
    reservations.append({
        "booking_id": booking_id,
        "restaurant_id": restaurant_id,
        "date": date,
        "time": time,
        "num_guests": num_guests,
        "name": name
    })
    return f"Reservation confirmed with ID {booking_id}"

def cancel_reservation(booking_id):
    global reservations
    before = len(reservations)
    reservations = [r for r in reservations if r["booking_id"] != booking_id]
    after = len(reservations)
    return "Reservation cancelled." if before != after else "No reservation found with that ID."

# ------------------- LLM Tool Calling -------------------
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.environ.get("GROQ_API_KEY")  # Secure API key usage

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Search restaurants by filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "cuisine": {"type": "string"},
                    "num_guests": {"type": "integer"}
                },
                "required": []
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_restaurants",
            "description": "Recommend top-rated restaurants",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_reservation",
            "description": "Make a reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "num_guests": {"type": "integer"},
                    "name": {"type": "string"},
                },
                "required": ["restaurant_id", "date", "time", "num_guests", "name"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_reservation",
            "description": "Cancel a reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string"}
                },
                "required": ["booking_id"]
            },
        },
    },
]

SYSTEM_PROMPT = """
You are a smart restaurant booking assistant for GoodFoods.
Your job is to help users find and book restaurants.

Behaviors to follow:
- Understand user intent from conversation history and use the correct tool.
- Don't hallucinate responses; call tools when you need information.
- Be polite, clear, and concise.
- If required arguments are missing, ask the user for them.

Edge cases to handle:
- Unavailable restaurants or no matches: respond kindly and suggest alternative inputs.
- Missing dates, times, or names: ask for those explicitly.
- If the number of guests exceeds the restaurant's capacity, ask to try fewer guests or pick another place.

Examples:
User: I want to book a table for 4 in Koramangala
Tool: call search_restaurants(location="Koramangala", num_guests=4)

User: Book Cafe Rio for 2 people on Saturday at 8PM under John
Tool: call make_reservation with appropriate parameters

User: Cancel my reservation with ID BOOK1234
Tool: call cancel_reservation(booking_id="BOOK1234")

If unsure, ask clarifying questions. Avoid assumptions.
"""

def call_llm(messages):
    if not API_KEY:
        return {"choices": [{"message": {"content": "Missing API key."}}]}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto"
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"choices": [{"message": {"content": f"LLM call failed: {e}"}}]}

def invoke_tool(tool_call):
    try:
        name = tool_call['function']['name']
        args = json.loads(tool_call['function']['arguments'])
        if name == "search_restaurants":
            return search_restaurants(**args)
        elif name == "recommend_restaurants":
            return recommend_restaurants()
        elif name == "make_reservation":
            return make_reservation(**args)
        elif name == "cancel_reservation":
            return cancel_reservation(**args)
    except Exception as e:
        return f"Tool invocation failed: {e}"

# ------------------- Streamlit UI -------------------

st.title("GoodFoods AI Reservation Assistant")

if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

user_input = st.chat_input("Try: 'Find Chinese food in Indiranagar' or 'Book table at Cafe Mocha'")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        response = call_llm(st.session_state.history)
        msg = response["choices"][0]["message"]
        st.session_state.history.append(msg)

        if "tool_calls" in msg:
            for call in msg["tool_calls"]:
                result = invoke_tool(call)
                st.session_state.history.append({
                    "role": "function",
                    "name": call['function']['name'],
                    "content": str(result)
                })

# Show conversation
for h in st.session_state.history[1:]:
    with st.chat_message(h["role"]):
        st.markdown(h["content"])

# Optional: Display sample restaurant cards
if st.button("Show top recommendations"):
    recs = recommend_restaurants()
    for r in recs:
        st.markdown(f"**{r['name']}** | {r['cuisine']} | {r['location']} ⭐{r['rating']}")