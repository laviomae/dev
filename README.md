# Site portfolio — Maëva Laviolette, Photographie

Site statique (HTML/CSS/JS, aucune dépendance à installer) pour présenter tes photos.

## Structure

- `index.html` — le contenu de la page (galerie, à propos, contact)
- `css/style.css` — le style
- `js/script.js` — la galerie, le filtre par catégorie, la visionneuse (lightbox), le menu mobile
- `images/` — dossier où ajouter tes vraies photos

## Personnaliser

### Ajouter tes photos

Le site utilise pour l'instant des visuels de remplacement (placeholders colorés). Pour les remplacer :

1. Ajoute tes fichiers photo dans le dossier `images/` (idéalement compressés, format `.jpg` ou `.webp`, ~1500px de large max pour un chargement rapide).
2. Dans `js/script.js`, modifie le tableau `PHOTOS` en haut du fichier : remplace chaque `src: placeholderImage(...)` par `src: 'images/ton-fichier.jpg'`, et adapte `category` (`portrait`, `paysage`, `urbain`, `nature`) et `caption`.

Exemple :

```js
{ src: 'images/portrait-01.jpg', category: 'portrait', caption: 'Portrait — lumière naturelle' },
```

### Modifier les textes

- Le texte "À propos" est dans `index.html`, section `<section id="about">`.
- L'adresse email et le lien Instagram sont dans la section `<section id="contact">` — remplace `contact@example.com` et le lien `#` par tes vraies coordonnées (l'adresse email doit aussi être mise à jour dans `js/script.js`, fonction du formulaire de contact).

### Couleurs

Les couleurs principales sont définies en haut de `css/style.css` dans `:root` (variables `--color-accent`, `--color-bg`, etc.).

## Voir le site en local

Ouvre simplement `index.html` dans un navigateur, ou lance un petit serveur local :

```bash
python3 -m http.server 8000
```

puis va sur `http://localhost:8000`.

## Héberger le site gratuitement

Le plus simple est **GitHub Pages** :

1. Pousse ce dépôt sur GitHub (déjà fait si tu lis ce README depuis le dépôt).
2. Dans les paramètres du dépôt GitHub → *Pages*, choisis la branche à publier et le dossier `/ (root)`.
3. Le site sera disponible à une adresse du type `https://ton-compte.github.io/nom-du-depot/`.

Alternatives simples : Netlify ou Vercel (glisser-déposer le dossier, ou connecter le dépôt GitHub).
