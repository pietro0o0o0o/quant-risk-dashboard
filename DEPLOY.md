# 🚀 Deploy Guide — step by step

## Prerequisiti
- Account GitHub (gratis): https://github.com
- Account Streamlit Cloud (gratis): https://streamlit.io/cloud
- Python 3.9+ installato

---

## STEP 1 — Crea repo GitHub

1. Vai su https://github.com/new
2. Repository name: `quant-risk-dashboard`
3. Visibility: **Public** (necessario per Streamlit Cloud gratis)
4. Click **Create repository**

---

## STEP 2 — Push dei file

Apri terminale nella cartella del progetto:

```bash
git init
git add .
git commit -m "feat: initial quant risk dashboard"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/quant-risk-dashboard.git
git push -u origin main
```

---

## STEP 3 — Deploy su Streamlit Cloud

1. Vai su https://share.streamlit.io
2. Click **New app**
3. Repository: `TUO_USERNAME/quant-risk-dashboard`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **Deploy**

Dopo ~2 minuti hai URL tipo:
`https://tuo-username-quant-risk-dashboard-app-xxxxx.streamlit.app`

---

## STEP 4 — Abilita GitHub Pages (landing page)

1. Vai su repo GitHub → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Click **Save**

Dopo ~1 minuto hai URL tipo:
`https://tuo-username.github.io/quant-risk-dashboard`

---

## STEP 5 — Collega i link

Aggiorna questi file con i tuoi URL reali:

**README.md** — riga 5:
```
**[🚀 Live Demo](https://TUO-URL.streamlit.app)**
```

**index.html** — riga con "Launch live app":
```html
<a href="https://TUO-URL.streamlit.app" ...>
```

Sostituisci anche `YOUR_USERNAME` e `YOUR_PROFILE` con i tuoi dati reali.

```bash
git add .
git commit -m "chore: update live links"
git push
```

---

## STEP 6 — LinkedIn

1. Vai su profilo LinkedIn → **Featured** → **+** → **Add a link**
2. URL: `https://tuo-username.github.io/quant-risk-dashboard`
3. Title: `Quantitative Risk Dashboard — Live Demo`

---

## Test locale (opzionale)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Apre automaticamente su `http://localhost:8501`
