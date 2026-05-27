/**
 * DVDcoin Bank - Sistema de Navegación Unificada
 * Gestiona la navegación según roles: miembro, admin, superadmin, dvd
 */

(function() {
  'use strict';

  // Configuración de pestañas según roles
  const NAV_CONFIG = {
    // Pestañas visibles para todos los usuarios autenticados
    common: [
      { id: 'home', icon: '🏦', label: 'Inicio', href: '/', hash: '' },
      { id: 'transfer', icon: '💸', label: 'Transferir', href: '/', hash: '#transfer' },
      { id: 'history', icon: '📜', label: 'Historial', href: '/', hash: '#history' },
      { id: 'gallery', icon: '🖼️', label: 'Galería', href: '/', hash: '#gallery' }
    ],
    
    // Pestañas para miembros (no admins)
    member: [
      { id: 'cuentos', icon: '📖', label: 'Cuentos', href: '/cuentos.html', dynamic: true, checkEndpoint: '/api/cuentos/status' },
      { id: 'social', icon: '💬', label: 'Social', href: '/', hash: '#social', dynamic: true, checkEndpoint: '/api/messages/status' },
      { id: 'video', icon: '🎥', label: 'Video', href: '/video.html', dynamic: true, checkEndpoint: '/api/rooms/status' },
      { id: 'pasapalabra', icon: '🎯', label: 'Pasapalabra', href: '/pasapalabra/game.html', dynamic: true, checkEndpoint: '/api/pasapalabra/status' },
      { id: 'millonario', icon: '💰', label: 'Millonario', href: '/millonario/game.html', dynamic: true, checkEndpoint: '/api/millonario/status' },
      { id: 'quiensoy', icon: '🎭', label: '¿Quién soy?', href: '/quiensoy/game.html', dynamic: true, checkEndpoint: '/api/quiensoy/status' },
      { id: 'cifrasletras', icon: '🔤', label: 'Cifras y Letras', href: '/cifrasletras/game.html', dynamic: true, checkEndpoint: '/api/cifrasletras/status' },
      { id: 'hundirlaflota', icon: '⚓', label: 'Hundir la Flota', href: '/hundirlaflota/game.html', dynamic: true, checkEndpoint: '/api/hundirlaflota/status' },
      { id: 'apuestas', icon: '🎲', label: 'Apuestas', href: '/apuestas' },
      { id: 'votaciones', icon: '🗳️', label: 'Votaciones', href: '/votaciones' }
    ],
    
    // Pestañas para admins (no superadmins)
    admin: [
      { id: 'cuentos-admin', icon: '📖', label: 'Cuentos', href: '/cuentos.html' },
      { id: 'mensajes-admin', icon: '💬', label: 'Mensajes', href: '/mensajes.html' },
      { id: 'video-admin', icon: '🎥', label: 'Video', href: '/video.html' },
      { id: 'pasapalabra-admin', icon: '🎯', label: 'Pasapalabra', href: '/pasapalabra.html' },
      { id: 'millonario-admin', icon: '💰', label: 'Millonario', href: '/millonario.html' },
      { id: 'quiensoy-admin', icon: '🎭', label: '¿Quién soy?', href: '/quiensoy.html' },
      { id: 'cifrasletras-admin', icon: '🔤', label: 'Cifras y Letras', href: '/cifrasletras.html' },
      { id: 'apuestas-admin', icon: '🎲', label: 'Apuestas', href: '/apuestas' },
      { id: 'votaciones-admin', icon: '🗳️', label: 'Votaciones', href: '/votaciones' },
      { id: 'admin', icon: '⚙️', label: 'Admin', href: '/', hash: '#admin' }
    ],
    
    // Pestañas adicionales para superadmin
    superadmin: [
      { id: 'stats', icon: '📊', label: 'Stats', href: '/stats' }
    ],
    
    // Pestañas exclusivas para dvd
    dvd: [
      { id: 'opo', icon: '🎓', label: 'OPO', href: '/opo', hash: '' }
    ]
  };

  // Estado global
  let currentUser = null;
  let dynamicStates = {};

  /**
   * Inicializa el sistema de navegación
   */
  async function init() {
    // Obtener usuario actual
    const token = localStorage.getItem('dvd_token');
    if (!token) {
      console.warn('[UnifiedNav] No token found');
      return;
    }

    try {
      currentUser = await fetchAPI('/api/me');
      
      // Verificar estados dinámicos (juegos, features)
      await checkDynamicStates();
      
      // Renderizar navegación
      renderNav();
      
      // Marcar pestaña activa
      setActiveTab();
      
      // Escuchar cambios de hash
      window.addEventListener('hashchange', setActiveTab);
      
    } catch (error) {
      console.error('[UnifiedNav] Init error:', error);
    }
  }

  /**
   * Verifica el estado de features dinámicas (juegos habilitados, etc)
   */
  async function checkDynamicStates() {
    const checks = [];
    
    // Solo verificar para miembros
    if (!currentUser.is_admin) {
      NAV_CONFIG.member.forEach(tab => {
        if (tab.dynamic && tab.checkEndpoint) {
          checks.push(
            fetchAPI(tab.checkEndpoint)
              .then(data => {
                dynamicStates[tab.id] = data.enabled || false;
              })
              .catch(() => {
                dynamicStates[tab.id] = false;
              })
          );
        }
      });
    }
    
    await Promise.all(checks);
  }

  /**
   * Obtiene las pestañas que debe ver el usuario actual
   */
  function getVisibleTabs() {
    if (!currentUser) return [];
    
    let tabs = [...NAV_CONFIG.common];
    
    // Determinar rol
    const isDvd = currentUser.username === 'dvd';
    const isSuperadmin = currentUser.is_superadmin || isDvd;
    const isAdmin = currentUser.is_admin || isSuperadmin;
    
    if (isAdmin) {
      // Admins y superadmins ven pestañas de admin
      tabs = [...tabs, ...NAV_CONFIG.admin];
      
      if (isSuperadmin) {
        // Superadmins ven pestañas adicionales
        tabs = [...tabs, ...NAV_CONFIG.superadmin];
      }
      
      if (isDvd) {
        // DVD ve pestañas exclusivas
        tabs = [...tabs, ...NAV_CONFIG.dvd];
      }
    } else {
      // Miembros ven pestañas de miembro
      tabs = [...tabs, ...NAV_CONFIG.member.filter(tab => {
        // Filtrar pestañas dinámicas según su estado
        if (tab.dynamic) {
          return dynamicStates[tab.id] === true;
        }
        return true;
      })];
    }
    
    return tabs;
  }

  /**
   * Renderiza la barra de navegación
   */
  function renderNav() {
    const container = document.getElementById('unifiedNavContainer');
    if (!container) {
      console.warn('[UnifiedNav] Container #unifiedNavContainer not found');
      return;
    }
    
    const tabs = getVisibleTabs();
    
    const html = `
      <nav class="unified-nav">
        <div class="nav-tabs">
          ${tabs.map(tab => {
            const href = tab.hash ? `${tab.href}${tab.hash}` : tab.href;
            // Ensure label doesn't contain emoji - icon is already shown separately
            const cleanLabel = tab.label.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').trim();
            return `
              <a href="${href}" 
                 class="nav-tab" 
                 data-tab-id="${tab.id}"
                 data-tab-href="${tab.href}"
                 data-tab-hash="${tab.hash || ''}"
                 data-i18n="${tab.i18nKey || ''}">
                <span class="nav-icon">${tab.icon}</span>
                <span class="nav-label">${cleanLabel}</span>
              </a>
            `;
          }).join('')}
        </div>
      </nav>
    `;
    
    container.innerHTML = html;
    
    // Trigger i18n translation if available
    if (window.i18n && typeof window.i18n.translatePage === 'function') {
      window.i18n.translatePage();
    }
  }

  /**
   * Marca la pestaña activa según la URL actual
   */
  function setActiveTab() {
    const path = window.location.pathname;
    const hash = window.location.hash;
    
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.classList.remove('active');
      
      const tabHref = tab.getAttribute('data-tab-href');
      const tabHash = tab.getAttribute('data-tab-hash');
      
      // Lógica de activación
      let isActive = false;
      
      if (path === '/' && !hash && tabHref === '/' && !tabHash) {
        // Página de inicio sin hash
        isActive = true;
      } else if (path === '/' && hash && tabHash === hash) {
        // Página de inicio con hash específico
        isActive = true;
      } else if (path !== '/' && path.includes(tabHref) && tabHref !== '/') {
        // Otras páginas
        isActive = true;
      }
      
      if (isActive) {
        tab.classList.add('active');
      }
    });
  }

  /**
   * Helper para hacer peticiones a la API
   */
  async function fetchAPI(endpoint) {
    const token = localStorage.getItem('dvd_token');
    const response = await fetch(endpoint, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'ngrok-skip-browser-warning': '1'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response.json();
  }

  /**
   * Exponer API pública
   */
  window.UnifiedNav = {
    init,
    refresh: async function() {
      await checkDynamicStates();
      renderNav();
      setActiveTab();
    }
  };

  // Auto-inicializar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
