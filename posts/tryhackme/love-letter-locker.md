---
title: "Love Letter Locker"
section: tryhackme
date: "2026-08-12T19:28:48+05:00"
summary: "An insecure direct object reference exposes another user’s private letter—and the flag—by changing its numeric ID."
tags: ["tryhackme", "love-at-first-breach", "idor", "access-control", "web-security"]
image: "/assets/images/tryhackme/love-letter-locker/banner-love-letter-locker.png"
---
**Room:** [Love at First Breach 2026 – Love Letter Locker](https://tryhackme.com/room/lafb2026e2)

An IDOR vulnerability that lets you read other users' private love letters just by changing a number in the URL.

![Love Letter Locker banner](/assets/images/tryhackme/love-letter-locker/banner-love-letter-locker.png)

---

## Recon

Let's do an nmap scan on the target IP:

```
nmap -sC -sV -p- -T4 10.112.137.43
```

![Nmap scan](/assets/images/tryhackme/love-letter-locker/02-nmap-scan.png)

After doing the nmap scan I found 2 open ports which are:

- **22/tcp** — SSH
- **5000/tcp** — HTTP

---

## Exploring the Web App

Let's check port 5000 and see what we can do there.

![Port 5000 homepage](/assets/images/tryhackme/love-letter-locker/03-port-5000-homepage.png)

Make an account here and check what we see.

![Account created](/assets/images/tryhackme/love-letter-locker/04-account-created.png)

After login we can see that there is a **Tip from Cupid** that says:

> "Every love letter gets a unique number in the archive. Numbers make everything easier to find."

That's a good hint as it tells about the IDOR vulnerability. Let's check where it actually is.

![My Letters - Tip from Cupid](/assets/images/tryhackme/love-letter-locker/05-my-letters-cupid-tip.png)

---

## Finding the IDOR

I write a letter just to check what we get from it.

![Write a love letter](/assets/images/tryhackme/love-letter-locker/06-write-love-letter.png)

Once the letter is saved, I open it and look at the URL it contains the number **3**.

```
http://10.112.137.43:5000/letter/3
```

![Letter with ID in URL](/assets/images/tryhackme/love-letter-locker/07-letter-id-in-url.png)

Let's try to change it and check what happens.

When I change the ID to **1**, it gives us the flag meaning letter #1 belongs to another user, and there is no access control checking whether the logged-in user actually owns that letter ID.

```
http://10.112.137.43:5000/letter/1
```

![IDOR - flag in another user's letter](/assets/images/tryhackme/love-letter-locker/08-idor-flag.png)

Letter #1 turns out to belong to another user ("Gonz0") titled *"To my secret Valentine"* and it contains the flag directly in the message body.

---

## Flag

```
THM{1_c4n_r3ad_4ll_l3tters_w1th_th1s_1d0r}
```

---
