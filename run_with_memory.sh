#!/usr/bin/env bash
# Drop-in replacement for `sweagent run` with Mem0 context recall and outcome recording.
# Usage: ./run_with_memory.sh [sweagent run args...]
# Example: ./run_with_memory.sh --agent.model.name="openai/nemotron3super_chat" \
#            --env.repo.path="/home/tpcoleary/myrepo" \
#            --problem_statement.path="/home/tpcoleary/myrepo/issue.md"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
source .venv/bin/activate

# Extract repo name from --env.repo.path= argument
REPO_NAME="unknown"
for arg in "$@"; do
    if [[ "$arg" == --env.repo.path=* ]]; then
        REPO_NAME=$(basename "${arg#*=}")
        break
    fi
done

# Pre-run: recall relevant memories
python3 "$SCRIPT_DIR/mem0_session.py" search "$REPO_NAME"
echo ""

# Run sweagent
sweagent run "$@"
EXIT_CODE=$?

# Post-run: record outcome
echo ""
python3 "$SCRIPT_DIR/mem0_session.py" record "$REPO_NAME" "$EXIT_CODE"

exit $EXIT_CODE
