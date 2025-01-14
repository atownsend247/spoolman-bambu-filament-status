FROM python:3.12-bookworm AS python-builder

# Install dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    python3-dev \
    libpq-dev \
    libffi-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-pdm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add local user so we don't run as root
RUN groupmod -g 1000 users \
    && useradd -u 911 -U app \
    && usermod -G users app

ENV PATH="/home/app/.local/bin:${PATH}"

# Copy and install dependencies
COPY --chown=app:app .env /home/app/spoolman_bambu/.env
COPY --chown=app:app pyproject.toml /home/app/spoolman_bambu/
COPY --chown=app:app pdm.lock /home/app/spoolman_bambu/
WORKDIR /home/app/spoolman_bambu
RUN pdm sync --prod --no-editable

# Copy and install app
COPY --chown=app:app spoolman_bambu /home/app/spoolman_bambu/spoolman_bambu
COPY --chown=app:app spoolman_bambu /home/app/spoolman_bambu/spoolman_bambu
COPY --chown=app:app README.md /home/app/spoolman_bambu/

FROM python:3.12-bookworm AS python-runner

LABEL org.opencontainers.image.source=https://github.com/atownsend247/spoolman-bambu-filament-status
LABEL org.opencontainers.image.description="Sync your BambuLab AMS spools directly with Spoolman."
LABEL org.opencontainers.image.licenses=MIT

# Install latest su-exec
RUN set -ex; \
    \
    curl -o /usr/local/bin/su-exec.c https://raw.githubusercontent.com/ncopa/su-exec/master/su-exec.c; \
    \
    fetch_deps='gcc libc-dev'; \
    apt-get update; \
    apt-get install -y --no-install-recommends $fetch_deps; \
    rm -rf /var/lib/apt/lists/*; \
    gcc -Wall \
    /usr/local/bin/su-exec.c -o/usr/local/bin/su-exec; \
    chown root:root /usr/local/bin/su-exec; \
    chmod 0755 /usr/local/bin/su-exec; \
    rm /usr/local/bin/su-exec.c; \
    \
    apt-get purge -y --auto-remove $fetch_deps

# Add local user so we don't run as root
RUN groupmod -g 1000 users \
    && useradd -u 1000 -U app \
    && usermod -G users app \
    && mkdir -p /home/app/.local/share/spoolman_bambu \
    && chown -R app:app /home/app/.local/share/spoolman_bambu

# Copy built client
COPY --chown=app:app ./client/dist /home/app/spoolman_bambu/client/dist

# Copy built app
COPY --chown=app:app --from=python-builder /home/app/spoolman_bambu /home/app/spoolman_bambu

COPY entrypoint.sh /home/app/spoolman_bambu/entrypoint.sh
RUN chmod +x /home/app/spoolman_bambu/entrypoint.sh

WORKDIR /home/app/spoolman_bambu

ENV PATH="/home/app/spoolman_bambu/.venv/bin:${PATH}"
ENV PYTHONPATH="/home/app/spoolman_bambu:${PYTHONPATH}"

ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BUILD_DATE=${BUILD_DATE}

# Write GIT_COMMIT and BUILD_DATE to a build.txt file
RUN echo "GIT_COMMIT=${GIT_COMMIT}" > build.txt \
    && echo "BUILD_DATE=${BUILD_DATE}" >> build.txt

# Run command
EXPOSE 8000
ENTRYPOINT ["/home/app/spoolman_bambu/entrypoint.sh"]