#!/usr/bin/env bash

set -u

check_tool() {
  local name="$1"
  local command_name="$2"
  local version_command="$3"

  if command -v "$command_name" >/dev/null 2>&1; then
    local version
    version="$($version_command 2>/dev/null | head -n 1 || true)"
    if [ -n "$version" ]; then
      printf "OK      %-10s %s\n" "$name" "$version"
    else
      printf "OK      %-10s installed\n" "$name"
    fi
  else
    printf "MISSING %-10s not found\n" "$name"
  fi
}

echo "Checking local development environment..."
echo

check_tool "git" "git" "git --version"
check_tool "docker" "docker" "docker --version"
check_tool "kubectl" "kubectl" "kubectl version --client"
check_tool "helm" "helm" "helm version --short"
check_tool "faas-cli" "faas-cli" "faas-cli version"
check_tool "python3" "python3" "python3 --version"
check_tool "pip3" "pip3" "pip3 --version"
check_tool "node" "node" "node --version"
check_tool "npm" "npm" "npm --version"

echo
echo "If a tool is MISSING, follow docs/setup-local.md."
