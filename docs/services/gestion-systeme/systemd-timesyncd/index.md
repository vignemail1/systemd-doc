# systemd-timesyncd

`systemd-timesyncd` est un client SNTP léger intégré à systemd. Il synchronise l'horloge système avec des serveurs configurés globalement ou annoncés par le réseau.

## Activation

```bash
systemctl enable --now systemd-timesyncd
timedatectl status
```

Une seule implémentation NTP doit gérer l'horloge : ne pas exécuter simultanément `chronyd`, `ntpd` et `systemd-timesyncd`.

## Vérification

```bash
timedatectl show-timesync --all
timedatectl timesync-status
timedatectl show -p NTPSynchronized
```

`System clock synchronized: yes` indique que l'horloge a été synchronisée ; cela ne signifie pas nécessairement qu'une source particulière est joignable à chaque instant.

## Fonctionnement

Le service choisit des serveurs globaux, de secours et éventuellement des serveurs fournis par `systemd-networkd`. Il peut synchroniser l'horloge dès que le réseau est disponible.
