document.addEventListener('DOMContentLoaded', () => {
    const faqQuestions = document.querySelectorAll('.faq-question');

    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const item = question.parentNode;
            const answer = item.querySelector('.faq-answer');
            const willOpen = !item.classList.contains('active');

            // Fecha todos os painéis antes de abrir o clicado
            faqQuestions.forEach(otherQuestion => {
                const otherItem = otherQuestion.parentNode;
                otherItem.classList.remove('active');
                otherItem.querySelector('.faq-answer').style.maxHeight = null;
            });

            if (willOpen) {
                item.classList.add('active');
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });
    });

    // Ao girar o celular ou redimensionar, o texto muda de altura.
    // Sem isso o painel aberto fica cortado no mobile.
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            document.querySelectorAll('.faq-item.active .faq-answer').forEach(answer => {
                answer.style.maxHeight = 'none';
                const height = answer.scrollHeight;
                answer.style.maxHeight = height + 'px';
            });
        }, 150);
    });
});
