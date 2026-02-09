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

# Correction automatique des erreurs courantes (MD031, MD032, MD049, MD060, MD040)
mise run fix-markdown

# Corriger tous les fichiers Markdown
mise run fix-markdown-all
```

### Erreurs corrigées automatiquement

Le script `scripts/fix-markdown.py` corrige :

- **MD031** : Lignes vides manquantes autour des blocs de code
- **MD032** : Lignes vides manquantes autour des listes
- **MD049** : Remplacement `_emphase_` par `*emphase*`
- **MD060** : Espaces manquants autour des pipes dans tableaux
- **MD040** : Langage manquant dans les blocs de code

Voir [scripts/README.md](scripts/README.md) pour plus de détails.

### Règles de formatage

La documentation suit les règles MkDocs :

- **Indentation des listes** : 3 espaces par niveau
- **Lignes vides** : Avant et après chaque liste
- **Lignes vides** : Avant et après les blocs de code
- **Pas d'espaces** en fin de ligne
- **Une ligne vide** maximum entre les sections
- **Emphase** : `*texte*` au lieu de `_texte_`
- **Tableaux** : Espaces autour des `|`

## 📏 Structure du projet

```
systemd-doc/
├── docs/                    # Documentation source
│   ├── introduction/        # Introduction à systemd
│   ├── unites/              # Types d'unités
│   ├── outils/              # Outils systemd
│   ├── cas-pratiques/       # Cas d'usage concrets
│   ├── versions-systemd.md  # Référence versions
│   └── index.md             # Page d'accueil
├── scripts/                # Scripts utilitaires
│   ├── fix-markdown.py      # Correction Markdown automatique
│   └── README.md            # Documentation scripts
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
- `lint-fix` : Correction automatique markdownlint
- `fix-markdown` : Correction erreurs courantes
- `fix-markdown-all` : Correction tous fichiers

### MkDocs (mkdocs.yml)

- Thème Material Design
- Navigation automatique avec awesome-pages
- Diagrammes Mermaid intégrés
- Extensions Markdown (admonitions, tabs, code highlighting...)
- Support multi-langue

## 👥 Contribution

### Ajouter du contenu

1. Créer ou modifier un fichier `.md` dans `docs/`
2. Utiliser la syntaxe Markdown avec les extensions MkDocs
3. Exécuter `mise run fix-markdown` pour formater
4. Tester avec `mise run dev`
5. Vérifier avec `mise run lint`
6. Commiter et pusher

### Standards de qualité

- **Langage** : Français clair et technique
- **Exemples** : Code fonctionnel et commenté
- **Structure** : En-têtes hiérarchiques
- **Format** : Respect des règles markdownlint
- **Diagrammes** : Utiliser Mermaid pour les schémas
- **Versions** : Indiquer versions minimums systemd si pertinent

## 📦 Déploiement

Le déploiement est **automatique** via GitHub Actions :

- Push sur `main` → Build et déploiement sur GitHub Pages
- Le workflow lint exécute automatiquement `fix-markdown.py` avant le linting
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
- [Mermaid](https://mermaid.js.org/) - Diagrammes
