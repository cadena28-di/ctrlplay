# Auditoría Chain Industria Agent

**Fecha:** Sat May 23 13:56:09 -05 2026
**Proyecto:** chain_industria_agent
**Directorio esperado:** /home/chainindustria/agents

---

# 1. Resumen inicial

✅ Directorio del proyecto encontrado: /home/chainindustria/agents

# 2. Diagnóstico del sistema


## Usuario actual

```bash
$ whoami
```

```text
chainindustria
```


## Directorio actual

```bash
$ pwd
```

```text
/home/chainindustria/agents
```


## Sistema operativo

```bash
$ uname -a
```

```text
Linux Chainindustria 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun  5 18:30:46 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux
```


## Versión Ubuntu

```bash
$ lsb_release -a || cat /etc/os-release
```

```text
Distributor ID:	Ubuntu
Description:	Ubuntu 24.04.4 LTS
Release:	24.04
Codename:	noble
```


## Fecha del sistema

```bash
$ date
```

```text
Sat May 23 13:56:09 -05 2026
```


## Uso de disco

```bash
$ df -h .
```

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdd       1007G   19G  937G   2% /
```


## Memoria

```bash
$ free -h
```

```text
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       609Mi       3.0Gi       3.5Mi       226Mi       3.1Gi
Swap:          1.0Gi          0B       1.0Gi
```


## IP WSL

```bash
$ hostname -I || true
```

```text
172.26.190.43 
```


# 3. Herramientas instaladas


## Git

```bash
$ git --version || true
```

```text
git version 2.43.0
```


## GitHub CLI

```bash
$ gh --version || true
```

```text
gh version 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu0.3)
https://github.com/cli/cli/releases/tag/v2.45.0
```


## GitHub Auth Status

```bash
$ gh auth status || true
```

```text
You are not logged into any GitHub hosts. To log in, run: gh auth login
```


## Python

```bash
$ python3 --version || true
```

```text
Python 3.12.3
```


## Pip

```bash
$ python3 -m pip --version || true
```

```text
pip 24.0 from /home/chainindustria/agents/chain_industria_agent/.venv/lib/python3.12/site-packages/pip (python 3.12)
```


## Node

```bash
$ node -v || true
```

```text
v24.15.0
```


## NPM

```bash
$ npm -v || true
```

```text
11.12.1
```


## NVM

```bash
$ command -v nvm || true
```

```text
```


## PM2

```bash
$ pm2 -v || true
```

```text
[PM2] Spawning PM2 daemon with pm2_home=/home/chainindustria/.pm2
[PM2] PM2 Successfully daemonized
7.0.1
```


## AgentMemory path

```bash
$ which agentmemory || true
```

```text
/home/chainindustria/.nvm/versions/node/v24.15.0/bin/agentmemory
```


## AgentMemory version

```bash
$ agentmemory --version || true
```

```text
