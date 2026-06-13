import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Initialize dotenv to read keys from .env file
load_dotenv()

# Initialize Flask app
# By default, we place HTML files inside templates/ and CSS/JS inside static/
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Fetch the Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check if the API key is a placeholder or empty
has_real_groq_key = (
    GROQ_API_KEY 
    and GROQ_API_KEY.strip() 
    and "your_groq" not in GROQ_API_KEY.lower()
)

# Setup Groq Client if API key is present
if has_real_groq_key:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("🍳 Groq client successfully initialized.")
    except ImportError:
        print("⚠️ Warning: 'groq' package is not installed. Will use fallback database.")
        has_real_groq_key = False
else:
    print("ℹ️ Info: Running in Local Rule-Based Mode. Please set a valid GROQ_API_KEY in the .env file for dynamic generations.")

# --- LOCAL RULE-BASED FALLBACK DATABASE ---
# Serves high-quality responses even if no Groq API Key is configured.
LOCAL_RECIPE_DB = {
    "breakfast": {
        "none_hectic_eco": {
            "name": "Peanut Butter & Banana Toast",
            "time": 5,
            "calories": 320,
            "difficulty": "Easy",
            "image": "https://images.unsplash.com/photo-1541532713592-79a0317b6b77?auto=format&fit=crop&w=400&q=80",
            "prep": ["Slice 1 ripe banana into thin rounds.", "Toast 2 slices of whole wheat bread."],
            "cook": ["Spread 2 tbsp of peanut butter evenly across both slices.", "Top with sliced bananas and a pinch of cinnamon."],
            "ingredients": [
                {"name": "Whole Wheat Bread", "qty": "2 slices", "cost": 0.50, "category": "Pantry", "sub": "Gluten-free bread", "subReason": "for GF alternative"},
                {"name": "Peanut Butter", "qty": "2 tbsp", "cost": 0.30, "category": "Pantry", "sub": "Sunflower seed butter", "subReason": "for nut allergy"},
                {"name": "Banana", "qty": "1 medium", "cost": 0.25, "category": "Produce", "sub": "Apple slices", "subReason": "for a crisp fruit alternative"}
            ]
        },
        "none_balanced_mid": {
            "name": "Smashed Avocado Toast with Eggs",
            "time": 15,
            "calories": 410,
            "difficulty": "Medium",
            "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=400&q=80",
            "prep": ["Pit and smash 1 avocado with lime juice, salt, and red pepper flakes.", "Boil water with vinegar for poaching."],
            "cook": ["Poach 2 eggs for exactly 3 minutes.", "Toast sourdough slices.", "Spread avocado, lay eggs on top, and season with Bagel spice."],
            "ingredients": [
                {"name": "Avocado", "qty": "1 whole", "cost": 1.50, "category": "Produce", "sub": "Hummus", "subReason": "to save $1.00 on budget"},
                {"name": "Fresh Eggs", "qty": "2 large", "cost": 0.60, "category": "Proteins & Dairy", "sub": "Tofu scramble slices", "subReason": "for vegan option"},
                {"name": "Sourdough Bread", "qty": "2 slices", "cost": 0.80, "category": "Pantry", "sub": "Whole wheat bread", "subReason": "to save $0.40"}
            ]
        },
        "none_leisurely_lux": {
            "name": "Ultimate Smoked Salmon Benedict",
            "time": 30,
            "calories": 580,
            "difficulty": "Hard",
            "image": "https://images.unsplash.com/photo-1485921325833-c519f76c4927?auto=format&fit=crop&w=400&q=80",
            "prep": ["Melt butter and whisk egg yolks with lemon juice to prep hollandaise.", "Slice English muffins and prep smoked salmon folds."],
            "cook": ["Whisk and warm hollandaise until thick.", "Poach 2 eggs.", "Toast english muffins, layer salmon and eggs, spoon warm hollandaise over them."],
            "ingredients": [
                {"name": "Smoked Salmon", "qty": "3 oz", "cost": 6.50, "category": "Proteins & Dairy", "sub": "Crispy bacon", "subReason": "to save $4.00 on luxury ingredients"},
                {"name": "English Muffins", "qty": "1 pack", "cost": 1.50, "category": "Pantry", "sub": "Sourdough bread", "subReason": "if muffins are unavailable"},
                {"name": "Butter & Eggs", "qty": "4 oz / 2 eggs", "cost": 1.20, "category": "Proteins & Dairy", "sub": "Avocado crema", "subReason": "for a lighter alternative"}
            ]
        }
    },
    "lunch": {
        "none_hectic_eco": {
            "name": "Classic Chickpea Salad Wrap",
            "time": 10,
            "calories": 450,
            "difficulty": "Easy",
            "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=400&q=80",
            "prep": ["Rinse and drain 1 can of chickpeas.", "Mash chickpeas with 1 tbsp mayonnaise, mustard, salt, and pepper."],
            "cook": ["Lay out a large flour tortilla.", "Spread chickpea mixture, add salad leaves, and roll tightly."],
            "ingredients": [
                {"name": "Canned Chickpeas", "qty": "1 can", "cost": 0.85, "category": "Pantry", "sub": "Canned white beans", "subReason": "to substitute similar protein"},
                {"name": "Mayonnaise", "qty": "1 tbsp", "cost": 0.20, "category": "Pantry", "sub": "Greek yogurt", "subReason": "for lower fat"},
                {"name": "Large Tortillas", "qty": "1 unit", "cost": 0.40, "category": "Pantry", "sub": "Lettuce wraps", "subReason": "for gluten-free/low carb"}
            ]
        },
        "none_balanced_mid": {
            "name": "Mediterranean Grilled Chicken Bowl",
            "time": 25,
            "calories": 520,
            "difficulty": "Medium",
            "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=400&q=80",
            "prep": ["Dice chicken breast into bite-sized cubes.", "Chop cucumber, cherry tomatoes, and red onion."],
            "cook": ["Sauté chicken breast with oregano, garlic, and lemon juice for 8-10 minutes.", "Assemble bowl: base of pre-cooked quinoa, topped with chicken, chopped veggies, and tzatziki."],
            "ingredients": [
                {"name": "Chicken Breast", "qty": "6 oz", "cost": 2.80, "category": "Proteins & Dairy", "sub": "Canned chickpeas", "subReason": "to save $2.00 on meat budget"},
                {"name": "Quinoa", "qty": "0.5 cup dry", "cost": 0.60, "category": "Pantry", "sub": "Brown rice", "subReason": "to save $0.30"},
                {"name": "Cucumber & Tomatoes", "qty": "1 cup", "cost": 1.20, "category": "Produce", "sub": "Mixed greens", "subReason": "if fresh ingredients are sparse"}
            ]
        },
        "none_leisurely_lux": {
            "name": "Pan-Seared Steak & Arugula Salad",
            "time": 35,
            "calories": 710,
            "difficulty": "Medium",
            "image": "https://images.unsplash.com/photo-1485921325833-c519f76c4927?auto=format&fit=crop&w=400&q=80",
            "prep": ["Bring steak to room temp and pat dry.", "Chop walnuts and shave parmesan."],
            "cook": ["Sear steak in cast iron skillet with garlic butter for 3-4 mins per side.", "Let rest for 5 mins.", "Toss wild arugula with olive oil, lemon juice, walnuts, and shaved parmesan.", "Slice steak and serve over salad."],
            "ingredients": [
                {"name": "Ribeye Steak", "qty": "8 oz", "cost": 10.50, "category": "Proteins & Dairy", "sub": "Flank steak", "subReason": "to save $4.00 on premium steak"},
                {"name": "Baby Arugula", "qty": "2 cups", "cost": 1.80, "category": "Produce", "sub": "Baby spinach", "subReason": "for milder greens"},
                {"name": "Parmesan Cheese", "qty": "1 oz", "cost": 1.00, "category": "Proteins & Dairy", "sub": "Feta cheese", "subReason": "for tangy flavor"}
            ]
        }
    },
    "dinner": {
        "none_hectic_eco": {
            "name": "One-Pan Garlic Herb Pasta",
            "time": 15,
            "calories": 490,
            "difficulty": "Easy",
            "image": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80",
            "prep": ["Mince 3 cloves of garlic.", "Boil water for spaghetti."],
            "cook": ["Cook spaghetti in salted water.", "In a pan, heat olive oil, sauté garlic and red pepper flakes.", "Toss pasta directly into garlic oil with some parsley and a splash of cooking water."],
            "ingredients": [
                {"name": "Spaghetti Pasta", "qty": "4 oz", "cost": 0.40, "category": "Pantry", "sub": "Gluten-free pasta", "subReason": "for GF diet"},
                {"name": "Garlic & Olive Oil", "qty": "3 cloves", "cost": 0.60, "category": "Pantry", "sub": "Butter", "subReason": "if olive oil is out"},
                {"name": "Parmesan Cheese", "qty": "0.5 oz", "cost": 0.50, "category": "Proteins & Dairy", "sub": "Nutritional yeast", "subReason": "for vegan meal"}
            ]
        },
        "none_balanced_mid": {
            "name": "Sheet-Pan Teriyaki Salmon & Broccoli",
            "time": 25,
            "calories": 550,
            "difficulty": "Easy",
            "image": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=400&q=80",
            "prep": ["Preheat oven to 400°F.", "Cut broccoli into small florets.", "Pat dry salmon fillet."],
            "cook": ["Arrange salmon and broccoli on baking sheet.", "Brush salmon with teriyaki glaze, oil broccoli.", "Bake for 12-15 minutes.", "Serve alongside a cup of jasmine rice."],
            "ingredients": [
                {"name": "Salmon Fillet", "qty": "6 oz", "cost": 5.50, "category": "Proteins & Dairy", "sub": "Firm Tofu Block", "subReason": "to save $4.00 on protein cost"},
                {"name": "Broccoli Head", "qty": "1 medium", "cost": 1.20, "category": "Produce", "sub": "Frozen green beans", "subReason": "to save $0.60"},
                {"name": "Jasmine Rice", "qty": "0.5 cup dry", "cost": 0.35, "category": "Pantry", "sub": "Cauliflower rice", "subReason": "for keto low-carb"}
            ]
        },
        "none_leisurely_lux": {
            "name": "Tuscan Wine Cream Shrimp Pasta",
            "time": 45,
            "calories": 780,
            "difficulty": "Hard",
            "image": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=400&q=80",
            "prep": ["Peel and devein shrimp.", "Dice shallots, grate fresh parmesan, and wash baby spinach."],
            "cook": ["Sauté shrimp in butter and olive oil; remove from pan.", "Cook fettuccine pasta.", "In same pan, sauté shallots and garlic; deglaze with dry white wine.", "Stir in heavy cream, spinach, and cherry tomatoes.", "Reincorporate shrimp and toss with pasta and parmesan."],
            "ingredients": [
                {"name": "Jumbo Shrimp", "qty": "8 oz", "cost": 8.00, "category": "Proteins & Dairy", "sub": "Diced chicken thighs", "subReason": "to save $4.50 on seafood"},
                {"name": "Heavy Cream", "qty": "1 cup", "cost": 2.50, "category": "Proteins & Dairy", "sub": "Coconut milk", "subReason": "for dairy-free cream sauce"},
                {"name": "Fettuccine Pasta", "qty": "4 oz", "cost": 0.45, "category": "Pantry", "sub": "Spaghetti squash", "subReason": "for low-calorie option"}
            ]
        }
    }
}

def get_fallback_recipe(meal_type, schedule, dietary, budget):
    """
    Grabs local recipe baseline and modifies it to respect dietary restrictions dynamically.
    """
    import copy
    
    # Map budget selection to template tier
    tier = "eco"
    if budget == "mid":
        tier = "mid"
    elif budget == "lux":
        tier = "lux"
        
    general_key = f"none_{schedule}_{tier}"
    if general_key not in LOCAL_RECIPE_DB[meal_type]:
        # Absolute fallback to hectic eco if key is invalid
        general_key = f"none_hectic_eco"
        
    meal = copy.deepcopy(LOCAL_RECIPE_DB[meal_type][general_key])
    
    # Process dietary adjustments dynamically if needed
    if dietary == "vegetarian":
        meal["name"] = meal["name"].replace("Chicken", "Tofu").replace("Salmon", "Tempeh").replace("Shrimp", "Chickpea").replace("Steak", "Portobello Mushroom")
        for ing in meal["ingredients"]:
            name_l = ing["name"].lower()
            if any(x in name_l for x in ["chicken", "salmon", "shrimp", "steak"]):
                ing["name"] = ing["sub"]
                ing["cost"] = max(0.5, ing["cost"] - 2.0)
    elif dietary == "vegan":
        meal["name"] = (meal["name"]
                       .replace("Chicken", "Tofu")
                       .replace("Salmon", "Tempeh")
                       .replace("Shrimp", "Chickpea")
                       .replace("Steak", "Portobello")
                       .replace("Egg", "Tofu Scramble")
                       .replace("Cream", "Coconut Milk"))
        for ing in meal["ingredients"]:
            name_l = ing["name"].lower()
            if any(x in name_l for x in ["chicken", "salmon", "shrimp", "steak", "egg", "yogurt", "cheese", "cream"]):
                ing["name"] = ing["sub"]
                ing["cost"] = max(0.5, ing["cost"] - 1.5)
    elif dietary == "keto":
        meal["name"] = f"{meal['name']} (Low Carb)"
        for ing in meal["ingredients"]:
            name_l = ing["name"].lower()
            if any(x in name_l for x in ["bread", "pasta", "rice", "tortilla"]):
                ing["name"] = ing["sub"]
                ing["cost"] += 0.50
    elif dietary == "gluten-free":
        meal["name"] = f"{meal['name']} (GF)"
        for ing in meal["ingredients"]:
            name_l = ing["name"].lower()
            if any(x in name_l for x in ["bread", "pasta", "tortilla"]):
                ing["name"] = "Gluten-Free " + ing["name"]
                ing["cost"] += 0.60
                
    return meal

def process_local_recipe_generation(schedule, dietary, budget, pantry_list):
    """
    Aggregates breakfast, lunch, and dinner recipe options, matches with pantry,
    and runs the budget feasibility logic.
    """
    bf = get_fallback_recipe("breakfast", schedule, dietary, budget)
    ln = get_fallback_recipe("lunch", schedule, dietary, budget)
    dn = get_fallback_recipe("dinner", schedule, dietary, budget)
    
    # Assemble grocery items
    grocery_items = []
    
    def add_ingredients(ingredients_list):
        for ing in ingredients_list:
            # Check for duplication
            exists = next((g for g in grocery_items if g["name"].lower() == ing["name"].lower()), None)
            if exists:
                exists["cost"] += ing["cost"]
                exists["qty"] = f"{exists['qty']} & {ing['qty']}"
            else:
                grocery_items.append({
                    "name": ing["name"],
                    "qty": ing["qty"],
                    "cost": ing["cost"],
                    "category": ing["category"],
                    "checked": False
                })
                
    add_ingredients(bf["ingredients"])
    add_ingredients(ln["ingredients"])
    add_ingredients(dn["ingredients"])
    
    # Mark pantry list matches as free
    pantry_savings = 0.0
    for item in grocery_items:
        matches_pantry = any(p.strip().lower() in item["name"].lower() for p in pantry_list if p.strip())
        if matches_pantry:
            pantry_savings += item["cost"]
            item["inPantry"] = True
            item["cost"] = 0.0
            item["checked"] = True
            
    total_cost = sum(item["cost"] for item in grocery_items)
    
    limit = 15.0
    if budget == "mid":
        limit = 30.0
    elif budget == "lux":
        limit = 60.0
        
    rating = "ON BUDGET"
    if total_cost < limit * 0.8:
        rating = "UNDER BUDGET"
    elif total_cost > limit:
        rating = "OVER BUDGET"
        
    # Compile substitution list
    subs = []
    for ing in bf["ingredients"] + ln["ingredients"] + dn["ingredients"]:
        if ing.get("sub") and not any(s["original"] == ing["name"] for s in subs):
            subs.append({
                "original": ing["name"],
                "replacement": ing["sub"],
                "reason": ing["subReason"]
            })
            
    # Budget tips list
    tips = []
    if rating == "OVER BUDGET":
        tips.append({
            "strong": "Ingredient swaps:",
            "text": "Switch out fresh proteins or premium greens for canned beans/lentils or frozen vegetables to cut costs."
        })
        tips.append({
            "strong": "Pantry check:",
            "text": f"Adding elements to your pantry list cuts costs. You saved ${pantry_savings:.2f} today using pantry items."
        })
    else:
        tips.append({
            "strong": "Optimal Pricing:",
            "text": "Your selection successfully fits within targeted budget boundaries. Batch cook to save energy."
        })
        if pantry_savings > 0:
            tips.append({
                "strong": "Fridge utilization:",
                "text": f"Reusing items already in your pantry saved you a total of ${pantry_savings:.2f}."
            })
            
    return {
        "meta": {
            "schedule": schedule.capitalize(),
            "dietary": dietary.capitalize(),
            "budgetLimit": limit,
            "budgetTier": budget
        },
        "breakfast": bf,
        "lunch": ln,
        "dinner": dn,
        "groceries": grocery_items,
        "budget": {
            "total": total_cost,
            "limit": limit,
            "rating": rating,
            "tips": tips,
            "savings": pantry_savings
        },
        "substitutions": subs
    }


# --- FLASK ENDPOINTS ---

@app.route("/")
def index():
    """
    Serves the main application landing page.
    """
    return render_template("index.html")


@app.route("/api/status")
def status():
    """
    Returns the backend configuration status.
    """
    return jsonify({
        "has_api_key": has_real_groq_key
    })


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    API endpoint that accepts meal constraints, runs Groq LLM generations
    if a key is configured, or runs the local database rule engine.
    """
    data = request.json or {}
    schedule = data.get("schedule", "hectic")
    dietary = data.get("dietary", "none")
    budget = data.get("budget", "eco")
    pantry = data.get("pantry", [])
    
    # Determine budget limit dollar value
    limit_val = 15.0
    if budget == "mid":
        limit_val = 30.0
    elif budget == "lux":
        limit_val = 60.0

    # If the user has a valid Groq API Key, run dynamic LLM generation
    if has_real_groq_key:
        try:
            print("🚀 Fetching live plan from Groq model: llama-3.3-70b-versatile...")
            
            pantry_str = ", ".join(pantry) if pantry else "None specified"
            
            system_prompt = (
                "You are an expert chef and budget-friendly meal planner. You generate structured 1-day meal plans.\n"
                "You must strictly return a valid JSON object matching the following structure:\n"
                "{\n"
                "  \"breakfast\": {\n"
                "    \"name\": \"Meal Title\",\n"
                "    \"time\": 10,\n"
                "    \"calories\": 350,\n"
                "    \"difficulty\": \"Easy\",\n"
                "    \"prep\": [\"Prep step 1\", \"Prep step 2\"],\n"
                "    \"cook\": [\"Cooking step 1\", \"Cooking step 2\"],\n"
                "    \"ingredients\": [\n"
                "      {\"name\": \"Ingredient Name\", \"qty\": \"Quantity\", \"cost\": 1.20, \"category\": \"Produce\", \"sub\": \"Alternative ingredient\", \"subReason\": \"Reason for sub\"}\n"
                "    ]\n"
                "  },\n"
                "  \"lunch\": { ... same layout as breakfast ... },\n"
                "  \"dinner\": { ... same layout as breakfast ... },\n"
                "  \"budgetTip\": \"A sentence detailing optimization suggestions.\",\n"
                "  \"costExplanation\": \"A sentence explaining how this plan respects the daily budget target.\"\n"
                "}\n"
                "Make sure ingredient costs are realistic, and categories are Produce, Pantry, or Proteins & Dairy."
            )
            
            user_prompt = (
                f"Generate a meal plan with these constraints:\n"
                f"- Day Schedule: {schedule} (Hectic: meals under 15m; Balanced: under 30m; Leisurely: detailed cooking)\n"
                f"- Dietary Restrictions: {dietary}\n"
                f"- Total Daily Budget Target: ${limit_val}\n"
                f"- Pantry ingredients to use up (set their cost to 0.00 if included in recipes): [{pantry_str}]\n"
            )

            # Invoke Groq Chat Completion with JSON mode enabled
            completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2048
            )
            
            # Parse response content
            raw_response = completion.choices[0].message.content
            parsed = json.loads(raw_response)
            
            # Post-process parsed results to ensure consistency
            bf = parsed["breakfast"]
            ln = parsed["lunch"]
            dn = parsed["dinner"]
            
            # Add Unsplash food illustrations based on keywords
            bf["image"] = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80"
            ln["image"] = "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=400&q=80"
            dn["image"] = "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=400&q=80"
            
            # Build global grocery shopping lists
            grocery_items = []
            def aggregate_items(ingredients):
                for ing in ingredients:
                    exists = next((g for g in grocery_items if g["name"].lower() == ing["name"].lower()), None)
                    if exists:
                        exists["cost"] += ing["cost"]
                        exists["qty"] = f"{exists['qty']} & {ing['qty']}"
                    else:
                        grocery_items.append({
                            "name": ing["name"],
                            "qty": ing["qty"],
                            "cost": ing["cost"],
                            "category": ing.get("category", "Pantry"),
                            "checked": False
                        })
                        
            aggregate_items(bf["ingredients"])
            aggregate_items(ln["ingredients"])
            aggregate_items(dn["ingredients"])
            
            # Calculate pantry savings and adjust matching ingredient costs to 0
            pantry_savings = 0.0
            for item in grocery_items:
                matches_pantry = any(p.strip().lower() in item["name"].lower() for p in pantry if p.strip())
                if matches_pantry:
                    pantry_savings += item["cost"]
                    item["inPantry"] = True
                    item["cost"] = 0.0
                    item["checked"] = True
                    
            total_cost = sum(item["cost"] for item in grocery_items)
            
            rating = "ON BUDGET"
            if total_cost < limit_val * 0.8:
                rating = "UNDER BUDGET"
            elif total_cost > limit_val:
                rating = "OVER BUDGET"
                
            # Compile substitutions list
            subs = []
            for ing in bf["ingredients"] + ln["ingredients"] + dn["ingredients"]:
                if ing.get("sub") and not any(s["original"] == ing["name"] for s in subs):
                    subs.append({
                        "original": ing["name"],
                        "replacement": ing["sub"],
                        "reason": ing.get("subReason", "alternative option")
                    })
                    
            # Set up budget tips list
            tips = [
                {"strong": "Groq AI Cost Check:", "text": parsed.get("costExplanation", "Estimated cost calculated successfully.")},
                {"strong": "Optimization Hint:", "text": parsed.get("budgetTip", "Swap fresh components to reduce expenses.")}
            ]
            if pantry_savings > 0:
                tips.append({
                    "strong": "Pantry Utilization:",
                    "text": f"Using items in your fridge saved a total of ${pantry_savings:.2f}."
                })
                
            response_payload = {
                "meta": {
                    "schedule": schedule.capitalize(),
                    "dietary": dietary.capitalize(),
                    "budgetLimit": limit_val,
                    "budgetTier": budget
                },
                "breakfast": bf,
                "lunch": ln,
                "dinner": dn,
                "groceries": grocery_items,
                "budget": {
                    "total": total_cost,
                    "limit": limit_val,
                    "rating": rating,
                    "tips": tips,
                    "savings": pantry_savings
                },
                "substitutions": subs
            }
            return jsonify(response_payload)
            
        except Exception as e:
            print(f"❌ Error during Groq API execution: {str(e)}. Falling back to local data.")
            # Fall back to local processing if API fails or throws errors
            local_fallback = process_local_recipe_generation(schedule, dietary, budget, pantry)
            local_fallback["meta"]["api_error"] = str(e)
            return jsonify(local_fallback)
            
    else:
        # If no key, process and serve local recipe database matching input values
        print("ℹ️ Processing request using local rule-based database...")
        plan = process_local_recipe_generation(schedule, dietary, budget, pantry)
        return jsonify(plan)


# Run server locally on port 5000
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
