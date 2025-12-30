import typer
import re
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from prepress import __version__
from prepress.core.drivers.python import PythonDriver
from prepress.core.drivers.rust import RustDriver
from prepress.core.drivers.node import NodeDriver
from prepress.core.drivers.changelog import ChangelogDriver

app = typer.Typer(
    name="pps",
    help="Prepress: A modern, polyglot release management tool",
    add_completion=False,
)
console = Console()

def get_drivers(root: Path):
    drivers = []
    if PythonDriver(root).detect():
        drivers.append(PythonDriver(root))
    if RustDriver(root).detect():
        drivers.append(RustDriver(root))
    if NodeDriver(root).detect():
        drivers.append(NodeDriver(root))
    return drivers

@app.command()
def version():
    """Show the version of prepress."""
    console.print(f"Prepress [bold cyan]v{__version__}[/bold cyan]")

@app.command()
def init():
    """Initialize the project for Prepress."""
    root = Path.cwd()
    console.print("[bold blue]🚀 Initializing Prepress...[/bold blue]")

    # 1. Changelog
    changelog = ChangelogDriver(root / "CHANGELOG.md")
    if not changelog.exists():
        if Confirm.ask("CHANGELOG.md missing. Create it?"):
            template = (Path(__file__).parent / "templates" / "CHANGELOG.md").read_text()
            (root / "CHANGELOG.md").write_text(template)
            console.print("[green]✓ Created CHANGELOG.md[/green]")

    # 2. Drivers & Version Modernization
    drivers = get_drivers(root)
    for driver in drivers:
        if isinstance(driver, PythonDriver):
            # Check for __init__.py modernization
            # Only look in src/ or root, excluding .venv and hidden dirs
            search_dirs = [root / "src"] if (root / "src").exists() else [root]
            for search_dir in search_dirs:
                for init_py in search_dir.rglob("__init__.py"):
                    if ".venv" in str(init_py) or "/." in str(init_py):
                        continue
                    
                    content = init_py.read_text()
                    if "__version__" in content and "importlib.metadata" not in content:
                        if Confirm.ask(f"Modernize versioning in {init_py.relative_to(root)}?"):
                            # Actually get name from pyproject.toml
                            try:
                                import tomllib
                            except ImportError:
                                import tomli as tomllib
                            
                            with open(root / "pyproject.toml", "rb") as f:
                                pkg_name = tomllib.load(f).get("project", {}).get("name", "package")
                            
                            new_content = f"""from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("{pkg_name}")
except PackageNotFoundError:
    __version__ = "0.0.0"
"""
                            init_py.write_text(new_content)
                            console.print(f"[green]✓ Modernized {init_py.relative_to(root)}[/green]")

    # 3. GitHub Actions
    github_dir = root / ".github" / "workflows"
    if not (github_dir / "publish.yml").exists():
        if Confirm.ask("Create GitHub Action for Trusted Publishing?"):
            github_dir.mkdir(parents=True, exist_ok=True)
            if any(isinstance(d, PythonDriver) for d in drivers):
                template = (Path(__file__).parent / "templates" / "python_publish.yml").read_text()
                # Simple template replacement
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib
                
                with open(root / "pyproject.toml", "rb") as f:
                    pkg_name = tomllib.load(f).get("project", {}).get("name", "package")
                template = template.replace("{{ package_name }}", pkg_name)
                (github_dir / "publish.yml").write_text(template)
                console.print("[green]✓ Created .github/workflows/publish.yml[/green]")

    console.print("[bold green]✨ Prepress initialization complete![/bold green]")

@app.command()
def preview():
    """Preview the current release."""
    root = Path.cwd()
    drivers = get_drivers(root)
    if not drivers:
        console.print("[red]No supported project detected.[/red]")
        return

    version = drivers[0].get_version()
    changelog = ChangelogDriver(root / "CHANGELOG.md")
    notes = changelog.get_unreleased_notes()

    # If notes only contain headers or are empty, try to get the current version's notes
    is_effectively_empty = not notes or not any(line.strip().startswith("-") for line in notes.splitlines())

    if is_effectively_empty and version:
        # Try to get notes for the current version
        content = (root / "CHANGELOG.md").read_text()
        pattern = rf'## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            notes = match.group(1).strip()

    console.print(f"[bold blue]Previewing Release[/bold blue]")
    console.print(f"Version: [green]{version}[/green]")
    console.print("-" * 20)
    console.print("[bold]Release Notes:[/bold]")
    console.print(notes if notes else "[yellow]No unreleased notes found.[/yellow]")
    console.print("-" * 20)

@app.command()
def bump(
    increment: str = typer.Argument(..., help="The version increment (patch, minor, major) or a specific version")
):
    """Bump the project version."""
    root = Path.cwd()
    drivers = get_drivers(root)
    if not drivers:
        console.print("[red]No supported project detected.[/red]")
        return

    current_v = drivers[0].get_version()
    if not current_v:
        console.print("[red]Could not detect current version.[/red]")
        return

    import semver
    if increment in ["patch", "minor", "major"]:
        ver = semver.Version.parse(current_v)
        if increment == "patch":
            new_v = str(ver.bump_patch())
        elif increment == "minor":
            new_v = str(ver.bump_minor())
        else:
            new_v = str(ver.bump_major())
    else:
        # Assume it's a specific version
        try:
            new_v = str(semver.Version.parse(increment))
        except ValueError:
            console.print(f"[red]Invalid version or increment: {increment}[/red]")
            return

    console.print(f"Bumping version: [yellow]{current_v}[/yellow] -> [bold green]{new_v}[/bold green]")
    
    if Confirm.ask("Proceed?"):
        for driver in drivers:
            driver.set_version(new_v)
        
        changelog = ChangelogDriver(root / "CHANGELOG.md")
        if changelog.exists():
            changelog.bump(new_v)
        
        console.print("[green]✓ Version bumped successfully![/green]")
        console.print("[blue]Next step: pps release[/blue]")

import subprocess

def run_cmd(cmd: list[str], check: bool = True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)

@app.command()
def release():
    """Tag and release the project."""
    root = Path.cwd()
    drivers = get_drivers(root)
    if not drivers:
        console.print("[red]No supported project detected.[/red]")
        return

    version = drivers[0].get_version()
    changelog = ChangelogDriver(root / "CHANGELOG.md")
    notes = changelog.get_unreleased_notes()
    
    # If notes only contain headers or are empty, try to get the current version's notes
    is_effectively_empty = not notes or not any(line.strip().startswith("-") for line in notes.splitlines())

    if is_effectively_empty:
        content = (root / "CHANGELOG.md").read_text()
        pattern = rf'## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            notes = match.group(1).strip()

    console.print(f"[bold blue]🚀 Releasing v{version}[/bold blue]")

    # 1. Git Clean Check
    try:
        run_cmd(["git", "diff", "--quiet"])
        run_cmd(["git", "diff", "--cached", "--quiet"])
    except subprocess.CalledProcessError:
        console.print("[red]Error: Working directory is not clean. Commit your changes first.[/red]")
        return

    # 2. Tag
    tag = f"v{version}"
    if Confirm.ask(f"Create tag [bold cyan]{tag}[/bold cyan] and push?"):
        try:
            run_cmd(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
            run_cmd(["git", "push", "origin", "main"]) # Assume main for now
            run_cmd(["git", "push", "origin", tag])
            console.print(f"[green]✓ Tag {tag} created and pushed.[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Git error: {e.stderr}[/red]")
            return

    # 3. GitHub Release
    if Confirm.ask("Create GitHub Release?"):
        try:
            # Check if gh is installed
            run_cmd(["which", "gh"])
            
            # Create release
            cmd = ["gh", "release", "create", tag, "--title", tag, "--notes", notes]
            run_cmd(cmd)
            console.print("[green]✓ GitHub Release created successfully![/green]")
        except subprocess.CalledProcessError:
            console.print("[yellow]Warning: GitHub CLI (gh) not found or failed. Skipping GitHub Release.[/yellow]")
            console.print("[blue]You can create it manually at: https://github.com/<user>/<repo>/releases[/blue]")

@app.command()
def note(
    message: str = typer.Argument(..., help="The note to add to the changelog"),
    section: str = typer.Option("Added", "--section", "-s", help="The section to add the note to (Added, Fixed, Changed, etc.)")
):
    """Add a note to the [Unreleased] section of the changelog."""
    root = Path.cwd()
    changelog = ChangelogDriver(root / "CHANGELOG.md")
    if not changelog.exists():
        console.print("[red]CHANGELOG.md not found. Run 'pps init' first.[/red]")
        return
    
    changelog.add_note(message, section)
    console.print(f"[green]✓ Added note to {section} section.[/green]")

@app.command()
def status():
    """Show the current release status."""
    root = Path.cwd()
    drivers = get_drivers(root)
    if not drivers:
        console.print("[red]No supported project detected.[/red]")
        return

    version = drivers[0].get_version()
    changelog = ChangelogDriver(root / "CHANGELOG.md")
    latest_ch = changelog.get_latest_version()
    unreleased = changelog.get_unreleased_notes()

    from rich.table import Table
    table = Table(title="Prepress Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")

    table.add_row("Manifest Version", f"[green]{version}[/green]")
    table.add_row("Changelog Latest", f"[green]{latest_ch}[/green]" if latest_ch == version else f"[red]{latest_ch}[/red]")
    table.add_row("Unreleased Notes", "[green]Yes[/green]" if unreleased else "[yellow]No[/yellow]")
    
    # Git status
    try:
        run_cmd(["git", "diff", "--quiet"])
        git_clean = "[green]Clean[/green]"
    except subprocess.CalledProcessError:
        git_clean = "[yellow]Dirty[/yellow]"
    table.add_row("Git Status", git_clean)

    console.print(table)

    if version != latest_ch:
        console.print("[yellow]⚠ Manifest version and Changelog version are out of sync![/yellow]")
    if not unreleased and version == latest_ch:
        console.print("[blue]Ready to develop. Add notes with 'pps note'.[/blue]")
    elif unreleased and version == latest_ch:
        console.print("[blue]Ready to bump. Run 'pps bump'.[/blue]")
    elif not unreleased and version != latest_ch:
        console.print("[blue]Ready to release. Run 'pps release'.[/blue]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Prepress: A modern, polyglot release management tool."""
    if ctx.invoked_subcommand is not None:
        return

    root = Path.cwd()
    drivers = get_drivers(root)
    changelog = ChangelogDriver(root / "CHANGELOG.md")

    if not drivers:
        console.print("[bold red]No manifest found.[/bold red]")
        console.print("\nPrepress needs a project manifest to work. Supported files:")
        console.print("  - [cyan]pyproject.toml[/cyan] (Python)")
        console.print("  - [cyan]Cargo.toml[/cyan] (Rust)")
        console.print("  - [cyan]package.json[/cyan] (Node.js)")
        console.print("\n[dim]Example: Create a pyproject.toml to get started.[/dim]")
        raise typer.Exit(0)

    if not changelog.exists():
        console.print("[yellow]Manifest found, but no CHANGELOG.md detected.[/yellow]")
        console.print("\nRun [bold cyan]pps init[/bold cyan] to set up your project for Prepress.")
        raise typer.Exit(0)

    # Default behavior: show status
    ctx.invoke(status)

if __name__ == "__main__":
    app()
