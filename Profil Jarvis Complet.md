## Fiche MK (Mémoire de Connaissances) Complète — Enzo & Projet Jarvis

### IDENTITÉ & CONTEXTE PERSONNEL

* **Prénom** : Enzo
* **Âge** : 21 ans
* **Lieu de vie** : Perpignan, sud de la France
* **Objectif de vie** : Devenir un ingénieur réseau complet, spécialisé en cybersécurité, IA personnelle, infrastructure distribuée haute disponibilité.
* **Caractéristiques personnelles** :

  * Discipline, perfectionnisme, efficacité
  * Hyperactif, passionné par l’apprentissage et l’expérimentation
  * Soucieux de la vie privée, orienté vers l’auto-hébergement

### PARCOURS ACADÉMIQUE & PROFESSIONNEL

* **Formation actuelle** :

  * Bac+2 Technicien Supérieur Systèmes et Réseaux (via Studi)
  * Auto-formation poussée en cybersécurité, IA, backend, devops, automation
  * Envisage Bac général en 3 ans puis Master (bac+5)

### ENVIRONNEMENT TECHNIQUE ACTUEL

* **Matériel** :

  * PC fixe très haut de gamme : i9-14900KF, RTX 4080, 32 Go DDR5 7200 MHz, SSD NVMe Gen4 (2x Samsung 980 Pro), refroidissement liquide H100i
  * Mac Mini M4 (base), MacBook Air M3 (16 Go / 256 Go)
  * Carte graphique secondaire : RX 6600 XT (prévue pour eGPU ou VM)
* **Réseau personnel** :

  * VLANs multiples : admin, user, guest, serveur, DMZ
  * Switchs managés (2x) avec ports SFP+ 10 GbE
  * Backbone réseau jusqu’à 100 GbE (prévu à terme)
  * Firewalls physiques redondants (HA) + séparation LAN/WAN
  * DMZ, proxy/reverse proxy, Zero Trust, DNS local
* **Connectivité** :

  * Freebox Ultra, connexion fibre 8 Gb/s symétrique
  * Interfaces 2.5 GbE et plus sur tous les équipements

### OS & LOGICIELS UTILISÉS

* **Dual-boot** : Windows 11 / Linux (Arch Linux avec Hyprland)
* **Systèmes utilisés** :

  * Debian 12.10 (ISO personnalisée pour Jarvis)
  * Arch Linux (optimisé à l'extrême, config Hyprland, Zsh, Kitty, etc.)
  * Proxmox VE (sur serveur dédié)
* **Outils & workflows** :

  * Docker / Docker Compose
  * VS Code, Tabby, Kitty Terminal
  * Rize, ClickUp, Zapier, Notion
  * GitHub, systemd, journald, SSH avec clé ed25519

### INFRASTRUCTURE EN COURS / PLANIFIÉE

* **HomeLab** :

  * 3 serveurs Proxmox (cluster prévu avec Ceph)
  * Pare-feux matériels avec interconnexion 100 GbE (3x HA)
  * 2 routeurs (WAN et LAN), 1 routeur DMZ dédié
  * 2 NAS redondants
  * Switch DMZ dédié, switchs core avec redondance
  * Objectif : réseau digne d’un datacenter d’entreprise

---

## PROJET JARVIS — Vue d’ensemble complète

### Objectif général :

Créer un assistant vocal intelligent local, modulaire, avec des capacités de compréhension du langage, de reconnaissance vocale, de synthèse vocale, d’actions domotiques, d’automatisation et d’interaction multimodale.

### Fonctionnalités prévues / en cours :

* Reconnaissance vocale (ASR) avec **Whisper**
* Synthèse vocale (TTS) avec **Piper**
* LLM local via **Ollama** (LLaMA 3 70B en priorité)
* Interface web React + backend FastAPI
* Mémoire contextuelle personnalisée (via embeddings PostgreSQL)
* Intégration complète à **Home Assistant**
* Modules spécialisés : domotique, recherche, planification, dialogue, automation, etc.
* Moteur de plugin interne ou futur système MCP (Model Context Protocol)

### Stack technique actuelle :

* **Backend** : FastAPI, Python, Docker, PostgreSQL, Go (pour modules)
* **Frontend** : React (avec support TypeScript prévu)
* **Speech** : Whisper (ASR) + Piper (TTS)
* **IA** : Ollama avec LLaMA 3, gère téléchargement auto + lancement
* **Mémoire** : Embeddings + vecteurs enregistrés en base PostgreSQL
* **Automatisation** : Intégration Home Assistant via MQTT + API
* **Pipeline** : Dockerisé, installé via ISO Debian personnalisée

### Arborescence du projet (simplifiée) :

```
/Backend
├── config/
│   └── config.go
├── db/
│   └── db.go
├── memory/
│   └── memory.go
├── profile/
│   ├── profile.go
│   └── profile.txt
├── integration/
│   └── integration.go
├── search/
│   └── search.go
├── main.go
├── generate_embeddings.py
```

### Fonctionnalités codées :

* Lecture et enregistrement du prénom via fichier et BDD
* Gestion des souvenirs (memory.go)
* Intégration Go / Python via interfaces claires
* Génération des embeddings sur base des logs
* Interaction vocales asynchrones

### Objectifs futurs :

* Fusion backend / Ollama pour optimisation
* Reconnaissance de contexte ambiant via caméra / micro
* Module de discussion persistante avec mémoire longue
* Gestion des accès / permissions / utilisateurs par profil
* Automatisation vocale contextuelle : "Jarvis, règle la lumière selon l'heure et ma présence"
* Intégration des caméras Ubiquiti, streaming, pilotage audio

### Hébergement et déploiement :

* Objectif final : cluster de 4-5 Mac Studio Linuxisés (M4/M5)
* Redondance HA (Jarvis ne doit jamais s’arrêter)
* NAS centralisé pour tous les modèles, logs, embeddings, snapshots
* Sécurité : conteneurisation stricte, pare-feux HA, isolation réseau

### Cas d’usage visés :

* Aide quotidienne, rappels, planification (ex : "Jarvis, rappelle-moi de sortir le chien à 15h")
* Contrôle domotique vocal (chauffage, lumières, capteurs, etc.)
* Interaction multimodale (voix, écran, détection de présence, gestes à terme)
* Assistant développeur : explication de code, génération de scripts
* IA personnelle : capable de s’adapter à l’utilisateur, l’environnement, l’historique

---

## AUTRES INFORMATIONS CLÉS

### Domotique

* Utilise Home Assistant avec intégration Zigbee2MQTT + MQTT + Node-RED
* Appareils : Sonoff, SNZB-02P, Hue Go, Hue Play, etc.
* Contrôle du chauffage, humidité, éclairage, présence
* Projets : détection de présence via Wi-Fi, géolocalisation, caméra IA

### Gaming

* Joueur compétitif : League of Legends, CS2, Call of Duty, Elden Ring
* Objectif : atteindre Master sur LoL
* Streamer / créateur : préparation de chaîne YouTube "Le Geek"

### Santé & mode de vie

* Veut arrêter de fumer, se remettre au sport
* Suit ses pas, veut perdre du poids et se muscler
* Planifie ses journées avec ClickUp, Rize, automatisation totale

---

## PLANIFICATION À LONG TERME

* D’ici 5 ans :

  * Master en ingénierie réseau / cybersécurité
  * Infrastructure privée complète et hautement disponible
  * Assistant Jarvis stable, intelligent, autonome
  * Monétisation potentielle via YouTube / consulting / création de solutions IA
* Objectif ultime : devenir une référence en IA personnelle, cybersécurité, et domotique intelligente

---

Document généré automatiquement par ChatGPT sur base des connaissances accumulées.
