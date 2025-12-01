"""
MCP Manager pour Jarvis
Gestionnaire centralisé de tous les serveurs MCP
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MCPServerInfo:
    """Information sur un serveur MCP"""
    name: str
    path: Path
    config_path: Path
    install_script: Path
    status: str  # "installed", "configured", "running", "error"
    description: str
    capabilities: List[str]

class MCPManager:
    """Gestionnaire des serveurs MCP de Jarvis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mcp_root = Path(__file__).parent
        self.servers_dir = self.mcp_root / "servers"
        self.configs_dir = self.mcp_root / "configs" 
        self.scripts_dir = self.mcp_root / "scripts"
        self.available_servers: Dict[str, MCPServerInfo] = {}
        
        self.scan_available_servers()
    
    def scan_available_servers(self):
        """Scanne tous les serveurs MCP disponibles"""
        self.available_servers.clear()
        
        # Scanner le dossier configs pour trouver tous les MCP
        for config_file in self.configs_dir.glob("*.json"):
            server_name = config_file.stem  # nom sans .json
            
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                server_path = self.servers_dir / server_name
                install_script = self.scripts_dir / f"install_{server_name}.sh"
                
                # Déterminer le statut
                status = self.check_server_status(server_name, config)
                
                self.available_servers[server_name] = MCPServerInfo(
                    name=server_name,
                    path=server_path,
                    config_path=config_file,
                    install_script=install_script,
                    status=status,
                    description=config.get("description", ""),
                    capabilities=config.get("capabilities", [])
                )
                
                self.logger.info(f" [MCP] Serveur trouvé: {server_name} ({status})")
                
            except Exception as e:
                self.logger.error(f" [MCP] Erreur lecture config {server_name}: {e}")
    
    def check_server_status(self, server_name: str, config: Dict[str, Any]) -> str:
        """Vérifie le statut d'un serveur MCP"""
        try:
            server_path = self.servers_dir / server_name
            
            if not server_path.exists():
                return "not_installed"
            
            # Vérifier si le chemin d'exécution existe
            install_config = config.get("installation", {})
            exec_path = install_config.get("path", "")
            
            if exec_path and not Path(exec_path).exists():
                return "missing_executable"
            
            # Vérifier les variables d'environnement requises
            requirements = install_config.get("requirements", {})
            for env_var, required in requirements.items():
                if required == "required" and not os.getenv(env_var):
                    return "missing_config"
            
            return "configured"
            
        except Exception as e:
            self.logger.error(f" [MCP] Erreur vérification statut {server_name}: {e}")
            return "error"
    
    def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """Liste tous les serveurs MCP avec leur statut"""
        servers_info = {}
        
        for name, server in self.available_servers.items():
            servers_info[name] = {
                "description": server.description,
                "status": server.status,
                "capabilities": server.capabilities,
                "path": str(server.path),
                "has_install_script": server.install_script.exists()
            }
        
        return servers_info
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Récupère la configuration d'un serveur"""
        if server_name not in self.available_servers:
            return None
        
        try:
            config_path = self.available_servers[server_name].config_path
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f" [MCP] Erreur lecture config {server_name}: {e}")
            return None
    
    def install_server(self, server_name: str) -> bool:
        """Installe un serveur MCP"""
        if server_name not in self.available_servers:
            self.logger.error(f" [MCP] Serveur {server_name} non trouvé")
            return False
        
        server = self.available_servers[server_name]
        
        if not server.install_script.exists():
            self.logger.error(f" [MCP] Script d'installation manquant: {server.install_script}")
            return False
        
        try:
            import subprocess
            result = subprocess.run([str(server.install_script)], 
                                  capture_output=True, text=True, check=True)
            
            self.logger.info(f" [MCP] Installation {server_name} réussie")
            self.logger.info(f" [MCP] Sortie: {result.stdout}")
            
            # Re-scanner pour mettre à jour le statut
            self.scan_available_servers()
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f" [MCP] Erreur installation {server_name}: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f" [MCP] Erreur installation {server_name}: {e}")
            return False
    
    def add_new_server_template(self, server_name: str, description: str, capabilities: List[str]) -> bool:
        """Crée un template pour un nouveau serveur MCP"""
        try:
            # Créer le dossier serveur
            server_dir = self.servers_dir / server_name
            server_dir.mkdir(exist_ok=True)
            
            # Créer le fichier de configuration
            config = {
                "name": server_name,
                "description": description,
                "version": "1.0.0",
                "capabilities": capabilities,
                "installation": {
                    "method": "local",
                    "path": f"/home/enzo/Projet-Jarvis/MCP/servers/{server_name}/dist/index.js",
                    "command": "node",
                    "requirements": {}
                },
                "configuration": {},
                "tools": {},
                "status": "template"
            }
            
            config_path = self.configs_dir / f"{server_name}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Créer le script d'installation template
            install_script_content = f"""#!/bin/bash
# Installation du serveur MCP {server_name} pour Jarvis

set -e

echo " Installation du serveur MCP {server_name}..."

# TODO: Ajouter les étapes d'installation spécifiques

echo " Serveur MCP {server_name} installé avec succès"
"""
            
            install_script = self.scripts_dir / f"install_{server_name}.sh"
            with open(install_script, 'w') as f:
                f.write(install_script_content)
            
            install_script.chmod(0o755)
            
            self.logger.info(f" [MCP] Template créé pour {server_name}")
            self.scan_available_servers()
            return True
            
        except Exception as e:
            self.logger.error(f" [MCP] Erreur création template {server_name}: {e}")
            return False

if __name__ == "__main__":
    # Test du gestionnaire MCP
    logging.basicConfig(level=logging.INFO)
    manager = MCPManager()
    
    print(" Serveurs MCP disponibles:")
    servers = manager.list_servers()
    
    for name, info in servers.items():
        print(f"  • {name}: {info['description']} ({info['status']})")
        print(f"    Capacités: {', '.join(info['capabilities'])}")
        print()