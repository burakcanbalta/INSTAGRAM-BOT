# 📱 INSTAGRAM BOT

## 🎯 Objective
A professional, secure, and automation-driven Instagram bot for **ethical growth and engagement**.
This tool features realistic interaction timing, AI-like behavior simulation, and built-in **rate-limit protection** to ensure safe automation while mimicking natural user actions.

---

## 🛡️ Security Measures

### 🔒 Core Security
- Local database — **no passwords are stored in plain text**
- SSL-encrypted connections for safe communication
- **Headless browser option** for stealth operation
- Activity logs — maintain a full audit trail for every action

### 🤖 Automation Safety
- Realistic **human-like time intervals** between actions
- Daily interaction limits (follow, like, comment, unfollow)
- Smart **anti-ban** behavior to avoid detection
- Database-based rate control and tracking

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/InstagramBotAdvanced.git
cd InstagramBotAdvanced
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure settings
Edit the `config.json` file to match your preferences.

**Example configuration:**
```json
{
  "browser": {
    "headless": true,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  "limits": {
    "daily_follows": 150,
    "daily_likes": 300,
    "daily_comments": 50
  },
  "timing": {
    "min_delay": 2,
    "max_delay": 5,
    "between_actions": 10
  },
  "targeting": {
    "hashtags": ["python", "cybersecurity", "ai", "tech"]
  }
}
```

---

## 🚀 Usage Examples

### ▶️ Full Automation Mode
Runs a full engagement cycle including hashtag exploration, likes, follows, and scheduled unfollows.
```bash
python instagram_bot.py --username myaccount --password mypass123 --mode auto
```

### 👤 Manual Follow Mode
Follow a specific user manually:
```bash
python instagram_bot.py --username myaccount --password mypass123 --mode follow --target python.hub
```

### ❤️ Like Mode
Like a specific post by URL:
```bash
python instagram_bot.py --username myaccount --password mypass123 --mode like --target https://www.instagram.com/p/ExamplePost/
```

### 🚫 Unfollow Mode
Unfollow a specific user:
```bash
python instagram_bot.py --username myaccount --password mypass123 --mode unfollow --target example_user
```

---

## 📊 Features Overview
| Feature | Description |
|----------|--------------|
| 🧠 Smart Action Control | Prevents over-interaction and randomizes behavior |
| 🗂️ SQLite Logging | Stores all activities for full transparency |
| ⏱️ Realistic Delays | Human-like delays between actions |
| 🔁 Auto-Unfollow | Automatically unfollows old accounts |
| 🧩 Modular Design | Easy to extend for new features |
| 🧑‍💻 Developer-Friendly | Fully open-source and customizable |

---

**Author:** [Burak Can Balta](https://github.com/burakcanbalta)  
**Project:** [INSTAGRAM-BOT — Advanced Level](https://github.com/burakcanbalta)  
**Version:** 1.0.0  
**License:** MIT
