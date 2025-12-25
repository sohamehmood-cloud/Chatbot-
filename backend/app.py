from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
import re
from dotenv import load_dotenv

# Load environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder='.')
CORS(app)

CRISIS_PATTERNS = [
    r"\bsuicid(e|al)\b",
    r"\bkill myself\b",
    r"\bwant to die\b",
    r"\bharm myself\b",
    r"\bend my life\b",
    r"\bself[- ]harm\b",
    r"\bpanic attack\b",
    r"\bI can't go on\b"
]

# Knowledge base for mental health topics
KNOWLEDGE_BASE = {
    # Greetings
    ("hello", "hi", "hey", "greetings", "howdy"): {
        "response": "Hello! Welcome to MindBuddy. 😊 I'm here to help you with mental health and wellbeing topics. Feel free to ask me about stress, anxiety, sleep, relationships, or any other mental health concern you have.",
        "tips": []
    },

    # Anxiety
    ("anxiety", "anxious", "panic", "worried", "nervous"): {
        "response": "I hear you — anxiety can feel overwhelming. Here are some helpful strategies:",
        "tips": [
            "🫁 **Breathe**: Try the 4-7-8 technique: breathe in for 4 counts, hold for 7, exhale for 8.",
            "🧘 **Ground yourself**: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "📝 **Write it down**: Journaling can help process worried thoughts.",
            "🚶 **Move**: A short walk or stretching releases nervous energy.",
            "⏸️ **Limit triggers**: Reduce caffeine and news consumption if they worsen anxiety.",
            "🤝 **Talk to someone**: Share your feelings with a trusted friend or therapist."
        ]
    },

    # Depression
    ("depression", "depressed", "sad", "hopeless", "blue", "down", "depressive"): {
        "response": "I'm sorry you're feeling this way. Depression is real, and you're not alone. Here's what can help:",
        "tips": [
            "🌅 **Sunlight**: Get 10–15 minutes of morning sunlight to boost mood.",
            "🏃 **Exercise**: Even a 10-minute walk increases endorphins.",
            "🛏️ **Sleep routine**: Try to keep consistent sleep/wake times.",
            "👥 **Connect**: Reach out to friends or family, even briefly.",
            "🎨 **Do something small**: Wash hands, make tea, or tidy one area to feel a sense of progress.",
            "🎵 **Music & hobbies**: Engage in things you used to enjoy.",
            "👨‍⚕️ **Seek professional help**: A therapist or counselor can provide real support."
        ]
    },

    # Stress
    ("stress", "stressed", "overwhelmed", "overworked", "burnout", "burnt out"): {
        "response": "Stress and overwhelm are tough. Here are practical ways to reduce it:",
        "tips": [
            "✋ **Prioritize**: Do one important task first, then one easier one.",
            "🧘‍♀️ **Meditation**: Even 3 minutes of mindfulness can calm the nervous system.",
            "📵 **Digital detox**: Take breaks from work emails and social media.",
            "💬 **Talk**: Tell someone how you feel — don't keep it bottled up.",
            "🎯 **Set boundaries**: It's okay to say 'no' to protect your energy.",
            "🏃‍♀️ **Exercise**: Physical activity is one of the best stress relievers.",
            "😴 **Sleep**: Prioritize rest — most stress feels worse when tired."
        ]
    },

    # Sleep issues
    ("sleep", "insomnia", "can't sleep", "tired", "exhausted", "fatigue", "sleeping"): {
        "response": "Sleep problems can really affect your wellbeing. Try these proven techniques:",
        "tips": [
            "⏰ **Consistent schedule**: Go to bed and wake up at the same time daily.",
            "🌙 **Wind down**: Put away screens 1 hour before bed.",
            "🛏️ **Good environment**: Keep your bedroom cool, dark, and quiet.",
            "🍵 **Avoid stimulants**: No caffeine after 2 PM.",
            "📱 **No phones in bed**: Use your bed only for sleep.",
            "🧘 **Relaxation**: Try deep breathing, progressive muscle relaxation, or guided sleep meditations.",
            "👨‍⚕️ **See a doctor**: If it lasts weeks, talk to your healthcare provider."
        ]
    },

    # Loneliness
    ("lonely", "loneliness", "alone", "isolated", "no friends"): {
        "response": "Loneliness is painful, but there are ways to build connection:",
        "tips": [
            "📱 **Reach out**: Text or call one person, even briefly.",
            "👥 **Join groups**: Take a class, join a club, or volunteer.",
            "🐕 **Pet companionship**: Spending time with animals helps.",
            "💻 **Online communities**: Find groups with shared interests.",
            "🎨 **Hobbies**: Engage in activities where you might meet others.",
            "🤝 **Be kind to yourself**: Loneliness is temporary; self-compassion helps.",
            "👨‍⚕️ **Talk to a therapist**: They can help address deeper feelings."
        ]
    },

    # Relationship issues
    ("relationship", "breakup", "broken up", "heartbreak", "conflict", "fight", "partner", "spouse"): {
        "response": "Relationship challenges are difficult. Here's how to navigate them:",
        "tips": [
            "💬 **Communicate**: Use 'I feel' statements instead of blame.",
            "⏸️ **Take a break**: Step away before heated conversations.",
            "🎯 **Listen**: Try to understand the other person's perspective.",
            "⏰ **Time helps**: Heartbreak and conflict fade with time.",
            "👥 **Lean on support**: Talk to friends or a therapist.",
            "📝 **Journal**: Write down your feelings to process them.",
            "❤️ **Self-care**: Invest in activities that restore you."
        ]
    },

    # Self-esteem
    ("self-esteem", "low self esteem", "not good enough", "worthless", "confidence", "insecure"): {
        "response": "Low self-esteem is painful. You deserve to see your own worth. Here's how to build it:",
        "tips": [
            "💭 **Challenge negative thoughts**: Notice them, then ask: Is this really true?",
            "📝 **Affirmations**: Say 3 things you're proud of each morning.",
            "✅ **Small wins**: Celebrate small accomplishments.",
            "🚫 **Stop comparing**: Limit time on social media.",
            "💪 **Set boundaries**: Say no to people who drain your energy.",
            "🎯 **Build skills**: Learn something new to boost confidence.",
            "👨‍⚕️ **Therapy**: A therapist can help reprogram negative self-talk."
        ]
    },

    # Anger
    ("anger", "angry", "irritable", "rage", "furious", "frustrated"): {
        "response": "Anger is valid, but managing it helps. Here are strategies:",
        "tips": [
            "🫁 **Pause & breathe**: Take 10 deep breaths before reacting.",
            "🚶 **Step away**: Remove yourself from the triggering situation.",
            "💪 **Physical activity**: Exercise gets anger out safely.",
            "📝 **Journal**: Write angry thoughts without filtering.",
            "🎵 **Healthy outlets**: Listen to music, punch a pillow, or scream into one.",
            "🤝 **Talk it out**: Express anger to someone you trust.",
            "👨‍⚕️ **Explore roots**: A therapist can help identify what triggers anger."
        ]
    },

    # Burnout
    ("burnout", "tired of work", "no motivation", "exhausted at work"): {
        "response": "Burnout is serious and requires action. Here's what can help:",
        "tips": [
            "✋ **Take time off**: Even a weekend away helps reset.",
            "🎯 **Set work boundaries**: Don't work outside office hours.",
            "💬 **Talk to your manager**: Discuss workload and priorities.",
            "🧘 **Mindfulness**: Daily meditation reduces burnout symptoms.",
            "🎨 **Rediscover joy**: Do things you love outside work.",
            "🏃 **Exercise**: Builds resilience and mood.",
            "👨‍⚕️ **Consider a career change**: If unhappy, explore other options."
        ]
    },

    # Focus/concentration
    ("focus", "can't concentrate", "distracted", "adhd", "attention", "focus problems"): {
        "response": "Trouble focusing is frustrating. Try these proven techniques:",
        "tips": [
            "🍅 **Pomodoro**: Work 25 minutes, break 5 minutes.",
            "📵 **Eliminate distractions**: Put phone in another room.",
            "☕ **Fuel your brain**: Eat protein and drink water.",
            "🎧 **White noise**: Some people focus better with background sounds.",
            "📍 **One task**: Don't multitask; do one thing at a time.",
            "😴 **Rest first**: Tired brains can't focus; prioritize sleep.",
            "👨‍⚕️ **See a doctor**: ADHD or other conditions might need professional support."
        ]
    },

    # Grief/loss
    ("grief", "grieving", "loss", "lost someone", "died", "death", "mourning"): {
        "response": "Grief is profound. There's no timeline — take the time you need:",
        "tips": [
            "💭 **Allow emotions**: Crying and sadness are healthy parts of grief.",
            "👥 **Be with others**: Spend time with people who understand.",
            "📝 **Honor their memory**: Write, make art, or talk about them.",
            "⏸️ **Self-care**: Eat, sleep, and move even when it's hard.",
            "🙏 **Support groups**: Connect with others who've experienced loss.",
            "🚫 **Avoid numbing**: Don't escape with substances; face the feelings.",
            "👨‍⚕️ **Grief counseling**: A therapist specializing in grief can help immensely."
        ]
    },

    # Self-harm
    ("self-harm", "cutting", "self-injury", "hurt myself"): {
        "response": "I'm concerned, and I'm glad you're reaching out. Self-harm is a sign you need real support.",
        "tips": [
            "🆘 **Crisis support**: Call 988 (US) or your local crisis line immediately.",
            "👥 **Tell someone**: Confide in a trusted person today.",
            "🧊 **Alternative coping**: Hold ice, take a cold shower, or snap a rubber band.",
            "✍️ **Journal**: Write about what you're feeling instead of hurting yourself.",
            "🎨 **Outlet**: Draw, scream, exercise, or use a punching bag.",
            "👨‍⚕️ **Get professional help**: A therapist can teach healthier coping strategies.",
            "💬 **Crisis text line**: Text HOME to 741741 (US)."
        ]
    },

    # Body image
    ("body image", "fat", "ugly", "hate my body", "appearance", "looks"): {
        "response": "Body image struggles are common and painful. Here's how to heal:",
        "tips": [
            "📱 **Unfollow**: Remove accounts that trigger comparison.",
            "🪞 **Reframe mirrors**: Look for what your body can do, not just how it looks.",
            "💬 **Challenge criticism**: Replace negative self-talk with kindness.",
            "👗 **Wear what feels good**: Clothes that make you comfortable.",
            "👥 **Surround yourself**: Spend time with people who value you for you.",
            "🚫 **Avoid diet culture**: Restrict extremes and obsessive health tracking.",
            "👨‍⚕️ **Therapy**: Body image issues benefit greatly from professional support."
        ]
    },

    # Wellbeing tips
    ("tips", "help", "advice", "wellness", "self-care", "healthy"): {
        "response": "Here are universal wellbeing tips that help most people:",
        "tips": [
            "😴 **Sleep**: 7–9 hours of consistent sleep is foundational.",
            "🏃 **Move**: 30 minutes of activity 5 days/week boosts mood.",
            "🥗 **Eat well**: Balanced nutrition supports mental health.",
            "👥 **Connect**: Spend time with people you care about.",
            "🧘 **Meditate**: Even 5 minutes daily reduces stress.",
            "🌙 **Limit screen time**: Especially before bed.",
            "🎨 **Do what you enjoy**: Hobbies and interests matter."
        ]
    },
}


def find_best_match(user_message):
    """Find the best response from knowledge base based on keywords."""
    user_lower = user_message.lower()

    best_match = None
    best_score = 0

    for keywords, content in KNOWLEDGE_BASE.items():
        score = 0
        for keyword in keywords:
            if keyword in user_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_match = content

    return best_match if best_score > 0 else None


def format_response_with_tips(content):
    """Format response with tips."""
    response = content["response"]
    if content["tips"]:
        response += "\n\n" + "\n".join(content["tips"])
    response += "\n\n*If you need professional support, please reach out to a mental health professional.*"
    return response


def is_crisis(text):
    text = text.lower()
    for p in CRISIS_PATTERNS:
        if re.search(p, text):
            return True
    return False


@app.route("/")
def home():
    return send_from_directory('.', 'index.html')


@app.route("/<path:filename>")
def serve_static(filename):
    if filename:
        return send_from_directory('.', filename)
    return send_from_directory('.', 'index.html')


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"answer": "Please provide a message.", "crisis": False}), 400

    # Crisis detection (highest priority)
    if is_crisis(user_message):
        safe_reply = (
            "I'm really sorry you're feeling this way. If you are in immediate danger or "
            "thinking about harming yourself, please contact your local emergency services right now. "
            "If you can, consider contacting a crisis hotline — for example, in the United States call or text 988, "
            "or find local resources at https://www.opencounseling.com/suicide-hotlines. "
            "You don't have to go through this alone; reach out to someone you trust or a professional."
        )
        return jsonify({"answer": safe_reply, "crisis": True})

    # Try to match with knowledge base
    kb_match = find_best_match(user_message)
    if kb_match:
        answer = format_response_with_tips(kb_match)
        return jsonify({"answer": answer, "crisis": False})

    # If no knowledge base match, try OpenAI
    system_prompt = (
        "You are MindBuddy, a compassionate mental well-being assistant. "
        "Provide empathetic, non-judgmental, and practical coping strategies and resources. "
        "Do NOT provide medical diagnosis, legal, or emergency services instructions. "
        "Always include a suggestion to seek professional help when appropriate, and offer self-care tips."
    )

    if openai.api_key:
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()
            return jsonify({"answer": answer, "crisis": False})
        except Exception:
            pass

    # Default fallback response when no OpenAI and no KB match
    fallback = (
        "Thanks for sharing — I hear you. While I might not have specific advice for this topic, "
        "here are some universally helpful strategies: \n\n"
        "1) 🫁 **Breathe**: Take slow, deep breaths for one minute.\n"
        "2) 🧘 **Ground yourself**: Name five things you can see around you.\n"
        "3) 🚶 **Move**: Try a short walk or a change of scene.\n"
        "4) 💬 **Talk**: Reach out to someone you trust.\n"
        "5) 👨‍⚕️ **Get professional help**: A therapist or counselor can provide real support.\n\n"
        "Feel free to ask me about anxiety, stress, sleep, relationships, depression, or any other mental health topic!"
    )
    return jsonify({"answer": fallback, "crisis": False})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
