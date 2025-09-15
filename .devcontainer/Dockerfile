# Base universal image with common dev tools
FROM mcr.microsoft.com/devcontainers/universal:2

# Install Node.js LTS (if not included in base image)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs build-essential pkg-config libssl-dev

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Solana CLI (latest stable)
RUN sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:${PATH}"

# Install Anchor (via Anchor Version Manager)
RUN cargo install --git https://github.com/coral-xyz/anchor avm --force \
    && avm install latest \
    && avm use latest

# Install Python and pip
RUN apt-get install -y python3 python3-pip
