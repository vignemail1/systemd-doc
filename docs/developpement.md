# Guide de développement

Ce guide explique comment contribuer à cette documentation et utiliser l'environnement de développement.

## Environnement de développement

### Installation avec mise

Ce projet utilise [mise](https://mise.jdx.dev) pour gérer l'environnement Python et les dépendances.

```bash
# Installer mise (si pas déjà fait)
curl https://mise.run | sh

# Ou avec Homebrew sur macOS
brew install mise

# Activer mise dans votre shell
echo 'eval "$(mise activate bash)"' >> ~/.bashrc  # bash
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc   # zsh
```

### Setup du projet

```bash
# Cloner le repository
git clone https://github.com/vignemail1/systemd-doc.git
cd systemd-doc

# mise va automatiquement :
# - Installer Python 3.12
# - Créer un virtualenv dans .venv/
# - Installer les dépendances
mise install
mise run install
```

## Commandes disponibles

### Développement

```bash
# Démarrer le serveur de dev avec live-reload
mise run dev

# Accéder au site sur http://127.0.0.1:8000
```

Le serveur se recharge automatiquement à chaque modification.

### Build

```bash
# Construire le site statique
mise run build

# Le résultat est dans ./site/
```

### Déploiement

```bash
# Déployer manuellement sur GitHub Pages
mise run deploy
```

⚠️ **Note** : Le déploiement automatique via GitHub Actions est configuré sur push vers `main`.

### Nettoyage

```bash
# Supprimer les fichiers générés
mise run clean
```

### Lister les tâches

```bash
# Voir toutes les tâches disponibles
mise tasks
```

## Structure des fichiers

### Organisation du contenu

```text
docs/
├── index.md                    # Page d'accueil
├── .pages                      # Configuration awesome-pages (ordre navigation)
├── introduction/
│   ├── index.md
│   ├── .pages
│   ├── architecture.md
│   └── ...
├── unites/
│   ├── index.md
│   ├── .pages
│   ├── services.md
│   └── ...
└── stylesheets/
    └── extra.css               # Styles personnalisés
```

### Fichier .pages

Le plugin `awesome-pages` utilise des fichiers `.pages` pour contrôler l'ordre de navigation :

```yaml
title: Titre de la section
arrange:

  - index.md
  - fichier1.md
  - fichier2.md
  - sous-dossier

```

## Syntaxe Markdown

### Extensions activées

Le projet utilise de nombreuses extensions Markdown :

#### Admonitions

```markdown
!!! note "Titre optionnel"
    Contenu de la note

!!! warning
    Attention !

!!! info
    Information

!!! tip
    Conseil

!!! danger
    Danger
```

#### Code avec highlighting

```markdown
\`\`\`bash
# Commande bash
systemctl status nginx.service
\`\`\`

\`\`\`ini
# Fichier systemd
[Unit]
Description=Mon service
\`\`\`

\`\`\`python
# Code Python
import systemd.daemon
\`\`\`
```

#### Tabs

```markdown
=== "Tab 1"
    Contenu du premier tab

=== "Tab 2"
    Contenu du second tab
```

#### Definition lists

```markdown
Terme
: Définition du terme

Autre terme
: Autre définition
```

#### Tables

```markdown
| Colonne 1 | Colonne 2 |
|-----------|----------|
| Valeur 1  | Valeur 2 |
```

#### Footnotes

```markdown
Texte avec note[^1].

[^1]: Contenu de la note de bas de page.
```

#### Emoji

```markdown
:smile: :rocket: :fire:
```

### Variables spéciales

Dans le contexte systemd :

```markdown

- `%n` : Nom de l'unité
- `%i` : Instance
- `$MAINPID` : PID principal

```

## Bonnes pratiques

### Style d'écriture

1. **Titres** : Utiliser la hiérarchie (# ## ### ####)
2. **Code** : Toujours spécifier le langage
3. **Exemples** : Fournir des exemples complets et testés
4. **Liens** : Utiliser des liens relatifs pour la navigation interne
5. **Images** : Placer dans `docs/images/` si nécessaire

### Organisation du contenu

1. **Une page = un sujet** : Ne pas tout mettre dans un seul fichier
2. **Index** : Chaque section a un `index.md` qui introduit
3. **Navigation** : Utiliser `.pages` pour contrôler l'ordre
4. **Cross-references** : Lier les concepts entre eux

### Commits

Messages de commit clairs :

```bash
git commit -m "Ajout section sur systemd-resolved"
git commit -m "Fix: Correction exemple socket activation"
git commit -m "Docs: Amélioration explications cgroups"
```

## Configuration MkDocs

### mkdocs.yml

Le fichier `mkdocs.yml` configure :

- **site_name** : Nom du site
- **theme** : Configuration Material
- **markdown_extensions** : Extensions Markdown activées
- **plugins** : Plugins utilisés (awesome-pages, search...)
- **extra** : Métadonnées (réseaux sociaux, analytics...)

### Thème Material

Options configurables dans `theme` :

- **palette** : Couleurs et mode sombre/clair
- **font** : Polices utilisées
- **features** : Fonctionnalités activées (navigation, search...)
- **logo** / **favicon** : Personnalisation visuelle

## GitHub Actions

Le workflow `.github/workflows/deploy.yml` :

1. Checkout du code
2. Installation de mise
3. Installation des dépendances Python
4. Build du site avec MkDocs
5. Déploiement sur GitHub Pages

Déclenché automatiquement sur push vers `main`.

## Dépannage

### mise : command not found

```bash
# Réinstaller mise
curl https://mise.run | sh

# Activer dans le shell
eval "$(mise activate bash)"
```

### Python version incorrecte

```bash
# Forcer l'installation de Python 3.12
mise install python@3.12
```

### Dépendances manquantes

```bash
# Réinstaller les dépendances
mise run install

# Ou manuellement
source .venv/bin/activate
pip install -r requirements.txt
```

### Site ne se build pas

```bash
# Vérifier les erreurs de syntaxe
mise run build

# Nettoyer et rebuilder
mise run clean
mise run build
```

### GitHub Pages ne se met pas à jour

1. Vérifier que les GitHub Actions sont activées
2. Aller dans Settings > Pages
3. Source doit être "GitHub Actions"
4. Vérifier les logs de workflow dans Actions

## Ressources

- [Material for MkDocs Documentation](https://squidfunk.github.io/mkdocs-material/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)
- [awesome-pages plugin](https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin)
- [mise Documentation](https://mise.jdx.dev/)
