#!/usr/bin/env bash
set -euo pipefail

echo "🛠️ Installation Complète Arch Linux WSL - Setup Jarvis"

# -------------------------------------------------------
# 1. MISE À JOUR SYSTÈME
# -------------------------------------------------------
echo "🚀 Mise à jour du système..."
sudo pacman -Syu --noconfirm

# -------------------------------------------------------
# 2. OUTILS DE BASE
# -------------------------------------------------------
echo "📦 Installation outils de base..."
sudo pacman -S --needed --noconfirm base-devel git curl wget vim nano htop tree fd ripgrep bat exa

# -------------------------------------------------------
# 3. INSTALLATION YAY
# -------------------------------------------------------
if ! command -v yay &>/dev/null; then
  echo "📦 Installation de yay (AUR helper)..."
  git clone https://aur.archlinux.org/yay.git /tmp/yay
  cd /tmp/yay
  makepkg -si --noconfirm
  cd ~ && rm -rf /tmp/yay
else
  echo "✅ yay déjà installé, skip."
fi

# -------------------------------------------------------
# 4. DOCKER & CONTAINERS
# -------------------------------------------------------
if ! command -v docker &>/dev/null; then
  echo "🐳 Installation Docker..."
  sudo pacman -S --needed --noconfirm docker docker-compose
  sudo systemctl enable --now docker
  sudo usermod -aG docker $USER || true
else
  echo "✅ Docker déjà installé, skip."
fi

# -------------------------------------------------------
# 5. ENVIRONNEMENT PYTHON
# -------------------------------------------------------
if ! command -v python &>/dev/null; then
  echo "🐍 Installation Python..."
  sudo pacman -S --needed --noconfirm python python-pip python-virtualenv python-wheel python-setuptools
  pip install --user safety bandit semgrep || true
else
  echo "✅ Python déjà installé, skip."
fi

# -------------------------------------------------------
# 6. NODE.JS & NPM
# -------------------------------------------------------
if ! command -v node &>/dev/null; then
  echo "🟢 Installation Node.js..."
  sudo pacman -S --needed --noconfirm nodejs npm yarn
else
  echo "✅ Node.js déjà installé, skip."
fi

# Fix global npm dans $HOME
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
if ! grep -q ".npm-global/bin" ~/.bashrc; then
  echo 'export PATH=$HOME/.npm-global/bin:$PATH' >> ~/.bashrc
fi
export PATH=$HOME/.npm-global/bin:$PATH

# Outils sécurité Node.js
if ! npm list -g @snyk/cli &>/dev/null; then
  npm install -g @snyk/cli audit-ci
fi

# -------------------------------------------------------
# 7. BASES DE DONNÉES
# -------------------------------------------------------
echo "🗄️ Installation clients DB..."
sudo pacman -S --needed --noconfirm postgresql-libs redis pgcli
yay -S --needed --noconfirm redis-cli

# -------------------------------------------------------
# 8. OUTILS SÉCURITÉ & MONITORING
# -------------------------------------------------------
echo "🛡️ Installation outils sécurité & monitoring..."
sudo pacman -S --needed --noconfirm nmap netcat openssh prometheus grafana

# Trivy (container security scan)
mkdir -p ~/.local/bin
if ! command -v trivy &>/dev/null; then
  curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ~/.local/bin
fi
if ! grep -q ".local/bin" ~/.bashrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# -------------------------------------------------------
# 9. GIT & CONFIG
# -------------------------------------------------------
if ! git config user.name &>/dev/null; then
  git config --global user.name "Enzo"
  git config --global user.email "ton-email@domain.com"
  git config --global init.defaultBranch main
fi

# -------------------------------------------------------
# 10. ZSH + OH-MY-ZSH
# -------------------------------------------------------
if ! command -v zsh &>/dev/null; then
  echo "💻 Installation ZSH..."
  sudo pacman -S --needed --noconfirm zsh zsh-completions
  yay -S --needed --noconfirm oh-my-zsh-git
else
  echo "✅ ZSH déjà installé, skip."
fi

# -------------------------------------------------------
# 11. SETUP PROJET JARVIS
# -------------------------------------------------------
echo "📂 Clone Projet Jarvis..."
cd ~
if [ ! -d "Projet-Jarvis" ]; then
  git clone <URL_DU_PROJET> Projet-Jarvis
fi
cd Projet-Jarvis

# Python venv
if [ ! -d "venv" ]; then
  python -m venv venv
fi
source venv/bin/activate
cd backend && pip install -r requirements.txt || true
cd ../frontend && npm install || true
cd ..

# -------------------------------------------------------
# 12. CONFIG DOCKER SECURISEE
# -------------------------------------------------------
echo "🔐 Configuration sécurisée Docker..."
sudo mkdir -p /home/docker-data
if [ ! -f "/etc/docker/daemon.json" ]; then
  sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "data-root": "/home/docker-data",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "experimental": true,
  "features": {
    "buildkit": true
  }
}
EOF
  sudo systemctl restart docker
else
  echo "✅ Docker déjà configuré, skip."
fi

# -------------------------------------------------------
# 13. SSH & FIREWALL
# -------------------------------------------------------
echo "🔒 Sécurisation SSH & firewall..."
sudo pacman -S --needed --noconfirm ufw
sudo systemctl enable --now sshd
sudo ufw allow ssh || true
sudo ufw default deny incoming || true
sudo ufw default allow outgoing || true
sudo ufw enable || true

# -------------------------------------------------------
# 14. VARIABLES D'ENVIRONNEMENT
# -------------------------------------------------------
echo "⚙️ Configuration variables secrètes..."
if ! grep -q "JARVIS_API_KEY" ~/.bashrc; then
  {
    echo "export JARVIS_API_KEY=\"$(openssl rand -hex 32)\""
    echo "export POSTGRES_PASSWORD=\"$(openssl rand -hex 16)\""
    echo "export SECRET_KEY=\"$(openssl rand -hex 32)\""
  } >> ~/.bashrc
fi

# -------------------------------------------------------
# 15. OPTIMISATIONS WSL
# -------------------------------------------------------
echo "⚡ Optimisations WSL..."
if ! grep -q "\[wsl2\]" /etc/wsl.conf 2>/dev/null; then
  sudo tee -a /etc/wsl.conf > /dev/null <<EOF
[wsl2]
memory=4GB
processors=4
swap=2GB
EOF
fi

# -------------------------------------------------------
# 16. TESTS
# -------------------------------------------------------
echo "🧪 Vérifications installation..."
docker --version || echo "Docker FAIL"
python --version || echo "Python FAIL"
node --version || echo "Node FAIL"
git --version || echo "Git FAIL"
trivy --version || echo "Trivy FAIL"
safety --version || echo "Safety FAIL"

echo "✅ Installation complète terminée !"
echo "👉 Redémarre ta session (ou 'exec bash') pour appliquer PATH et groupes."

