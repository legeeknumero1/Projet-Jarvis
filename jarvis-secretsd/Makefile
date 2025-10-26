.PHONY: build run fmt lint audit test scan install

build:
	cargo build --release

run:
	RUST_LOG=info ./target/release/jarvis-secretsd --config config.toml.example

fmt:
	cargo fmt

lint:
	cargo clippy -- -D warnings

audit:
	cargo install cargo-audit || true
	cargo audit

test:
	cargo test

scan: audit lint
	@echo "✅ Security scan complete"

install: build
	sudo cp target/release/jarvis-secretsd /usr/local/bin/
	sudo mkdir -p /etc/jarvis-secretsd /opt/jarvis/secrets /opt/jarvis/audit
	sudo cp config.toml.example /etc/jarvis-secretsd/config.toml.example
	sudo cp policy.yaml.example /etc/jarvis-secretsd/policy.yaml.example
	@echo "✅ Installed to /usr/local/bin/jarvis-secretsd"
	@echo "⚠️  Configure /etc/jarvis-secretsd/config.toml before running"

clean:
	cargo clean
