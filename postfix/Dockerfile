FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends postfix postfix-mysql gettext-base && rm -rf /var/lib/apt/lists/*
COPY conf/ /tmp/conf/
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["postfix", "start-fg"]
