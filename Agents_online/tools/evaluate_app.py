from pathlib import Path
from typing import List

import click

from second_brain_online.application.evaluation import evaluate_agent

EVALUATION_PROMPTS: List[str] = [
    # General Fitness Knowledge Questions
    """What is progressive overload?

Explain to me:
- what is progressive overload
- how it works in practice
- why it's essential for muscle growth
- different ways to implement it
- common mistakes to avoid

Retrieve the sources when compiling the answer. Also, return the sources you used as context.
""",
    
    # Muscle Building Questions
    "What is muscle protein synthesis and how can I optimize it?",
    "Explain the difference between compound and isolation exercises with examples.",
    """Write me a paragraph on muscle hypertrophy following this structure:

- introduction to muscle growth
- what are the main mechanisms (mechanical tension, metabolic stress, muscle damage)
- practical recommendations for maximizing growth

Include scientific sources where applicable.""",
    
    # Fat Loss Questions
    "What is the role of caloric deficit in fat loss and how do I calculate mine?",
    "List 5 evidence-based strategies for sustainable fat loss and explain why each works.",
    """How does High-Intensity Interval Training (HIIT) compare to steady-state cardio for fat loss?

Explain:
- what is HIIT
- benefits vs drawbacks
- when to use each method
- sample protocols for beginners
""",
    
    # Nutrition Questions
    "What are macronutrients and how should I distribute them for muscle gain?",
    "Explain the importance of meal timing around workouts for performance and recovery.",
    """List the top 5 supplements for muscle building with:
- what they do
- recommended dosages
- timing
- scientific evidence level
""",
    
    # Training Programming Questions
    "What is periodization in training and why is it important?",
    "Explain the differences between training for strength vs hypertrophy vs endurance.",
    """How do I know if I'm overtraining?

Include:
- signs and symptoms
- how to prevent it
- recovery strategies
- when to deload
""",
    
    # Safety and Form Questions
    "What are the most common deadlift mistakes and how to fix them?",
    "I have lower back pain - what exercises should I avoid and what are safe alternatives?",
    
    # Women's Fitness Questions
    "How should women adjust their training during different phases of their menstrual cycle?",
    "Is it true that lifting weights will make women bulky? Explain the science.",
    
    # Recovery Questions
    "What is the optimal amount of sleep for muscle recovery and why?",
    "List 5 active recovery methods and their benefits for muscle growth.",
    
    # Beginner Questions
    """I'm completely new to fitness. Create a beginner's roadmap including:
- where to start
- basic exercises to master
- nutrition basics
- common mistakes to avoid
- realistic timeline for results
""",
    
    # Advanced/Specific Questions
    "What is blood flow restriction training and is it effective?",
    "How can I break through a strength plateau on bench press?",
    "What's the science behind German Volume Training?",
    
    # Lifestyle Integration Questions
    "How can I maintain muscle mass while traveling frequently?",
    "What are the best strategies for fitting workouts into a busy schedule?",
    
    # Sports-Specific Questions
    "How should a runner incorporate strength training without hurting running performance?",
    "What's the difference between training for powerlifting vs bodybuilding?",
    
    # Injury Prevention Questions
    "What are the best exercises for preventing knee injuries?",
    "How do I properly warm up before heavy lifting?",
    
    # Motivation and Adherence Questions
    "What are evidence-based strategies for maintaining long-term exercise adherence?",
    "How do I stay motivated when I'm not seeing results?",
]

# Additional test cases for the specialized tools
TOOL_SPECIFIC_PROMPTS: List[str] = [
    # Workout Generator Tests
    "Create a 3-day beginner workout plan for fat loss with only dumbbells available.",
    "I'm intermediate level, want to build muscle, have access to a full gym, and can train 5 days per week. Design a program for me.",
    
    # Nutrition Calculator Tests
    "I'm a 30-year-old woman, 65kg, 165cm, moderately active, and want to lose fat. Calculate my daily calories and macros.",
    "Calculate nutrition needs for a 25-year-old male, 80kg, 180cm, very active, trying to gain muscle.",
    
    # Safety Validator Tests
    "Is it safe to do squats if I have knee pain?",
    "I'm a beginner with lower back issues - check if deadlifts are safe for me.",
    
    # Complex Multi-Tool Tests
    "I'm 35, male, 90kg, 175cm, sedentary, with mild back pain. I want to lose weight and get stronger. Create a complete plan including safe exercises and nutrition.",
    "Design a muscle-building program for someone who can only train 2 days per week, including nutrition recommendations.",
]


@click.command()
@click.option(
    "--retriever-config-path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the retriever configuration file",
)
@click.option(
    "--include-tool-tests",
    is_flag=True,
    default=False,
    help="Include tests for specialized tools (workout generator, nutrition calculator, safety validator)",
)
@click.option(
    "--category",
    type=click.Choice([
        "all", "general", "muscle-building", "fat-loss", "nutrition", 
        "training", "safety", "women", "recovery", "beginner", "advanced"
    ]),
    default="all",
    help="Test only specific category of questions",
)
@click.option(
    "--output-file",
    type=click.Path(path_type=Path),
    default="evaluation_results.json",
    help="Path to save evaluation results",
)
def main(
    retriever_config_path: Path,
    include_tool_tests: bool,
    category: str
    # output_file: Path
) -> None:
    """Evaluate fitness AI assistant with domain-specific questions."""
    
    # Filter prompts by category if specified
    prompts = EVALUATION_PROMPTS
    
    if category != "all":
        # Simple category filtering based on keywords
        category_keywords = {
            "muscle-building": ["muscle", "hypertrophy", "protein synthesis", "compound"],
            "fat-loss": ["fat loss", "caloric deficit", "HIIT", "cardio"],
            "nutrition": ["macronutrients", "meal timing", "supplements"],
            "training": ["periodization", "strength", "overtraining", "plateau"],
            "safety": ["mistakes", "pain", "injury", "warm up"],
            "women": ["women", "menstrual"],
            "recovery": ["sleep", "recovery"],
            "beginner": ["new to fitness", "beginner"],
            "advanced": ["blood flow restriction", "German Volume", "plateau"],
        }
        
        if category in category_keywords:
            keywords = category_keywords[category]
            prompts = [p for p in prompts if any(kw.lower() in p.lower() for kw in keywords)]
    
    # Add tool-specific tests if requested
    if include_tool_tests:
        prompts.extend(TOOL_SPECIFIC_PROMPTS)
    
    click.echo(f"Running evaluation with {len(prompts)} prompts...")
    click.echo(f"Category: {category}")
    click.echo(f"Include tool tests: {include_tool_tests}")
    # click.echo(f"Output file: {output_file}")
    
    # Run evaluation
    results = evaluate_agent(
        prompts, 
        retriever_config_path=retriever_config_path,
    )
    
    # Print summary
    click.echo("\n" + "="*50)
    click.echo("EVALUATION SUMMARY")
    click.echo("="*50)
    click.echo(f"Total prompts evaluated: {len(prompts)}")
    
    if results:
        avg_score = sum(r.get("score", 0) for r in results) / len(results)
        click.echo(f"Average score: {avg_score:.2f}")
        
        # Show best and worst performing queries
        sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
        
        click.echo("\nTop 3 best responses:")
        for i, result in enumerate(sorted_results[:3]):
            click.echo(f"{i+1}. Score: {result['score']:.2f} - {result['prompt'][:50]}...")
        
        click.echo("\nTop 3 worst responses:")
        for i, result in enumerate(sorted_results[-3:]):
            click.echo(f"{i+1}. Score: {result['score']:.2f} - {result['prompt'][:50]}...")


if __name__ == "__main__":
    main()