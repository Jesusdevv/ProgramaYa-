const courseCard = document.querySelector('.glass-card .bg-primary')?.closest('.glass-card');
const progressBar = courseCard ? courseCard.querySelector('.bg-primary') : null;

if (courseCard && progressBar) {
    courseCard.addEventListener('mouseenter', () => {
        progressBar.style.width = '10%';
        progressBar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
    });
    courseCard.addEventListener('mouseleave', () => {
        progressBar.style.width = '0%';
    });
}
