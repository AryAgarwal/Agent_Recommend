
# GoodFoods AI Reservation Agent

An end-to-end restaurant booking assistant powered by LLM tool-calling, built without LangChain or similar frameworks.

---

## 🛠 Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/goodfoods-reservation-agent.git
   cd goodfoods-reservation-agent
   ```

2. **Create virtual environment (recommended)**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Groq API key (uses LLaMA-3 8B)**  
   ```bash
   export GROQ_API_KEY=your_api_key  # Add this to .env if using dotenv
   ```

5. **Run the Streamlit app**  
   ```bash
   streamlit run restaurant_agent_app.py
   ```

---

## 🧠 Prompt Engineering Documentation

We use a **structured system prompt** to guide the LLM’s reasoning and tool usage. Key design considerations:

- Clear role: _“You are a smart restaurant booking assistant for GoodFoods.”_
- Behavior rules:
  - Never hallucinate
  - Use tools when facts are needed
  - Ask for missing info
- **Edge case coverage**: missing info, no matches, invalid inputs
- **Few-shot examples** added to show expected tool-calling format

### Sample System Prompt (Excerpt)

```
User: Book Cafe Rio for 2 people on Saturday at 8PM under John  
Tool: call make_reservation with appropriate parameters

User: Cancel my reservation with ID BOOK1234  
Tool: call cancel_reservation(booking_id="BOOK1234")
```

---

## 💬 Example Conversations (User Journeys)

### 1. Basic restaurant search
```
User: Find Italian food in Indiranagar for 2 people  
→ Calls: search_restaurants(location="Indiranagar", cuisine="Italian", num_guests=2)
```

### 2. Recommendation request
```
User: Recommend a good restaurant  
→ Calls: recommend_restaurants()
```

### 3. Full reservation
```
User: Book Tandoori Hub for 4 on 2024-08-01 at 7PM under Riya  
→ Calls: make_reservation with all fields
```

### 4. Reservation cancellation
```
User: Cancel my booking with ID BOOK1056  
→ Calls: cancel_reservation(booking_id="BOOK1056")
```

---

## 📈 Business Strategy Summary

### 🧭 Goals
- Simplify the reservation experience using AI
- Increase table occupancy rates for partner restaurants
- Drive user engagement with seamless AI chat UX

### 💡 Business Opportunities
- Plug-and-play solution for restaurant chains
- White-label for food courts, cafes, hotel groups
- Extend to spas, gyms, cinemas (appointment-based)

### 📊 ROI Metrics
- Avg bookings per user per week  
- Table utilization rate  
- Agent response time & conversion rate

### 🧱 Vertical Expansion
- Generic booking agent platform
- Industry-specific tweaks: healthcare, salons, retail support

### 🏆 Competitive Advantages
- No hardcoded logic: pure intent understanding
- LLM-powered fallback chat, not just buttons
- Fully extensible, cloud-deployable, 100% custom

---

## ⚠️ Assumptions

- LLM provider (Groq) is consistently available and performant
- Data privacy is managed by backend infra
- No user login system assumed in MVP

---

## 🚧 Limitations & Future Enhancements

- Currently no multi-turn memory or follow-ups
- No real-time capacity checks with restaurants
- Limited language support (English-only for now)
- Could add user authentication, reservation history tracking

---

## 🧾 License

MIT License © 2025 GoodFoods AI
