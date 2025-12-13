const track = document.getElementById('services-track') as HTMLElement;
const prevBtn = document.getElementById('prev-btn') as HTMLElement;
const nextBtn = document.getElementById('next-btn') as HTMLElement;
const dotsContainer = document.getElementById('carousel-dots') as HTMLElement;

if (track && prevBtn && nextBtn && dotsContainer) {
  const cards = track.children;
  let currentIndex = 0;
  const visibleCards = 2;

  // Get actual card width dynamically
  const getCardWidth = () => {
    if (cards.length > 0) {
      const firstCard = cards[0] as HTMLElement;
      return firstCard.offsetWidth;
    }
    return 320; // fallback
  };

  const getGap = () => {
    const computedStyle = window.getComputedStyle(track);
    const gap = computedStyle.gap || '24px';
    return parseInt(gap);
  };

  const maxIndex = Math.max(0, cards.length - visibleCards);

  // Create 3 dots
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('button');
    dot.className =
      'h-2 w-2 rounded-full transition-all duration-200 ' +
      (i === 0 ? 'bg-primary w-8' : 'bg-gray-600');
    dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
    dot.addEventListener('click', () => goToSlide(i));
    dotsContainer.appendChild(dot);
  }

  function updateCarousel() {
    const cardWidth = getCardWidth();
    const gap = getGap();
    const offset = -(currentIndex * (cardWidth + gap));
    track.style.transform = `translateX(${offset}px)`;

    // Update dots
    const dots = dotsContainer.children;
    for (let i = 0; i < dots.length; i++) {
      if (i === currentIndex) {
        dots[i].className =
          'h-2 w-8 rounded-full bg-primary transition-all duration-200';
      } else {
        dots[i].className =
          'h-2 w-2 rounded-full bg-gray-600 transition-all duration-200';
      }
    }
  }

  function goToSlide(index: number) {
    currentIndex = Math.max(0, Math.min(index, Math.min(maxIndex, 2)));
    updateCarousel();
  }

  prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentIndex < maxIndex) {
      currentIndex++;
      updateCarousel();
    }
  });

  // Touch/Drag functionality
  let isDragging = false;
  let startPos = 0;
  let currentTranslate = 0;
  let prevTranslate = 0;
  let animationID: number;

  // Mouse events
  track.addEventListener('mousedown', dragStart);
  track.addEventListener('mousemove', drag);
  track.addEventListener('mouseup', dragEnd);
  track.addEventListener('mouseleave', dragEnd);

  // Touch events
  track.addEventListener('touchstart', dragStart);
  track.addEventListener('touchmove', drag);
  track.addEventListener('touchend', dragEnd);

  function dragStart(event: MouseEvent | TouchEvent) {
    isDragging = true;
    startPos = getPositionX(event);
    animationID = requestAnimationFrame(animation);
    track.style.cursor = 'grabbing';
  }

  function drag(event: MouseEvent | TouchEvent) {
    if (isDragging) {
      const currentPosition = getPositionX(event);
      currentTranslate = prevTranslate + currentPosition - startPos;
    }
  }

  function dragEnd() {
    if (!isDragging) return;

    isDragging = false;
    cancelAnimationFrame(animationID);
    track.style.cursor = 'grab';

    const movedBy = currentTranslate - prevTranslate;
    const cardWidth = getCardWidth();
    const gap = getGap();

    // Determine if swipe was significant enough
    if (movedBy < -(cardWidth / 4) && currentIndex < maxIndex) {
      currentIndex++;
    } else if (movedBy > cardWidth / 4 && currentIndex > 0) {
      currentIndex--;
    }

    // Reset to proper position
    const offset = -(currentIndex * (cardWidth + gap));
    prevTranslate = offset;
    currentTranslate = offset;

    updateCarousel();
  }

  function getPositionX(event: MouseEvent | TouchEvent): number {
    return event instanceof MouseEvent ? event.pageX : event.touches[0].clientX;
  }

  function animation() {
    if (isDragging) {
      track.style.transform = `translateX(${currentTranslate}px)`;
      requestAnimationFrame(animation);
    }
  }

  // Set initial cursor style
  track.style.cursor = 'grab';

  // Prevent context menu on long press
  track.addEventListener('contextmenu', (e) => {
    e.preventDefault();
  });

  // Prevent text selection while dragging
  track.addEventListener('selectstart', (e) => {
    if (isDragging) e.preventDefault();
  });
}
