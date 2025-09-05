#!/bin/bash
set -e

# Determine le repertoire du projet automatiquement (repertoire ou se trouve ce script)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOKEN_FILE="$PROJECT_DIR/token_youtube.json"

echo "[$(date)] : Generation d'un nouveau PO token..."

# Generation et ecriture dans token_youtube.json
youtube-po-token-generator > "$TOKEN_FILE"

# Verification du contenu
if grep -q '"poToken":' "$TOKEN_FILE"; then
  echo "[$(date)] : PO token genere avec succes et enregistre dans $TOKEN_FILE"
else
  echo "[$(date)] : echec de la generation du PO token !" >&2
  exit 1
fi

# (Optionnel) Redemarrage automatique de l'API si elle tourne via systemd
if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet youtube-api; then
  echo "[$(date)] : Redemarrage de l'API..."
  systemctl restart youtube-api
fi


