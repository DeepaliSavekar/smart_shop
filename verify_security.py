"""
Security Verification Script
Run this before pushing to GitHub to ensure no sensitive data is exposed
"""

import os
import re

def check_file_for_secrets(filepath):
    """Check a file for potential secrets"""
    dangerous_patterns = [
        (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
        (r'AC[a-z0-9]{32}', 'Twilio Account SID'),
        (r'SK[a-z0-9]{32}', 'Twilio Secret Key'),
        (r'mysql://.*:.*@', 'Database connection string with password'),
        (r'secret[_-]?key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret key'),
    ]
    
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            line_number = 0
            
            for line in content.split('\n'):
                line_number += 1
                for pattern, description in dangerous_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip if it's a comment or example
                        if not any(x in line.lower() for x in ['example', 'your_', 'placeholder', '#', '//']):
                            issues.append({
                                'file': filepath,
                                'line': line_number,
                                'issue': description,
                                'content': line.strip()[:80]
                            })
    except:
        pass
    
    return issues

def verify_gitignore():
    """Verify .gitignore contains essential entries"""
    required_entries = ['.env', 'venv', '__pycache__']
    
    if not os.path.exists('.gitignore'):
        return False, "❌ .gitignore file not found!"
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    missing = [entry for entry in required_entries if entry not in content]
    
    if missing:
        return False, f"❌ .gitignore missing: {', '.join(missing)}"
    
    return True, "✅ .gitignore properly configured"

def verify_env_files():
    """Verify .env and .env.example setup"""
    issues = []
    
    if not os.path.exists('.env.example'):
        issues.append("⚠️  .env.example not found - create one for documentation")
    
    if os.path.exists('.env'):
        # Check if .env would be committed
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'check-ignore', '.env'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                issues.append("🚨 CRITICAL: .env is NOT in .gitignore!")
        except:
            pass
    
    return issues

def main():
    print("=" * 70)
    print("🔒 SECURITY VERIFICATION FOR GITHUB")
    print("=" * 70)
    print()
    
    all_issues = []
    
    # Check .gitignore
    print("📋 Checking .gitignore...")
    status, message = verify_gitignore()
    print(f"   {message}")
    if not status:
        all_issues.append(message)
    print()
    
    # Check .env files
    print("📋 Checking environment files...")
    env_issues = verify_env_files()
    for issue in env_issues:
        print(f"   {issue}")
        all_issues.append(issue)
    if not env_issues:
        print("   ✅ Environment files properly configured")
    print()
    
    # Check Python files for hardcoded secrets
    print("📋 Scanning Python files for hardcoded secrets...")
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip venv and git directories
        dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__', 'env']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    secrets_found = []
    for filepath in python_files:
        issues = check_file_for_secrets(filepath)
        secrets_found.extend(issues)
    
    if secrets_found:
        print("   🚨 POTENTIAL SECRETS FOUND:")
        for issue in secrets_found:
            print(f"      File: {issue['file']}")
            print(f"      Line: {issue['line']}")
            print(f"      Issue: {issue['issue']}")
            print(f"      Content: {issue['content']}")
            print()
            all_issues.append(f"Secret in {issue['file']}:{issue['line']}")
    else:
        print("   ✅ No hardcoded secrets detected")
    print()
    
    # Check for required documentation
    print("📋 Checking documentation...")
    docs = {
        'README.md': 'Project documentation',
        'SECURITY.md': 'Security policy',
        'LICENSE': 'License file',
        '.env.example': 'Environment template'
    }
    
    for doc, description in docs.items():
        if os.path.exists(doc):
            print(f"   ✅ {doc} - {description}")
        else:
            print(f"   ⚠️  {doc} missing - {description}")
    print()
    
    # Final verdict
    print("=" * 70)
    if all_issues:
        print("❌ SECURITY ISSUES FOUND - DO NOT PUSH TO GITHUB YET!")
        print("=" * 70)
        print("\nIssues to fix:")
        for issue in all_issues:
            print(f"  • {issue}")
        print("\nFix these issues before pushing to GitHub.")
        return 1
    else:
        print("✅ SECURITY VERIFICATION PASSED!")
        print("=" * 70)
        print("\n✨ Your project is ready to be pushed to GitHub!")
        print("\nNext steps:")
        print("  1. git add .")
        print("  2. git commit -m 'Security fixes: Remove hardcoded credentials'")
        print("  3. git push origin main")
        print("\n⚠️  Remember: NEVER commit your .env file!")
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
