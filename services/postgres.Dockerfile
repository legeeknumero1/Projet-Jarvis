FROM postgres:15-alpine
RUN apk add --no-cache curl jq bash
COPY scripts/fetch-secrets-db.sh /usr/local/bin/fetch-secrets-db.sh
RUN chmod +x /usr/local/bin/fetch-secrets-db.sh
ENTRYPOINT ["/usr/local/bin/fetch-secrets-db.sh"]
CMD ["postgres"]
