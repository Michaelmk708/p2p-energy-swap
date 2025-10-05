# Make targets to run the P2P demo on any machine without needing PATH tweaks.

SHELL := /usr/bin/env bash

.PHONY: run stop status logs install-cli

run:
	@bash ./p2p run

stop:
	@bash ./p2p stop

status:
	@bash ./p2p status

logs:
	@bash ./p2p logs all

# Install a global symlink to ~/.local/bin/p2p (Linux/macOS)
install-cli:
	@bash ./scripts/install-cli.sh
