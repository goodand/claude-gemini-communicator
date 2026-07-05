#!/usr/bin/env python3
"""
Bisect Runner - Phase 3-1

Git bisect를 자동화하여 Bad Commit을 빠르게 찾습니다.

Usage:
    python bisect_runner.py --good abc123 --bad def456 --test "./test.sh"
    python bisect_runner.py --good abc123 --bad HEAD --test "npm test -- login"
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_script(test_command):
    """테스트 명령을 bisect run 스크립트로 변환"""
    script_content = f"""#!/bin/bash
set -e

# Run test command
{test_command}

# Exit code: 0 = Good, 1 = Bad
exit $?
"""
    
    # Create temporary script
    script_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.sh',
        delete=False
    )
    script_file.write(script_content)
    script_file.close()
    
    # Make executable
    Path(script_file.name).chmod(0o755)
    
    return script_file.name


def run_bisect(good_commit, bad_commit, test_script):
    """Git bisect 실행"""
    
    print(f"🔍 Starting git bisect")
    print(f"   Good commit: {good_commit}")
    print(f"   Bad commit: {bad_commit}")
    print(f"   Test script: {test_script}")
    print()
    
    # Start bisect
    try:
        subprocess.run(
            ['git', 'bisect', 'start', bad_commit, good_commit],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error starting bisect: {e}", file=sys.stderr)
        return None
    
    # Run bisect
    try:
        result = subprocess.run(
            ['git', 'bisect', 'run', test_script],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        
        # Parse result
        for line in output.split('\n'):
            if 'is the first bad commit' in line:
                # Extract commit hash
                parts = line.split()
                if parts:
                    bad_commit_hash = parts[0]
                    return bad_commit_hash
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error running bisect: {e}", file=sys.stderr)
        return None
    
    finally:
        # Reset bisect
        subprocess.run(['git', 'bisect', 'reset'], capture_output=True)


def get_commit_info(commit_hash):
    """커밋 상세 정보 가져오기"""
    try:
        # Get commit message
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%H%n%an%n%ae%n%ad%n%s', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        
        return {
            'hash': lines[0],
            'author': lines[1],
            'email': lines[2],
            'date': lines[3],
            'message': lines[4]
        }
    except subprocess.CalledProcessError:
        return None


def get_commit_diff(commit_hash):
    """커밋 diff 가져오기"""
    try:
        result = subprocess.run(
            ['git', 'show', '--stat', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def main():
    parser = argparse.ArgumentParser(description='Automate git bisect')
    parser.add_argument('--good', required=True, help='Good commit hash')
    parser.add_argument('--bad', required=True, help='Bad commit hash')
    parser.add_argument('--test', required=True, help='Test command')
    
    args = parser.parse_args()
    
    # Create test script
    test_script = create_test_script(args.test)
    
    try:
        # Run bisect
        bad_commit = run_bisect(args.good, args.bad, test_script)
        
        if bad_commit:
            print()
            print(f"✅ First bad commit found: {bad_commit}")
            print()
            
            # Get commit details
            info = get_commit_info(bad_commit)
            if info:
                print("Commit Details:")
                print(f"  Hash: {info['hash']}")
                print(f"  Author: {info['author']} <{info['email']}>")
                print(f"  Date: {info['date']}")
                print(f"  Message: {info['message']}")
                print()
            
            # Get diff
            diff = get_commit_diff(bad_commit)
            if diff:
                print("Changed files:")
                print(diff)
                print()
            
            print("Next steps:")
            print(f"  1. Analyze commit: git show {bad_commit}")
            print(f"  2. Review diff: git diff {bad_commit}~1 {bad_commit}")
            print("  3. Proceed to Phase 2 (Good/Bad Case analysis)")
            
            return 0
        else:
            print()
            print("❌ Could not find first bad commit")
            print("   Check if test script works correctly")
            
            return 1
    
    finally:
        # Clean up test script
        try:
            Path(test_script).unlink()
        except:
            pass


if __name__ == '__main__':
    sys.exit(main())
