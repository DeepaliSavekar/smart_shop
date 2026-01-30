"""
GitHub Publish Helper
This script helps you safely publish your project to GitHub
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 GITHUB PUBLISH HELPER")
    print("=" * 70)
    print()
    print("This script will help you safely publish your project to GitHub.")
    print()
    
    # Step 1: Verify security
    print("Step 1: Running security verification...")
    if not run_command("python verify_security.py", "Security verification"):
        print("\n❌ Security verification failed!")
        print("Please fix the issues before publishing.")
        return 1
    
    # Step 2: Check git status
    print("\nStep 2: Checking git status...")
    result = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
    if result.stdout:
        print("\nFiles to be committed:")
        print(result.stdout)
    
    # Step 3: Confirm with user
    print("\n" + "=" * 70)
    print("⚠️  IMPORTANT SECURITY REMINDERS:")
    print("=" * 70)
    print("1. Your .env file will NOT be committed (it's in .gitignore)")
    print("2. All hardcoded credentials have been removed")
    print("3. Only safe files will be pushed to GitHub")
    print()
    
    response = input("Do you want to proceed with committing these changes? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Cancelled by user.")
        return 0
    
    # Step 4: Stage all files
    if not run_command("git add .", "Staging all files"):
        return 1
    
    # Step 5: Show what will be committed
    print("\n📋 Files staged for commit:")
    subprocess.run("git diff --cached --name-only", shell=True)
    
    # Step 6: Verify .env is NOT staged
    result = subprocess.run("git diff --cached --name-only", shell=True, capture_output=True, text=True)
    if '.env' in result.stdout and '.env.example' not in result.stdout:
        print("\n🚨 CRITICAL ERROR: .env file is staged for commit!")
        print("Running: git reset HEAD .env")
        subprocess.run("git reset HEAD .env", shell=True)
        print("\n❌ Removed .env from staging. Please try again.")
        return 1
    
    # Step 7: Commit
    commit_message = "Security fixes: Remove hardcoded credentials and implement security best practices\n\n- Move all credentials to environment variables\n- Implement PCI-compliant card storage\n- Add session security and rate limiting\n- Create comprehensive documentation\n- Add security verification tools"
    
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("\n⚠️  Commit failed. This might be because there are no changes to commit.")
        return 1
    
    # Step 8: Ask about pushing
    print("\n" + "=" * 70)
    print("✅ Changes committed successfully!")
    print("=" * 70)
    print()
    
    push_response = input("Do you want to push to GitHub now? (yes/no): ")
    if push_response.lower() not in ['yes', 'y']:
        print("\n✅ Changes committed locally.")
        print("You can push later with: git push origin main")
        return 0
    
    # Step 9: Push to GitHub
    print("\n🚀 Pushing to GitHub...")
    if run_command("git push origin main", "Pushing to GitHub"):
        print("\n" + "=" * 70)
        print("🎉 SUCCESS! Your project is now on GitHub!")
        print("=" * 70)
        print()
        print("✨ Your project has been securely published to GitHub!")
        print()
        print("📝 Next steps:")
        print("1. Verify your repository on GitHub")
        print("2. Check that .env is NOT visible in the repository")
        print("3. Update repository description and topics")
        print("4. Share your project with others!")
        print()
        return 0
    else:
        print("\n❌ Push failed. Please check your GitHub credentials and try:")
        print("   git push origin main")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
