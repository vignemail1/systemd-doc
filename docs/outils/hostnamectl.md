# hostnamectl

`hostnamectl` est l'outil de configuration du nom d'hôte sous systemd. Il gère les trois types de nom d'hôte Linux et les métadonnées machine (type, chassis, déploiement).

## Syntaxe générale

```bash
hostnamectl [OPTIONS] COMMANDE
```

## Les trois types de nom d'hôte

| Type | Description | Exemple |
| ---- | ----------- | ------- |
| **Static** | Nom persistant stocké dans `/etc/hostname` | `web-prod-01` |
| **Transient** | Nom temporaire reçu via DHCP ou mDNS (perd au reboot) | `dhcp-192-168-1-42` |
| **Pretty** | Nom libre en UTF-8, peut contenir espaces et caractères spéciaux | `Serveur Web Production` |

## Afficher l'état

```bash
# Vue complète : noms, type de machine, OS, noyau
hostnamectl status

# Vue condensée (propriétés brutes)
hostnamectl

# Propriété spécifique
hostnamectl --json=short
```

Exemple de sortie :

```
 Static hostname: web-prod-01
 Pretty hostname: Serveur Web Production
       Icon name: computer-server
         Chassis: server 💻
      Machine ID: a1b2c3d4e5f6...
         Boot ID: f1e2d3c4b5a6...
Operating System: Debian GNU/Linux 12 (bookworm)
          Kernel: Linux 6.1.0-21-amd64
    Architecture: x86-64
 Hardware Vendor: Dell Inc.
  Hardware Model: PowerEdge R650
```

## Configurer le nom d'hôte

```bash
# Définir le nom statique (modifie /etc/hostname)
sudo hostnamectl set-hostname web-prod-01

# Définir le nom joli (UTF-8)
sudo hostnamectl set-hostname "Serveur Web Production" --pretty

# Définir le nom transitoire
sudo hostnamectl set-hostname dhcp-host --transient

# Supprimer le nom joli (revient au nom statique)
sudo hostnamectl set-hostname "" --pretty
```

!!! tip "Convention de nommage"
    Le nom statique doit respecter les règles DNS : lettres, chiffres et tirets uniquement, sans point (le FQDN est géré par le DNS). Exemple : `web-prod-01`, `db-replica-03`, `monitoring`.

## Métadonnées machine

```bash
# Définir le type de déploiement
sudo hostnamectl set-deployment production
sudo hostnamectl set-deployment staging
sudo hostnamectl set-deployment development

# Définir l'emplacement
sudo hostnamectl set-location "Datacenter Paris, rack A3, U12"

# Définir le type de chassis
sudo hostnamectl set-chassis server
sudo hostnamectl set-chassis vm
sudo hostnamectl set-chassis container
sudo hostnamectl set-chassis desktop
sudo hostnamectl set-chassis laptop
```

Types de chassis disponibles : `desktop`, `laptop`, `convertible`, `server`, `tablet`, `handset`, `watch`, `embedded`, `vm`, `container`.

Ces métadonnées sont stockées dans `/etc/machine-info` et accessibles via D-Bus par d'autres services systemd.

## Machine ID

```bash
# Afficher le machine-id (identifiant unique de l'installation)
cat /etc/machine-id

# Générer un nouveau machine-id (utile après clonage de VM)
sudo systemd-machine-id-setup --commit

# Ou manuellement
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
```

!!! warning "Clonage de VM"
    Après avoir cloné une VM, il faut régénérer le `machine-id` et le nom d'hôte. Un `machine-id` identique entre deux machines cause des conflits DHCP et des problèmes de journalisation centralisée.

## Opérations à distance

```bash
# Lire le nom d'hôte d'un serveur distant
hostnamectl -H root@192.168.1.10 status

# Modifier le nom d'hôte à distance
sudo hostnamectl -H root@192.168.1.10 set-hostname nouveau-nom

# Dans un conteneur
hostnamectl -M monconteneur status
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--static` | Opérer sur le nom statique |
| `--transient` | Opérer sur le nom transitoire |
| `--pretty` | Opérer sur le nom joli |
| `-H <hôte>` | Hôte distant (via SSH) |
| `-M <machine>` | Machine / conteneur systemd-nspawn |
| `--no-ask-password` | Ne pas demander le mot de passe polkit |
| `--json=short` | Sortie JSON compacte |
| `--json=pretty` | Sortie JSON formatée |

## Voir aussi

- [localectl](localectl.md) — configuration locale et clavier
- `man hostnamectl`
- `man hostname(5)` — format du fichier `/etc/hostname`
- `man machine-info(5)` — format du fichier `/etc/machine-info`
