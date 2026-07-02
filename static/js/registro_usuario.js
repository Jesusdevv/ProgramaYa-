document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', () => {
        input.parentElement.classList.add('scale-[1.01]');
    });
    input.addEventListener('blur', () => {
        input.parentElement.classList.remove('scale-[1.01]');
    });
});

const btn = document.querySelector('button[type="submit"]');
btn.addEventListener('mousedown', () => {
    btn.classList.add('opacity-90');
});
btn.addEventListener('mouseup', () => {
    btn.classList.remove('opacity-90');
});
