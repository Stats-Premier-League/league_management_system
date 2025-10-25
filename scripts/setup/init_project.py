# PROJECT INITIALIZATION SCRIPT 
# Main Purpose: To automate the initial, mandatory setup steps for a new
# developer cloning the project or setting up a new environment. This script
# ensures all prerequisites are met, installs dependencies, and prepares the
# necessary configuration files to get the Django application ready to run.

#!/usr/bin/env python
"""
Initial project setup script
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    print(f"🚀 {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ {description} completed successfully")
    return True


def main():
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create virtual environment
    if not Path('venv').exists():
        if not run_command('python -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    
    # Install requirements
    pip_path = 'venv/Scripts/pip' if os.name == 'nt' else 'venv/bin/pip'
    if not run_command(f'{pip_path} install -r requirements/base.txt', 'Installing requirements'):
        sys.exit(1)
    
    # Copy environment file
    if not Path('.env').exists():
        if Path('.env.example').exists():
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file from .env.example")
        else:
            print("⚠️  .env.example not found, creating basic .env file")
            with open('.env', 'w') as f:
                f.write('SECRET_KEY=your-secret-key-change-this-in-production\n')
                f.write('DEBUG=True\n')
    
    print("\n🎉 Project setup completed!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Mac/Linux: source venv/bin/activate")
    print("2. Run migrations: python manage.py migrate")
    print("3. Create superuser: python manage.py createsuperuser")
    print("4. Run server: python manage.py runserver")


if __name__ == '__main__':
    main()