# ChefFlow AI 🍲

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/imajaymoladiya/hack2skill_ajaymoladiya)

ChefFlow AI is a premium, responsive single-page web application designed to help users structure their daily meal plans (Breakfast, Lunch, Dinner), manage interactive cooking checklists, organize a categorized grocery shopping list, and evaluate budget feasibility. 

It is powered by a **Python Flask** backend and integrates with the **Groq Cloud API** using `llama-3.3-70b-versatile` in JSON mode, with a robust local rule-based fallback database.

---

## ✨ Features

- **Daily Schedule Adaptability:** Generates recipe workflows tailored to your busy level (Hectic: quick 10-15m prep, Balanced: 25-30m prep, Leisurely: detailed cooking).
- **Dietary Focus Customization:** Options for Anything, Vegetarian, Vegan, Keto (Low Carb), and Gluten-Free preferences.
- **Smart Budget Feasibility Logic:**
  - Evaluates total daily meal cost against three budget targets: Eco ($15), Mid ($30), and Gourmet ($60).
  - Renders a color-coded cost gauge bar (Green = Safe/Under, Yellow = Approaching, Red = Over Budget limit).
  - Provides dynamic money-saving tips and advice.
- **Pantry Inventory Discounting:** Input items already in your fridge/pantry. ChefFlow AI includes them in your recipe instructions but sets their grocery cost to `$0.00`, adjusting the budget analysis accordingly.
- **Interactive Substitutions:** Displays smart replacement suggestions for expensive or dietary-restricted ingredients.
- **Interactive Checklists:** Tap to check off prep tasks, active cooking steps, and grocery items. Your progress is persisted in local storage.
- **Exporting Options:** Copy the structured plan to your clipboard with one click, or print the plan formatted using a clean CSS print stylesheet.
- **Resilient Fallbacks:** Runs automatically in Local Rule-Based Mode if a Groq API key is missing or encounters a rate-limit error.

---

## 📂 Project Structure

```
d:\Ajay\Hack2Skill\
├── .env                  # Secrets configuration (Groq API Key)
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── app.py                # Flask Backend Web Server & Groq integration
├── templates/
│   └── index.html        # Glassmorphic Frontend Dashboard
└── static/
    ├── css/
    │   └── index.css     # Premium dark-mode styling rules & animations
    └── js/
        └── app.js        # Client-side form handlers & UI rendering logic
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher.
- A Groq Cloud API key (Optional: app falls back to local database if not present).

### Installation & Run Setup

1. **Activate the Virtual Environment:**
   Open PowerShell and navigate to the project directory:
   ```powershell
   .\myenv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure your API Key:**
   Open the `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=gsk_your_actual_groq_key_here
   ```

4. **Start the Web Server:**
   ```powershell
   python app.py
   ```

5. **Open the Application:**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask, Groq SDK, Python-dotenv
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Custom Variables, Flexbox, Grid), JavaScript (ES6+ Fetch API, LocalStorage, Print API)
- **AI Model:** `llama-3.3-70b-versatile` (JSON Mode)
