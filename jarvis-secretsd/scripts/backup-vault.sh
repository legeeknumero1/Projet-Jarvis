#!/bin/bash
# Backup jarvis-secretsd vault with encryption

set -e

VAULT_PATH="${VAULT_PATH:-/opt/jarvis/secrets/vault.json}"
AUDIT_PATH="${AUDIT_PATH:-/opt/jarvis/audit/audit.jsonl}"
BACKUP_DIR="${BACKUP_DIR:-/opt/jarvis/backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vault-backup-$TIMESTAMP.tar.gz.gpg"

echo " Backing up jarvis-secretsd vault"
echo " Vault: $VAULT_PATH"
echo " Audit: $AUDIT_PATH"
echo " Backup: $BACKUP_FILE"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create temporary directory
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Copy files to temp directory
cp "$VAULT_PATH" "$TMP_DIR/vault.json"
cp "$AUDIT_PATH" "$TMP_DIR/audit.jsonl"

# Create metadata
cat > "$TMP_DIR/metadata.json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "vault_path": "$VAULT_PATH",
  "audit_path": "$AUDIT_PATH",
  "hostname": "$(hostname)",
  "version": "0.1.0"
}
EOF

# Create tarball and encrypt with GPG
cd "$TMP_DIR"
tar czf - . | gpg --symmetric --cipher-algo AES256 -o "$BACKUP_FILE"

echo " Backup created: $BACKUP_FILE"
echo " Encrypted with AES256 (GPG)"
echo ""
echo "To restore:"
echo "  gpg -d $BACKUP_FILE | tar xzf - -C /tmp/restore"
echo ""
echo "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
