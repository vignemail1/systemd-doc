# Configuration de systemd-logind

## Fichier de configuration

Le fichier principal est `/etc/systemd/logind.conf`. Les fragments locaux sont placés dans `/etc/systemd/logind.conf.d/`.

```ini
[Login]
NAutoVTs=6
ReserveVT=6
KillUserProcesses=no
KillExcludeUsers=root
IdleAction=ignore
HandlePowerKey=poweroff
HandleSuspendKey=suspend
HandleHibernateKey=hibernate
HandleLidSwitch=suspend
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
PowerKeyIgnoreInhibited=no
LidSwitchIgnoreInhibited=yes
```

Options courantes :

- `KillUserProcesses=` : terminer ou non les processus à la fermeture de session.
- `KillExcludeUsers=` : exceptions à cette règle.
- `IdleAction=` et `IdleActionSec=` : action après inactivité.
- `HandlePowerKey=`, `HandleSuspendKey=`, `HandleLidSwitch=` : actions matérielles.
- `InhibitDelayMaxSec=` : durée maximale des inhibitions retardées.
- `UserTasksMax=` : limite de tâches par utilisateur.

Les valeurs acceptées pour les actions incluent `ignore`, `poweroff`, `reboot`, `suspend`, `hibernate`, `lock` et `hybrid-sleep` selon l'option.

Appliquer la configuration :

```bash
systemctl restart systemd-logind
```

Un redémarrage peut fermer des sessions ; effectuer l'opération depuis une console de maintenance si nécessaire.

## Polkit et inhibiteurs

Les autorisations d'actions d'alimentation dépendent aussi de polkit. Inspecter les inhibiteurs :

```bash
loginctl list-inhibitors
```

Un inhibiteur peut expliquer pourquoi une action est ignorée ou retardée.
