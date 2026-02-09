#!/usr/bin/env python3
"""
Script de correction automatique des erreurs markdownlint
Corrige MD031, MD032, MD049, MD060, MD040, MD013 + fermetures blocs
"""
import re
import sys
from pathlib import Path


def fix_bad_fence_closures(content):
    """Corriger les fermetures de blocs mal formees comme ```text au lieu de ```"""
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detecter ouverture de fence
        if stripped.startswith('```') and not in_code_block:
            in_code_block = True
            result.append(line)
        # Detecter fermeture de fence (peut avoir du texte apres)
        elif stripped.startswith('```') and in_code_block:
            in_code_block = False
            # Si c'est ```xxx au lieu de ``` seul, corriger
            if len(stripped) > 3:
                # Extraire l'indentation originale
                indent = line[:len(line) - len(line.lstrip())]
                result.append(f"{indent}```")
            else:
                result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)


def fix_md031_fences(content):
    """MD031: Ajouter lignes vides autour des blocs de code"""
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detection d'ouverture de fence
        if stripped.startswith('```') and not in_code_block:
            in_code_block = True
            # Ajouter ligne vide avant si necessaire
            if result and result[-1].strip() != '' and not result[-1].strip().startswith('#'):
                result.append('')
            result.append(line)
        # Detection de fermeture de fence
        elif stripped.startswith('```') and in_code_block:
            in_code_block = False
            result.append(line)
            # Ajouter ligne vide apres si necessaire
            if i + 1 < len(lines) and lines[i + 1].strip() != '':
                result.append('')
        else:
            result.append(line)
    
    return '\n'.join(result)


def fix_md032_lists(content):
    """MD032: Ajouter lignes vides autour des listes"""
    lines = content.split('\n')
    result = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_list_item = stripped.startswith(('-', '*', '+')) or re.match(r'^\d+\.', stripped)
        
        prev_line = lines[i - 1].strip() if i > 0 else ''
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
        
        prev_is_list = prev_line.startswith(('-', '*', '+')) or re.match(r'^\d+\.', prev_line)
        next_is_list = next_line.startswith(('-', '*', '+')) or re.match(r'^\d+\.', next_line)
        
        # Ajouter ligne vide avant debut de liste
        if is_list_item and not prev_is_list and prev_line != '' and result:
            if result[-1].strip() != '':
                result.append('')
        
        result.append(line)
        
        # Ajouter ligne vide apres fin de liste
        if is_list_item and not next_is_list and next_line != '':
            result.append('')
    
    return '\n'.join(result)


def fix_md049_emphasis(content):
    """MD049: Remplacer _emphase_ par *emphase*"""
    # Remplacer _texte_ par *texte* en evitant les cas speciaux
    # Ne pas toucher dans les blocs de code
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue
        
        if not in_code_block:
            # Remplacer _text_ par *text* (pas dans URLs ou code inline)
            line = re.sub(r'(?<!`)_([^_`\n]+?)_(?!`)', r'*\1*', line)
        
        result.append(line)
    
    return '\n'.join(result)


def fix_md060_tables(content):
    """MD060: Ajouter espaces autour des pipes dans tableaux"""
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue
        
        # Detecter lignes de tableau (contiennent | mais pas dans code)
        if '|' in line and not in_code_block:
            # Traiter comme tableau
            parts = line.split('|')
            fixed_parts = []
            
            for j, part in enumerate(parts):
                # Premiere et derniere partie peuvent etre vides
                if j == 0 or j == len(parts) - 1:
                    fixed_parts.append(part)
                else:
                    # Ajouter espaces autour du contenu
                    content_stripped = part.strip()
                    if content_stripped:
                        fixed_parts.append(f' {content_stripped} ')
                    else:
                        fixed_parts.append(' ')
            
            result.append('|'.join(fixed_parts))
        else:
            result.append(line)
    
    return '\n'.join(result)


def fix_md040_code_lang(content):
    """MD040: Ajouter langage aux blocs de code"""
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Detecter ouverture de fence
        if stripped.startswith('```') and not in_code_block:
            # Verifier si un langage est specifie
            if stripped == '```':
                # Pas de langage, ajouter 'text'
                indent = line[:len(line) - len(line.lstrip())]
                result.append(f"{indent}```text")
                in_code_block = True
            else:
                # Langage specifie
                result.append(line)
                in_code_block = True
        # Detecter fermeture de fence
        elif stripped.startswith('```') and in_code_block:
            in_code_block = False
            result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)


def fix_md013_line_length(content, max_length=120):
    """MD013: Couper lignes trop longues (pour texte normal uniquement)"""
    lines = content.split('\n')
    result = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue
        
        # Ne pas toucher au code, tableaux, URLs
        if in_code_block or '|' in line or 'http' in line or line.strip().startswith('#'):
            result.append(line)
            continue
        
        # Si ligne trop longue, essayer de couper intelligemment
        if len(line) > max_length:
            # Pour l'instant, juste signaler
            result.append(line)  # TODO: implementer coupure intelligente
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
        print(f"  X Erreur lecture: {e}")
        return False
    
    # Appliquer corrections dans l'ordre
    content = original
    content = fix_bad_fence_closures(content)  # NOUVEAU: corriger fermetures mal formees
    content = fix_md049_emphasis(content)
    content = fix_md060_tables(content)
    content = fix_md040_code_lang(content)
    content = fix_md031_fences(content)
    content = fix_md032_lists(content)
    content = fix_md013_line_length(content)
    
    # Ecrire si change
    if content != original:
        if not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  OK Corrige")
                return True
            except Exception as e:
                print(f"  X Erreur ecriture: {e}")
                return False
        else:
            print(f"  OK Changements detectes (non appliques)")
            return True
    else:
        print(f"  - Aucun changement necessaire")
        return False


def main():
    # Fichiers avec erreurs
    error_files = [
        'docs/unites/swap.md',
        'docs/unites/targets.md',
        'docs/unites/timers.md',
        'docs/versions-systemd.md',
    ]
    
    dry_run = '--dry-run' in sys.argv
    all_files = '--all' in sys.argv
    
    if all_files:
        # Traiter tous les fichiers .md
        docs_dir = Path('docs')
        files_to_fix = list(docs_dir.rglob('*.md'))
    else:
        # Traiter seulement les fichiers avec erreurs
        files_to_fix = [Path(f) for f in error_files if Path(f).exists()]
    
    print(f"Correction de {len(files_to_fix)} fichier(s)...\n")
    
    fixed_count = 0
    for file_path in files_to_fix:
        if fix_markdown_file(file_path, dry_run):
            fixed_count += 1
    
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}{fixed_count}/{len(files_to_fix)} fichier(s) corrige(s)")


if __name__ == '__main__':
    main()
