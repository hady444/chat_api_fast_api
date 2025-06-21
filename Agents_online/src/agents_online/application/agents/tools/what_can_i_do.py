import opik
from smolagents import tool


@opik.track(name="what_can_i_do")
@tool
def what_can_i_do(question: str) -> str:
    """Returns a comprehensive list of available fitness and health topics the assistant can help with.

    This tool should be used when:
    - The user explicitly asks what the system can do
    - The user asks about available fitness/health topics
    - The user seems unsure about what questions they can ask
    - The user wants to explore available knowledge areas

    This tool should NOT be used when:
    - The user asks a specific fitness/nutrition question
    - The user already knows what they want to learn about
    - The question is about a specific topic covered in the knowledge base

    Args:
        question: The user's query about system capabilities. While this parameter is required,
                 the function returns a standard capability list regardless of the specific question.

    Returns:
        str: A formatted string containing categorized lists of example questions and topics
             that users can explore within the fitness and health information system.

    Examples:
        >>> what_can_i_do("What can you help me with?")
        >>> what_can_i_do("What fitness topics do you cover?")
        >>> what_can_i_do("What kind of health questions can I ask?")
    """

    return """
I'm a fitness and health information assistant. I can provide general information about various fitness and wellness topics. Here's what I can help you learn about:

**IMPORTANT DISCLAIMER**: I am NOT a certified personal trainer, medical doctor, or nutritionist. I only provide general educational information. For personalized advice, medical concerns, or specific health conditions, please consult qualified professionals.

I can help you find information about:

💪 **Muscle Building & Strength Training:**
- Basic principles of muscle growth (hypertrophy)
- Common training splits and workout routines
- Progressive overload concepts
- Different training techniques (supersets, drop sets, etc.)
- Form tips for popular exercises

🔥 **Fat Loss & Body Composition:**
- General principles of caloric deficit
- Common fat loss strategies
- Metabolic adaptation basics
- Cardio vs strength training for fat loss
- Body recomposition concepts

🏋️ **Training & Exercise:**
- Different training styles (bodybuilding, powerlifting, crossfit)
- Beginner workout programs
- Exercise selection for different goals
- Training frequency and volume guidelines
- Home workout options

🥗 **Nutrition Basics:**
- Macronutrients (protein, carbs, fats) overview
- General meal timing concepts
- Pre and post-workout nutrition basics
- Common dietary approaches (NOT medical diets)
- Hydration guidelines

💊 **Supplements Information:**
- Common supplement types and their reported uses
- General information about protein powders, creatine, etc.
- Supplement timing basics
- What research says about popular supplements
- (NOT medical advice or dosing recommendations)

👩 **Women's Fitness Topics:**
- Training considerations for women
- Common myths about women and weights
- General menstrual cycle and training information
- Pregnancy and postpartum fitness basics (general info only)

🧠 **Motivation & Mindset:**
- Goal setting strategies
- Habit formation tips
- Dealing with plateaus
- Consistency techniques
- Finding your "why"

😴 **Recovery & Rest:**
- Importance of sleep for fitness goals
- Active recovery concepts
- Rest day guidelines
- Basic stretching and mobility
- Stress management basics

⚽ **Sports & Performance:**
- General athletic performance concepts
- Sport-specific training basics
- Agility and speed training principles
- Endurance vs power training

🤕 **Injury Prevention (General Info Only):**
- Common injury prevention strategies
- Warm-up and cool-down importance
- When to rest vs push through
- Basic mobility work
- (Always see a medical professional for actual injuries!)

🌟 **Lifestyle & Wellness:**
- Balancing fitness with life
- Creating sustainable habits
- Fitness for different age groups
- Desk job fitness tips
- Travel and fitness

Remember: I provide general educational information only. For personalized programs, medical advice, injury treatment, or specific health conditions, always consult with qualified professionals like certified trainers, registered dietitians, or medical doctors.

What would you like to learn more about?
"""