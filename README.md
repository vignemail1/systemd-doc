# Documentation systemd

Documentation complète sur systemd et son écosystème, construite avec [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## 🚀 Démarrage rapide

### Prérequis

- [mise](https://mise.jdx.dev) - Gestionnaire d'outils et d'environnement

### Installation

```bash
# Cloner le repository
git clone https://github.com/vignemail1/systemd-doc.git
cd systemd-doc

# Installer mise si nécessaire
curl https://mise.run | sh

# Installer les dépendances
mise install
mise run install
```

### Développement

```bash
# Démarrer le serveur de développement
mise run dev

# Le site sera accessible sur http://127.0.0.1:8000
```

### Build

```bash
# Construire le site statique
mise run build

# Les fichiers générés seront dans ./site/
```

### Déploiement

Le déploiement sur GitHub Pages est automatique via GitHub Actions lors d'un push sur `main`.

Pour déployer manuellement :

```bash
mise run deploy
```

## 📚 Structure

```
.
├── docs/                      # Contenu de la documentation
│   ├── index.md              # Page d'accueil
│   ├── introduction/         # Introduction à systemd
│   ├── unites/               # Types d'unités systemd
│   ├── outils/               # Outils de l'écosystème
│   ├── gestion-services/     # Gestion des services
│   ├── journal-logging/      # Journal et logging
│   ├── securite/             # Sécurité et isolation
│   └── cas-pratiques/        # Exemples pratiques
├── mkdocs.yml                # Configuration MkDocs
├── .mise.toml                # Configuration mise
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

## 🛠️ Commandes mise disponibles

```bash
mise tasks                    # Lister toutes les tâches
mise run install             # Installer les dépendances
mise run dev                 # Serveur de développement
mise run build               # Construire le site
mise run deploy              # Déployer sur GitHub Pages
mise run clean               # Nettoyer les fichiers générés
```

## 📖 Contenu

Cette documentation couvre :

- **Introduction** : Architecture, histoire, comparaison avec SysVinit
- **Unités** : Services, sockets, timers, targets, mount, path, device, swap
- **Outils** : systemctl, journalctl, networkctl, resolvectl, etc.
- **Gestion** : Création, modification, debugging de services
- **Logging** : Exploitation du journal systemd
- **Sécurité** : Isolation, sandboxing, best practices
- **Cas pratiques** : Exemples concrets et patterns courants

## 🌐 Site en ligne

La documentation est accessible sur : [https://vignemail1.github.io/systemd-doc/](https://vignemail1.github.io/systemd-doc/)

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle section'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📝 Licence

Cette documentation est mise à disposition selon les termes de la licence MIT.

## 🔗 Ressources

- [Site officiel systemd](https://systemd.io/)
- [Documentation freedesktop.org](https://www.freedesktop.org/software/systemd/man/)
- [Code source systemd](https://github.com/systemd/systemd)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mise](https://mise.jdx.dev)
