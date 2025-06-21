from smolagents import Tool
from opik import track
import json
from typing import Dict, List, Optional
from datetime import datetime
class ExerciseSafetyValidatorTool(Tool):
    name = "exercise_safety_validator"
    description = """Validate if exercises are safe given user's conditions, experience level, or physical limitations. 
    Provides safety warnings and exercise modifications when needed."""
    
    inputs = {
        "exercise": {
            "type": "string",
            "description": "The exercise name to validate (e.g., 'deadlift', 'bench press', 'squats')"
            },
        "conditions": {
            "type": "string",
            "description": "User conditions/limitations as comma-separated list (e.g., 'lower_back_pain,beginner,knee_issues')",
            "nullable": True
        }
    }
    output_type = "string"
    
    # Common exercise risks and contraindications
    EXERCISE_RISKS = {
        "deadlift": {
            "risks": ["lower back strain", "hamstring injury", "bicep tear"],
            "contraindications": ["acute_back_pain", "herniated_disc", "severe_scoliosis"],
            "high_risk_for": ["lower_back_pain", "back_injury", "beginner"],
            "modifications": {
                "lower_back_pain": "Try trap bar deadlifts or Romanian deadlifts with lighter weight",
                "beginner": "Start with Romanian deadlifts or rack pulls to learn the movement",
                "knee_issues": "Use sumo stance for better knee angle"
            }
        },
        "squats": {
            "risks": ["knee strain", "lower back compression", "hip impingement"],
            "contraindications": ["acute_knee_injury", "severe_hip_issues"],
            "high_risk_for": ["knee_issues", "hip_issues", "ankle_mobility", "beginner"],
            "modifications": {
                "knee_issues": "Try box squats, goblet squats, or leg press instead",
                "hip_issues": "Use wider stance or switch to split squats",
                "ankle_mobility": "Use heel elevation or work on mobility first",
                "beginner": "Start with goblet squats or bodyweight squats"
            }
        },
        "bench_press": {
            "risks": ["shoulder impingement", "rotator cuff injury", "elbow strain"],
            "contraindications": ["acute_shoulder_injury", "torn_rotator_cuff"],
            "high_risk_for": ["shoulder_issues", "elbow_issues", "beginner"],
            "modifications": {
                "shoulder_issues": "Use dumbbells with neutral grip or decline angle",
                "elbow_issues": "Reduce range of motion or use lighter weight",
                "beginner": "Start with dumbbells for better control"
            }
        },
        "overhead_press": {
            "risks": ["shoulder impingement", "lower back hyperextension"],
            "contraindications": ["shoulder_impingement", "acute_shoulder_injury"],
            "high_risk_for": ["shoulder_issues", "lower_back_pain", "neck_issues"],
            "modifications": {
                "shoulder_issues": "Use landmine press or Arnold press variation",
                "lower_back_pain": "Perform seated with back support",
                "neck_issues": "Use dumbbells and avoid behind-the-neck variation"
            }
        },
        "pull_ups": {
            "risks": ["shoulder strain", "elbow tendonitis", "grip fatigue"],
            "contraindications": ["acute_shoulder_injury", "severe_elbow_issues"],
            "high_risk_for": ["shoulder_issues", "elbow_issues", "overweight", "beginner"],
            "modifications": {
                "beginner": "Use assisted pull-up machine or resistance bands",
                "overweight": "Start with lat pulldowns until strength improves",
                "shoulder_issues": "Use neutral grip or wider grip"
            }
        }
    }
    
    # General safety guidelines
    SAFETY_GUIDELINES = {
        "beginner": [
            "Always start with bodyweight or light weights",
            "Focus on form over weight",
            "Consider working with a trainer initially",
            "Progress gradually (10% increase per week maximum)"
        ],
        "lower_back_pain": [
            "Avoid heavy axial loading",
            "Strengthen core before heavy compounds",
            "Maintain neutral spine at all times",
            "Consider using a belt for support on heavy lifts"
        ],
        "knee_issues": [
            "Avoid deep knee flexion initially",
            "Focus on proper knee tracking",
            "Strengthen supporting muscles (quads, hamstrings, glutes)",
            "Consider knee sleeves for support"
        ],
        "shoulder_issues": [
            "Warm up thoroughly with band work",
            "Avoid behind-the-neck movements",
            "Focus on scapular stability",
            "Limit overhead work until cleared"
        ]
    }
    
    def _normalize_exercise_name(self, exercise: str) -> str:
        """Normalize exercise name for matching"""
        exercise = exercise.lower().strip()
        
        # Common variations mapping
        variations = {
            "back squat": "squats",
            "barbell squat": "squats",
            "squat": "squats",
            "conventional deadlift": "deadlift",
            "barbell deadlift": "deadlift",
            "military press": "overhead_press",
            "shoulder press": "overhead_press",
            "ohp": "overhead_press",
            "pullups": "pull_ups",
            "chin ups": "pull_ups",
            "chinups": "pull_ups"
        }
        
        return variations.get(exercise, exercise.replace(" ", "_"))
    
    def _parse_conditions(self, conditions: str) -> List[str]:
        """Parse and normalize conditions"""
        if not conditions:
            return []
        
        normalized = []
        for condition in conditions.split(","):
            condition = condition.strip().lower().replace(" ", "_")
            normalized.append(condition)
        
        return normalized
    
    @track(name="ExerciseSafetyValidatorTool.forward")
    def forward(self, exercise: str, conditions: str = "") -> str:
        """Validate exercise safety and provide recommendations"""
        try:
            # Normalize inputs
            exercise_normalized = self._normalize_exercise_name(exercise)
            user_conditions = self._parse_conditions(conditions)
            
            # Get exercise info
            exercise_info = self.EXERCISE_RISKS.get(exercise_normalized)
            
            if not exercise_info:
                # Exercise not in database - provide general guidance
                return f"""# Safety Assessment: {exercise.title()}

## Status: ⚠️ Limited Information Available

This exercise is not in our detailed safety database. Here are general safety guidelines:

### General Precautions:
1. **Learn Proper Form**: Work with a qualified trainer or study reputable sources
2. **Start Light**: Begin with minimal weight to master the movement
3. **Warm Up**: Always perform dynamic warm-up before exercising
4. **Listen to Your Body**: Stop if you feel pain (not to be confused with muscle fatigue)
5. **Progress Gradually**: Increase weight/intensity by no more than 10% per week

### Red Flags to Stop Immediately:
- Sharp or shooting pain
- Joint pain (not muscle soreness)
- Dizziness or lightheadedness
- Unusual shortness of breath
- Numbness or tingling

⚠️ **Important**: Always consult with a fitness professional for exercises you're unfamiliar with.
"""
            
            # Check for contraindications
            contraindications_found = []
            high_risks_found = []
            applicable_modifications = {}
            
            for condition in user_conditions:
                if condition in exercise_info["contraindications"]:
                    contraindications_found.append(condition)
                elif condition in exercise_info["high_risk_for"]:
                    high_risks_found.append(condition)
                    if condition in exercise_info["modifications"]:
                        applicable_modifications[condition] = exercise_info["modifications"][condition]
            
            # Build safety assessment
            if contraindications_found:
                status = "❌ NOT RECOMMENDED"
                safety_level = "HIGH RISK"
            elif high_risks_found:
                status = "⚠️ CAUTION ADVISED"
                safety_level = "MODERATE RISK"
            else:
                status = "✅ GENERALLY SAFE"
                safety_level = "LOW RISK"
            
            output = f"""# Safety Assessment: {exercise.title()}

## Status: {status}
**Safety Level**: {safety_level}
**Your Conditions**: {', '.join(user_conditions) if user_conditions else 'None specified'}

## Risk Analysis
### General Risks for {exercise.title()}:
"""
            for risk in exercise_info["risks"]:
                output += f"- {risk.title()}\n"
            
            if contraindications_found:
                output += f"\n### ❌ CONTRAINDICATIONS FOUND: **This exercise is NOT recommended due to:**\n"
                for contra in contraindications_found:
                    output += f"- {contra.replace('_', ' ').title()}\n"
                
                output += "\n**Recommended Alternatives:**\n"
                output += "- Consult with a physical therapist for safe alternatives\n"
                output += "- Focus on rehabilitation exercises first\n"
                output += "- Consider lower-impact variations\n"
            
            elif high_risks_found:
                output += f"\n### ⚠️ CAUTION AREAS: **Extra care needed due to:**\n"
                for risk in high_risks_found:
                    output += f"- {risk.replace('_', ' ').title()}\n"
                
                output += "\n### Recommended Modifications:\n"
                for condition, modification in applicable_modifications.items():
                    output += f"**For {condition.replace('_', ' ')}**: {modification}\n"
            
            # Add specific guidelines for conditions
            output += "\n## Safety Guidelines:\n"
            guidelines_added = set()
            for condition in user_conditions:
                if condition in self.SAFETY_GUIDELINES and condition not in guidelines_added:
                    output += f"\n### For {condition.replace('_', ' ').title()}:\n"
                    for guideline in self.SAFETY_GUIDELINES[condition]:
                        output += f"- {guideline}\n"
                    guidelines_added.add(condition)
            
            # Add general safety tips
            output += """
## General Safety Protocol:
1. **Warm-Up**: 5-10 minutes of light cardio + dynamic stretching
2. **Form Check**: Use mirrors or record yourself
3. **Breathing**: Never hold your breath - exhale on exertion
4. **Spotter**: Use one for heavy lifts when applicable
5. **Recovery**: Allow 48-72 hours between training same muscle groups

## Progressive Loading:
- **Week 1-2**: Master form with bodyweight/empty bar
- **Week 3-4**: Add minimal weight (5-10 lbs)
- **Week 5+**: Increase by 5-10% when you can complete all sets with good form

## When to Stop:
- Any sharp or acute pain
- Feeling of instability or "giving out"
- Significant form breakdown
- Dizziness or nausea

⚠️ **Medical Disclaimer**: This is general safety information only. Always consult with healthcare providers about your specific conditions before starting any exercise program. If you have injuries or medical conditions, work with qualified professionals.

Generated on: {datetime.now().strftime('%Y-%m-%d')}
"""
            
            return output
            
        except Exception as e:
            return f"Error validating exercise safety: {str(e)}"
        

n=ExerciseSafetyValidatorTool()
print(n.name)