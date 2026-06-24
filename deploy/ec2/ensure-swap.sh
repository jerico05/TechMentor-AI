#!/usr/bin/env bash
# Ajoute 2 Go de swap si absent (evite OOM pendant docker build sur petit EC2).
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Lancez avec sudo: sudo bash deploy/ec2/ensure-swap.sh"
  exit 1
fi

swap_kb="$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)"
if [[ "$swap_kb" -gt 1048576 ]]; then
  echo ">> Swap deja present ($(( swap_kb / 1024 )) Mo). Rien a faire."
  exit 0
fi

if [[ ! -f /swapfile ]]; then
  echo ">> Creation /swapfile (2 Go)..."
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048 status=progress
  chmod 600 /swapfile
  mkswap /swapfile
fi

swapon /swapfile 2>/dev/null || true
grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
echo ">> Swap actif:"
free -h
