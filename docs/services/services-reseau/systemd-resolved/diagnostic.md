# Diagnostic de systemd-resolved

## Vérifier le service

```bash
systemctl status systemd-resolved
journalctl -u systemd-resolved -b
resolvectl status
```

## Tester une interface ou un serveur

```bash
resolvectl query www.example.org
resolvectl query --legend=no www.example.org
resolvectl dns
resolvectl domain
```

## Problèmes fréquents

### Aucun serveur DNS

Vérifier `DNS=` dans `resolved.conf`, les paramètres fournis par `networkd` et la connectivité IP. `resolvectl status` indique les liens et leurs DNS actifs.

### `/etc/resolv.conf` incorrect

```bash
readlink -f /etc/resolv.conf
cat /etc/resolv.conf
```

Le fichier doit contenir le stub `127.0.0.53` ou être géré explicitement par un autre résolveur.

### Cache obsolète

```bash
resolvectl flush-caches
resolvectl statistics
```

### Conflit de résolveurs

```bash
ss -lntup | grep ':53'
systemctl --type=service | grep -E 'dnsmasq|named|unbound|resolved'
```

Désactiver ou reconfigurer le service concurrent.
