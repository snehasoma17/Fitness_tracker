#!/usr/bin/env bash
# =============================================================================
# setup-gitlab-runner.sh
# One-shot setup script to register a local GitLab Runner for this project.
# Based on: https://code.swecha.org/-/snippets/2749
#
# Usage:
#   1. Fill in the variables below (GITLAB_URL, PROJECT_TOKEN).
#   2. Run: bash setup-gitlab-runner.sh
# =============================================================================

set -e

# ── CONFIGURE THESE ──────────────────────────────────────────────────────────
GITLAB_URL="https://code.swecha.org"
PROJECT_TOKEN=""          # ← paste your project runner token here
                          #   (Settings → CI/CD → Runners → New project runner)
RUNNER_NAME="fitness-tracker-local-runner"
RUNNER_TAGS="python,fitness-tracker,local"
# ─────────────────────────────────────────────────────────────────────────────

if [ -z "$PROJECT_TOKEN" ]; then
  echo "❌ ERROR: PROJECT_TOKEN is not set."
  echo "   Go to: $GITLAB_URL/<your-group>/<your-project>/-/settings/ci_cd#js-runners-settings"
  echo "   Click 'New project runner', copy the token, and paste it above."
  exit 1
fi

echo "🔧 Checking for gitlab-runner..."

# Install gitlab-runner if not present
if ! command -v gitlab-runner &>/dev/null; then
  echo "📦 Installing GitLab Runner..."
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
    sudo apt-get install gitlab-runner -y
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install gitlab-runner
  else
    echo "⚠️  Windows detected. Please download the runner manually from:"
    echo "   https://docs.gitlab.com/runner/install/windows.html"
    exit 1
  fi
fi

echo "✅ gitlab-runner found: $(gitlab-runner --version | head -1)"

echo "🔗 Registering runner with $GITLAB_URL..."

gitlab-runner register \
  --non-interactive \
  --url "$GITLAB_URL" \
  --token "$PROJECT_TOKEN" \
  --executor "shell" \
  --description "$RUNNER_NAME" \
  --tag-list "$RUNNER_TAGS" \
  --run-untagged="true" \
  --locked="false"

echo "🚀 Starting the runner service..."
gitlab-runner start || gitlab-runner run &

echo ""
echo "✅ Runner registered and started!"
echo "   You can verify at: $GITLAB_URL/<your-group>/<your-project>/-/settings/ci_cd#js-runners-settings"
