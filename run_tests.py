#!/usr/bin/env python3
"""
Test runner for Jishu Backend
Provides comprehensive testing with coverage reporting and detailed output
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(command)}")
    print()
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {command[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False

def check_dependencies():
    """Check if required testing dependencies are installed"""
    print("🔍 Checking testing dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-flask',
        'pytest-cov',
        'pytest-mock',
        'coverage'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("\n✅ All testing dependencies are installed!")
    return True

def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    command = ['python', '-m', 'pytest', 'tests/']
    
    if verbose:
        command.append('-v')
    
    if coverage:
        command.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
    
    # Add specific test files
    command.extend([
        'tests/test_auth.py',
        'tests/test_courses.py',
        'tests/test_ai_services.py'
    ])
    
    return run_command(command, "Running Unit Tests")

def run_integration_tests(verbose=False):
    """Run integration tests"""
    command = ['python', '-m', 'pytest', 'tests/test_integration.py']
    
    if verbose:
        command.append('-v')
    
    return run_command(command, "Running Integration Tests")

def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function"""
    command = ['python', '-m', 'pytest', test_path]
    
    if verbose:
        command.append('-v')
    
    return run_command(command, f"Running Specific Test: {test_path}")

def run_coverage_report():
    """Generate and display coverage report"""
    commands = [
        (['python', '-m', 'coverage', 'html'], "Generating HTML Coverage Report"),
        (['python', '-m', 'coverage', 'report'], "Displaying Coverage Summary")
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    if success:
        print(f"\n📊 Coverage report generated in: {os.path.abspath('htmlcov/index.html')}")
    
    return success

def run_linting():
    """Run code linting (if available)"""
    linters = [
        (['python', '-m', 'flake8', 'tests/', '--max-line-length=120'], "Running Flake8 Linting"),
        (['python', '-m', 'pylint', 'tests/'], "Running Pylint Analysis")
    ]
    
    for command, description in linters:
        try:
            run_command(command, description)
        except:
            print(f"⚠️  {description} skipped (not installed)")

def setup_test_environment():
    """Setup test environment"""
    print("🔧 Setting up test environment...")
    
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    # Create necessary directories
    test_dirs = ['tests', 'htmlcov', 'test_reports']
    for directory in test_dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ Directory: {directory}")
    
    print("✅ Test environment setup complete!")

def cleanup_test_artifacts():
    """Clean up test artifacts"""
    print("🧹 Cleaning up test artifacts...")
    
    artifacts = [
        '.coverage',
        '.pytest_cache',
        '__pycache__',
        'htmlcov',
        '*.pyc'
    ]
    
    for artifact in artifacts:
        try:
            if os.path.isfile(artifact):
                os.remove(artifact)
                print(f"  🗑️  Removed file: {artifact}")
            elif os.path.isdir(artifact):
                import shutil
                shutil.rmtree(artifact)
                print(f"  🗑️  Removed directory: {artifact}")
        except:
            pass
    
    print("✅ Cleanup complete!")

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Jishu Backend Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--lint', action='store_true', help='Run code linting')
    parser.add_argument('--cleanup', action='store_true', help='Clean up test artifacts')
    parser.add_argument('--test', type=str, help='Run specific test file or function')
    parser.add_argument('--setup', action='store_true', help='Setup test environment only')
    
    args = parser.parse_args()
    
    print("🚀 Jishu Backend Test Runner")
    print("=" * 60)
    
    # Handle cleanup
    if args.cleanup:
        cleanup_test_artifacts()
        return
    
    # Handle setup
    if args.setup:
        setup_test_environment()
        return
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup test environment
    setup_test_environment()
    
    success = True
    
    # Run specific test
    if args.test:
        success = run_specific_test(args.test, args.verbose)
    
    # Run unit tests
    elif args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    
    # Run integration tests
    elif args.integration:
        success = run_integration_tests(args.verbose)
    
    # Run all tests
    else:
        print("🧪 Running Complete Test Suite")
        
        # Unit tests
        if not run_unit_tests(args.verbose, args.coverage):
            success = False
        
        # Integration tests
        if not run_integration_tests(args.verbose):
            success = False
    
    # Generate coverage report
    if args.coverage:
        run_coverage_report()
    
    # Run linting
    if args.lint:
        run_linting()
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ Test suite passed")
    else:
        print("❌ Some tests failed")
        print("🔍 Check the output above for details")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
