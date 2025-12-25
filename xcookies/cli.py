"""CLI interface for XCookie Extractor."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .extractor import CookieExtractor, AccountCredentials, ExtractedCookies

app = typer.Typer(
    name="xcookie",
    help="Extract cookies from X accounts using auth tokens.",
    add_completion=False,
)

console = Console()


@app.command()
def main(
    input_file: Path = typer.Argument(
        Path("credentials.txt"),
        help="Input file with accounts (username<TAB>auth_token)",
    ),
    output_file: Path = typer.Option(
        Path("cookies.json"),
        "--output", "-o",
        help="Output JSON file for extracted cookies.",
    ),
) -> None:
    """Extract cookies from X accounts.
    
    Input format: username<TAB>auth_token (one per line)
    """
    if not input_file.exists():
        console.print(f"[red]✗ File not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    # Load accounts
    accounts = load_accounts(input_file)
    
    if not accounts:
        console.print(f"[red]✗ No valid accounts found in {input_file}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(
        f"[bold cyan]Input:[/bold cyan]  {input_file}\n"
        f"[bold cyan]Output:[/bold cyan] {output_file}\n"
        f"[bold cyan]Accounts:[/bold cyan] {len(accounts)}",
        title="XCookie Extractor",
        border_style="cyan",
    ))
    
    # Extract cookies
    extractor = CookieExtractor()
    results: list[ExtractedCookies] = []
    failed: list[str] = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting cookies...", total=len(accounts))
        
        for creds in accounts:
            progress.update(task, description=f"[cyan]{creds.username}[/cyan]")
            
            result = extractor.extract_single(creds)
            
            if result:
                results.append(result)
                console.print(f"  [green]✓[/green] {creds.username}")
            else:
                failed.append(creds.username)
                console.print(f"  [red]✗[/red] {creds.username}")
            
            progress.advance(task)
    
    # Save results
    save_results(results, output_file)
    
    # Summary
    console.print()
    if failed:
        console.print(Panel(
            f"[green]✓ Success:[/green] {len(results)}\n"
            f"[red]✗ Failed:[/red] {len(failed)}",
            title="Complete",
            border_style="yellow",
        ))
    else:
        console.print(Panel(
            f"[green]✓ All {len(results)} accounts extracted successfully![/green]",
            title="Complete",
            border_style="green",
        ))
    
    console.print(f"\n[dim]Saved to {output_file}[/dim]")


def load_accounts(path: Path) -> list[AccountCredentials]:
    """Load accounts from file (username<TAB>auth_token)."""
    accounts = []
    
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Skip header
            if line.lower().startswith("username"):
                continue
            
            # Parse tab-separated or whitespace-separated
            parts = line.split('\t') if '\t' in line else line.split()
            
            if len(parts) >= 2:
                username = parts[0].strip()
                auth_token = parts[1].strip()
                
                if username and auth_token:
                    accounts.append(AccountCredentials(
                        username=username,
                        auth_token=auth_token,
                    ))
    
    return accounts


def save_results(results: list[ExtractedCookies], path: Path) -> None:
    """Save results to JSON file."""
    data = [
        {
            "username": r.username,
            "auth_token": r.auth_token,
            "ct0": r.ct0,
            "twid": r.twid,
            "guest_id": r.guest_id,
        }
        for r in results
    ]
    
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    app()

