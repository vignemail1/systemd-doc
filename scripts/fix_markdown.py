#!/usr/bin/env python3
"""
Script de correction automatique des fichiers Markdown pour MkDocs.

Règles appliquées :
- Indentation des listes : 3 espaces
- Lignes vides avant et après chaque liste
- Lignes vides avant et après les blocs de code
- Pas de trailing whitespace
- Une seule ligne vide entre les sections
"""

import re
from pathlib import Path


def fix_list_indentation(content: str) -> str:
    """Convertit l'indentation des listes de 2 ou 4 espaces vers 3 espaces."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Détecter les listes avec tirets ou puces
        match = re.match(r'^(\s*)([-*+])\s+(.*)$', line)
        if match:
            indent, marker, text = match.groups()
            # Calculer le niveau d'indentation (chaque niveau = 3 espaces)
            level = len(indent) // 2 if len(indent) > 0 else 0
            new_indent = '   ' * level  # 3 espaces par niveau
            fixed_lines.append(f"{new_indent}{marker} {text}")
        else:
            # Détecter les listes numérotées
            match = re.match(r'^(\s*)(\d+\.)\s+(.*)$', line)
            if match:
                indent, marker, text = match.groups()
                level = len(indent) // 2 if len(indent) > 0 else 0
                new_indent = '   ' * level
                fixed_lines.append(f"{new_indent}{marker} {text}")
            else:
                fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def ensure_blank_lines_around_lists(content: str) -> str:
    """Ajoute des lignes vides avant et après les listes."""
    lines = content.split('\n')
    fixed_lines = []
    in_list = False
    prev_was_blank = False
    
    for i, line in enumerate(lines):
        is_list = bool(re.match(r'^(\s*)([-*+]|\d+\.)\s+', line))
        is_blank = line.strip() == ''
        is_code_block = line.strip().startswith('```')
        is_heading = line.strip().startswith('#')
        
        # Détecter le début d'une liste
        if is_list and not in_list:
            # Ajouter une ligne vide avant si nécessaire
            if fixed_lines and not prev_was_blank and not is_heading:
                fixed_lines.append('')
            fixed_lines.append(line)
            in_list = True
        # Détecter la fin d'une liste
        elif in_list and not is_list and not is_blank:
            # Ajouter une ligne vide après la liste
            if not is_code_block:
                fixed_lines.append('')
            fixed_lines.append(line)
            in_list = False
        else:
            fixed_lines.append(line)
        
        prev_was_blank = is_blank
    
    return '\n'.join(fixed_lines)


def ensure_blank_lines_around_code_blocks(content: str) -> str:
    """Ajoute des lignes vides avant et après les blocs de code."""
    lines = content.split('\n')
    fixed_lines = []
    prev_was_blank = False
    
    for i, line in enumerate(lines):
        is_code_fence = line.strip().startswith('```')
        is_blank = line.strip() == ''
        
        if is_code_fence:
            # Ajouter ligne vide avant le début du bloc de code
            if fixed_lines and not prev_was_blank:
                fixed_lines.append('')
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        prev_was_blank = is_blank
    
    return '\n'.join(fixed_lines)


def remove_trailing_whitespace(content: str) -> str:
    """Supprime les espaces en fin de ligne."""
    lines = content.split('\n')
    return '\n'.join(line.rstrip() for line in lines)


def normalize_blank_lines(content: str) -> str:
    """Limite les lignes vides multiples à une seule."""
    # Remplacer 3+ lignes vides par 2 lignes vides (= 1 ligne vide visible)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content


def fix_markdown_file(filepath: Path) -> bool:
    """
    Corrige un fichier Markdown.
    
    Returns:
        True si le fichier a été modifié, False sinon.
    """
    print(f"Traitement de {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Appliquer les corrections
    content = original_content
    content = remove_trailing_whitespace(content)
    content = fix_list_indentation(content)
    content = ensure_blank_lines_around_lists(content)
    content = ensure_blank_lines_around_code_blocks(content)
    content = normalize_blank_lines(content)
    
    # Assurer une ligne vide à la fin du fichier
    if not content.endswith('\n'):
        content += '\n'
    
    # Vérifier si le fichier a changé
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Corrigé")
        return True
    else:
        print(f"  - Aucune modification nécessaire")
        return False


def main():
    """Parcourt tous les fichiers Markdown et les corrige."""
    docs_dir = Path('docs')
    
    if not docs_dir.exists():
        print(f"Erreur : Le répertoire {docs_dir} n'existe pas")
        return 1
    
    md_files = list(docs_dir.rglob('*.md'))
    
    if not md_files:
        print(f"Aucun fichier Markdown trouvé dans {docs_dir}")
        return 1
    
    print(f"Trouvé {len(md_files)} fichiers Markdown\n")
    
    modified_count = 0
    for md_file in md_files:
        if fix_markdown_file(md_file):
            modified_count += 1
    
    print(f"\n{modified_count}/{len(md_files)} fichiers modifiés")
    return 0


if __name__ == '__main__':
    exit(main())
