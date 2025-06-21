from smolagents import Tool
from opik import track
import json
from typing import Dict, List, Optional
from datetime import datetime


class WorkoutPlanGeneratorTool(Tool):
    name = "workout_plan_generator"
    description = """Generate personalized workout plans based on user goals, experience level, and available equipment. 
    This tool creates structured workout routines with exercises, sets, reps, and rest periods."""
    
    inputs = {
        "goals": {
            "type": "string", 
            "description": "User's fitness goals: 'muscle_gain', 'fat_loss', 'strength', 'endurance', or 'general_fitness'"
        },
        "experience": {
            "type": "string", 
            "description": "Experience level: 'beginner', 'intermediate', or 'advanced'"
        },
        "equipment": {
            "type": "string", 
            "description": "Available equipment: 'full_gym', 'home_basic' (dumbbells/bands), or 'bodyweight_only'"
        },
        "days_per_week": {
            "type": "integer", 
            "description": "Number of training days per week (2-6)"
        }
    }
    output_type = "string"
    
    # Workout templates based on experience and equipment
    WORKOUT_TEMPLATES = {
        "beginner": {
            "full_gym": {
                "upper": ["Bench Press", "Lat Pulldown", "Shoulder Press", "Seated Row", "Bicep Curls", "Tricep Pushdowns"],
                "lower": ["Squats", "Leg Press", "Leg Curls", "Leg Extensions", "Calf Raises", "Planks"],
                "full_body": ["Squats", "Bench Press", "Bent-Over Row", "Shoulder Press", "Deadlifts", "Planks"]
            },
            "home_basic": {
                "upper": ["Dumbbell Press", "Dumbbell Rows", "Shoulder Press", "Bicep Curls", "Tricep Extensions", "Band Pull-Aparts"],
                "lower": ["Goblet Squats", "Lunges", "Romanian Deadlifts", "Calf Raises", "Glute Bridges", "Planks"],
                "full_body": ["Goblet Squats", "Dumbbell Press", "Dumbbell Rows", "Lunges", "Shoulder Press", "Planks"]
            },
            "bodyweight_only": {
                "upper": ["Push-ups", "Pull-ups/Inverted Rows", "Pike Push-ups", "Dips", "Diamond Push-ups", "Planks"],
                "lower": ["Bodyweight Squats", "Lunges", "Jump Squats", "Single-Leg Deadlifts", "Calf Raises", "Wall Sits"],
                "full_body": ["Burpees", "Push-ups", "Squats", "Mountain Climbers", "Lunges", "Planks"]
            }
        },
        "intermediate": {
            "full_gym": {
                "push": ["Bench Press", "Incline Dumbbell Press", "Shoulder Press", "Lateral Raises", "Tricep Dips", "Cable Flyes"],
                "pull": ["Deadlifts", "Pull-ups", "Barbell Rows", "Face Pulls", "Bicep Curls", "Shrugs"],
                "legs": ["Squats", "Romanian Deadlifts", "Leg Press", "Walking Lunges", "Leg Curls", "Calf Raises"],
                "upper": ["Bench Press", "Bent-Over Row", "Overhead Press", "Pull-ups", "Dumbbell Curls", "Skullcrushers"],
                "lower": ["Front Squats", "Deadlifts", "Bulgarian Split Squats", "Leg Curls", "Leg Extensions", "Calf Raises"]
            }
        },
        "advanced": {
            "full_gym": {
                "push": ["Bench Press", "Incline Barbell Press", "Dumbbell Press", "Military Press", "Dips", "Cable Crossovers", "Tricep Extensions"],
                "pull": ["Deadlifts", "Weighted Pull-ups", "T-Bar Rows", "Cable Rows", "Barbell Curls", "Hammer Curls", "Face Pulls"],
                "legs": ["Back Squats", "Front Squats", "Romanian Deadlifts", "Walking Lunges", "Leg Press", "Leg Curls", "Calf Raises"]
            }
        }
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _get_rep_scheme(self, goal: str, experience: str) -> Dict[str, str]:
        """Determine rep ranges based on goal and experience"""
        schemes = {
            "muscle_gain": {
                "beginner": {"sets": "3", "reps": "8-12", "rest": "60-90 seconds"},
                "intermediate": {"sets": "4", "reps": "8-12", "rest": "60-90 seconds"},
                "advanced": {"sets": "4-5", "reps": "6-12", "rest": "90-120 seconds"}
            },
            "strength": {
                "beginner": {"sets": "3", "reps": "5-8", "rest": "2-3 minutes"},
                "intermediate": {"sets": "4-5", "reps": "3-6", "rest": "3-4 minutes"},
                "advanced": {"sets": "5-6", "reps": "1-5", "rest": "3-5 minutes"}
            },
            "fat_loss": {
                "beginner": {"sets": "3", "reps": "12-15", "rest": "30-45 seconds"},
                "intermediate": {"sets": "3-4", "reps": "12-20", "rest": "30-45 seconds"},
                "advanced": {"sets": "4", "reps": "15-20", "rest": "30 seconds"}
            },
            "endurance": {
                "beginner": {"sets": "2-3", "reps": "15-20", "rest": "30 seconds"},
                "intermediate": {"sets": "3", "reps": "15-25", "rest": "30 seconds"},
                "advanced": {"sets": "3-4", "reps": "20-30", "rest": "15-30 seconds"}
            },
            "general_fitness": {
                "beginner": {"sets": "3", "reps": "10-12", "rest": "60 seconds"},
                "intermediate": {"sets": "3-4", "reps": "10-15", "rest": "45-60 seconds"},
                "advanced": {"sets": "4", "reps": "8-15", "rest": "45-60 seconds"}
            }
        }
        return schemes.get(goal, schemes["general_fitness"]).get(experience, schemes["general_fitness"]["beginner"])
    
    def _get_split(self, days_per_week: int, experience: str) -> List[str]:
        """Determine workout split based on frequency and experience"""
        splits = {
            2: ["full_body", "full_body"],
            3: ["full_body", "full_body", "full_body"] if experience == "beginner" else ["push", "pull", "legs"],
            4: ["upper", "lower", "upper", "lower"],
            5: ["push", "pull", "legs", "upper", "lower"],
            6: ["push", "pull", "legs", "push", "pull", "legs"]
        }
        return splits.get(days_per_week, splits[3])
    
    @track(name="WorkoutPlanGeneratorTool.forward")
    def forward(self, goals: str, experience: str, equipment: str, days_per_week: int) -> str:
        """Generate a structured workout plan"""
        try:
            # Validate inputs
            if days_per_week < 2 or days_per_week > 6:
                return "Error: Training days must be between 2 and 6 per week."
            
            goals = goals.lower()
            experience = experience.lower()
            equipment = equipment.lower()
            
            # Get appropriate workout split
            split = self._get_split(days_per_week, experience)
            
            # Get rep scheme
            rep_scheme = self._get_rep_scheme(goals, experience)
            
            # Build workout plan
            plan = f"""# Personalized Workout Plan

## Overview
- **Goal**: {goals.replace('_', ' ').title()}
- **Experience**: {experience.title()}
- **Equipment**: {equipment.replace('_', ' ').title()}
- **Frequency**: {days_per_week} days per week
- **Split**: {', '.join(split).replace('_', ' ').title()}

## Training Parameters
- **Sets**: {rep_scheme['sets']} per exercise
- **Reps**: {rep_scheme['reps']}
- **Rest**: {rep_scheme['rest']}

## Weekly Schedule
"""
            # Get exercises for each day
            templates = self.WORKOUT_TEMPLATES.get(experience, self.WORKOUT_TEMPLATES["beginner"])
            equipment_exercises = templates.get(equipment, templates.get("full_gym", {}))
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            workout_days = []
            
            for i, workout_type in enumerate(split):
                day = days[i] if i < len(days) else f"Day {i+1}"
                exercises = equipment_exercises.get(workout_type, equipment_exercises.get("full_body", []))
                
                workout_days.append(f"\n### {day}: {workout_type.replace('_', ' ').title()}")
                for j, exercise in enumerate(exercises[:6], 1):  # Limit to 6 exercises
                    workout_days.append(f"{j}. **{exercise}** - {rep_scheme['sets']} sets x {rep_scheme['reps']} reps")
            
            plan += "\n".join(workout_days)
            
            # Add important notes
            plan += f"""

## Important Notes
- **Warm-up**: Always start with 5-10 minutes of light cardio and dynamic stretching
- **Cool-down**: End with 5-10 minutes of stretching
- **Progressive Overload**: Increase weight/reps/sets gradually each week
- **Form First**: Focus on proper form before increasing weight
- **Rest Days**: Take at least {7 - days_per_week} rest days per week
- **Nutrition**: Ensure adequate protein intake (0.7-1g per lb of body weight)
- **Hydration**: Drink plenty of water before, during, and after workouts

⚠️ **Disclaimer**: This is a general workout plan. Consult with a certified personal trainer for personalized guidance, especially if you have any injuries or health conditions.

Generated on: {datetime.now().strftime('%Y-%m-%d')}
"""
            
            return plan
            
        except Exception as e:
            return f"Error generating workout plan: {str(e)}"