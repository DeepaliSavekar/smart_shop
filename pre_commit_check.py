#!/usr/bin/env python3
"""
Pre-commit Security Check
This script checks for common security issues before allowing a commit
"""

import sys
import re
import os

def check_for_secrets(file_path):
    """Check if file contains potential secrets"""
    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'API key'),
        (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Secret key'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'Token'),
        (r'mysql://[^@]+:[^@]+@', 'Database connection string'),
        (r'AC[a-z0-9]{32}', 'Twilio Account SID'),
        (r'SK[a-z0-9]{32}', 'Twilio API Key'),
    ]
    
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for pattern, description in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"  ⚠️  Potential {description} found in {file_path}")
    except Exception as e:
        pass
    
    return issues

def main():
    print("🔒 Running pre-commit security checks...")
    
    # Files to check
    files_to_check = []
    
    # Get staged files
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True
        )
        files_to_check = result.stdout.strip().split('\n')
    except:
        print("⚠️  Could not get staged files")
        return 0
    
    all_issues = []
    
    # Check for .env file
    if '.env' in files_to_check:
        all_issues.append("  🚨 CRITICAL: .env file is staged for commit!")
        all_issues.append("     Run: git reset HEAD .env")
    
    # Check Python files for hardcoded secrets
    for file_path in files_to_check:
        if file_path.endswith('.py') and os.path.exists(file_path):
            issues = check_for_secrets(file_path)
            all_issues.extend(issues)
    
    if all_issues:
        print("\n❌ Security issues found:\n")
        for issue in all_issues:
            print(issue)
        print("\n🛑 Commit blocked for security reasons!")
        print("   Fix the issues above before committing.\n")
        return 1
    
    print("✅ Security checks passed!\n")
    return 0

if __name__ == '__main__':
    sys.exit(main())
