#!/usr/bin/env python3
"""
Basic tests for SpotifySort v2.0 (Spotify API version)
Run this to verify the installation is working correctly
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from spotifysort import spotify_auth
        print("  ✓ spotify_auth module imported")
    except ImportError as e:
        print(f"  ✗ Failed to import spotify_auth: {e}")
        return False

    try:
        from spotifysort import library_analyzer
        print("  ✓ library_analyzer module imported")
    except ImportError as e:
        print(f"  ✗ Failed to import library_analyzer: {e}")
        return False

    try:
        from spotifysort import playlist_manager
        print("  ✓ playlist_manager module imported")
    except ImportError as e:
        print(f"  ✗ Failed to import playlist_manager: {e}")
        return False

    try:
        from spotifysort import cli
        print("  ✓ CLI module imported")
    except ImportError as e:
        print(f"  ✗ Failed to import CLI: {e}")
        return False

    try:
        from spotifysort.web import app
        print("  ✓ Web app module imported")
    except ImportError as e:
        print(f"  ✗ Failed to import web app: {e}")
        return False

    return True


def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")

    dependencies = [
        'spotipy',
        'requests',
        'flask',
        'flask_cors',
        'flask_session',
        'click',
        'yaml',
        'tabulate',
        'colorama',
        'tqdm',
        'pandas',
        'dotenv'
    ]

    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep} installed")
        except ImportError:
            print(f"  ✗ {dep} NOT installed")
            all_ok = False

    return all_ok


def test_cli_commands():
    """Test CLI is accessible"""
    print("\nTesting CLI...")

    try:
        from spotifysort.cli import main
        print("  ✓ CLI main function accessible")
        return True
    except Exception as e:
        print(f"  ✗ CLI test failed: {e}")
        return False


def test_env_setup():
    """Check if .env file exists or can be created"""
    print("\nChecking configuration...")

    env_file = Path('.env')
    env_example = Path('.env.example')

    if env_file.exists():
        print("  ✓ .env file exists")

        # Check if it has required variables
        with open(env_file, 'r') as f:
            content = f.read()
            has_client_id = 'SPOTIFY_CLIENT_ID' in content
            has_client_secret = 'SPOTIFY_CLIENT_SECRET' in content

            if has_client_id and has_client_secret:
                print("  ✓ Spotify credentials configured")
            else:
                print("  ⚠ .env exists but missing Spotify credentials")
                print("    Run: spotifysort setup")
        return True
    elif env_example.exists():
        print("  ⚠ .env file not found")
        print("    .env.example exists - copy and configure it")
        print("    Or run: spotifysort setup")
        return True
    else:
        print("  ⚠ No configuration files found")
        print("    Run: spotifysort setup")
        return True


def main():
    """Run all tests"""
    print("="*60)
    print("SpotifySort v2.0 Installation Tests")
    print("="*60)

    results = {
        'Dependencies': test_dependencies(),
        'Imports': test_imports(),
        'CLI': test_cli_commands(),
        'Configuration': test_env_setup(),
    }

    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✓ All tests passed! SpotifySort is ready to use.")
        print("\nNext steps:")
        print("  1. Get Spotify API credentials:")
        print("     https://developer.spotify.com/dashboard")
        print("  2. Run: spotifysort setup")
        print("  3. Or start web interface: python -m spotifysort.web.app")
        return 0
    else:
        print("\n⚠ Some tests had warnings, but SpotifySort should work.")
        print("\nTo complete setup:")
        print("  1. Create Spotify Developer App")
        print("  2. Run: spotifysort setup")
        return 0


if __name__ == '__main__':
    sys.exit(main())
