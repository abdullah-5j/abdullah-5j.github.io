# verox — Cybersecurity Writeups & Thoughts

A responsive, dark/light-mode cybersecurity writeups + thoughts blog inspired by the familiar Jekyll Chirpy layout. This is an original static implementation, not a copy of TheCyberSimon's writing or assets.

## Preview locally

1. Open `index.html` in a modern browser, OR
2. In this folder run `python -m http.server 8000`, then open `http://localhost:8000`.

All pages work without a server or external CSS/JS CDNs.

## Change profile and accounts

Open `build.py` and edit the `SITE` dictionary near the top. Replace `assets/avatar.jpg` with another image if wanted. Your avatar is the provided uploaded image.

The contact information provided for this starter is PUBLICLY visible on the About page. Remove the email or Discord username if you don't want it public.

## Publish new posts

1. Add a Markdown file in `posts/` (e.g., `my-new-writeup.md`).
2. Add a corresponding entry in the `posts` list in `build.py`: `slug`, `title`, `date`, `category`, `tags`, `summary`, `read`, `kind` (`writeups` or `thoughts`), and `file`.
3. Run `python build.py` (requires Python and the `mistune` package: `pip install mistune`).
4. Commit the generated HTML and assets.

Remove the sample articles by removing their entries in the `posts` list. The welcome post is a starter post that you can personalize.

## Host for free on GitHub Pages

The simplest option: create a new public GitHub repo named `abdullah-5j.github.io`, upload the files in this folder (including generated HTML, assets, and posts), then enable GitHub Pages: **Settings → Pages → Deploy from a branch → main / (root)**. The public site becomes `https://abdullah-5j.github.io/` (the exact address depends on your repo name and GitHub Pages settings).

For a different repository name the site can still work under a subpath because all assets and internal links are relative. 

## Notes

- Search searches titles, categories, summaries, and tags (not article body text).
- This is a standalone static site, not the original Jekyll Chirpy theme.
- No external services, tracking pixels or analytics are enabled.
- The GitHub link is prefilled from previous context; verify that this is the right GitHub profile before publishing.

## Custom domain setup (GitHub Pages)

**The preferred domain is verox.com, but it has not been purchased or connected.** The website works without one; do not add a placeholder `CNAME` file.

1. Buy or use a domain you own, such as `yourdomain.com`.
2. Publish the site to a GitHub Pages repository (instructions above).
3. At **Settings → Pages → Custom domain**, enter the actual domain and save it.
4. In your domain registrar's DNS settings, set records according to GitHub's official guide: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site . For a `www` subdomain, use a CNAME pointing to your GitHub Pages host (your GitHub username followed by `.github.io`), not to this project's repository URL. For an apex/root domain, use GitHub Pages' documented A/AAAA records.
5. Wait for DNS verification and enable **Enforce HTTPS** when available.
6. GitHub Pages can manage a `CNAME` file for branch-based deployment. If you add one manually, it should contain **only your actual domain**, on one line.

## Finalized profile

- Public display name/site title: `verox`
- Avatar: your provided Hacker Pepe image
- Discord: `notabdu11ah`
- Email: `abdullah5j009@gmail.com`
- X: https://x.com/abdullah5j009
- TryHackMe: https://tryhackme.com/p/Verox.
- Hack The Box: https://app.hackthebox.com/users/2654143
- GitHub: prefilled; verify account ownership before publishing

This design takes inspiration from the Chirpy-style layout but is not the original theme or an identical reproduction.
