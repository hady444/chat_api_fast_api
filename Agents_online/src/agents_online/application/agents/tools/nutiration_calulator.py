from smolagents import Tool
from opik import track
import json
from typing import Dict, List, Optional
from datetime import datetime

class NutritionCalculatorTool(Tool):
    name = "nutrition_calculator"
    description = """Calculate daily caloric needs and macronutrient splits based on user stats and fitness goals. 
    Provides TDEE (Total Daily Energy Expenditure) and recommended protein, carb, and fat intake."""
    
    inputs = {
        "age": {
            "type": "integer",
            "description": "Age in years"
        },
        "weight": {
            "type": "number",
            "description": "Body weight in kilograms"
        },
        "height": {
            "type": "number",
            "description": "Height in centimeters"
        },
        "gender": {
            "type": "string",
            "description": "Biological gender: 'male' or 'female'"
        },
        "activity_level": {
            "type": "string",
            "description": "Activity level: 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'"
        },
        "goal": {
            "type": "string",
            "description": "Fitness goal: 'lose_fat', 'gain_muscle', 'maintain', or 'recomp'"
        }
    }
    output_type = "string"
    
    # Activity multipliers for TDEE calculation
    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,        # Little to no exercise
        "lightly_active": 1.375,  # Exercise 1-3 days/week
                "moderately_active": 1.55,  # Exercise 3-5 days/week
        "very_active": 1.725,       # Exercise 6-7 days/week
        "extra_active": 1.9         # Very intense exercise daily
    }
    
    # Goal adjustments
    GOAL_ADJUSTMENTS = {
        "lose_fat": -500,      # 500 calorie deficit for ~1 lb/week loss
        "gain_muscle": 300,    # 300 calorie surplus for lean gains
        "maintain": 0,         # No adjustment
        "recomp": -100        # Slight deficit for body recomposition
    }
    
    def _calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
        if gender.lower() == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return bmr
    
    def _calculate_macros(self, calories: float, weight: float, goal: str) -> Dict[str, Dict[str, float]]:
        """Calculate macronutrient distribution based on goal"""
        weight_lbs = weight * 2.205  # Convert kg to lbs
        
        macro_splits = {
            "lose_fat": {
                "protein_g_per_lb": 1.0,    # Higher protein to preserve muscle
                "fat_percentage": 0.25,       # 25% from fats
                "carb_percentage": "remainder"
            },
            "gain_muscle": {
                "protein_g_per_lb": 0.8,     # Moderate-high protein
                "fat_percentage": 0.25,       # 25% from fats
                "carb_percentage": "remainder"
            },
            "maintain": {
                "protein_g_per_lb": 0.8,     # Moderate protein
                "fat_percentage": 0.30,       # 30% from fats
                "carb_percentage": "remainder"
            },
            "recomp": {
                "protein_g_per_lb": 1.0,     # High protein for recomp
                "fat_percentage": 0.30,       # 30% from fats
                "carb_percentage": "remainder"
            }
        }
        
        split = macro_splits.get(goal, macro_splits["maintain"])
        
        # Calculate protein
        protein_g = weight_lbs * split["protein_g_per_lb"]
        protein_cal = protein_g * 4  # 4 calories per gram
        
        # Calculate fat
        fat_cal = calories * split["fat_percentage"]
        fat_g = fat_cal / 9  # 9 calories per gram
        
        # Calculate carbs (remainder)
        carb_cal = calories - protein_cal - fat_cal
        carb_g = carb_cal / 4  # 4 calories per gram
        
        return {
            "protein": {"grams": round(protein_g), "calories": round(protein_cal), "percentage": round(protein_cal/calories*100)},
            "carbs": {"grams": round(carb_g), "calories": round(carb_cal), "percentage": round(carb_cal/calories*100)},
            "fat": {"grams": round(fat_g), "calories": round(fat_cal), "percentage": round(fat_cal/calories*100)}
        }
    
    @track(name="NutritionCalculatorTool.forward")
    def forward(self, age: int, weight: float, height: float, gender: str, activity_level: str, goal: str) -> str:
        """Calculate nutrition requirements"""
        try:
            # Validate inputs
            if age < 15 or age > 100:
                return "Error: Age must be between 15 and 100 years."
            if weight < 30 or weight > 300:
                return "Error: Weight must be between 30 and 300 kg."
            if height < 100 or height > 250:
                return "Error: Height must be between 100 and 250 cm."
            
            gender = gender.lower()
            activity_level = activity_level.lower()
            goal = goal.lower()
            
            # Calculate BMR
            bmr = self._calculate_bmr(weight, height, age, gender)
            
            # Calculate TDEE
            activity_multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
            tdee = bmr * activity_multiplier
            
            # Apply goal adjustment
            goal_adjustment = self.GOAL_ADJUSTMENTS.get(goal, 0)
            target_calories = tdee + goal_adjustment
            
            # Calculate macros
            macros = self._calculate_macros(target_calories, weight, goal)
            
            # Format output
            output = f"""# Personalized Nutrition Plan

## Your Stats
- **Age**: {age} years
- **Weight**: {weight} kg ({round(weight * 2.205)} lbs)
- **Height**: {height} cm ({round(height / 2.54)} inches)
- **Gender**: {gender.title()}
- **Activity Level**: {activity_level.replace('_', ' ').title()}
- **Goal**: {goal.replace('_', ' ').title()}

## Calorie Calculations
- **BMR (Basal Metabolic Rate)**: {round(bmr)} calories/day
- **TDEE (Total Daily Energy Expenditure)**: {round(tdee)} calories/day
- **Target Daily Calories**: **{round(target_calories)}** calories/day

## Macronutrient Breakdown
### Protein 🥩
- **{macros['protein']['grams']}g** daily ({macros['protein']['percentage']}% of calories)
- {round(macros['protein']['grams']/4)} servings of 25g protein portions

### Carbohydrates 🍞
- **{macros['carbs']['grams']}g** daily ({macros['carbs']['percentage']}% of calories)
- Focus on complex carbs: oats, rice, sweet potatoes, fruits

### Fats 🥑
- **{macros['fat']['grams']}g** daily ({macros['fat']['percentage']}% of calories)
- Include healthy fats: nuts, avocado, olive oil, fatty fish

## Meal Timing Suggestions
- **Protein**: Spread evenly across {round(macros['protein']['grams']/30)} meals
- **Pre-workout**: 20-30g carbs, 10-15g protein (1-2 hours before)
- **Post-workout**: 30-40g carbs, 20-30g protein (within 2 hours)
- **Hydration**: Minimum {round(weight * 0.033)} liters of water daily

## Important Notes
- These are estimates based on formulas - individual needs vary
- Track progress and adjust calories by 100-200 if needed
- Weigh yourself weekly at the same time for consistency
- Focus on whole, minimally processed foods
- Consider a multivitamin and omega-3 supplement

⚠️ **Disclaimer**: This is general nutritional guidance. Consult with a registered dietitian for personalized meal planning, especially if you have health conditions or dietary restrictions.

Generated on: {datetime.now().strftime('%Y-%m-%d')}
"""
            
            return output
            
        except Exception as e:
            return f"Error calculating nutrition: {str(e)}"