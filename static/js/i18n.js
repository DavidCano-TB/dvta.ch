/**
 * DVDcoin Bank - Internationalization System
 * Handles multi-language support with auto-hide language bar
 */

(function() {
  'use strict';

  const SUPPORTED_LANGUAGES = {
    es: { name: 'Español', flag: '🇪🇸' },
    en: { name: 'English', flag: '🇬🇧' },
    fr: { name: 'Français', flag: '🇫🇷' },
    ca: { name: 'Català', flag: '🏴' },
    eu: { name: 'Euskara', flag: '🏴' },
    de: { name: 'Deutsch', flag: '🇩🇪' },
    it: { name: 'Italiano', flag: '🇮🇹' }
  };

  const DEFAULT_LANGUAGE = 'es';
  const STORAGE_KEY = 'dvdcoin_language';
  
  let currentLanguage = localStorage.getItem(STORAGE_KEY) || DEFAULT_LANGUAGE;
  let translations = {};
  let lastScrollY = 0;
  let ticking = false;

  /**
   * Initialize the i18n system
   */
  async function init() {
    // Load translations
    await loadTranslations(currentLanguage);
    
    // Create language bar
    createLanguageBar();
    
    // Apply translations to page
    translatePage();
    
    // Setup scroll listener for auto-hide
    setupScrollListener();
    
    // Expose global API
    window.i18n = {
      t: translate,
      setLanguage: setLanguage,
      getCurrentLanguage: () => currentLanguage,
      getSupportedLanguages: () => SUPPORTED_LANGUAGES
    };
  }

  /**
   * Load translation file for a language
   */
  async function loadTranslations(lang) {
    try {
      const response = await fetch(`/bank/static/i18n/${lang}.json`);
      if (!response.ok) throw new Error(`Failed to load ${lang}`);
      translations = await response.json();
      return true;
    } catch (error) {
      console.warn(`Failed to load translations for ${lang}, falling back to ${DEFAULT_LANGUAGE}`, error);
      if (lang !== DEFAULT_LANGUAGE) {
        return loadTranslations(DEFAULT_LANGUAGE);
      }
      return false;
    }
  }

  /**
   * Translate a key
   */
  function translate(key, replacements = {}) {
    let text = translations[key] || key;
    
    // Replace placeholders like {user}
    Object.keys(replacements).forEach(placeholder => {
      text = text.replace(new RegExp(`\\{${placeholder}\\}`, 'g'), replacements[placeholder]);
    });
    
    return text;
  }

  /**
   * Create the language selection bar
   */
  function createLanguageBar() {
    // Check if already exists
    if (document.querySelector('.language-bar')) return;

    const bar = document.createElement('div');
    bar.className = 'language-bar';
    bar.innerHTML = `
      <span class="language-bar__label">🌐 Language:</span>
      ${Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => `
        <button 
          class="language-bar__button ${code === currentLanguage ? 'active' : ''}" 
          data-lang="${code}"
          title="${info.name}"
        >
          ${info.flag} ${code.toUpperCase()}
        </button>
      `).join('')}
    `;

    // Add click handlers
    bar.querySelectorAll('.language-bar__button').forEach(btn => {
      btn.addEventListener('click', () => {
        const lang = btn.dataset.lang;
        setLanguage(lang);
      });
    });

    // Insert at the beginning of body
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add('has-language-bar');
  }

  /**
   * Change the current language
   */
  async function setLanguage(lang) {
    if (!SUPPORTED_LANGUAGES[lang]) {
      console.warn(`Language ${lang} not supported`);
      return;
    }

    currentLanguage = lang;
    localStorage.setItem(STORAGE_KEY, lang);

    // Load new translations
    await loadTranslations(lang);

    // Update active button
    document.querySelectorAll('.language-bar__button').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Re-translate page
    translatePage();

    // Dispatch event for custom handlers
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
  }

  /**
   * Translate all elements with data-i18n attribute
   */
  function translatePage() {
    // Translate elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.dataset.i18n;
      const text = translate(key);
      
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        if (el.placeholder !== undefined) {
          el.placeholder = text;
        } else {
          el.value = text;
        }
      } else {
        el.textContent = text;
      }
    });

    // Translate elements with data-i18n-html (allows HTML content)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.dataset.i18nHtml;
      el.innerHTML = translate(key);
    });

    // Translate placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.dataset.i18nPlaceholder;
      el.placeholder = translate(key);
    });

    // Translate titles
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.dataset.i18nTitle;
      el.title = translate(key);
    });

    // Update page title if specified
    const titleEl = document.querySelector('[data-i18n-page-title]');
    if (titleEl) {
      document.title = translate(titleEl.dataset.i18nPageTitle);
    }
  }

  /**
   * Setup scroll listener to auto-hide language bar
   */
  function setupScrollListener() {
    const bar = document.querySelector('.language-bar');
    if (!bar) return;

    let hideTimeout;

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const currentScrollY = window.scrollY;

          // Clear any existing timeout
          clearTimeout(hideTimeout);

          // Show bar when scrolling up or at top
          if (currentScrollY < lastScrollY || currentScrollY < 10) {
            bar.classList.remove('hidden');
          } 
          // Hide bar when scrolling down (after 50px)
          else if (currentScrollY > 50) {
            hideTimeout = setTimeout(() => {
              bar.classList.add('hidden');
            }, 150);
          }

          lastScrollY = currentScrollY;
          ticking = false;
        });

        ticking = true;
      }
    });

    // Show bar on mouse move near top
    document.addEventListener('mousemove', (e) => {
      if (e.clientY < 60) {
        bar.classList.remove('hidden');
      }
    });
  }

  /**
   * Helper to add translations dynamically
   */
  function addTranslations(newTranslations) {
    Object.assign(translations, newTranslations);
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose addTranslations for dynamic content
  window.i18nAddTranslations = addTranslations;

})();
