/**
 * Portal Corporativo Mendonça Galvão Contadores Associados
 * JavaScript principal - Funcionalidades interativas
 * 
 * FUNCIONALIDADES:
 * - FAQ Accordion (expandir/colapsar perguntas)
 * - Smooth scroll (se necessário)
 * - Animações de entrada
 */

// ========================================
// FAQ ACCORDION
// ========================================

/**
 * Inicializa o accordion do FAQ
 * Permite expandir/colapsar as respostas ao clicar nas perguntas
 */
function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const pergunta = item.querySelector('.faq-pergunta');

        pergunta.addEventListener('click', () => {
            // Toggle da classe 'active' no item clicado
            const isActive = item.classList.contains('active');

            // Opcional: Fechar outros itens ao abrir um novo (accordion exclusivo)
            // Comente as 3 linhas abaixo se quiser permitir múltiplos itens abertos
            faqItems.forEach(otherItem => {
                otherItem.classList.remove('active');
            });

            // Toggle do item atual
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });
}

// ========================================
// ANIMAÇÕES DE ENTRADA
// ========================================

/**
 * Adiciona animações de fade-in aos elementos quando entram no viewport
 * Usa Intersection Observer API para performance otimizada
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target); // Para de observar após animar
            }
        });
    }, observerOptions);

    // Observar cards de sistemas
    const cards = document.querySelectorAll('.sistema-card');
    cards.forEach(card => observer.observe(card));

    // Observar seção Núcleo Digital
    const nucleoSection = document.querySelector('.nucleo-container');
    if (nucleoSection) {
        observer.observe(nucleoSection);
    }
}

// ========================================
// LINKS EXTERNOS
// ========================================

/**
 * Adiciona atributos de segurança a todos os links externos
 * Previne vulnerabilidades de segurança ao abrir em nova aba
 */
function secureExternalLinks() {
    const externalLinks = document.querySelectorAll('a[target="_blank"]');

    externalLinks.forEach(link => {
        // Adiciona rel="noopener noreferrer" para segurança
        if (!link.hasAttribute('rel')) {
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
}

// ========================================
// INICIALIZAÇÃO
// ========================================

/**
 * Executa todas as inicializações quando o DOM estiver pronto
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Portal MG - Inicializando...');

    // Inicializar funcionalidades
    initFaqAccordion();
    initScrollAnimations();
    secureExternalLinks();

    console.log('Portal MG - Pronto!');
});

// ========================================
// UTILITÁRIOS
// ========================================

/**
 * Smooth scroll para âncoras (se necessário no futuro)
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}
