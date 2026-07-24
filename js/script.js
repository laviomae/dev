// ---------------------------------------------------------------------------
// Photos de la galerie.
// Pour ajouter tes propres photos : place tes fichiers dans le dossier
// "images/", puis remplace le champ "src" ci-dessous par le chemin du fichier
// (ex: "images/portrait-01.jpg"). Le champ "category" doit être l'une de :
// "portrait", "paysage", "urbain", "nature".
// ---------------------------------------------------------------------------
const PHOTOS = [
  { src: placeholderImage('#8f6249', '#d9a679', 'Portrait'), category: 'portrait', caption: 'Portrait — lumière naturelle' },
  { src: placeholderImage('#5c7a6b', '#a9c9b8', 'Paysage'), category: 'paysage', caption: 'Paysage — heure dorée' },
  { src: placeholderImage('#4a5568', '#a0aec0', 'Urbain'), category: 'urbain', caption: 'Urbain — rue et architecture' },
  { src: placeholderImage('#3f6b4f', '#8fbf8f', 'Nature'), category: 'nature', caption: 'Nature — forêt et lumière' },
  { src: placeholderImage('#7a5c47', '#f0c896', 'Portrait'), category: 'portrait', caption: 'Portrait — extérieur' },
  { src: placeholderImage('#6b5b7a', '#c9a9d9', 'Paysage'), category: 'paysage', caption: 'Paysage — montagne' },
  { src: placeholderImage('#2f3b4c', '#7d95b3', 'Urbain'), category: 'urbain', caption: 'Urbain — nuit' },
  { src: placeholderImage('#4f6b3f', '#a3d97a', 'Nature'), category: 'nature', caption: 'Nature — macro' },
  { src: placeholderImage('#8a5a4a', '#e0a98f', 'Portrait'), category: 'portrait', caption: 'Portrait — studio' },
];

// Génère une image placeholder en SVG (à remplacer par de vraies photos).
function placeholderImage(colorA, colorB, label) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="750">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="${colorA}"/>
          <stop offset="100%" stop-color="${colorB}"/>
        </linearGradient>
      </defs>
      <rect width="600" height="750" fill="url(#g)"/>
      <text x="50%" y="52%" font-family="sans-serif" font-size="28" fill="#ffffffcc"
            text-anchor="middle" dominant-baseline="middle">${label}</text>
      <text x="50%" y="58%" font-family="sans-serif" font-size="14" fill="#ffffff99"
            text-anchor="middle" dominant-baseline="middle">Photo à venir</text>
    </svg>`;
  return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
}

const galleryGrid = document.getElementById('galleryGrid');
const filterBtns = document.querySelectorAll('.filter-btn');

function renderGallery() {
  galleryGrid.innerHTML = '';
  PHOTOS.forEach((photo, index) => {
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.dataset.category = photo.category;
    item.dataset.index = index;
    item.innerHTML = `
      <img src="${photo.src}" alt="${photo.caption}" loading="lazy" />
      <div class="caption">${photo.caption}</div>
    `;
    item.addEventListener('click', () => openLightbox(index));
    galleryGrid.appendChild(item);
  });
}

renderGallery();

filterBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    filterBtns.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.gallery-item').forEach((item) => {
      const match = filter === 'all' || item.dataset.category === filter;
      item.classList.toggle('hidden', !match);
    });
  });
});

// Lightbox
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');
let currentIndex = 0;

function openLightbox(index) {
  currentIndex = index;
  updateLightboxImage();
  lightbox.classList.add('open');
}

function updateLightboxImage() {
  const photo = PHOTOS[currentIndex];
  lightboxImg.src = photo.src;
  lightboxImg.alt = photo.caption;
}

function closeLightbox() {
  lightbox.classList.remove('open');
}

document.getElementById('lightboxClose').addEventListener('click', closeLightbox);
document.getElementById('lightboxNext').addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % PHOTOS.length;
  updateLightboxImage();
});
document.getElementById('lightboxPrev').addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + PHOTOS.length) % PHOTOS.length;
  updateLightboxImage();
});
lightbox.addEventListener('click', (e) => {
  if (e.target === lightbox) closeLightbox();
});
document.addEventListener('keydown', (e) => {
  if (!lightbox.classList.contains('open')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowRight') document.getElementById('lightboxNext').click();
  if (e.key === 'ArrowLeft') document.getElementById('lightboxPrev').click();
});

// Mobile nav toggle
const navToggle = document.querySelector('.nav-toggle');
const mainNav = document.querySelector('.main-nav');
navToggle.addEventListener('click', () => {
  const isOpen = mainNav.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', isOpen);
});
mainNav.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => mainNav.classList.remove('open'));
});

// Contact form -> ouvre le client mail avec le message pré-rempli
document.getElementById('contactForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const message = document.getElementById('message').value;
  const subject = encodeURIComponent(`Contact site — ${name}`);
  const body = encodeURIComponent(`${message}\n\n— ${name} (${email})`);
  window.location.href = `mailto:laviolettemaeva.m@gmail.com?subject=${subject}&body=${body}`;
});

// Année dynamique dans le footer
document.getElementById('year').textContent = new Date().getFullYear();
