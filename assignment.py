# restaurant_agent_app.py

import streamlit as st
import json
import datetime
import random
from typing import List, Dict
import requests

# ------------------- Load Restaurant Data -------------------
st.set_page_config(page_title="Restaurant AI Agent", layout="centered")

@st.cache_data
def load_restaurants() -> List[Dict]:
    with open("restaurants.json", "r") as f:
        return json.load(f)

restaurants = load_restaurants()

# ------------------- Simulated Reservation Store -------------------
if "reservations" not in st.session_state:
    st.session_state.reservations = []

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
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        datetime.datetime.strptime(time, "%H:%M")
        assert num_guests > 0
        
        # Find restaurant to validate it exists
        restaurant = next((r for r in restaurants if r["id"] == restaurant_id), None)
        if not restaurant:
            return "Restaurant not found."
        
        if num_guests > restaurant["capacity"]:
            return f"Sorry, {restaurant['name']} can only accommodate {restaurant['capacity']} guests."
            
    except (ValueError, AssertionError):
        return "Invalid reservation input. Please check date/time/guest count."

    booking_id = f"BOOK{random.randint(1000, 9999)}"
    st.session_state.reservations.append({
        "booking_id": booking_id,
        "restaurant_id": restaurant_id,
        "date": date,
        "time": time,
        "num_guests": num_guests,
        "name": name
    })
    
    restaurant_name = next(r["name"] for r in restaurants if r["id"] == restaurant_id)
    return f"Reservation confirmed at {restaurant_name} for {num_guests} guests on {date} at {time}. Booking ID: {booking_id}"

def cancel_reservation(booking_id):
    before = len(st.session_state.reservations)
    st.session_state.reservations = [r for r in st.session_state.reservations if r["booking_id"] != booking_id]
    after = len(st.session_state.reservations)
    return "Reservation cancelled successfully." if before != after else "No reservation found with that ID."

# ------------------- LLM Tool Calling -------------------
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = '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'

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Search restaurants by filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location to search in"},
                    "cuisine": {"type": "string", "description": "Type of cuisine"},
                    "num_guests": {"type": "integer", "description": "Number of guests"}
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
            "description": "Make a reservation at a restaurant",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "ID of the restaurant"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM format"},
                    "num_guests": {"type": "integer", "description": "Number of guests"},
                    "name": {"type": "string", "description": "Name for the reservation"},
                },
                "required": ["restaurant_id", "date", "time", "num_guests", "name"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_reservation",
            "description": "Cancel an existing reservation",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string", "description": "Booking ID to cancel"}
                },
                "required": ["booking_id"]
            },
        },
    },
]

SYSTEM_PROMPT = """
You are a smart restaurant booking assistant for GoodFoods.
Your job is to help users find and book restaurants.

When presenting restaurant results, always format them clearly with:
- Restaurant name
- Cuisine type  
- Location
- Rating
- Capacity
- Special tags

Behaviors to follow:
- Understand user intent from conversation history and use the correct tool.
- Don't hallucinate responses; call tools when you need information.
- Be polite, clear, and concise.
- If required arguments are missing, ask the user for them.
- Always show restaurant details when search results are returned.

Edge cases to handle:
- Unavailable restaurants or no matches: respond kindly and suggest alternative inputs.
- Missing dates, times, or names: ask for those explicitly.
- If the number of guests exceeds the restaurant's capacity, ask to try fewer guests or pick another place.

Examples:
User: I want to book a table for 4 in Koramangala
Tool: call search_restaurants(location="Koramangala", num_guests=4)

User: Book Restaurant 2 for 2 people on 2024-08-15 at 19:00 under John
Tool: call make_reservation(restaurant_id=2, date="2024-08-15", time="19:00", num_guests=2, name="John")

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
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
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
        else:
            return f"Unknown tool: {name}"
            
    except Exception as e:
        return f"Tool invocation failed: {e}"

# ------------------- Streamlit UI -------------------
st.title("🍽️ GoodFoods AI Reservation Assistant")

if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display conversation history
for h in st.session_state.history[1:]:  # Skip system message
    role = h.get("role")
    if role in ["user", "assistant"]:
        with st.chat_message(role):
            st.markdown(h["content"])

# Chat input
user_input = st.chat_input("Try: 'Find Chinese food in Indiranagar' or 'Book table at Restaurant 2'")

if user_input:
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get LLM response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_llm(st.session_state.history)
            
            if "choices" not in response or not response["choices"]:
                st.error("No response from LLM")
            else:
                msg = response["choices"][0]["message"]
                
                # Handle tool calls
                if "tool_calls" in msg and msg["tool_calls"]:
                    # Add assistant message with tool calls to history
                    st.session_state.history.append(msg)
                    
                    # Execute each tool call
                    for call in msg["tool_calls"]:
                        result = invoke_tool(call)
                        st.session_state.history.append({
                            "role": "tool",
                            "tool_call_id": call.get("id", "unknown"),
                            "name": call['function']['name'],
                            "content": json.dumps(result) if not isinstance(result, str) else result
                        })
                    
                    # Get final response from LLM with tool results
                    followup = call_llm(st.session_state.history)
                    if "choices" in followup and followup["choices"]:
                        followup_msg = followup["choices"][0]["message"]
                        st.session_state.history.append(followup_msg)
                        st.markdown(followup_msg["content"])
                    else:
                        st.error("Failed to get followup response")
                        
                else:
                    # Direct response without tools
                    st.session_state.history.append(msg)
                    st.markdown(msg["content"])

# Sidebar with current reservations
st.sidebar.title("📋 Current Reservations")
if st.session_state.reservations:
    for res in st.session_state.reservations:
        restaurant_name = next((r["name"] for r in restaurants if r["id"] == res["restaurant_id"]), "Unknown")
        st.sidebar.markdown(f"""
        **{res['booking_id']}**
        - {restaurant_name}
        - {res['date']} at {res['time']}
        - {res['num_guests']} guests
        - Name: {res['name']}
        """)
else:
    st.sidebar.write("No reservations yet")

# Optional: Display sample restaurant cards
if st.button("🌟 Show Top Recommendations"):
    recs = recommend_restaurants()
    st.subheader("Top Rated Restaurants")
    for r in recs:
        st.markdown(f"""
        **{r['name']}** (ID: {r['id']})
        - 🍽️ {r['cuisine']} cuisine
        - 📍 {r['location']}  
        - ⭐ {r['rating']}/5.0
        - 👥 Capacity: {r['capacity']} guests
        - 🏷️ Tags: {', '.join(r['tags'])}
        """)
