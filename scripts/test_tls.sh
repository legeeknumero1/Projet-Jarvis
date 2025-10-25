#!/bin/bash
export JWT_SECRET="test-secret-key-that-is-definitely-longer-than-32-chars"
export POSTGRES_PASSWORD="postgres-test-pwd-12345"
export CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
export TLS_CERT_PATH=../certs/server.crt
export TLS_KEY_PATH=../certs/server.key

cd core
timeout 8 /c/Users/Le\ Geek/.cargo/bin/cargo run 2>&1
