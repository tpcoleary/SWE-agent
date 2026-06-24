"""CLI helper for SWE-agent Mem0 pre/post-run hooks.

Usage:
    python mem0_session.py search <repo_name>
    python mem0_session.py record <repo_name> <exit_code>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mem0_client as mem0

cmd = sys.argv[1] if len(sys.argv) > 1 else ""
repo = sys.argv[2] if len(sys.argv) > 2 else "unknown"

if cmd == "search":
    memories = mem0.search(f"SWE-agent repository {repo} bug fix issue", cross_agent=True)
    if memories:
        print("[mem0] Relevant context from memory:")
        for m in memories:
            print(f"  · {m}")
    else:
        print("[mem0] No relevant memories found.")

elif cmd == "record":
    exit_code = sys.argv[3] if len(sys.argv) > 3 else "0"
    status = "succeeded" if exit_code == "0" else f"failed (exit {exit_code})"
    mem0.add(f"SWE-agent run on repository '{repo}' {status}.")
    print("[mem0] Session outcome recorded.")
