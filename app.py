import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import pandas as pd

# ✅ Configure Gemini with your API key
genai.configure(api_key="your GEMINI_API_KEY")

# ✅ Use the correct working model
MODEL_NAME = "models/gemini-pro-latest"

def generate_response(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # Some responses have .text, some need parts joined
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        parts = []
        for cand in getattr(response, "candidates", []) or []:
            for part in getattr(cand, "content", {}).get("parts", []):
                text = getattr(part, "text", None)
                if text:
                    parts.append(text.strip())

        return "\n".join(parts) if parts else "I'm here for you, but I couldn't generate a response."
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.5: return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5: return "Positive", polarity
    elif -0.1 <= polarity <= 0.1: return "Neutral", polarity
    elif -0.5 < polarity < -0.1: return "Negative", polarity
    else: return "Very Negative", polarity


def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Awesome vibes! Share your positivity with someone 😊",
        "Positive": "Nice! Keep doing what makes you feel good ✅",
        "Neutral": "Neutral is okay. Maybe listen to music or take a short walk.",
        "Negative": "Try a break, deep breathing, or talking to a friend.",
        "Very Negative": "You're not alone. Consider talking to someone you trust ❤️"
    }
    return strategies.get(sentiment, "Stay strong, one step at a time 💛")


# ✅ UI starts
st.title("Mental Health Support Chatbot (Gemini)")
st.caption(f"Using model: **{MODEL_NAME}**")

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "moods" not in st.session_state:
    st.session_state["moods"] = []

with st.form("chat"):
    user_input = st.text_input("How are you feeling?")
    send = st.form_submit_button("Send")

if send and user_input:
    st.session_state["messages"].append(("You", user_input))

    sentiment, polarity = analyze_sentiment(user_input)
    strategy = provide_coping_strategy(sentiment)

    reply = generate_response(user_input)
    st.session_state["messages"].append(("Bot", reply))
    st.session_state["moods"].append((user_input, sentiment, polarity))

# ✅ Display chat
for sender, msg in st.session_state["messages"]:
    st.write(f"**{sender}:** {msg}")

# ✅ Mood chart
if st.session_state["moods"]:
    df = pd.DataFrame(st.session_state["moods"], columns=["Message", "Sentiment", "Polarity"])
    st.line_chart(df["Polarity"])

# ✅ Strategy
if send and user_input:
    st.write(f"✅ **Coping Tip:** {strategy}")

st.sidebar.title("Quick Help")
st.sidebar.write("- Crisis Text Line: Text HELLO to 741741")
st.sidebar.write("- Suicide Prevention Lifeline: 1-800-273-8255")
st.sidebar.write("[More Resources](https://www.mentalhealth.gov/get-help/immediate-help)")

if st.sidebar.button("Session Summary"):
    for i, (msg, sent, pol) in enumerate(st.session_state["moods"], 1):
        st.sidebar.write(f"{i}. {msg} → {sent} ({pol:.2f})")
