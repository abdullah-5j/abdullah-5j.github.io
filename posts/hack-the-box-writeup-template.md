> **Template:** Replace this example with your own authorized lab notes. Do not present it as a completed machine.

## Overview

| Field | Value |
| --- | --- |
| Platform | Hack The Box |
| Machine | YOUR_MACHINE_NAME |
| Difficulty | Easy / Medium / Hard |
| OS | Linux / Windows |

## Enumeration

Start by recording the host and services that you are authorized to assess.

```bash
nmap -sC -sV -oN scans/initial.txt TARGET_IP
```

Explain **what the output revealed** and why it matters. Avoid pasting raw output without context.

## Initial foothold

Document the finding, how you validated it, and the sequence of steps you took. Add screenshots where they help.

## Privilege escalation

Describe the misconfiguration or vulnerability and the evidence that led you to it.

## Lessons learned

- What clue mattered most?
- What didn't work?
- What would you do differently next time?

**Reminder:** Only include flags or proof-of-concept details if the platform's rules allow publication.
