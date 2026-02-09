# Scripts utilitaires

Ce répertoire contient des scripts pour maintenir la qualité de la documentation.

## fix-markdown.py

Script de correction automatique des erreurs markdownlint.

### Erreurs corrigées

- **MD031** : Ajoute lignes vides autour des blocs de code
- **MD032** : Ajoute lignes vides autour des listes
- **MD049** : Remplace `_emphase_` par `*emphase*`
- **MD060** : Ajoute espaces autour des pipes dans les tableaux
- **MD040** : Ajoute langage aux blocs de code sans langage
- **MD013** : Détecte (mais ne corrige pas encore) les lignes trop longues

### Utilisation

#### Corriger les fichiers avec erreurs connues

```bash
python scripts/fix-markdown.py
```

Cela corrige uniquement les fichiers listés dans le script :

- `docs/unites/swap.md`
- `docs/unites/targets.md`
- `docs/unites/timers.md`
- `docs/versions-systemd.md`

#### Corriger tous les fichiers Markdown

```bash
python scripts/fix-markdown.py --all
```

Parcoure récursivement `docs/` et corrige tous les fichiers `.md`.

#### Dry-run (aperçu sans modification)

```bash
python scripts/fix-markdown.py --dry-run
python scripts/fix-markdown.py --all --dry-run
```

### Avec mise

```bash
# Installer les dépendances
mise install

# Corriger fichiers avec erreurs
mise run fix-markdown

# Corriger tous les fichiers
mise run fix-markdown-all

# Puis linter
mise run lint
```

### Dans CI/CD

Le workflow GitHub Actions `.github/workflows/lint.yml` exécute automatiquement ce script avant le linting pour corriger les erreurs courantes.

### Limitations

- **MD013 (longueur de ligne)** : Détectée mais pas corrigée automatiquement, car la coupure intelligente de lignes est complexe
- **Contexte** : Les corrections sont appliquées de manière conservative pour ne pas casser le contenu existant
- **Blocs de code** : Tout le contenu entre \`\`\` est préservé tel quel

### Développement

Pour ajouter une nouvelle correction :

1. Créer une fonction `fix_mdXXX_description(content)`
2. Ajouter dans `fix_markdown_file()` après les autres corrections
3. Tester avec `--dry-run` d'abord
4. Documenter ici

### Exemple de sortie

```
Correction de 4 fichier(s)...

Traitement de docs/unites/swap.md...
  ✓ Corrigé
Traitement de docs/unites/targets.md...
  ✓ Corrigé
Traitement de docs/unites/timers.md...
  ✓ Corrigé
Traitement de docs/versions-systemd.md...
  ✓ Corrigé

4/4 fichier(s) corrigé(s)
```
