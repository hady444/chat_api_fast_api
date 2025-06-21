
from pathlib import Path
import sys

import click
from smolagents import GradioUI
from loguru import logger

from agents_online.application.agents import get_agent


# Fitness-specific example queries
EXAMPLE_QUERIES = {
    "beginner": "I'm new to fitness. What's a good starter workout routine?",
    "nutrition": "Calculate my daily calories: 30yo male, 80kg, 180cm, moderately active, want to lose fat",
    "safety": "Is deadlifting safe if I have lower back pain?",
    "muscle": "What's the best way to build muscle as a beginner?",
    "program": "Create a 3-day workout plan for muscle gain with full gym access",
}


@click.command()
@click.option(
    "--retriever-config-path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the retriever config file",
)
@click.option(
    "--ui",
    is_flag=True,
    default=False,
    help="Launch with Gradio UI instead of CLI mode",
)
@click.option(
    "--query",
    "-q",
    type=str,
    default=None,
    help="Query to run in CLI mode",
)
@click.option(
    "--example",
    "-e",
    type=click.Choice(list(EXAMPLE_QUERIES.keys())),
    help="Use a predefined example query",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show detailed agent reasoning",
)
def main(
    retriever_config_path: Path,
    ui: bool, 
    query: str, 
    example: str,
    verbose: bool
) -> None:
    """Run the Fitness AI Assistant in Gradio UI or CLI mode.
    
    Examples:
        # Run with UI
        python run_agent.py --retriever-config-path configs/retriever_config.yaml --ui
        
        # Run with custom query
        python run_agent.py --retriever-config-path configs/retriever_config.yaml -q "How do I lose weight?"
        
        # Run with example query
        python run_agent.py --retriever-config-path configs/retriever_config.yaml -e beginner
    """
    try:
        # Initialize agent
        logger.info(f"Loading agent with config: {retriever_config_path}")
        print("HERE")
        agent = get_agent(retriever_config_path=retriever_config_path)
 
        if ui:
            GradioUI(agent).launch()
        else:
            # CLI mode
            # Determine query to use
            if example:
                query = EXAMPLE_QUERIES[example]
                logger.info(f"Using example query: {example}")
            elif not query:
                # Interactive mode if no query provided
                logger.info("No query provided. Entering interactive mode...")
                query = click.prompt("\n💪 What's your fitness question?", type=str)
            
            # Show what query we're running
            click.echo(f"\n📝 Query: {query}")
            click.echo("-" * 50)
            
            # Run agent
            if verbose:
                # Set verbosity for detailed output
                agent.agent.verbosity_level = 2
            
            logger.info("Processing query...")
            result = agent.run(query)
            
            # Format and display result
            click.echo("\n🤖 Fitness AI Assistant Response:")
            click.echo("=" * 50)
            click.echo(result)
            click.echo("=" * 50)
            
            # Add disclaimer
            click.echo("\n⚠️  Disclaimer: This is general information only. Consult professionals for personalized advice.")
            
    except KeyboardInterrupt:
        click.echo("\n\n👋 Goodbye! Stay fit!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()