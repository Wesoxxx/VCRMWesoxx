# Déploiement 100% gratuit (PC éteint) – Vinted CRM + Scraper

## Vue d'ensemble
- **Scraping automatique** toutes les 30 minutes via **GitHub Actions (cron)**.
- **Stockage**: **Supabase** (PostgreSQL) **Free tier**.
- **Interface**: **Streamlit Community Cloud** (gratuit) connecté à Supabase.
- Aucun serveur à payer. Secrets gardés dans GitHub/Streamlit.

---

## Étape 1 — Créer la base Supabase (gratuite)
1. Ouvre https://supabase.com/ et crée un projet **Free**.
2. Va dans **SQL Editor** et exécute le contenu de `supabase_schema.sql` pour créer la table `items`.
3. Récupère :
   - **Project URL** → `SUPABASE_URL`
   - **Service role key** → `SUPABASE_SERVICE_ROLE_KEY` (clé secrète côté serveur)

---

## Étape 2 — Préparer le dépôt GitHub public
1. Crée un repo **public**.
2. Ajoute ces fichiers à la racine (y compris `.github/workflows/scrape.yml`).
3. Dans **Settings → Secrets and variables → Actions**, ajoute :
   - `PROFILE_URL` = URL publique de ton profil Vinted
   - `MAX_PAGES` = `5` (exemple)
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
4. `git add . && git commit -m "cron + scraper" && git push`

Le workflow tourne toutes les **30 min** et remplit la table `items`.

---

## Étape 3 — Déployer l’UI sur Streamlit Cloud
1. Relie ton repo à Streamlit Cloud.
2. Fichier d’app : `streamlit_app_supabase.py`
3. Dans **Secrets**, ajoute `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY`.
4. Déploie.

---

## Tests locaux
```bash
pip install -r requirements.txt
python -m playwright install --with-deps firefox
export PROFILE_URL="https://www.vinted.fr/member/xxx"
export SUPABASE_URL="..."
export SUPABASE_SERVICE_ROLE_KEY="..."
python cron_scrape.py
```
