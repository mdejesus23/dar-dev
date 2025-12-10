const faqToggles = document.querySelectorAll('.faq-toggle');

faqToggles.forEach((toggle) => {
  toggle.addEventListener('click', () => {
    const faqItem = toggle.closest('.faq-item');
    const answer = faqItem?.querySelector('.faq-answer');
    const arrow = faqItem?.querySelector('.faq-arrow');
    const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

    // Toggle current item
    if (answer && arrow) {
      if (isExpanded) {
        // Close
        answer.classList.remove('grid-rows-[1fr]');
        answer.classList.add('grid-rows-[0fr]');
        arrow.classList.remove('rotate-90');
        toggle.setAttribute('aria-expanded', 'false');
      } else {
        // Open
        answer.classList.remove('grid-rows-[0fr]');
        answer.classList.add('grid-rows-[1fr]');
        arrow.classList.add('rotate-90');
        toggle.setAttribute('aria-expanded', 'true');
      }
    }
  });
});
