# Configuration de systemd-timesyncd

## Fichier principal

Configurer `/etc/systemd/timesyncd.conf` ou un fragment dans `/etc/systemd/timesyncd.conf.d/` :

```ini
[Time]
NTP=ntp1.example.net ntp2.example.net
FallbackNTP=time.cloudflare.com time.google.com
RootDistanceMaxSec=5
PollIntervalMinSec=32
PollIntervalMaxSec=2048
ConnectionRetrySec=30
SaveIntervalSec=60
```

- `NTP=` : serveurs prioritaires.
- `FallbackNTP=` : serveurs utilisés sans source spécifique.
- `RootDistanceMaxSec=` : distance maximale acceptée vis-à-vis de la source.
- `PollIntervalMinSec=` et `PollIntervalMaxSec=` : intervalle adaptatif de sondage.
- `SaveIntervalSec=` : fréquence de sauvegarde de l'heure estimée, si prise en charge.

Appliquer :

```bash
systemctl restart systemd-timesyncd
```

## Serveurs par lien

`systemd-networkd` peut annoncer des serveurs NTP via `NTP=` dans `[Network]` :

```ini
[Network]
NTP=192.0.2.123
```

Cette configuration peut être préférée aux serveurs globaux pour un réseau d'entreprise.

## Synchronisation initiale

`timesyncd` corrige progressivement l'horloge. Pour définir immédiatement une heure approximative avant synchronisation :

```bash
timedatectl set-ntp true
```

Ne pas utiliser `date -s` comme mécanisme permanent : corriger la source NTP et la connectivité.
