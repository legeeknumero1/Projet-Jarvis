#!/bin/bash
set -e

# Configuration
PKI_DIR="./certs/pki"
CA_DIR="$PKI_DIR/ca"
ISSUED_DIR="$PKI_DIR/issued"
PRIVATE_DIR="$PKI_DIR/private"
DAYS_VALID=3650

# Liste des services nécessitant un certificat
SERVICES=("jarvis-secretsd" "backend" "postgres" "timescale" "open-webui")

echo "🔐 Initialisation de l'infrastructure PKI Ultra-Sécurisée..."

# 1. Création de la structure de dossiers
mkdir -p "$CA_DIR" "$ISSUED_DIR" "$PRIVATE_DIR"
chmod 700 "$PRIVATE_DIR"

# 2. Génération de la CA (Autorité de Certification)
if [ ! -f "$CA_DIR/ca.key" ]; then
    echo "Creating Root CA..."
    openssl genrsa -out "$CA_DIR/ca.key" 4096
    openssl req -x509 -new -nodes -key "$CA_DIR/ca.key" -sha256 -days 3650 \
        -subj "/C=FR/ST=France/L=Paris/O=Jarvis-Corp/OU=Security/CN=Jarvis-Internal-CA" \
        -out "$CA_DIR/ca.crt"
else
    echo "Root CA already exists."
fi

# 3. Génération des certificats pour chaque service
for SERVICE in "${SERVICES[@]}"; do
    echo "Processing service: $SERVICE"
    
    # Génération Clé Privée
    if [ ! -f "$PRIVATE_DIR/$SERVICE.key" ]; then
        openssl genrsa -out "$PRIVATE_DIR/$SERVICE.key" 4096
    fi

    # Création config OpenSSL pour SAN (Subject Alternative Name)
    cat > "/tmp/$SERVICE.cnf" <<EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
C = FR
ST = France
L = Paris
O = Jarvis-Corp
OU = Service
CN = $SERVICE

[req_ext]
subjectAltName = @alt_names
EOF

    # Ajout des usages de clé
    if [ "$SERVICE" == "jarvis-secretsd" ]; then
        echo "extendedKeyUsage = serverAuth, clientAuth" >> "/tmp/$SERVICE.cnf"
    else
        echo "extendedKeyUsage = clientAuth" >> "/tmp/$SERVICE.cnf"
    fi

    # Ajout des SANs
    cat >> "/tmp/$SERVICE.cnf" <<EOF

[alt_names]
DNS.1 = $SERVICE
DNS.2 = localhost
IP.1 = 127.0.0.1
IP.2 = 172.20.0.5
EOF

    # Génération CSR
    openssl req -new -key "$PRIVATE_DIR/$SERVICE.key" -config "/tmp/$SERVICE.cnf" -out "/tmp/$SERVICE.csr"

    # Signature par la CA
    openssl x509 -req -in "/tmp/$SERVICE.csr" -CA "$CA_DIR/ca.crt" -CAkey "$CA_DIR/ca.key" \
        -CAcreateserial -out "$ISSUED_DIR/$SERVICE.crt" -days $DAYS_VALID -sha256 \
        -extensions req_ext -extfile "/tmp/$SERVICE.cnf"

    rm "/tmp/$SERVICE.csr" "/tmp/$SERVICE.cnf"
    echo "✅ $SERVICE certifié."
done

# Permissions restrictives
chmod 600 "$PRIVATE_DIR"/*.key
chmod 644 "$ISSUED_DIR"/*.crt
chmod 644 "$CA_DIR"/*.crt

echo "🎉 Infrastructure PKI déployée avec succès dans $PKI_DIR"
