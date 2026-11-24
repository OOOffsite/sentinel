(() => {
  'use strict';
  const states = {
    observed: {
      value: 'Sampled working',
      explanation: 'A fresh, supported sample can show working activity for a verified seat. It does not establish whether the agent is coding, testing, or reviewing.',
      identity: 'Verified binding',
      freshness: 'Within configured TTL'
    },
    stale: {
      value: 'Current activity unknown',
      explanation: 'A sample past its freshness limit cannot establish current activity. A previous working state remains historical evidence, not a claim about the present.',
      identity: 'Verified binding',
      freshness: 'Past configured TTL'
    },
    unmapped: {
      value: 'Seat identity unknown',
      explanation: 'An observed node without an authoritative binding stays unmapped. A familiar name, list position, or recent timestamp does not establish which declared seat it belongs to.',
      identity: 'No verified binding',
      freshness: 'Does not establish identity'
    }
  };
  const stateContent = document.querySelector('.state-content');
  document.querySelectorAll('[data-state]').forEach(button => {
    button.addEventListener('click', () => {
      const state = states[button.dataset.state];
      if (!state || !stateContent) return;
      document.querySelectorAll('[data-state]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      stateContent.dataset.currentState = button.dataset.state;
      ['value', 'explanation', 'identity', 'freshness'].forEach(key => {
        document.getElementById(`state-${key}`).textContent = state[key];
      });
    });
  });

  document.querySelectorAll('.mobile-nav a').forEach(link => {
    link.addEventListener('click', () => link.closest('details').removeAttribute('open'));
  });
  document.querySelectorAll('.mobile-nav').forEach(menu => {
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
  });

  const path = window.location.pathname.replace(/\/$/, '/index.html');
  document.querySelectorAll('.docs-sidebar a').forEach(link => {
    if (new URL(link.href).pathname === path) link.setAttribute('aria-current', 'page');
  });
  const docsNavigation = document.querySelector('.docs-navigation');
  if (docsNavigation && window.matchMedia('(max-width: 960px)').matches) docsNavigation.open = false;

  document.querySelectorAll('.prose pre').forEach(pre => {
    const code = pre.querySelector('code');
    if (!code || !navigator.clipboard || !window.isSecureContext) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code example');
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.textContent = 'Copied';
        button.setAttribute('aria-label', 'Code example copied');
      } catch {
        button.textContent = 'Select to copy';
        button.setAttribute('aria-label', 'Clipboard unavailable; select the code to copy');
      }
      window.setTimeout(() => {
        button.textContent = 'Copy';
        button.setAttribute('aria-label', 'Copy code example');
      }, 2000);
    });
    pre.appendChild(button);
  });
})();
