#GoodFoods AI Reservation Assistant

##Overview

GoodFoods AI Reservation Assistant is an intelligent, end-to-end restaurant booking agent. It enables users to search, recommend, reserve, and cancel restaurant bookings via a natural language interface, powered by LLM tool-calling. The system supports real-time interaction through a Streamlit frontend and integrates with a curated knowledge base of 50+ restaurants.

##🛠️ Setup Instructions

1. Clone the Repository

git clone https://github.com/your-org/restaurant-agent.git
cd restaurant-agent

2. Environment Setup

Install dependencies:

pip install -r requirements.txt

Create a .env file:

GROQ_API_KEY=your_groq_api_key_here

Ensure a restaurants.json file exists with 50-100 restaurant entries, including fields like name, location, capacity, cuisine, and rating.

3. Run the Application

streamlit run restaurant_agent_app.py

🤖 Prompt Engineering Approach

##System Prompt Design

The system prompt was crafted with the following goals:

Clear role: Establish the agent as a polite, smart restaurant assistant

Explicit behaviors: Avoid hallucination, ask clarifying questions, call tools

Edge case handling: Invalid dates, guest capacity limits, no matches

Few-shot examples: Provided in-system examples of real conversations

Few-shot Examples

User: "Book Cafe Rio for 2 people at 8PM"

User: "Cancel my reservation with ID BOOK3423"

The examples were chosen to trigger various tools and validate end-to-end coverage.

##💬 Example Conversations

1. Restaurant Search

User: "Find Indian food in Koramangala for 4 people"
Agent: Calls search_restaurants tool → Returns top 5 matches

2. Make Reservation

User: "Book Saffron Spice for 2 people at 7PM tomorrow under Sara"
Agent: Calls make_reservation tool → Confirms booking ID

3. Cancel Reservation

User: "Cancel booking ID BOOK1563"
Agent: Calls cancel_reservation tool → Confirms cancellation

4. Get Recommendations

User: "Suggest good places in Indiranagar"
Agent: Calls recommend_restaurants tool → Lists top-rated spots

##📈 Business Strategy Summary

Key Business Problems Addressed

Manual, inconsistent restaurant booking experience

Low customer retention due to lack of personalized recommendations

Limited operational insights into demand trends

##Success Metrics

Booking success rate: Target 95%

User satisfaction score > 4.5/5

Time-to-book < 2 minutes on average

##ROI Potential

Increased conversions by 30% due to convenience

Reduced support cost via automation

Potential data monetization (footfall trends, cuisine preferences)

##Vertical Expansion

Hotel bookings

Event venue reservations

Salon/spa scheduling

##Competitive Advantages

LLM-based flexible agent (not hardcoded flow)

Tool calling with structured function architecture

Easily customizable to other domains

##📝 Assumptions, Limitations, and Future Enhancements

Assumptions

Restaurant availability is static (not dynamically updated)

User input is reasonably structured and in English

Known Limitations

No real-time seat availability checks

No user authentication system

Cannot handle simultaneous multi-reservation scenarios

Future Enhancements

Real-time capacity sync via APIs

User login + history

Multi-lingual support

Admin dashboard for restaurant partners
