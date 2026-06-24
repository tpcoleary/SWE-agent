# SWE-agent Integration & Custom Sandbox Development Guide

This guide describes how to integrate and run SWE-agent inside sandboxed Docker containers, configure model parameters using the local LiteLLM Proxy, execute test suites, and troubleshoot common execution loops.

---

## 1. Setup & Environment Configurations

SWE-agent operates by launching language models as developers within an isolated Docker sandbox. The host configuration needs to point to the local LiteLLM Proxy:

### Environment File (`~/swe-agent/.env`)
Configure the following options in your workspace `.env` file:

```env
# Route LLM queries to local LiteLLM proxy
OPENAI_API_BASE=http://localhost:4000/v1
OPENAI_API_KEY=sk-any-key-value

# Required for cloning repositories or creating PRs (optional)
GITHUB_TOKEN=your_github_token_here
```

---

## 2. Running the Agent on a Workspace

To run the agent, specify the model, target codebase path, and the issue statement:

```bash
cd ~/swe-agent
source .venv/bin/activate

# Execute SWE-agent run
sweagent run \
  --agent.model.name="openai/nemotron3super_chat" \
  --env.repo.path="/home/tpcoleary/projects/your-target-repo" \
  --problem_statement.path="/home/tpcoleary/projects/your-target-repo/issue.md"
```

*Tip: For models without native tool-calling capabilities (e.g. custom local models), use `--agent.tools.parse_function=thought_action` to run via structured text parser.*

---

## 3. Best Practices & Troubleshooting

### Prevent WSL File Lockups (0x8007274c)
* **Problem:** If the repository directory contains virtual environments (`.venv`) or heavy node_modules folders, SWE-agent will attempt to zip and copy them across the WSL/Docker volume boundary, causing WSL to hang or throw network/memory timeout errors.
* **Fix:** Temporarily move virtual environment directories outside the repo path prior to starting the run:
  ```bash
  mv /path/to/repo/.venv /path/to/repo-venv-backup
  ```
  Restore it once the execution is completed:
  ```bash
  mv /path/to/repo-venv-backup /path/to/repo/.venv
  ```

### Resolving Indefinite echo Loops on Completion
* **Problem:** The agent successfully implements a fix and verifies it using the test suite, but endlessly repeats validation commands and fails to submit the solution. This happens when the system template lacks a submission command instruction.
* **Fix:** Ensure the active agent config file (e.g. `config/default.yaml`) includes the following snippet in its `system_template`:
  ```yaml
  When you have completed the task and verified your changes, you must run the command 'submit' to submit your work and end the session.
  ```

### Handling Edit Constraints on Test Files
* **Problem:** SWE-agent's default system instructions explicitly forbid modifying test scripts. If a bug's logic is defined inside a test script itself, the agent will loop searching for other source files.
* **Fix:** Before running the agent, refactor any code under test into a separate source module (e.g., `logic.py`), import it inside the test file, and commit this separation of concerns to Git (`git commit`).

---

## 4. Applying Patches

SWE-agent does not modify the host repository directly. Instead, it outputs a trajectory folder containing a unified diff (`.patch` file).

To apply the patch to your local workspace, use `git apply`, ensuring you exclude temporary compiled Python cache files:
```bash
git apply --exclude="__pycache__/*" /path/to/swe-agent/trajectories/tpcoleary/run_xxxxx/patch.patch
```

---

## 5. Docker Sandbox Resource Management

SWE-agent containers are named with a `swe-` prefix. Use these commands to monitor and clean up execution environments:

```bash
# Monitor container resource utilization
docker stats $(docker ps -q --filter name=swe-)

# Stop a hung container
docker stop <container_name_or_id>

# Clean up all stopped/hanging SWE-agent containers
docker rm -f $(docker ps -aq --filter name=swe-)
```
