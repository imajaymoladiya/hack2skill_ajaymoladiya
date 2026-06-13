// ChefFlow AI Client-side Application Script

// UI State
let currentPlan = null;
let currentMealTab = 'breakfast';
let pantryIngredients = [];

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  initPantryTags();
  initTabListeners();
  initExportListeners();
  checkBackendStatus();

  // Load from local storage if available
  const savedPlan = localStorage.getItem('chefflow_saved_plan');
  if (savedPlan) {
    try {
      currentPlan = JSON.parse(savedPlan);
      renderResults();
    } catch (e) {
      console.error("Error parsing saved plan", e);
    }
  }

  document.getElementById('generate-plan-btn').addEventListener('click', generatePlan);
});

// Check if Backend server has a valid Groq API Key
async function checkBackendStatus() {
  const badge = document.getElementById('backend-status-badge');
  try {
    const response = await fetch('/api/status');
    if (response.ok) {
      const data = await response.json();
      if (data.has_api_key) {
        badge.innerHTML = "<span>⚡</span> Groq API Ready";
        badge.className = "settings-btn api-active";
      } else {
        badge.innerHTML = "<span>⚠️</span> Local AI Mode";
        badge.className = "settings-btn api-inactive";
      }
    } else {
      badge.innerHTML = "<span>❌</span> Server Offline";
      badge.className = "settings-btn api-inactive";
    }
  } catch (e) {
    badge.innerHTML = "<span>❌</span> Connection Lost";
    badge.className = "settings-btn api-inactive";
  }
}

// Tag selector logic for fridge/pantry inventory
function initPantryTags() {
  const input = document.getElementById('pantry-raw-input');
  const container = document.getElementById('pantry-tags-container');

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const val = input.value.trim().replace(/,/g, '');
      if (val && !pantryIngredients.includes(val.toLowerCase())) {
        addPantryTag(val);
      }
      input.value = '';
    }
  });

  // Fallback on blur
  input.addEventListener('blur', () => {
    const val = input.value.trim().replace(/,/g, '');
    if (val && !pantryIngredients.includes(val.toLowerCase())) {
      addPantryTag(val);
    }
    input.value = '';
  });
}

function addPantryTag(name) {
  const container = document.getElementById('pantry-tags-container');
  const input = document.getElementById('pantry-raw-input');
  
  const cleanName = name.toLowerCase();
  pantryIngredients.push(cleanName);

  const tag = document.createElement('span');
  tag.className = 'tag';
  tag.dataset.value = cleanName;
  tag.innerHTML = `${name} <span class="tag-remove">&times;</span>`;

  tag.querySelector('.tag-remove').addEventListener('click', () => {
    pantryIngredients = pantryIngredients.filter(item => item !== cleanName);
    tag.remove();
  });

  container.insertBefore(tag, input);
}

// Tab handlers for meal timelines (Breakfast, Lunch, Dinner)
function initTabListeners() {
  const buttons = document.querySelectorAll('.meal-tab-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentMealTab = btn.dataset.meal;
      renderActiveMeal();
    });
  });
}

// Post form parameters to Flask API
async function generatePlan() {
  const schedule = document.querySelector('input[name="schedule"]:checked').value;
  const dietary = document.getElementById('dietary-select').value;
  const budget = document.querySelector('input[name="budget"]:checked').value;

  // Toggle Loading visual states
  document.getElementById('state-placeholder').style.display = 'none';
  document.getElementById('state-results').style.display = 'none';
  document.getElementById('state-loading').style.display = 'flex';

  resetLoadingProgress();

  try {
    // Start animation step flow
    const stepsPromise = animateSteps(2000);

    // Call Flask backend
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        schedule: schedule,
        dietary: dietary,
        budget: budget,
        pantry: pantryIngredients
      })
    });

    if (!response.ok) {
      throw new Error("Server API call failed.");
    }

    const planData = await response.json();
    
    // Wait for the steps animation to look natural
    await stepsPromise;

    currentPlan = planData;
    localStorage.setItem('chefflow_saved_plan', JSON.stringify(currentPlan));
    
    renderResults();
    
    // Display API warnings if Groq failed during execution
    if (currentPlan.meta.api_error) {
      showToast("⚠️ API error: Used local rule fallback database.");
    } else {
      showToast("✨ AI Meal Plan Created!");
    }

  } catch (err) {
    console.error(err);
    showToast("❌ Plan Generation Failed. Try checking python console.");
    document.getElementById('state-loading').style.display = 'none';
    document.getElementById('state-placeholder').style.display = 'flex';
  }
}

// Loading steps animations
function resetLoadingProgress() {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`load-step-${i}`);
    el.classList.remove('active', 'completed');
  }
}

async function animateSteps(timeTotal) {
  const stepTime = timeTotal / 4;
  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`load-step-${i}`);
    el.classList.add('active');
    await delay(stepTime);
    el.classList.remove('active');
    el.classList.add('completed');
  }
}

// Render Results layout
function renderResults() {
  document.getElementById('state-loading').style.display = 'none';
  document.getElementById('state-placeholder').style.display = 'none';
  
  const resultsView = document.getElementById('state-results');
  resultsView.style.display = 'flex';

  // Summary headline details
  const headlineDesc = document.getElementById('plan-headline-desc');
  headlineDesc.textContent = `Optimized for a ${currentPlan.meta.schedule} day, ${currentPlan.meta.dietary} focus, $${currentPlan.meta.budgetLimit.toFixed(2)} target.`;

  renderActiveMeal();
  renderGroceries();
  renderBudgetFeasibility();
  renderSubstitutions();
}

// Render active selected tab
function renderActiveMeal() {
  const meal = currentPlan[currentMealTab];
  if (!meal) return;

  document.getElementById('meal-card-title').textContent = meal.name;
  document.getElementById('meal-card-type').textContent = currentMealTab.toUpperCase();
  document.getElementById('meal-card-tag').textContent = `${meal.time} Min • ${meal.difficulty}`;
  document.getElementById('meal-card-image').style.backgroundImage = `url('${meal.image}')`;

  document.getElementById('meal-card-time').textContent = `${meal.time} mins`;
  document.getElementById('meal-card-calories').textContent = `${meal.calories} kcal`;
  document.getElementById('meal-card-difficulty').textContent = meal.difficulty;

  // Prep steps
  const prepList = document.getElementById('meal-prep-checklist');
  prepList.innerHTML = '';
  meal.prep.forEach((step, idx) => {
    const item = createChecklistItem(`prep-${currentMealTab}-${idx}`, step);
    prepList.appendChild(item);
  });

  // Cook steps
  const cookList = document.getElementById('meal-cook-checklist');
  cookList.innerHTML = '';
  meal.cook.forEach((step, idx) => {
    const item = createChecklistItem(`cook-${currentMealTab}-${idx}`, step);
    cookList.appendChild(item);
  });
}

function createChecklistItem(id, text) {
  const label = document.createElement('label');
  label.className = 'checklist-item';
  label.id = `label-${id}`;
  
  const isChecked = localStorage.getItem(`chk-${id}`) === 'true';
  if (isChecked) {
    label.classList.add('checked');
  }

  label.innerHTML = `
    <div class="checkbox-custom"></div>
    <span class="checklist-text">${text}</span>
  `;

  label.addEventListener('click', (e) => {
    e.preventDefault();
    const checked = label.classList.toggle('checked');
    localStorage.setItem(`chk-${id}`, checked);
  });

  return label;
}

// Render shopping lists
function renderGroceries() {
  const container = document.getElementById('grocery-list-container');
  container.innerHTML = '';

  const grouped = {};
  currentPlan.groceries.forEach(item => {
    const cat = item.category || 'Pantry';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(item);
  });

  Object.keys(grouped).forEach(category => {
    const cardGroup = document.createElement('div');
    cardGroup.className = 'grocery-category-group';

    let catEmoji = '📦';
    if (category.toLowerCase().includes('produce')) catEmoji = '🥦';
    if (category.toLowerCase().includes('protein') || category.toLowerCase().includes('dairy')) catEmoji = '🥩';

    cardGroup.innerHTML = `
      <div class="grocery-category-title">${catEmoji} ${category}</div>
      <div class="checklist" id="category-${category.replace(/\s+/g, '')}"></div>
    `;

    const listContainer = cardGroup.querySelector('.checklist');

    grouped[category].forEach(item => {
      const itemRow = document.createElement('div');
      itemRow.className = 'grocery-item';
      
      const itemLabel = document.createElement('label');
      itemLabel.className = 'checklist-item';
      if (item.checked || item.inPantry) itemLabel.classList.add('checked');

      const storeKey = `grocery-${item.name.replace(/\s+/g, '')}`;
      if (localStorage.getItem(storeKey) === 'true' || item.inPantry) {
        itemLabel.classList.add('checked');
      }

      const pantryLabel = item.inPantry ? ' <span style="color:var(--primary); font-size:0.75rem;">(In Pantry)</span>' : '';

      itemLabel.innerHTML = `
        <div class="checkbox-custom"></div>
        <span class="checklist-text">${item.name} (${item.qty})${pantryLabel}</span>
      `;

      itemLabel.addEventListener('click', (e) => {
        e.preventDefault();
        const checked = itemLabel.classList.toggle('checked');
        localStorage.setItem(storeKey, checked);
      });

      const priceVal = item.inPantry ? '$0.00' : `$${item.cost.toFixed(2)}`;
      const price = document.createElement('span');
      price.className = 'grocery-cost';
      price.textContent = priceVal;

      itemRow.appendChild(itemLabel);
      itemRow.appendChild(price);
      listContainer.appendChild(itemRow);
    });

    container.appendChild(cardGroup);
  });
}

// Feasibility stats & progress bars
function renderBudgetFeasibility() {
  const total = currentPlan.budget.total;
  const limit = currentPlan.budget.limit;

  document.getElementById('budget-est-cost').textContent = `$${total.toFixed(2)}`;

  const badge = document.getElementById('feasibility-rating-badge');
  badge.textContent = currentPlan.budget.rating;
  badge.className = 'feasibility-badge';

  if (currentPlan.budget.rating === 'UNDER BUDGET') {
    badge.classList.add('status-under');
  } else if (currentPlan.budget.rating === 'OVER BUDGET') {
    badge.classList.add('status-over');
  } else {
    badge.classList.add('status-on');
  }

  const fill = document.getElementById('budget-gauge-fill');
  const percentage = Math.min(100, (total / limit) * 100);
  fill.style.width = `${percentage}%`;

  fill.className = 'gauge-bar-fill';
  if (percentage > 100) {
    fill.classList.add('danger');
  } else if (percentage > 80) {
    fill.classList.add('warning');
  }

  const tipsContainer = document.getElementById('budget-tips-list');
  tipsContainer.innerHTML = '';
  currentPlan.budget.tips.forEach(tip => {
    const tipEl = document.createElement('div');
    tipEl.className = 'budget-tip-card';
    tipEl.innerHTML = `
      <div class="budget-tip-icon">💡</div>
      <div class="budget-tip-content">
        <strong>${tip.strong}</strong> ${tip.text}
      </div>
    `;
    tipsContainer.appendChild(tipEl);
  });
}

// Render dynamic substitution alternatives
function renderSubstitutions() {
  const container = document.getElementById('substitutions-list');
  container.innerHTML = '';

  if (currentPlan.substitutions.length === 0) {
    container.innerHTML = `<p class="subtitle" style="font-style: italic;">No substitutions needed.</p>`;
    return;
  }

  currentPlan.substitutions.forEach(sub => {
    const div = document.createElement('div');
    div.className = 'sub-item';
    div.innerHTML = `
      <div>
        <span class="sub-original">${sub.original}</span>
        <span style="color:var(--text-muted); font-size:0.75rem;">(${sub.reason})</span>
      </div>
      <span class="sub-replacement">➔ ${sub.replacement}</span>
    `;
    container.appendChild(div);
  });
}

// Clipboard copying & print hooks
function initExportListeners() {
  document.getElementById('export-copy-btn').addEventListener('click', () => {
    if (!currentPlan) return;
    
    let text = `🍲 ChefFlow AI Daily Meal Plan 🍲\n`;
    text += `===================================\n`;
    text += `Schedule: ${currentPlan.meta.schedule} | Focus: ${currentPlan.meta.dietary}\n`;
    text += `Target Daily Budget: $${currentPlan.meta.budgetLimit.toFixed(2)}\n`;
    text += `Estimated Total Cost: $${currentPlan.budget.total.toFixed(2)}\n\n`;

    const formatMeal = (type, meal) => {
      let str = `🌅 ${type.toUpperCase()}: ${meal.name} (${meal.time} mins, ${meal.calories} kcal)\n`;
      str += `--- Ingredients ---\n`;
      meal.ingredients.forEach(i => {
        str += `- ${i.name} (${i.qty})\n`;
      });
      str += `--- Prep Steps ---\n`;
      meal.prep.forEach((p, idx) => str += `${idx + 1}. ${p}\n`);
      str += `--- Active Cooking ---\n`;
      meal.cook.forEach((c, idx) => str += `${idx + 1}. ${c}\n`);
      str += `\n`;
      return str;
    };

    text += formatMeal('Breakfast', currentPlan.breakfast);
    text += formatMeal('Lunch', currentPlan.lunch);
    text += formatMeal('Dinner', currentPlan.dinner);

    text += `🛒 grocery shopping list 🛒\n`;
    currentPlan.groceries.forEach(g => {
      const tag = g.inPantry ? ' (In Pantry)' : '';
      text += `[ ] ${g.name} (${g.qty}) - $${g.cost.toFixed(2)}${tag}\n`;
    });

    navigator.clipboard.writeText(text).then(() => {
      showToast("📋 Plan copied to clipboard!");
    }).catch(err => {
      console.error("Failed to copy", err);
      showToast("❌ Copy failed.");
    });
  });

  document.getElementById('export-print-btn').addEventListener('click', () => {
    window.print();
  });
}

function showToast(message) {
  const toast = document.getElementById('toast-notification');
  const msgSpan = document.getElementById('toast-message');
  msgSpan.textContent = message;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}
