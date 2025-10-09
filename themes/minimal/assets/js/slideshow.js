let slideIndex = 1;
let slides, dots;

function currentSlide(n) {
    showSlide(slideIndex = n);
}

function showSlide(n) {
    if (!slides) {
        slides = document.querySelectorAll('.slide');
        dots = document.querySelectorAll('.dot');
    }

    if (n > slides.length) { slideIndex = 1; }
    if (n < 1) { slideIndex = slides.length; }

    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    slides[slideIndex - 1].classList.add('active');
    dots[slideIndex - 1].classList.add('active');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    showSlide(slideIndex);
});

// Auto-advance slides every 6 seconds
setInterval(() => {
    if (!slides) return; // Don't run if not initialized
    slideIndex++;
    if (slideIndex > slides.length) slideIndex = 1;
    showSlide(slideIndex);
}, 6000);
