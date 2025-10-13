#!/usr/bin/env bash
set -Eeuo pipefail

# === paths ===
PROJECT_DIR="/opt/OnlineShop"
VENV_DIR="$PROJECT_DIR/venv"
MANAGE_PY="$PROJECT_DIR/manage.py"

# === helpers ===
unit_exists() {
  # есть ли такой unit-файл в системе
  systemctl list-unit-files --type=service | awk '{print $1}' | grep -qx "$1.service"
}

is_active() {
  systemctl --quiet is-active "$1"
}

restart_if_exists() {
  local svc="$1"
  if unit_exists "$svc"; then
    echo "→ Restart $svc"
    systemctl restart "$svc"
  else
    echo "→ Skip $svc (unit not found)"
  fi
}

# === go ===
echo "→ Enter $PROJECT_DIR"
cd "$PROJECT_DIR" || { echo "Project directory not found"; exit 1; }

# (опционально) обновить код, если это git-репозиторий
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "→ Git pull"
  git pull --ff-only || true
fi

echo "→ Activate venv"
source "$VENV_DIR/bin/activate" || { echo "Virtualenv not found"; exit 1; }

echo "→ Django checks & migrations"
python "$MANAGE_PY" check
python "$MANAGE_PY" migrate --noinput

# (опционально) статика, если используете
if [[ -d "$PROJECT_DIR/static" || -d "$PROJECT_DIR/staticfiles" ]]; then
  echo "→ Collect static"
  python "$MANAGE_PY" collectstatic --noinput || true
fi

echo "→ Restart application services"
restart_if_exists shop      
restart_if_exists celery       
restart_if_exists celery-beat 

echo "→ Reload nginx (no downtime)"
if unit_exists nginx; then
  if nginx -t; then
    systemctl reload nginx
  else
    echo "nginx config test failed, doing safe restart..."
    systemctl restart nginx
  fi
else
  echo "→ Skip nginx (unit not found)"
fi

echo "✓ Deployment finished successfully!"
