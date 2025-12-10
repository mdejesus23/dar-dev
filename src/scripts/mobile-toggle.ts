// Mobile menu toggle
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenuClose = document.getElementById('mobile-menu-close');
const mobileMenu = document.getElementById('mobile-menu');

mobileMenuButton?.addEventListener('click', () => {
  mobileMenu?.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
});

mobileMenuClose?.addEventListener('click', () => {
  mobileMenu?.classList.add('hidden');
  document.body.style.overflow = '';
});

// Close menu when clicking on a link
const mobileMenuLinks = mobileMenu?.querySelectorAll('a');
mobileMenuLinks?.forEach((link) => {
  link.addEventListener('click', () => {
    mobileMenu?.classList.add('hidden');
    document.body.style.overflow = '';
  });
});
