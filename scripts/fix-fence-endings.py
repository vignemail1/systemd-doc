#!/usr/bin/env python3
"""
Script pour corriger les fins de blocs de code incorrectes.

Corrige les cas où le fence de fermeture a du texte après, par exemple:
  ```ini
  Requires=postgresql.service
  ```text  # INCORRECT

Doit devenir:
  ```ini
  Requires=postgresql.service
  ```
  text  # ou supprimer 'text' si c'était une erreur
"""
import re
import sys
from pathlib import Path


def fix_fence_endings(content):
    """
    Corriger les fins de blocs de code avec du texte sur la même ligne.
    
    Patterns à corriger:
    - ```text
    - ```bash
    - ```ini
    - etc. en fin de bloc
    """
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Détection d'ouverture de fence
        if stripped.startswith('```') and not in_code_block:
            in_code_block = True
            result.append(line)
        # Détection de fermeture de fence (dans un bloc)
        elif in_code_block and stripped.startswith('```'):
            # Vérifier si il y a du texte après les ```
            if len(stripped) > 3:
                # Il y a du texte après, par exemple ```text ou ```bash
                # Extraire le texte
                extra_text = stripped[3:].strip()
                
                # Fermer proprement le bloc
                result.append('```')
                
                # Si le texte est significatif (pas juste un langage), l'ajouter sur ligne suivante
                # Sinon, c'était probablement une erreur de syntaxe
                if extra_text and extra_text not in ['text', 'bash', 'sh', 'ini', 'yaml', 'yml', 
                                                        'python', 'py', 'json', 'xml', 'html', 
                                                        'css', 'js', 'javascript', 'sql', 'c', 
                                                        'cpp', 'java', 'go', 'rust', 'toml']:
                    # C'est du vrai contenu, pas un langage
                    result.append('')
                    result.append(extra_text)
                # Sinon on ignore (c'était juste une erreur de syntaxe)
            else:
                # Fermeture propre
                result.append(line)
            
            in_code_block = False
        else:
            result.append(line)
    
    return '\n'.join(result)


def fix_markdown_file(file_path, dry_run=False):
    """Corriger un fichier markdown"""
    print(f"{'[DRY-RUN] ' if dry_run else ''}Traitement de {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        print(f"  ✗ Erreur lecture: {e}")
        return False
    
    # Appliquer correction
    content = fix_fence_endings(original)
    
    # Écrire si changé
    if content != original:
        if not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ Corrigé")
                return True
            except Exception as e:
                print(f"  ✗ Erreur écriture: {e}")
                return False
        else:
            print(f"  ✓ Changements détectés (non appliqués)")
            # Afficher les différences
            orig_lines = original.split('\n')
            new_lines = content.split('\n')
            for i, (orig, new) in enumerate(zip(orig_lines, new_lines), 1):
                if orig != new:
                    print(f"    L{i}: '{orig}' -> '{new}'")
            return True
    else:
        print(f"  - Aucun changement nécessaire")
        return False


def main():
    docs_dir = Path('docs')
    
    dry_run = '--dry-run' in sys.argv
    verbose = '--verbose' in sys.argv or dry_run
    
    # Traiter tous les fichiers .md
    files_to_fix = list(docs_dir.rglob('*.md'))
    
    print(f"Correction de {len(files_to_fix)} fichier(s)...\n")
    
    fixed_count = 0
    for file_path in sorted(files_to_fix):
        if fix_markdown_file(file_path, dry_run):
            fixed_count += 1
    
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}{fixed_count}/{len(files_to_fix)} fichier(s) corrigé(s)")
    
    if dry_run and fixed_count > 0:
        print("\nExécutez sans --dry-run pour appliquer les changements.")


if __name__ == '__main__':
    main()
