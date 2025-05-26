#!/bin/bash
# Setup branch protection for Claude Squad

echo "🔒 Setting up branch protection for main branch..."

gh api repos/ZeroSumQuant/luca-dev-assistant/branches/main/protection \
  --method PUT \
  --raw-field '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["test-and-build", "dependency-scan"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'

echo "✅ Branch protection enabled!"