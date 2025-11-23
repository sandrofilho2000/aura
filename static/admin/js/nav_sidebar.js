'use strict';
{
    function fixBreadcrumb() {
    const bc = document.querySelector('.breadcrumbs');
    if (!bc) return { ok: false, reason: 'no-breadcrumb' };

    // Normaliza texto: remove acentos, trim e lowercase
    const normalize = s =>
        String(s || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/›/g, '')
        .replace(/>/g, '')
        .trim()
        .toLowerCase();

    // Extrai tokens em ordem: ELEMENTS (<a>, <span>, etc.) ou TEXTS úteis (removendo '›')
    const tokens = [];
    for (const node of Array.from(bc.childNodes)) {
        if (node.nodeType === 1) { // ELEMENT_NODE
        // apenas elementos visíveis (links e spans normalmente)
        tokens.push({ kind: 'element', node });
        } else if (node.nodeType === 3) { // TEXT_NODE
        const cleaned = node.nodeValue.replace(/›/g, '').replace(/>/g, '').trim();
        if (cleaned.length > 0) {
            tokens.push({ kind: 'text', text: cleaned });
        }
        }
        // ignora outros tipos de nó
    }

    // Se não tem pelo menos 3 tokens (Home, app, model) nada a fazer
    if (tokens.length < 3) return { ok: true, changed: false, reason: 'not-enough-tokens' };

    // Transforma token em texto para comparação
    const tokenText = t => t.kind === 'element' ? (t.node.textContent || '') : (t.text || '');

    // Procura o primeiro par adjacente duplicado e remove o primeiro do par (o "app")
    let removed = false;
    for (let i = 0; i < tokens.length - 1; i++) {
        const t1 = normalize(tokenText(tokens[i]));
        const t2 = normalize(tokenText(tokens[i + 1]));
        if (t1 && t2 && t1 === t2) {
        // remove o token i (não o i+1)
        tokens.splice(i, 1);
        removed = true;
        break;
        }
    }

    if (!removed) return { ok: true, changed: false, reason: 'no-duplicate-found' };

    // Reconstrói o conteúdo do breadcrumb, preservando elementos originais quando existirem.
    // Limpamos tudo e recriamos: elemento/texto › elemento/texto ...
    bc.innerHTML = '';

    tokens.forEach((t, idx) => {
        if (t.kind === 'element') {
        // se o elemento já existe no DOM, ao appendChild ele será movido aqui (ok)
        bc.appendChild(t.node);
        } else {
        const span = document.createElement('span');
        span.textContent = t.text;
        bc.appendChild(span);
        }

        if (idx < tokens.length - 1) {
        bc.appendChild(document.createTextNode(' › '));
        }
    });

    return { ok: true, changed: true };
    }
    
    document.addEventListener("DOMContentLoaded", () => {
        fixBreadcrumb()
    });
    const toggleNavSidebar = document.querySelector('.menu-toggle-btn svg');
    if (toggleNavSidebar !== null) {
        const navSidebar = document.getElementById('nav-sidebar');
        const main = document.getElementById('main');
        let navSidebarIsOpen = 'false';
        if (navSidebarIsOpen === null) {
            navSidebarIsOpen = 'true';
        }
        main.classList.toggle('shifted', navSidebarIsOpen === 'true');
        navSidebar.setAttribute('aria-expanded', navSidebarIsOpen);

        toggleNavSidebar.addEventListener('click', function () {
            if (navSidebarIsOpen === 'true') {
                navSidebarIsOpen = 'false';
            } else {
                navSidebarIsOpen = 'true';
            }
            localStorage.setItem('django.admin.navSidebarIsOpen', navSidebarIsOpen);
            main.classList.toggle('shifted');
            navSidebar.setAttribute('aria-expanded', navSidebarIsOpen);
        });
    }

    function initSidebarQuickFilter() {
        const options = [];
        const navSidebar = document.getElementById('nav-sidebar');
        if (!navSidebar) {
            return;
        }
        navSidebar.querySelectorAll('th[scope=row] a').forEach((container) => {
            options.push({ title: container.innerHTML, node: container });
        });

        function checkValue(event) {
            let filterValue = event.target.value;
            if (filterValue) {
                filterValue = filterValue.toLowerCase();
            }
            if (event.key === 'Escape') {
                filterValue = '';
                event.target.value = ''; // clear input
            }
            let matches = false;
            for (const o of options) {
                let displayValue = '';
                if (filterValue) {
                    if (o.title.toLowerCase().indexOf(filterValue) === -1) {
                        displayValue = 'none';
                    } else {
                        matches = true;
                    }
                }
                // show/hide parent <TR>
                o.node.parentNode.parentNode.style.display = displayValue;
            }
            if (!filterValue || matches) {
                event.target.classList.remove('no-results');
            } else {
                event.target.classList.add('no-results');
            }
            sessionStorage.setItem('django.admin.navSidebarFilterValue', filterValue);
        }

        const nav = document.getElementById('nav-filter');
        nav.addEventListener('change', checkValue, false);
        nav.addEventListener('input', checkValue, false);
        nav.addEventListener('keyup', checkValue, false);

        const storedValue = sessionStorage.getItem('django.admin.navSidebarFilterValue');
        if (storedValue) {
            nav.value = storedValue;
            checkValue({ target: nav, key: '' });
        }
    }

    document.querySelectorAll("li.has-submenu").forEach((item) => {
        item.addEventListener("click", () => {
            item.classList.toggle("active")
        })
    })

    window.initSidebarQuickFilter = initSidebarQuickFilter;
    initSidebarQuickFilter();
}
function fixBreadcrumb() {
    const bc = document.querySelector(".breadcrumbs");
    if (!bc) return;

    // 1. Limpa separadores soltos (">" ou "›")
    const cleanSeparators = () => {
        [...bc.childNodes].forEach(n => {
            if (n.nodeType === 3) { // texto
                const txt = n.nodeValue.trim();
                if (txt === "›" || txt === ">") {
                    // remove separadores que não estão entre dois elementos válidos
                    const prev = n.previousSibling;
                    const next = n.nextSibling;
                    const prevIsElement = prev && prev.nodeType === 1;
                    const nextIsElement = next && next.nodeType === 1;
                    if (!prevIsElement || !nextIsElement) {
                        n.remove();
                    }
                }
            }
        });
    };

    cleanSeparators();

    // 2. Coleta somente ELEMENTOS (<a> e <span>)
    const elements = [...bc.querySelectorAll("a, span")];

    if (elements.length < 2) return;

    const normalize = s =>
        s.normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "") // remove acentos
            .trim()
            .toLowerCase();

    // 3. Se o penúltimo e o último forem duplicados, remove o penúltimo
    const last = normalize(elements[elements.length - 1].textContent);
    const beforeLast = normalize(elements[elements.length - 2].textContent);

    if (last === beforeLast) {
        elements[elements.length - 2].remove();
    }

    // 4. Depois de remover, limpa separadores soltos novamente
    cleanSeparators();

    // 5. Ajusta para garantir formato correto: elemento › elemento
    const finalElements = [...bc.querySelectorAll("a, span")];

    // remove tudo dentro do breadcrumb
    bc.innerHTML = "";

    // reinsere formatado corretamente
    finalElements.forEach((el, idx) => {
        bc.appendChild(el);
        if (idx < finalElements.length - 1) {
            bc.appendChild(document.createTextNode(" › "));
        }
    });
}

