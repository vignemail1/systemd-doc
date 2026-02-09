# Versions systemd

Ce document récapitule les versions minimales de systemd nécessaires pour chaque fonctionnalité documentée.

## Vérifier votre version

```bash
systemctl --version
# Ou
systemd --version
```

## Services

### Type de service

| Option | Version | Notes |
| -------- | --------- | ------- |
| `Type=simple` | systemd 1+ | Toutes versions |
| `Type=forking` | systemd 1+ | Toutes versions |
| `Type=oneshot` | systemd 1+ | Toutes versions |
| `Type=notify` | systemd 1+ | Toutes versions |
| `Type=dbus` | systemd 1+ | Toutes versions |
| `Type=idle` | systemd 189+ | |
| `Type=notify-reload` | systemd 249+ | Notification lors du reload |
| `Type=exec` | systemd 240+ | Attend après execve() |

### Options de sécurité

| Option | Version | Notes |
| -------- | --------- | ------- |
| `NoNewPrivileges=` | systemd 187+ | |
| `PrivateTmp=` | systemd 183+ | |
| `PrivateDevices=` | systemd 186+ | |
| `PrivateNetwork=` | systemd 186+ | |
| `ProtectSystem=` | systemd 214+ | |
| `ProtectHome=` | systemd 214+ | |
| `ReadOnlyPaths=` | systemd 214+ | |
| `ReadWritePaths=` | systemd 214+ | |
| `InaccessiblePaths=` | systemd 214+ | |
| `ProtectKernelTunables=` | systemd 232+ | |
| `ProtectKernelModules=` | systemd 232+ | |
| `ProtectControlGroups=` | systemd 232+ | |
| `ProtectKernelLogs=` | systemd 244+ | |
| `ProtectHostname=` | systemd 242+ | |
| `ProtectClock=` | systemd 245+ | |
| `ProtectProc=` | systemd 247+ | Nécessite Linux 5.8+ |
| `ProcSubset=` | systemd 247+ | Nécessite Linux 5.8+ |
| `PrivateUsers=` | systemd 232+ | |
| `PrivateIPC=` | systemd 232+ | |
| `DynamicUser=` | systemd 232+ | |
| `StateDirectory=` | systemd 235+ | |
| `CacheDirectory=` | systemd 235+ | |
| `LogsDirectory=` | systemd 235+ | |
| `ConfigurationDirectory=` | systemd 235+ | |
| `RuntimeDirectory=` | systemd 211+ | |

### Limitations ressources

| Option | Version | Notes |
| -------- | --------- | ------- |
| `MemoryLimit=` | systemd 208+ | Obsolète, utiliser MemoryMax |
| `MemoryMax=` | systemd 231+ | Nécessite cgroups v2 |
| `MemoryHigh=` | systemd 231+ | Nécessite cgroups v2 |
| `MemoryMin=` | systemd 240+ | Nécessite cgroups v2 |
| `MemoryLow=` | systemd 231+ | Nécessite cgroups v2 |
| `MemorySwapMax=` | systemd 232+ | Nécessite cgroups v2 |
| `CPUQuota=` | systemd 213+ | |
| `CPUWeight=` | systemd 232+ | Nécessite cgroups v2 |
| `CPUShares=` | systemd 208+ | Obsolète (cgroups v1) |
| `TasksMax=` | systemd 227+ | |
| `IOWeight=` | systemd 232+ | Nécessite cgroups v2 |
| `IOReadBandwidthMax=` | systemd 232+ | Nécessite cgroups v2 |
| `IOWriteBandwidthMax=` | systemd 232+ | Nécessite cgroups v2 |
| `IOReadIOPSMax=` | systemd 232+ | Nécessite cgroups v2 |
| `IOWriteIOPSMax=` | systemd 232+ | Nécessite cgroups v2 |

### Réseau

| Option | Version | Notes |
| -------- | --------- | ------- |
| `RestrictAddressFamilies=` | systemd 211+ | |
| `IPAccounting=` | systemd 235+ | Nécessite cgroups v2 |
| `IPAddressAllow=` | systemd 239+ | Nécessite cgroups v2 |
| `IPAddressDeny=` | systemd 239+ | Nécessite cgroups v2 |

### Seccomp

| Option | Version | Notes |
| -------- | --------- | ------- |
| `SystemCallFilter=` | systemd 187+ | |
| `SystemCallErrorNumber=` | systemd 209+ | |
| `SystemCallArchitectures=` | systemd 209+ | |
| `SystemCallLog=` | systemd 247+ | |

### Restrictions

| Option | Version | Notes |
| -------- | --------- | ------- |
| `LockPersonality=` | systemd 232+ | |
| `MemoryDenyWriteExecute=` | systemd 231+ | |
| `RestrictRealtime=` | systemd 231+ | |
| `RestrictSUIDSGID=` | systemd 242+ | |
| `RestrictNamespaces=` | systemd 233+ | |

### Capabilities

| Option | Version | Notes |
| -------- | --------- | ------- |
| `CapabilityBoundingSet=` | systemd 187+ | |
| `AmbientCapabilities=` | systemd 229+ | Nécessite Linux 4.3+ |

## Timers

| Option | Version | Notes |
| -------- | --------- | ------- |
| `OnCalendar=` | systemd 197+ | |
| `OnBootSec=` | systemd 197+ | |
| `OnStartupSec=` | systemd 197+ | |
| `OnUnitActiveSec=` | systemd 197+ | |
| `OnUnitInactiveSec=` | systemd 197+ | |
| `Persistent=` | systemd 212+ | |
| `RandomizedDelaySec=` | systemd 229+ | |
| `FixedRandomDelay=` | systemd 247+ | |
| `OnClockChange=` | systemd 242+ | |
| `OnTimezoneChange=` | systemd 242+ | |

## Sockets

| Option | Version | Notes |
| -------- | --------- | ------- |
| `ListenStream=` | systemd 1+ | |
| `ListenDatagram=` | systemd 1+ | |
| `ListenSequentialPacket=` | systemd 1+ | |
| `ListenFIFO=` | systemd 1+ | |
| `ListenNetlink=` | systemd 1+ | |
| `Accept=` | systemd 1+ | |
| `MaxConnections=` | systemd 1+ | |
| `SocketUser=` | systemd 206+ | |
| `SocketGroup=` | systemd 206+ | |
| `TriggerLimitBurst=` | systemd 230+ | |
| `TriggerLimitIntervalSec=` | systemd 230+ | |

## Mount

| Option | Version | Notes |
| -------- | --------- | ------- |
| `What=` | systemd 1+ | |
| `Where=` | systemd 1+ | |
| `Type=` | systemd 1+ | |
| `Options=` | systemd 1+ | |
| `TimeoutSec=` | systemd 1+ | |
| `DirectoryMode=` | systemd 1+ | |
| `SloppyOptions=` | systemd 215+ | |

## Path

| Option | Version | Notes |
| -------- | --------- | ------- |
| `PathExists=` | systemd 1+ | |
| `PathExistsGlob=` | systemd 1+ | |
| `PathChanged=` | systemd 1+ | |
| `PathModified=` | systemd 1+ | |
| `DirectoryNotEmpty=` | systemd 1+ | |
| `MakeDirectory=` | systemd 1+ | |
| `DirectoryMode=` | systemd 1+ | |
| `TriggerLimitBurst=` | systemd 230+ | |
| `TriggerLimitIntervalSec=` | systemd 230+ | |

## Slices et Cgroups

| Option | Version | Cgroups |
| -------- | --------- | ---------- |
| `CPUAccounting=` | systemd 208+ | v1 et v2 |
| `MemoryAccounting=` | systemd 208+ | v1 et v2 |
| `TasksAccounting=` | systemd 227+ | v2 |
| `IOAccounting=` | systemd 232+ | v2 |
| `IPAccounting=` | systemd 235+ | v2 |

## Journal

| Option | Version | Notes |
| -------- | --------- | ------- |
| `Storage=` | systemd 1+ | |
| `Compress=` | systemd 1+ | |
| `Seal=` | systemd 189+ | |
| `SystemMaxUse=` | systemd 1+ | |
| `ForwardToSyslog=` | systemd 1+ | |
| `MaxLevelStore=` | systemd 232+ | |
| `MaxRetentionSec=` | systemd 1+ | |
| `MaxFileSec=` | systemd 1+ | |
| `RateLimitIntervalSec=` | systemd 1+ | |
| `RateLimitBurst=` | systemd 1+ | |

## Commandes journalctl

| Option | Version | Notes |
| -------- | --------- | ------- |
| `journalctl` | systemd 1+ | |
| `--since` / `--until` | systemd 1+ | |
| `--vacuum-time` | systemd 218+ | |
| `--vacuum-size` | systemd 218+ | |
| `--vacuum-files` | systemd 233+ | |
| `--rotate` | systemd 227+ | |
| `--verify` | systemd 189+ | |
| `--disk-usage` | systemd 1+ | |
| `--list-boots` | systemd 1+ | |
| `-o json` | systemd 1+ | |
| `-o json-pretty` | systemd 1+ | |
| `--grep` | systemd 237+ | |
| `--case-sensitive` | systemd 237+ | |

## Logind

| Option | Version | Notes |
| -------- | --------- | ------- |
| `UserTasksMax=` | systemd 230+ | |
| `KillUserProcesses=` | systemd 230+ | |
| `KillOnlyUsers=` | systemd 230+ | |
| `KillExcludeUsers=` | systemd 230+ | |
| `InhibitDelayMaxSec=` | systemd 183+ | |
| `HandlePowerKey=` | systemd 1+ | |
| `HandleSuspendKey=` | systemd 1+ | |
| `HandleHibernateKey=` | systemd 1+ | |
| `HandleLidSwitch=` | systemd 1+ | |
| `IdleAction=` | systemd 198+ | |
| `IdleActionSec=` | systemd 198+ | |

## Networkd

| Option | Version | Notes |
| -------- | --------- | ------- |
| `[Match]` | systemd 210+ | |
| `[Network]` | systemd 210+ | |
| `[Address]` | systemd 210+ | |
| `[Route]` | systemd 210+ | |
| `DHCP=` | systemd 210+ | |
| `VLAN=` | systemd 210+ | |
| `Bridge=` | systemd 210+ | |
| `Bond=` | systemd 216+ | |
| `IPv6AcceptRA=` | systemd 218+ | |
| `LLDP=` | systemd 219+ | |
| `DHCPv6=` | systemd 221+ | |

## Resolved

| Option | Version | Notes |
| -------- | --------- | ------- |
| `DNS=` | systemd 216+ | |
| `FallbackDNS=` | systemd 216+ | |
| `Domains=` | systemd 216+ | |
| `LLMNR=` | systemd 216+ | |
| `MulticastDNS=` | systemd 231+ | |
| `DNSSEC=` | systemd 229+ | |
| `DNSOverTLS=` | systemd 239+ | |
| `Cache=` | systemd 231+ | |
| `CacheFromLocalhost=` | systemd 250+ | |

## Versions majeures

### systemd 250+ (2021)

- Support cgroups v2 complet
- Améliorations sécurité
- Nouveaux types de service
- Meilleur support conteneurs

### systemd 247+ (2020)

- `ProtectProc=`, `ProcSubset=`
- `FixedRandomDelay=` pour timers
- `SystemCallLog=`
- Améliorations slices

### systemd 240+ (2019)

- `Type=exec`
- `MemoryMin=`
- Améliorations networkd

### systemd 235+ (2018)

- Directories gérés (StateDirectory, etc.)
- IPAccounting
- Améliorations journal

### systemd 232+ (2017)

- Cgroups v2 support initial
- MemoryMax, CPUWeight, IOWeight
- DynamicUser
- Protection noyau avancée

### systemd 230+ (2016)

- UserTasksMax
- TriggerLimit pour sockets/paths
- Améliorations logind

## Distributions et versions

| Distribution | Version systemd | Sortie |
| -------------- | ----------------- | -------- |
| **RHEL / CentOS** | | |
| RHEL 9 / Rocky 9 | 250+ | 2022 |
| RHEL 8 / Rocky 8 | 239 | 2019 |
| CentOS 7 | 219 | 2015 |
| **Debian** | | |
| Debian 12 (Bookworm) | 252 | 2023 |
| Debian 11 (Bullseye) | 247 | 2021 |
| Debian 10 (Buster) | 241 | 2019 |
| **Ubuntu** | | |
| Ubuntu 24.04 LTS | 255 | 2024 |
| Ubuntu 22.04 LTS | 249 | 2022 |
| Ubuntu 20.04 LTS | 245 | 2020 |
| Ubuntu 18.04 LTS | 237 | 2018 |
| **Fedora** | | |
| Fedora 40 | 255 | 2024 |
| Fedora 38 | 253 | 2023 |
| Fedora 36 | 250 | 2022 |
| **Arch Linux** | | |
| Arch Linux | Toujours la dernière | Rolling |
| **openSUSE** | | |
| Leap 15.5 | 249 | 2023 |
| Tumbleweed | Toujours la dernière | Rolling |

## Compatibilité cgroups

Beaucoup de fonctionnalités modernes nécessitent **cgroups v2** :

- MemoryMax, MemoryHigh, MemoryMin, MemoryLow, MemorySwapMax
- CPUWeight, IOWeight
- IOReadBandwidthMax, IOWriteBandwidthMax
- IPAccounting, IPAddressAllow, IPAddressDeny

Vérifier la version cgroups :

```bash
stat -fc %T /sys/fs/cgroup/
# cgroup2fs = cgroups v2 (unified)
# tmpfs = cgroups v1 (legacy)
```

Activer cgroups v2 (si supporté) :

```bash
# Ajouter au kernel cmdline
systemd.unified_cgroup_hierarchy=1

# Ou
cgroup_no_v1=all
```

## Références

- [systemd NEWS](https://github.com/systemd/systemd/blob/main/NEWS) : Changelog officiel
- [systemd Release Notes](https://www.freedesktop.org/wiki/Software/systemd/) : Notes de versions
- [Arch Wiki - systemd](https://wiki.archlinux.org/title/Systemd) : Documentation version

Pour toute fonctionnalité non listée, consulter `man systemd.directives` ou la documentation officielle.
