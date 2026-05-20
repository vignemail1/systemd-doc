# localectl

`localectl` est l'outil de configuration de la locale système et de la disposition du clavier sous systemd. Il modifie `/etc/locale.conf` et `/etc/vconsole.conf` de façon cohérente, et peut appliquer les réglages à la session X11/Wayland courante.

## Syntaxe générale

```bash
localectl [OPTIONS] COMMANDE
```

## Afficher l'état

```bash
# Vue complète : locale, console keymap, layout X11
localectl status
```

Exemple de sortie :

```text
   System Locale: LANG=fr_FR.UTF-8
                  LC_TIME=fr_FR.UTF-8
       VC Keymap: fr
      X11 Layout: fr
     X11 Variant: oss
```

## Configuration de la locale

### Lister les locales disponibles

```bash
# Toutes les locales générées sur le système
localectl list-locales

# Filtrer
localectl list-locales | grep fr_FR
localectl list-locales | grep UTF-8
```

### Définir la locale système

```bash
# Définir LANG (locale principale)
sudo localectl set-locale LANG=fr_FR.UTF-8

# Définir plusieurs variables simultanément
sudo localectl set-locale LANG=fr_FR.UTF-8 LC_TIME=fr_FR.UTF-8 LC_MESSAGES=en_US.UTF-8

# Revenir à la locale C (neutre, ASCII)
sudo localectl set-locale LANG=C.UTF-8
```

Les variables de locale disponibles : `LANG`, `LANGUAGE`, `LC_CTYPE`, `LC_NUMERIC`, `LC_TIME`, `LC_COLLATE`, `LC_MONETARY`, `LC_MESSAGES`, `LC_PAPER`, `LC_NAME`, `LC_ADDRESS`, `LC_TELEPHONE`, `LC_MEASUREMENT`, `LC_IDENTIFICATION`, `LC_ALL`.

!!! tip "Locale pour serveurs"
    Sur un serveur headless, `LANG=C.UTF-8` ou `LANG=en_US.UTF-8` est recommandé. Une locale `fr_FR` peut provoquer des sorties de commandes en français, compliquant le parsing dans les scripts.

### Fichier `/etc/locale.conf`

`localectl set-locale` modifie directement ce fichier :

```ini
# /etc/locale.conf
LANG=fr_FR.UTF-8
LC_TIME=fr_FR.UTF-8
```

## Configuration du clavier

### Console virtuelle (TTY)

```bash
# Lister les keymaps disponibles
localectl list-keymaps

# Filtrer
localectl list-keymaps | grep fr
localectl list-keymaps | grep azerty

# Définir le keymap console
sudo localectl set-keymap fr
sudo localectl set-keymap fr-pc

# Keymap console + layout X11 en une commande
sudo localectl set-keymap fr --no-convert
```

### Layout X11 / Wayland

```bash
# Définir le layout X11 uniquement
sudo localectl set-x11-keymap fr

# Avec variante
sudo localectl set-x11-keymap fr oss

# Avec modèle de clavier
sudo localectl set-x11-keymap fr pc105 oss

# Avec options (ex: touche compose)
sudo localectl set-x11-keymap fr pc105 oss compose:ralt

# Syntaxe complète
# set-x11-keymap LAYOUT [MODEL [VARIANT [OPTIONS]]]
```

### Lister les layouts, modèles et variantes X11

```bash
# Layouts disponibles
localectl list-x11-keymap-layouts
localectl list-x11-keymap-layouts | grep fr

# Modèles de clavier
localectl list-x11-keymap-models

# Variantes pour un layout
localectl list-x11-keymap-variants fr

# Options disponibles
localectl list-x11-keymap-options
```

### Conversion automatique console ↔ X11

Par défaut, `set-keymap` tente de déduire le layout X11 équivalent et `set-x11-keymap` tente de déduire le keymap console.

```bash
# Désactiver la conversion automatique
sudo localectl set-keymap fr --no-convert
sudo localectl set-x11-keymap fr --no-convert
```

## Opérations à distance

```bash
# Lire la locale d'un serveur distant
localectl -H root@192.168.1.10 status

# Modifier à distance
sudo localectl -H root@192.168.1.10 set-locale LANG=en_US.UTF-8
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--no-pager` | Désactiver le paginateur |
| `--no-convert` | Ne pas convertir entre console et X11 |
| `-H <hôte>` | Hôte distant (via SSH) |
| `-M <machine>` | Machine / conteneur systemd-nspawn |
| `--no-ask-password` | Ne pas demander le mot de passe polkit |

## Voir aussi

- [hostnamectl](hostnamectl.md) — configuration du nom d'hôte
- `man localectl`
- `man locale.conf(5)` — format du fichier de locale
- `man vconsole.conf(5)` — format du fichier de configuration console
