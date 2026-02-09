# Documentation systemd

Documentation complète et en français de systemd, le système d'initialisation et de gestion des services Linux.

## 🌐 Site en ligne

**[https://vignemail1.github.io/systemd-doc/](https://vignemail1.github.io/systemd-doc/)**

## 📚 Contenu

### Introduction

- Vue d'ensemble de systemd
- Architecture et composants
- Histoire et évolution
- Comparaison avec SysVinit

### Types d'unités

- **Services** : Démons et services système
- **Sockets** : Activation à la demande
- **Timers** : Planification de tâches
- **Targets** : Groupes d'unités et runlevels
- **Mount/Automount** : Gestion des systèmes de fichiers
- **Path** : Surveillance de fichiers
- **Device** : Gestion des périphériques
- **Swap** : Mémoire virtuelle
- **Slices/Scopes** : Gestion des ressources et cgroups

### Outils

- systemctl, journalctl, systemd-analyze
- networkd, resolved, timesyncd
- Et bien d'autres...

## 🚀 Installation et développement

### Prérequis

- [mise](https://mise.jdx.dev) (gestionnaire d'environnement)
- Python 3.14+

### Installation rapide

```bash
# Cloner le repository
git clone https://github.com/vignemail1/systemd-doc.git
cd systemd-doc

# Installer mise si nécessaire
curl https://mise.run | sh

# Installer Python et les dépendances
mise install
mise run install
```

### Commandes disponibles

```bash
# Démarrer le serveur de développement
mise run dev
# Site accessible sur http://127.0.0.1:8000

# Construire le site statique
mise run build

# Déployer sur GitHub Pages
mise run deploy

# Nettoyer les fichiers générés
mise run clean
```

## 🔧 Qualité et linting

### Vérification Markdown

```bash
# Vérifier la syntaxe (nécessite markdownlint-cli2)
npm install -g markdownlint-cli2
mise run lint

# Correction automatique avec markdownlint
mise run lint-fix

# Correction du formatage (indentation, lignes vides)
mise run fix-markdown
```

### Règles de formatage

La documentation suit les règles MkDocs :

- **Indentation des listes** : 3 espaces par niveau
- **Lignes vides** : Avant et après chaque liste
- **Lignes vides** : Avant et après les blocs de code
- **Pas d'espaces** en fin de ligne
- **Une ligne vide** maximum entre les sections

Le script `scripts/fix_markdown.py` corrige automatiquement ces problèmes.

## 📝 Structure du projet

```
systemd-doc/
├── docs/                    # Documentation source
│   ├── introduction/        # Introduction à systemd
│   ├── unites/              # Types d'unités
│   ├── outils/              # Outils systemd
│   └── index.md             # Page d'accueil
├── scripts/                # Scripts utilitaires
│   └── fix_markdown.py      # Correction Markdown
├── .github/workflows/      # GitHub Actions
├── mkdocs.yml              # Configuration MkDocs
├── .mise.toml              # Configuration mise
├── .markdownlint.yaml      # Configuration linting
└── requirements.txt        # Dépendances Python
```

## ⚙️ Configuration

### mise (.mise.toml)

Gestionnaire d'environnement avec tâches prédéfinies :

- `install` : Installation des dépendances
- `dev` : Serveur de développement
- `build` : Construction du site
- `deploy` : Déploiement GitHub Pages
- `clean` : Nettoyage
- `lint` : Vérification Markdown
- `lint-fix` : Correction automatique
- `fix-markdown` : Formatage Markdown

### MkDocs (mkdocs.yml)

- Thème Material Design
- Navigation automatique avec awesome-pages
- Extensions Markdown (admonitions, tabs, code highlighting...)
- Support multi-langue

## 👥 Contribution

### Ajouter du contenu

1. Créer ou modifier un fichier `.md` dans `docs/`
2. Utiliser la syntaxe Markdown avec les extensions MkDocs
3. Exécuter `mise run fix-markdown` pour formater
4. Tester avec `mise run dev`
5. Commiter et pusher

### Standards de qualité

- **Langage** : Français clair et technique
- **Exemples** : Code fonctionnel et commenté
- **Structure** : En-têtes hiérarchiques
- **Format** : Respect des règles markdownlint

## 📦 Déploiement

Le déploiement est **automatique** via GitHub Actions :

- Push sur `main` → Build et déploiement sur GitHub Pages
- Le site est accessible sur `https://vignemail1.github.io/systemd-doc/`

Déploiement manuel possible avec `mise run deploy`.

## 📝 Licence

Documentation sous licence libre (préciser la licence si nécessaire).

## 🔗 Ressources

- [systemd.io](https://systemd.io/) - Site officiel
- [freedesktop.org](https://www.freedesktop.org/wiki/Software/systemd/) - Documentation officielle
- [Arch Wiki - systemd](https://wiki.archlinux.org/title/Systemd) - Excellente documentation
- [MkDocs](https://www.mkdocs.org/) - Générateur de documentation
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - Thème utilisé
