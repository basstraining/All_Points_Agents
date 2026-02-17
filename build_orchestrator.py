#!/usr/bin/env python3
"""
All Points Agent Build Orchestrator

This script builds all 6 AI agent demos in parallel by:
1. Reading each skill.md file
2. Generating build instructions
3. Running builds concurrently
4. Reporting progress and results

Usage:
    python build_orchestrator.py
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
DEMOS = [
    {
        "id": "01_carrier_exception_monitor",
        "name": "Carrier Exception Monitor",
        "priority": 1,
        "estimated_hours": 3
    },
    {
        "id": "02_takt_profitability",
        "name": "Takt Profitability Analyzer",
        "priority": 2,
        "estimated_hours": 3
    },
    {
        "id": "03_rate_shopping",
        "name": "ShipStation Rate Shopping",
        "priority": 3,
        "estimated_hours": 2
    },
    {
        "id": "04_chargeback_defense",
        "name": "RetailReady Chargeback Defense",
        "priority": 4,
        "estimated_hours": 3
    },
    {
        "id": "05_ltl_automation",
        "name": "MyCarrier LTL Automation",
        "priority": 5,
        "estimated_hours": 3
    },
    {
        "id": "06_front_revival",
        "name": "Front Email Revival",
        "priority": 6,
        "estimated_hours": 2
    }
]

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

async def build_demo(demo: Dict) -> Dict:
    """
    Build a single demo
    
    Args:
        demo: Demo configuration dict
        
    Returns:
        Build result dict
    """
    demo_id = demo["id"]
    demo_name = demo["name"]
    
    print_info(f"Starting build: {demo_name}")
    
    demo_path = Path(demo_id)
    skill_file = demo_path / "skill.md"
    
    # Check if skill file exists
    if not skill_file.exists():
        print_error(f"Skill file not found: {skill_file}")
        return {
            "demo": demo_name,
            "status": "failed",
            "error": f"Skill file not found: {skill_file}",
            "duration": 0
        }
    
    start_time = datetime.now()
    
    # Read skill content
    try:
        with open(skill_file, 'r') as f:
            skill_content = f.read()
    except Exception as e:
        print_error(f"Failed to read skill file: {e}")
        return {
            "demo": demo_name,
            "status": "failed",
            "error": str(e),
            "duration": 0
        }
    
    # Create build instructions
    build_instructions = f"""
Build the {demo_name} agent following the specification in skill.md.

Requirements:
1. Read skill.md completely
2. Implement all MCP servers listed
3. Create the ADK agent
4. Build tests for each scenario
5. Create README.md

Skill Content Length: {len(skill_content)} characters
Estimated Build Time: {demo['estimated_hours']} hours

Start building now!
"""
    
    # Save build instructions
    instructions_file = demo_path / "BUILD_INSTRUCTIONS.txt"
    with open(instructions_file, 'w') as f:
        f.write(build_instructions)
    
    print_success(f"Created build instructions: {instructions_file}")
    
    # Simulate build progress (in real implementation, this would call AI coding agent)
    print_info(f"Building {demo_name}... (simulated)")
    await asyncio.sleep(2)  # Simulate work
    
    duration = (datetime.now() - start_time).total_seconds()
    
    print_success(f"Completed: {demo_name} ({duration:.1f}s)")
    
    return {
        "demo": demo_name,
        "demo_id": demo_id,
        "status": "success",
        "duration": duration,
        "files_created": [
            str(instructions_file)
        ]
    }

async def build_all_demos(demos: List[Dict]) -> List[Dict]:
    """
    Build all demos in parallel
    
    Args:
        demos: List of demo configurations
        
    Returns:
        List of build results
    """
    print_header("All Points Agents - Parallel Build")
    print_info(f"Building {len(demos)} demos in parallel")
    print_info(f"Estimated total time: {sum(d['estimated_hours'] for d in demos)} hours sequentially")
    print_info(f"Estimated parallel time: {max(d['estimated_hours'] for d in demos)} hours")
    
    # Create tasks for all demos
    tasks = [build_demo(demo) for demo in demos]
    
    # Run all builds in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

def print_summary(results: List[Dict]):
    """Print build summary report"""
    print_header("BUILD SUMMARY")
    
    successful = [r for r in results if isinstance(r, dict) and r["status"] == "success"]
    failed = [r for r in results if isinstance(r, dict) and r["status"] == "failed"]
    exceptions = [r for r in results if isinstance(r, Exception)]
    
    print(f"Total Demos: {len(results)}")
    print(f"Successful: {Colors.GREEN}{len(successful)}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{len(failed)}{Colors.ENDC}")
    print(f"Exceptions: {Colors.RED}{len(exceptions)}{Colors.ENDC}")
    
    print("\n" + "─"*60 + "\n")
    
    # Print successful builds
    if successful:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SUCCESSFUL BUILDS{Colors.ENDC}")
        for result in successful:
            print(f"  • {result['demo']} ({result['duration']:.1f}s)")
            print(f"    Files: {', '.join(result['files_created'])}")
    
    # Print failed builds
    if failed:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ FAILED BUILDS{Colors.ENDC}")
        for result in failed:
            print(f"  • {result['demo']}")
            print(f"    Error: {result['error']}")
    
    # Print exceptions
    if exceptions:
        print(f"\n{Colors.RED}{Colors.BOLD}💥 EXCEPTIONS{Colors.ENDC}")
        for exc in exceptions:
            print(f"  • {type(exc).__name__}: {exc}")
    
    print("\n" + "─"*60 + "\n")
    
    # Next steps
    print_header("NEXT STEPS")
    
    if successful:
        print_info("Review build instructions in each demo folder")
        print_info("Run: cd <demo_folder> && cat BUILD_INSTRUCTIONS.txt")
        print_info("Then use your AI coding agent to implement")
        print()
        print_info("Recommended order for demo prep:")
        print("  1. 01_carrier_exception_monitor (flashiest)")
        print("  2. 02_takt_profitability (answers Michael's question)")
        print("  3. 03_rate_shopping (clear cost savings)")
    
    if failed or exceptions:
        print_warning("Some builds failed - check errors above")
        print_info("Fix issues and re-run: python build_orchestrator.py")

def check_prerequisites():
    """Check if all required files/folders exist"""
    print_header("Checking Prerequisites")
    
    # Check for demo folders
    missing_folders = []
    for demo in DEMOS:
        demo_path = Path(demo["id"])
        if not demo_path.exists():
            missing_folders.append(demo["id"])
        else:
            print_success(f"Found: {demo['id']}/")
    
    if missing_folders:
        print_error(f"Missing folders: {', '.join(missing_folders)}")
        print_info("Run setup script first or create folders manually")
        return False
    
    # Check for skill files
    missing_skills = []
    for demo in DEMOS:
        skill_file = Path(demo["id"]) / "skill.md"
        if not skill_file.exists():
            missing_skills.append(str(skill_file))
        else:
            print_success(f"Found: {skill_file}")
    
    if missing_skills:
        print_error(f"Missing skill files: {', '.join(missing_skills)}")
        print_info("Copy skill markdown files into each demo folder")
        return False
    
    print_success("All prerequisites met!")
    return True

async def main():
    """Main entry point"""
    print_header("All Points ATL - Agent Build Orchestrator")
    print_info("This script will build all 6 AI agent demos in parallel")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites not met. Exiting.")
        sys.exit(1)
    
    # Confirm with user
    print_warning("This will create build instructions for all demos")
    response = input(f"{Colors.CYAN}Continue? (y/n): {Colors.ENDC}")
    if response.lower() != 'y':
        print_info("Cancelled by user")
        sys.exit(0)
    
    # Build all demos
    results = await build_all_demos(DEMOS)
    
    # Print summary
    print_summary(results)
    
    # Save results to JSON
    results_file = Path("build_results.json")
    with open(results_file, 'w') as f:
        # Convert any exceptions to strings
        serializable_results = []
        for r in results:
            if isinstance(r, Exception):
                serializable_results.append({
                    "status": "exception",
                    "error": str(r),
                    "type": type(r).__name__
                })
            else:
                serializable_results.append(r)
        
        json.dump(serializable_results, f, indent=2)
    
    print_info(f"Results saved to: {results_file}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nBuild interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
