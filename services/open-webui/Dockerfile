FROM ghcr.io/open-webui/open-webui:main

USER root

# Install curl and jq for fetching secrets
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy secrets fetching script
COPY fetch-secrets-webui.sh /app/fetch-secrets-webui.sh
RUN chmod +x /app/fetch-secrets-webui.sh && \
    chown 1000:1000 /app/fetch-secrets-webui.sh

USER 1000

# Use fetch-secrets as entrypoint wrapper
ENTRYPOINT ["/app/fetch-secrets-webui.sh"]
CMD ["bash", "start.sh"]
