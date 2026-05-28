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
      { id: 'home', icon: '🏦', label: 'Inicio', href: '/bank', hash: '' },
      { id: 'transfer', icon: '💸', label: 'Transferir', href: '/bank', hash: '#transfer' },
      { id: 'history', icon: '📜', label: 'Historial', href: '/bank', hash: '#history' },
      { id: 'gallery', icon: '🖼️', label: 'Galería', href: '/bank', hash: '#gallery' }
    ],

    // Pestañas para miembros (no admins)
    member: [
      { id: 'cuentos', icon: '📖', label: 'Cuentos', href: '/bank/cuentos.html', dynamic: true, checkEndpoint: '/bank/api/cuentos/status' },
      { id: 'social', icon: '💬', label: 'Social', href: '/', hash: '#social', dynamic: true, checkEndpoint: '/bank/api/messages/status' },
      { id: 'video', icon: '🎥', label: 'Video', href: '/bank/video.html', dynamic: true, checkEndpoint: '/bank/api/rooms/status' },
      { id: 'pasapalabra', icon: '🎯', label: 'Pasapalabra', href: '/bank/pasapalabra/game.html', dynamic: true, checkEndpoint: '/bank/api/pasapalabra/status' },
      { id: 'millonario', icon: '💰', label: 'Millonario', href: '/bank/millonario/game.html', dynamic: true, checkEndpoint: '/bank/api/millonario/status' },
      { id: 'quiensoy', icon: '🎭', label: '¿Quién soy?', href: '/bank/quiensoy/game.html', dynamic: true, checkEndpoint: '/bank/api/quiensoy/status' },
      { id: 'cifrasletras', icon: '🔤', label: 'Cifras y Letras', href: '/bank/cifrasletras/game.html', dynamic: true, checkEndpoint: '/bank/api/cifrasletras/status' },
      { id: 'hundirlaflota', icon: '⚓', label: 'Hundir la Flota', href: '/bank/hundirlaflota/game.html', dynamic: true, checkEndpoint: '/bank/api/hundirlaflota/status' },
      { id: 'apuestas', icon: '🎲', label: 'Apuestas', href: '/bank/apuestas' },
      { id: 'votaciones', icon: '🗳️', label: 'Votaciones', href: '/bank/votaciones' }
    ],

    // Pestañas para admins (no superadmins)
    admin: [
      { id: 'cuentos-admin', icon: '📖', label: 'Cuentos', href: '/bank/cuentos.html' },
      { id: 'mensajes-admin', icon: '💬', label: 'Mensajes', href: '/bank/mensajes.html' },
      { id: 'video-admin', icon: '🎥', label: 'Video', href: '/bank/video.html' },
      { id: 'pasapalabra-admin', icon: '🎯', label: 'Pasapalabra', href: '/bank/pasapalabra.html' },
      { id: 'millonario-admin', icon: '💰', label: 'Millonario', href: '/bank/millonario.html' },
      { id: 'quiensoy-admin', icon: '🎭', label: '¿Quién soy?', href: '/bank/quiensoy.html' },
      { id: 'cifrasletras-admin', icon: '🔤', label: 'Cifras y Letras', href: '/bank/cifrasletras.html' },
      { id: 'apuestas-admin', icon: '🎲', label: 'Apuestas', href: '/bank/apuestas' },
      { id: 'votaciones-admin', icon: '🗳️', label: 'Votaciones', href: '/bank/votaciones' },
      { id: 'admin', icon: '⚙️', label: 'Admin', href: '/bank', hash: '#admin' }
    ],

    // Pestañas adicionales para superadmin
    superadmin: [
      { id: 'stats', icon: '📊', label: 'Stats', href: '/bank/stats' }
    ],

    // Pestañas exclusivas para dvd
    dvd: [
      { id: 'opo', icon: '🎓', label: 'OPO', href: '/bank/opo', hash: '' }
    ]
  };

  // Estado global
  let currentUser = null;
  let dynamicStates = {};

  /**
   * Inicializa el sistema de navegación
   */
  async function init() {
    const token = localStorage.getItem('dvd_token');
    if (!token) {
      console.warn('[UnifiedNav] No token found');
      return;
    }

    try {
      currentUser = await fetchAPI('/bank/api/me');
      await checkDynamicStates();
      renderNav();
      setActiveTab();
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

    if (!currentUser.is_admin) {
      NAV_CONFIG.member.forEach(function(tab) {
        if (tab.dynamic && tab.checkEndpoint) {
          checks.push(
            fetchAPI(tab.checkEndpoint)
              .then(function(data) { dynamicStates[tab.id] = data.enabled || false; })
              .catch(function() { dynamicStates[tab.id] = false; })
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

    var tabs = NAV_CONFIG.common.slice();

    var isDvd = currentUser.username === 'dvd';
    var isSuperadmin = currentUser.is_superadmin || isDvd;
    var isAdmin = currentUser.is_admin || isSuperadmin;

    if (isAdmin) {
      tabs = tabs.concat(NAV_CONFIG.admin);
      if (isSuperadmin) tabs = tabs.concat(NAV_CONFIG.superadmin);
      if (isDvd) tabs = tabs.concat(NAV_CONFIG.dvd);
    } else {
      tabs = tabs.concat(NAV_CONFIG.member.filter(function(tab) {
        if (tab.dynamic) return dynamicStates[tab.id] === true;
        return true;
      }));
    }

    return tabs;
  }

  /**
   * Renderiza la barra de navegación
   */
  function renderNav() {
    var container = document.getElementById('unifiedNavContainer');
    if (!container) {
      console.warn('[UnifiedNav] Container #unifiedNavContainer not found');
      return;
    }

    var tabs = getVisibleTabs();
    var html = '<nav class="unified-nav"><div class="nav-tabs">';

    tabs.forEach(function(tab) {
      var href = tab.hash ? tab.href + tab.hash : tab.href;
      var cleanLabel = tab.label.replace(/[\u{1F300}-\u{1F9FF}]/gu, '').trim();
      html += '<a href="' + href + '" class="nav-tab"' +
        ' data-tab-id="' + tab.id + '"' +
        ' data-tab-href="' + tab.href + '"' +
        ' data-tab-hash="' + (tab.hash || '') + '"' +
        ' data-i18n="' + (tab.i18nKey || '') + '">' +
        '<span class="nav-icon">' + tab.icon + '</span>' +
        '<span class="nav-label">' + cleanLabel + '</span>' +
        '</a>';
    });

    html += '</div></nav>';
    container.innerHTML = html;

    if (window.i18n && typeof window.i18n.translatePage === 'function') {
      window.i18n.translatePage();
    }
  }

  /**
   * Marca la pestaña activa según la URL actual
   */
  function setActiveTab() {
    var path = window.location.pathname;
    var hash = window.location.hash;

    document.querySelectorAll('.nav-tab').forEach(function(tab) {
      tab.classList.remove('active');

      var tabHref = tab.getAttribute('data-tab-href');
      var tabHash = tab.getAttribute('data-tab-hash');
      var isActive = false;

      if (path === '/' && !hash && tabHref === '/' && !tabHash) {
        isActive = true;
      } else if (path === '/' && hash && tabHash === hash) {
        isActive = true;
      } else if (path !== '/' && path.includes(tabHref) && tabHref !== '/') {
        isActive = true;
      }

      if (isActive) tab.classList.add('active');
    });
  }

  /**
   * Helper para hacer peticiones a la API
   */
  async function fetchAPI(endpoint) {
    var token = localStorage.getItem('dvd_token');
    var response = await fetch(endpoint, {
      headers: {
        'Authorization': 'Bearer ' + token,
        'ngrok-skip-browser-warning': '1'
      }
    });

    if (!response.ok) throw new Error('HTTP ' + response.status);
    return response.json();
  }

  // Exponer API pública
  window.UnifiedNav = {
    init: init,
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
