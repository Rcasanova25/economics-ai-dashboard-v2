"""
Archive old analysis scripts that have been replaced by the template
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Scripts to archive
SCRIPTS_TO_ARCHIVE = [
    # Old analysis scripts
    "analyze_source_7.py",
    "source_1_cleanup_analysis.py",
    "source_2_cleanup_analysis.py",
    "source_1_cleanup_analysis_fixed.py",
    "source_2_cleanup_analysis_fixed.py",
    "source_7_cleanup_analysis.py",
    
    # Old execution scripts
    "execute_source_1_cleanup.py",
    "execute_source_7_cleanup.py",
    
    # Initial exploration scripts
    "analyze_by_source.py",
    "analyze_data_quality.py",
]

def archive_old_scripts():
    """Move old scripts to an archive folder"""
    # Create archive directory
    archive_dir = Path("archived_scripts")
    archive_dir.mkdir(exist_ok=True)
    
    # Add a README to the archive
    readme_content = f"""# Archived Scripts

These scripts were archived on {datetime.now().strftime('%Y-%m-%d')} as they have been replaced by:
- `source_cleanup_template.py` - Universal cleanup template
- `run_source_cleanup.py` - Integrated cleanup runner

## Archived Files:
- Old source-specific analysis scripts
- Old execution scripts
- Initial data exploration scripts

These files are kept for reference but are no longer needed for the cleanup process.
"""
    
    with open(archive_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    # Archive each script
    archived = []
    not_found = []
    
    for script in SCRIPTS_TO_ARCHIVE:
        script_path = Path(script)
        if script_path.exists():
            # Move to archive
            dest = archive_dir / script
            shutil.move(str(script_path), str(dest))
            archived.append(script)
            print(f"[OK] Archived: {script}")
        else:
            not_found.append(script)
            print(f"[--] Not found: {script}")
    
    print(f"\n{'='*50}")
    print(f"Archived {len(archived)} scripts to 'archived_scripts/' folder")
    if not_found:
        print(f"Not found: {len(not_found)} scripts")
    print(f"{'='*50}")
    
    return archived, not_found

if __name__ == "__main__":
    print("Archiving old scripts that have been replaced by the template...")
    archived, not_found = archive_old_scripts()
    
    print("\nYour project is now cleaner!")
    print("Old scripts have been moved to 'archived_scripts/' for reference.")
    print("\nCurrent workflow uses:")
    print("  - source_cleanup_template.py")
    print("  - run_source_cleanup.py (to be created)")
    print("  - tests/test_data_cleanup.py")