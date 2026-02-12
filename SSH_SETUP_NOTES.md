# SSH + iPhone Remote Access Setup (Completed)

## What was set up
- **OpenSSH Server** on Windows 11 — running, auto-start on boot
- **Firewall rule** for port 22 (inbound TCP)
- **Claude Code v2.1.39** installed in WSL Ubuntu (`~/.local/bin/claude`)
- **tmux 3.4** available in WSL
- **VS Code** WSL extension + Claude Code extension already installed

## Your PC's local IP
192.168.1.184

## iPhone Setup (Termius)
1. Install Termius from App Store
2. New Host → Hostname: `192.168.1.184`, Username: `jcerv`, Password: your Windows password
3. Connect

## Once connected from iPhone
```bash
wsl -d Ubuntu
cd /mnt/c/Users/jcerv/Jose/sponsorship-network
tmux new -s claude
claude
```

## Reconnecting to an existing session
```bash
wsl -d Ubuntu
tmux attach -t claude
```

## tmux cheat sheet
- Detach (keep session alive): Ctrl+B then D
- Reattach: `tmux attach -t claude`
- Scroll up: Ctrl+B then [ then swipe/arrow up
- Exit scroll: q

## VS Code WSL workflow
- Ctrl+Shift+P → "WSL: Open Folder in WSL" → /mnt/c/Users/jcerv/Jose/sponsorship-network
- Integrated terminal = Linux bash, `claude` and `tmux` work directly

## Still TODO
- [x] Set up convenience aliases in WSL ~/.bashrc
- [x] Test SSH connection from iPhone with Termius
