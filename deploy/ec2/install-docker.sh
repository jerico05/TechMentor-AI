#!/usr/bin/env bash
# Installe Docker + Compose sur Ubuntu (EC2). A lancer une seule fois.
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Lancez avec sudo: sudo bash deploy/ec2/install-docker.sh"
  exit 1
fi

apt-get update
apt-get install -y ca-certificates curl gnupg

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${VERSION_CODENAME}") stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

usermod -aG docker "${SUDO_USER:-ubuntu}" || true

echo ">> Docker installe. Reconnectez-vous puis:"
echo "   cd TechMentor-AI"
echo "   cp backend/.env.production.example backend/.env"
echo "   docker compose --env-file backend/.env -f docker-compose.prod.yml up -d --build backend"
