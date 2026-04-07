"""
OpenClaw Harness CLI
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..planner import Planner
from ..generator import Generator
from ..evaluator import Evaluator
from ..skill_extractor import SkillExtractor
from ..golden_rules import GoldenRulesManager
from ..state_manager import StateManager
from ..llm_adapter import get_llm_adapter
from ..models import Task

console = Console()


@click.group()
def cli():
    """OpenClaw Harness - Harness Engineering Framework"""
    pass


@cli.command()
@click.option('--dir', default='.', help='Directory to initialize')
def init(dir: str):
    """Initialize Harness in directory"""
    harness_dir = Path(dir) / ".harness"
    harness_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (harness_dir / "state").mkdir(exist_ok=True)
    (harness_dir / "golden_rules").mkdir(exist_ok=True)
    (harness_dir / "skills").mkdir(exist_ok=True)
    (harness_dir / "logs").mkdir(exist_ok=True)

    # Initialize golden rules
    golden_rules = GoldenRulesManager(str(harness_dir))
    golden_rules.init_default_rules()

    # Initialize state manager
    state_manager = StateManager(str(harness_dir))
    state_manager.init()

    console.print(f"✓ Initialized Harness in {harness_dir}", style="green")


@cli.command()
@click.argument('task')
@click.option('--provider', default='openai', help='LLM provider')
@click.option('--model', default='gpt-4', help='Model name')
@click.option('--max-retries', default=3, help='Max retry attempts')
def run(task: str, provider: str, model: str, max_retries: int):
    """Run a task with automatic evaluation loop"""
    console.print(f"[bold]Running task:[/bold] {task}")

    # Initialize components
    llm = get_llm_adapter(provider, model=model)
    harness_dir = Path(".harness")

    golden_rules = GoldenRulesManager(str(harness_dir))
    state_manager = StateManager(str(harness_dir))
    planner = Planner(llm)
    generator = Generator(llm, golden_rules)
    evaluator = Evaluator(llm, golden_rules)
    skill_extractor = SkillExtractor(llm, str(harness_dir / "skills"))

    # Create task
    task_obj = Task(description=task)
    state_manager.save_task(task_obj)
    state_manager.update_progress(f"Task created: {task}")

    # Plan
    console.print("\n[bold blue]Planning...[/bold blue]")
    plan = planner.decompose(task_obj)
    state_manager.update_progress(f"Plan generated with {len(plan.steps)} steps")

    # Show plan
    table = Table(title="Execution Plan")
    table.add_column("Step", style="cyan")
    table.add_column("Description")
    for i, step in enumerate(plan.steps, 1):
        table.add_row(str(i), step.description)
    console.print(table)

    # Execute with evaluation loop
    results = []
    for i, step in enumerate(plan.steps, 1):
        console.print(f"\n[bold blue]Executing Step {i}/{len(plan.steps)}...[/bold blue]")

        # Generate
        output = generator.execute(step, {"task": task, "previous_results": results})
        results.append(output)
        state_manager.update_progress(f"Step {i} completed")

        # Evaluate
        console.print("[bold yellow]Evaluating...[/bold yellow]")
        eval_result = evaluator.evaluate(output, plan)
        state_manager.log_evaluation(eval_result)

        console.print(f"Score: {eval_result.score:.2f} | Passed: {eval_result.passed}")

        # Retry loop if needed
        retry_count = 0
        while not eval_result.passed and retry_count < max_retries:
            retry_count += 1
            console.print(f"[bold red]Issues found, retrying ({retry_count}/{max_retries})...[/bold red]")

            output = generator.fix(step, eval_result.issues, output)
            results[-1] = output

            eval_result = evaluator.evaluate(output, plan)
            state_manager.log_evaluation(eval_result)
            console.print(f"Score: {eval_result.score:.2f} | Passed: {eval_result.passed}")

    # Final result
    console.print("\n[bold green]Task Completed![/bold green]")
    console.print(f"Final score: {eval_result.score:.2f}")

    # Extract skill if complex task succeeded
    if plan.is_complex and eval_result.passed:
        console.print("\n[bold blue]Extracting skill...[/bold blue]")
        skill = skill_extractor.extract(task_obj, "\n\n".join(results), eval_result)
        if skill:
            skill_file = skill_extractor.save_skill(skill)
            console.print(f"✓ Skill extracted: {skill_file}")


@cli.command()
@click.argument('rule')
@click.option('--category', default='global', help='Rule category')
@click.option('--priority', default=3, help='Rule priority (1-5)')
def add_rule(rule: str, category: str, priority: int):
    """Add a golden rule"""
    golden_rules = GoldenRulesManager(".harness")
    new_rule = golden_rules.add_rule(rule, category, priority)
    console.print(f"✓ Rule added: {new_rule.id}", style="green")


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--provider', default='openai', help='LLM provider')
@click.option('--model', default='gpt-4', help='Model name')
def evaluate(file: str, provider: str, model: str):
    """Evaluate a result file"""
    llm = get_llm_adapter(provider, model=model)
    golden_rules = GoldenRulesManager(".harness")
    evaluator = Evaluator(llm, golden_rules)

    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple plan for evaluation
    from ..models import Plan, Step
    plan = Plan(
        task_id="manual_eval",
        steps=[Step(id="eval", description="Evaluate the content")]
    )

    result = evaluator.evaluate(content, plan)

    # Show results
    console.print(f"\n[bold]Evaluation Result[/bold]")
    console.print(f"Passed: {result.passed}")
    console.print(f"Score: {result.score:.2f}")

    if result.issues:
        console.print("\n[bold red]Issues:[/bold red]")
        for issue in result.issues:
            console.print(f"- [{issue.severity}] {issue.description}")

    if result.strengths:
        console.print("\n[bold green]Strengths:[/bold green]")
        for strength in result.strengths:
            console.print(f"- {strength}")


@cli.command()
@click.option('--task-file', type=click.Path(exists=True), help='Task file to extract from')
@click.option('--provider', default='openai', help='LLM provider')
@click.option('--model', default='gpt-4', help='Model name')
def extract_skill(task_file: str, provider: str, model: str):
    """Extract skill from completed task"""
    llm = get_llm_adapter(provider, model=model)
    skill_extractor = SkillExtractor(llm, ".harness/skills")
    state_manager = StateManager(".harness")

    # Load task
    task = state_manager.load_task()
    if not task:
        console.print("[red]No active task found[/red]")
        return

    # Get result
    result_file = Path(task_file) if task_file else Path(".harness/output/result.md")
    if not result_file.exists():
        console.print(f"[red]Result file not found: {result_file}[/red]")
        return

    with open(result_file, 'r', encoding='utf-8') as f:
        result = f.read()

    # Extract
    console.print("[bold blue]Extracting skill...[/bold blue]")
    skill = skill_extractor.extract(task, result, Evaluation(passed=True, score=0.9))

    if skill:
        skill_file = skill_extractor.save_skill(skill)
        console.print(f"✓ Skill extracted: {skill_file}", style="green")
    else:
        console.print("[red]Failed to extract skill[/red]")


@cli.command()
def status():
    """Show current state"""
    state_manager = StateManager(".harness")
    summary = state_manager.get_state_summary()
    console.print(summary)


@cli.command()
def list_rules():
    """List all golden rules"""
    golden_rules = GoldenRulesManager(".harness")
    rules = golden_rules.get_all_rules()

    table = Table(title="Golden Rules")
    table.add_column("ID", style="cyan")
    table.add_column("Category")
    table.add_column("Priority")
    table.add_column("Rule")

    for rule in rules:
        table.add_row(rule.id, rule.category, str(rule.priority), rule.content)

    console.print(table)


if __name__ == '__main__':
    cli()
