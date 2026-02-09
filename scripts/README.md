# Scripts utilitaires

Ce répertoire contient des scripts pour maintenir la qualité de la documentation.

## fix-markdown.py

Script de correction automatique des erreurs markdownlint.

### Erreurs corrigées

- **MD031** : Ajoute lignes vides autour des blocs de code
- **MD032** : Ajoute lignes vides autour des listes
- **MD049** : Remplace `_emphase_` par `*emphase*`
- **MD060** : Ajoute espaces autour des pipes dans les tableaux
- **MD040** : Ajoute langage aux blocs de code sans langage (`text` par défaut)
- **Fins de blocs** : Corrige les fermetures incorrectes comme `\`\`\`text` au lieu de `\`\`\``

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

## fix-fence-endings.py

Script spécialisé pour corriger les fins de blocs de code incorrectes.

### Problème corrigé

Les blocs de code doivent se terminer par `\`\`\`` seul sur la ligne, sans texte additionnel.

**Incorrect** :
```markdown
\`\`\`ini
Requires=postgresql.service
\`\`\`text
```

**Correct** :
```markdown
\`\`\`ini
Requires=postgresql.service
\`\`\`
```

### Utilisation

```bash
# Corriger tous les fichiers
python scripts/fix-fence-endings.py

# Dry-run avec détails
python scripts/fix-fence-endings.py --dry-run --verbose

# Avec mise
mise run fix-fence-endings
```

**Note** : Ce script est déjà intégré dans `fix-markdown.py`, mais peut être exécuté séparément pour diagnostic.

## Dans CI/CD

Le workflow GitHub Actions `.github/workflows/lint.yml` exécute automatiquement `fix-markdown.py` avant le linting pour corriger les erreurs courantes, incluant les fins de blocs incorrectes.

## Ordre d'exécution recommandé

1. **fix-markdown.py** : Corrige toutes les erreurs communes
2. **lint** : Vérifie qu'il ne reste pas d'erreurs
3. **lint-fix** : Si nécessaire, correction manuelle avec markdownlint

```bash
mise run fix-markdown-all
mise run lint
# Si erreurs persistantes :
mise run lint-fix
```

## Limitations

- **MD013 (longueur de ligne)** : Désactivée dans `.markdownlint.yaml`
- **MD036 (emphase comme en-tête)** : Désactivée dans `.markdownlint.yaml`
- **Contexte** : Les corrections sont appliquées de manière conservative
- **Blocs de code** : Le contenu entre \`\`\` est préservé tel quel

## Développement

Pour ajouter une nouvelle correction :

1. Créer une fonction `fix_mdXXX_description(content)`
2. Ajouter dans `fix_markdown_file()` après les autres corrections
3. Tester avec `--dry-run` d'abord
4. Documenter ici

## Exemple de sortie

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
