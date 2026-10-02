#!/usr/bin/env bash
# Локальная копия всех проверок CI. Команды совпадают с шагами пайплайна,
# поэтому «красный CI» воспроизводится на своей машине без GitHub.
#
#   ./scripts/check.sh

set -euo pipefail
# shellcheck source=scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
cd "$REPO_ROOT"

need_cmd git ""
command -v uv >/dev/null 2>&1 || die "uv не найден. Выполните: ./scripts/setup.sh"
[ -d .venv ] || die "Каталог .venv не найден. Выполните: ./scripts/setup.sh"

info "Репозиторий: $REPO_ROOT"

gate_format
gate_lint
gate_types
gate_tests
gate_tdd_history

print_summary "Итог: локальная копия CI"

if ! summary_exit_code; then
  printf '\n%sЧто читать дальше:%s\n' "$C_BOLD" "$C_RESET"
  printf '  docs/part1-red-ci.md  — часть 1, починка сборки\n'
  printf '  docs/part2-tdd-agent.md — часть 2, TDD и агент\n'
  printf '  docs/01-toolchain.md  — как читать вывод ruff, mypy и pytest\n'
  exit 1
fi
