// --- script block 0 ---

/* Register Service Worker to force fresh HTML on every load */
if('serviceWorker' in navigator){
  navigator.serviceWorker.register('/bank/static/sw.js?v=20260528')
    .then(reg => {
      /* Force update check immediately */
      reg.update();
      /* If a new SW is waiting, activate it immediately */
      if(reg.waiting) reg.waiting.postMessage({type:'SKIP_WAITING'});
      reg.addEventListener('updatefound', () => {
        const nw = reg.installing;
        nw.addEventListener('statechange', () => {
          if(nw.state === 'installed' && navigator.serviceWorker.controller){
            /* New version available — reload silently */
            window.location.reload();
          }
        });
      });
    }).catch(()=>{});
  /* If SW controller changes (new SW activated), reload */
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload();
  });
}

// --- script block 1 ---

(function(){
  /* ═══════════════════════════════════════════════════════
     Classic bank column — Ionic order
     Stone grey, starts at mid-screen, fades softly upward.
  ═══════════════════════════════════════════════════════ */
  var VH  = window.innerHeight;
  var W   = 88;          // column width
  var H   = VH;          // total SVG height = full viewport
  var cx  = W / 2;
  var ns  = "http://www.w3.org/2000/svg";

  /* Column starts at 50% of the screen and extends to the bottom */
  var startY = Math.round(VH * 0.50);  // column start Y position
  var colH   = H - startY;             // effective column height

  /* Proportions within colH */
  var plinH  = Math.round(colH * 0.038);
  var baseH  = Math.round(colH * 0.082);
  var capH   = Math.round(colH * 0.130);
  var shaftH = colH - plinH - baseH - capH;

  /* Shaft radius */
  var rBot = W * 0.330, rTop = W * 0.258;
  function shaftR(t) {
    return rTop + (rBot - rTop) * t + rBot * 0.042 * Math.sin(t * Math.PI);
  }

  /* ── Stone grey palette ──────────────────────────────── */
  /* Base: cold bluish grey, like granite or limestone */
  function stoneA(op) { return "rgba(180,185,195," + op + ")"; }
  function lightA(op) { return "rgba(220,225,232," + op + ")"; }
  function darkA(op)  { return "rgba(110,115,128," + op + ")"; }
  function shadowA(op){ return "rgba(0,0,0,"        + op + ")"; }

  function buildColumn(flip) {
    var svg = document.createElementNS(ns,"svg");
    svg.setAttribute("width",  W);
    svg.setAttribute("height", H);
    svg.setAttribute("viewBox","0 0 " + W + " " + H);
    svg.style.cssText = "display:block;";
    var defs = document.createElementNS(ns,"defs");
    svg.appendChild(defs);

    /* ── Gradients ───────────────────────────────────── */
    function mkLG(id, x1,y1,x2,y2, stops) {
      var lg = document.createElementNS(ns,"linearGradient");
      lg.setAttribute("id",id);
      lg.setAttribute("gradientUnits","userSpaceOnUse");
      lg.setAttribute("x1",x1); lg.setAttribute("y1",y1);
      lg.setAttribute("x2",x2); lg.setAttribute("y2",y2);
      stops.forEach(function(s){
        var st = document.createElementNS(ns,"stop");
        st.setAttribute("offset",   s[0]);
        st.setAttribute("stop-color",s[1]);
        lg.appendChild(st);
      });
      defs.appendChild(lg);
      return "url(#"+id+")";
    }

    var side = flip ? "r" : "l";

    /* Horizontal shaft gradient — light from the inside */
    var gS = mkLG("gs"+side, 0,0,W,0, flip ? [
      ["0%",   stoneA(.95)],
      ["15%",  lightA(1.0)],
      ["38%",  stoneA(.80)],
      ["62%",  stoneA(.55)],
      ["82%",  darkA(.45)],
      ["100%", shadowA(.12)]
    ] : [
      ["0%",   shadowA(.12)],
      ["18%",  darkA(.45)],
      ["38%",  stoneA(.55)],
      ["62%",  stoneA(.80)],
      ["85%",  lightA(1.0)],
      ["100%", stoneA(.95)]
    ]);

    /* Moulding gradient — more opaque */
    var gM = mkLG("gm"+side, 0,0,W,0, flip ? [
      ["0%",   stoneA(1.0)],
      ["18%",  lightA(1.0)],
      ["42%",  stoneA(.85)],
      ["70%",  darkA(.65)],
      ["100%", shadowA(.18)]
    ] : [
      ["0%",   shadowA(.18)],
      ["30%",  darkA(.65)],
      ["58%",  stoneA(.85)],
      ["82%",  lightA(1.0)],
      ["100%", stoneA(1.0)]
    ]);

    /* Fluting shadow gradient */
    var gF = mkLG("gf"+side, 0,0,W,0, [
      ["0%",   "rgba(0,0,0,.22)"],
      ["50%",  "rgba(0,0,0,0)"],
      ["100%", "rgba(0,0,0,.22)"]
    ]);

    /* Vertical fade gradient (fade-in from startY) */
    var fadeH = Math.round(colH * 0.22);  // fade zone height
    var gFade = mkLG("fade"+side, 0, startY, 0, startY+fadeH, [
      ["0%",   "rgba(0,0,0,0)"],   // transparente arriba
      ["100%", "rgba(0,0,0,1)"]    // opaco abajo
    ]);
    /* Fade mask */
    var mask = document.createElementNS(ns,"mask");
    mask.id = "mask"+side;
    var mRect = document.createElementNS(ns,"rect");
    mRect.setAttribute("x",0); mRect.setAttribute("y",startY);
    mRect.setAttribute("width",W); mRect.setAttribute("height",colH);
    mRect.setAttribute("fill","url(#fade"+side+")");
    mask.appendChild(mRect);
    defs.appendChild(mask);

    /* Masked group — everything visible */
    var g = document.createElementNS(ns,"g");
    g.setAttribute("mask","url(#mask"+side+")");
    svg.appendChild(g);

    /* ── Drawing helpers (operate on the masked group) ── */
    function R(x,y,w,h,fill){ var el=document.createElementNS(ns,"rect"); el.setAttribute("x",x);el.setAttribute("y",y);el.setAttribute("width",w);el.setAttribute("height",h);el.setAttribute("fill",fill);g.appendChild(el);return el; }
    function L(x1,y1,x2,y2,stroke,sw){ var el=document.createElementNS(ns,"line");el.setAttribute("x1",x1);el.setAttribute("y1",y1);el.setAttribute("x2",x2);el.setAttribute("y2",y2);el.setAttribute("stroke",stroke);el.setAttribute("stroke-width",sw||1);g.appendChild(el); }
    function P(d,fill,stroke,sw){ var el=document.createElementNS(ns,"path");el.setAttribute("d",d);el.setAttribute("fill",fill||"none");if(stroke){el.setAttribute("stroke",stroke);el.setAttribute("stroke-width",sw||1);}g.appendChild(el);return el; }
    function E(cx2,cy,rx,ry,fill,stroke,sw){ var el=document.createElementNS(ns,"ellipse");el.setAttribute("cx",cx2);el.setAttribute("cy",cy);el.setAttribute("rx",rx);el.setAttribute("ry",ry);el.setAttribute("fill",fill||"none");if(stroke){el.setAttribute("stroke",stroke);el.setAttribute("stroke-width",sw||1);}g.appendChild(el); }

    var y = startY;

    /* ════ IONIC CAPITAL ══════════════════════════════ */
    var capY = y;

    /* Abacus */
    var abH = Math.round(capH * 0.14);
    R(0, capY, W, abH, gM);
    L(0,capY,W,capY,lightA(.9),1.8);
    L(0,capY+abH,W,capY+abH,stoneA(.6),1);

    /* Ovolo (curved moulding) */
    var ovH = Math.round(capH * 0.11);
    var ovY = capY + abH;
    P("M0,"+(ovY+ovH)+" Q"+cx+","+ovY+" "+W+","+(ovY+ovH)+" L"+W+","+(ovY+ovH)+" L0,"+(ovY+ovH)+" Z", gM, stoneA(.5),.8);

    /* Channel */
    var chH = Math.round(capH * 0.07);
    var chY = ovY + ovH;
    R(Math.round(W*.05), chY, Math.round(W*.90), chH, darkA(.35));

    /* Ionic volutes */
    var volH = Math.round(capH * 0.46);
    var volY = chY + chH;
    var vW   = Math.round(W * 0.44);

    var vd  = "M0,"+(volY+volH);
    vd += " C"+(vW*.55)+","+(volY+volH)+" "+vW+","+(volY+volH*.65)+" "+vW+","+volY;
    vd += " C"+vW+","+(volY-volH*.08)+" "+(vW*.55)+","+(volY-volH*.02)+" "+(vW*.42)+","+(volY+volH*.25);
    vd += " C"+(vW*.35)+","+(volY+volH*.42)+" "+(vW*.40)+","+(volY+volH*.60)+" "+(vW*.50)+","+(volY+volH*.60);
    vd += " L"+(W-vW*.50)+","+(volY+volH*.60);
    vd += " C"+(W-vW*.40)+","+(volY+volH*.60)+" "+(W-vW*.35)+","+(volY+volH*.42)+" "+(W-vW*.42)+","+(volY+volH*.25);
    vd += " C"+(W-vW*.55)+","+(volY-volH*.02)+" "+(W-vW)+","+(volY-volH*.08)+" "+(W-vW)+","+volY;
    vd += " C"+(W-vW)+","+(volY+volH*.65)+" "+(W-vW*.55)+","+(volY+volH)+" "+W+","+(volY+volH)+" Z";
    P(vd, gS, stoneA(.45), .8);

    /* Spirals */
    [[vW*.38, volY+volH*.32, vW*.27, volH*.30],
     [vW*.38, volY+volH*.38, vW*.16, volH*.19],
     [vW*.38, volY+volH*.42, vW*.08, volH*.10]
    ].forEach(function(sp,k){
      E(sp[0],sp[1],sp[2],sp[3],null,lightA(.45-.10*k),.9);
      E(W-sp[0],sp[1],sp[2],sp[3],null,lightA(.45-.10*k),.9);
    });

    /* Neck */
    var nkH = Math.round(capH * 0.22);
    var nkY = volY + volH;
    var nkR0= rTop*1.05, nkR1=rTop*1.18;
    P("M"+(cx-nkR1)+","+(nkY+nkH)+" L"+(cx-nkR0)+","+nkY+" L"+(cx+nkR0)+","+nkY+" L"+(cx+nkR1)+","+(nkY+nkH)+" Z", gM, stoneA(.45),.8);
    [.28,.54,.78].forEach(function(f){ var ry=nkY+nkH*f,rx=nkR0+(nkR1-nkR0)*f; L(cx-rx,ry,cx+rx,ry,stoneA(.35),.9); });

    y += capH;

    /* ════ SHAFT ═══════════════════════════════════════ */
    var shY = y, shBot = y + shaftH;
    var STEPS=80, NFLUTES=24;
    var lP=[],rP=[];
    for(var i=0;i<=STEPS;i++){
      var t=i/STEPS, r=shaftR(t);
      lP.push([cx-r, shY+shaftH*t]);
      rP.push([cx+r, shY+shaftH*t]);
    }
    var shD="M"+lP[0][0]+","+lP[0][1];
    lP.slice(1).forEach(function(p){shD+=" L"+p[0]+","+p[1];});
    shD+=" L"+rP[rP.length-1][0]+","+rP[rP.length-1][1];
    for(var i=rP.length-2;i>=0;i--) shD+=" L"+rP[i][0]+","+rP[i][1]; shD+=" Z";

    /* Clip path */
    var cid="cl"+side;
    var cl=document.createElementNS(ns,"clipPath"); cl.id=cid;
    var cp=document.createElementNS(ns,"path"); cp.setAttribute("d",shD); cl.appendChild(cp); defs.appendChild(cl);
    var cu="url(#"+cid+")";

    P(shD, gS);
    R(0,shY,W,shaftH,gF);

    /* Flutes */
    for(var f=0;f<NFLUTES;f++){
      var ang=(f+.5)/NFLUTES*Math.PI;
      var fx=cx-Math.cos(ang)*(rTop*.88+(rBot*.88-rTop*.88)*.5);
      if(fx<1||fx>W-1) continue;
      var fl=document.createElementNS(ns,"line");
      fl.setAttribute("x1",fx);fl.setAttribute("y1",shY+5);fl.setAttribute("x2",fx);fl.setAttribute("y2",shBot-5);
      fl.setAttribute("stroke",stoneA(.13));fl.setAttribute("stroke-width","0.9");fl.setAttribute("clip-path",cu);
      g.appendChild(fl);
    }
    /* Highlight */
    var hlid="hl"+side;
    mkLG(hlid,cx-W*.11,0,cx+W*.11,0,[["0%","rgba(220,225,232,0)"],["50%","rgba(220,225,232,.18)"],["100%","rgba(220,225,232,0)"]]);
    R(cx-W*.11,shY,W*.22,shaftH,"url(#"+hlid+")");

    /* Edges */
    var dL="M"+lP[0][0]+","+lP[0][1]; lP.slice(1).forEach(function(p){dL+=" L"+p[0]+","+p[1];}); P(dL,null,lightA(.55),1.3);
    var dR="M"+rP[0][0]+","+rP[0][1]; rP.slice(1).forEach(function(p){dR+=" L"+p[0]+","+p[1];}); P(dR,null,darkA(.45),1.3);

    y += shaftH;

    /* ════ ATTIC BASE ══════════════════════════════════ */
    var baY=y;
    var t1H=Math.round(baseH*.30), scH=Math.round(baseH*.26), t2H=Math.round(baseH*.36);
    var scY=baY+t1H, t2Y=scY+scH;
    E(cx,baY+t1H/2,rBot*1.09,t1H/2,gM,lightA(.8),1.4);
    P("M"+(cx-rBot*1.06)+","+scY+" Q"+(cx-rBot*1.17)+","+(scY+scH/2)+" "+(cx-rBot*1.17)+","+(scY+scH)+" L"+(cx+rBot*1.17)+","+(scY+scH)+" Q"+(cx+rBot*1.17)+","+(scY+scH/2)+" "+(cx+rBot*1.06)+","+scY+" Z",gS,stoneA(.4),.8);
    L(cx-rBot*1.06,scY,cx+rBot*1.06,scY,stoneA(.6),1);
    L(cx-rBot*1.17,scY+scH,cx+rBot*1.17,scY+scH,stoneA(.6),1);
    E(cx,t2Y+t2H/2,rBot*1.23,t2H/2,gM,lightA(.75),1.4);
    L(cx-rBot*1.23,t2Y+t2H,cx+rBot*1.23,t2Y+t2H,lightA(.75),1.5);

    y += baseH;

    /* ════ PLINTH ══════════════════════════════════════ */
    R(0,y,W,plinH,gM);
    L(0,y,W,y,lightA(.9),2);
    R(Math.round(W*.05),y+Math.round(plinH*.55),Math.round(W*.90),Math.round(plinH*.32),darkA(.25));
    L(0,y+plinH,W,y+plinH,stoneA(.65),1.5);

    return svg;
  }

  var eL=document.getElementById("bcL");
  var eR=document.getElementById("bcR");
  if(eL) eL.appendChild(buildColumn(false));
  if(eR) eR.appendChild(buildColumn(true));
})();

// --- script block 2 ---

'use strict';
/* ============================================================
   DVDcoin Bank v5.1 — Application JavaScript
   1. Background canvas animation
   2. i18n
   3. In-app gallery carousel (reads /api/gallery — directory scan)
   4. API helper
   5. Auth (login / register / logout)
   6. App loader
   7. Transfer
   8. Transaction renderer + history
   9. Admin panel
  10. Navigation
  11. Boot sequence
============================================================ */

/* ── 1. Background canvas — particles + glow ────────────── */
(function () {
  const c = document.getElementById('bgCanvas'), ctx = c.getContext('2d');
  let W, H, pts = [];
  const resize = () => { W = c.width = innerWidth; H = c.height = innerHeight; };
  const mkPt = () => ({
    x: Math.random() * W, y: H + Math.random() * 60,
    r: Math.random() * 1.3 + .2,
    vx: (Math.random() - .5) * .22, vy: -(Math.random() * .45 + .12),
    o: Math.random() * .32 + .05,
    life: Math.random() * 260 + 110, age: 0,
    gold: Math.random() > .38
  });
  const init = () => { pts = Array.from({ length: 90 }, mkPt); pts.forEach(p => { p.y = Math.random() * H; }); };
  let af;
  const frame = () => {
    ctx.clearRect(0, 0, W, H);
    const g = ctx.createRadialGradient(W*.5, H*.22, 0, W*.5, H*.22, H*.72);
    g.addColorStop(0, 'rgba(212,168,67,.05)');
    g.addColorStop(.7, 'rgba(50,25,0,.015)');
    g.addColorStop(1, 'transparent');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    pts.forEach((p, i) => {
      p.x += p.vx; p.y += p.vy; p.age++;
      const fade = p.age < 25 ? p.age/25 : p.age > p.life-25 ? (p.life-p.age)/25 : 1;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = p.gold ? `rgba(212,168,67,${p.o*fade})` : `rgba(140,90,15,${p.o*.4*fade})`;
      ctx.fill();
      if (p.age >= p.life || p.y < -8) pts[i] = mkPt();
    });
    for (let y = 0; y < H; y += 4) { ctx.fillStyle = 'rgba(0,0,0,.01)'; ctx.fillRect(0, y, W, 1); }
    af = requestAnimationFrame(frame);
  };
  window.addEventListener('resize', () => { resize(); init(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) cancelAnimationFrame(af); else frame(); });
  resize(); init(); frame();
})();

/* ── 2. i18n ─────────────────────────────────────────────── */
let T = {}, curLang = localStorage.getItem('dvd_lang') || 'en';  // will be overridden by DB pref after login

async function loadLang(lang) {
  try {
    const r = await fetch(`/static/i18n/${lang}.json?v=5`, { headers: { 'ngrok-skip-browser-warning': '1' } });
    if (!r.ok) throw new Error();
    T = await r.json();
    curLang = lang;
    localStorage.setItem('dvd_lang', lang);
    applyTranslations();
    updateLangButtons();
    // Save to DB if logged in
    if (me) {
      req('POST', '/api/me/lang', { lang }).catch(() => {});
    }
  } catch (e) {
    if (lang !== 'en') await loadLang('en');
  }
}

function t(key, vars) {
  let s = T[key] || key;
  if (vars) Object.entries(vars).forEach(([k, v]) => { s = s.replace(`{${k}}`, v); });
  return s;
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const v = T[el.dataset.i18n];
    if (v !== undefined) el.innerHTML = v;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const v = T[el.dataset.i18nPlaceholder];
    if (v !== undefined) el.placeholder = v;
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const v = T[el.dataset.i18nTitle];
    if (v !== undefined) el.title = v;
  });
  // Set form title/subtitle (always reflects login state on load)
  const ft = document.getElementById('formTitle');
  const fs = document.getElementById('formSub');
  if (ft && !ft.dataset.manuallySet) {
    ft.textContent = t('formTitleLogin');
    fs.textContent = t('formSubLogin');
  }
  // Update autocomplete search placeholder
  const acIn = document.getElementById('acInput');
  if (acIn) acIn.placeholder = t('txPlaceholderSearch');
  // Update dashboard greeting if logged in
  if (me) {
    document.getElementById('dashGreet').textContent = t('dashGreet') + ', ' + me.username;
    document.getElementById('dType').textContent = me.is_admin ? t('dashTypeAdmin') : t('dashTypeStandard');
  }
}

function updateLangButtons() {
  document.querySelectorAll('.langBtn').forEach(b => b.classList.toggle('on', b.dataset.lang === curLang));
}
function setLang(lang) { loadLang(lang); }

/* ── 3. Gallery carousel — reads /api/gallery (directory scan) */
let gcImages = [], gcCur = 0, gcAuto;

async function loadGallery() {
  try {
    const r = await fetch(\'/bank/api/gallery\', { headers: { 'ngrok-skip-browser-warning': '1' } });
    if (!r.ok) throw new Error();
    gcImages = await r.json();
  } catch (e) {
    gcImages = [];
  }
  buildGallery();
}

function buildGallery() {
  const track   = document.getElementById('gcTrack');
  const emptyEl = document.getElementById('gcEmpty');
  const dots    = document.getElementById('gcDots');
  const thumbs  = document.getElementById('gcThumbs');
  const prevBtn = document.getElementById('gcPrev');
  const nextBtn = document.getElementById('gcNext');
  const counter = document.getElementById('gcCounter');

  if (!gcImages.length) {
    if (track)   track.innerHTML = '';
    if (emptyEl) emptyEl.style.display = '';
    if (dots)    dots.innerHTML = '';
    if (thumbs)  thumbs.innerHTML = '';
    if (prevBtn) prevBtn.style.display = 'none';
    if (nextBtn) nextBtn.style.display = 'none';
    if (counter) counter.style.display = 'none';
    return;
  }

  if (emptyEl) emptyEl.style.display = 'none';
  if (counter) counter.style.display = '';

  // Slides — object-fit:contain shows full image without cropping
  track.innerHTML = gcImages.map((img, i) => `
    <div class="gcSlide" data-idx="${i}">
      <img src="${img.url}" alt=""
        loading="${i === 0 ? 'eager' : 'lazy'}" decoding="async">
    </div>
  `).join('');

  // Dot indicators
  dots.innerHTML = gcImages.map((_, i) =>
    `<div class="gcDot ${i === 0 ? 'on' : ''}" onclick="gcGoTo(${i})"></div>`
  ).join('');

  // Thumbnail strip
  thumbs.innerHTML = gcImages.map((img, i) => `
    <div class="gcThumb ${i === 0 ? 'on' : ''}" onclick="gcGoTo(${i})" data-idx="${i}">
      <img src="${img.url}" alt="" loading="lazy" decoding="async">
    </div>
  `).join('');

  if (prevBtn) prevBtn.style.display = gcImages.length > 1 ? '' : 'none';
  if (nextBtn) nextBtn.style.display = gcImages.length > 1 ? '' : 'none';

  // Touch swipe
  const frame = document.getElementById('gcFrame');
  if (frame) {
    let tx = 0;
    frame.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
    frame.addEventListener('touchend',   e => {
      const dx = e.changedTouches[0].clientX - tx;
      if (Math.abs(dx) > 40) gcNav(dx < 0 ? 1 : -1);
    }, { passive: true });
  }

  // Keyboard arrows (only when gallery tab is active)
  document.addEventListener('keydown', e => {
    if (!document.getElementById('view-gallery')?.classList.contains('on')) return;
    if (e.key === 'ArrowLeft')  gcNav(-1);
    if (e.key === 'ArrowRight') gcNav(1);
  });

  gcGoTo(0, true);
  if (gcImages.length > 1) gcStartAuto();
}

function gcGoTo(idx, immediate) {
  gcCur = (idx + gcImages.length) % gcImages.length;
  const track = document.getElementById('gcTrack');
  const frame = document.getElementById('gcFrame');
  if (track && frame) {
    // Use offsetWidth; if 0 (hidden view), defer until visible
    const frameW = frame.offsetWidth;
    if (frameW === 0) {
      // Gallery is hidden — store index and apply when it becomes visible
      gcCur = idx;
      return;
    }
    if (immediate) { track.style.transition = 'none'; }
    track.style.transform = `translateX(-${gcCur * frameW}px)`;
    if (immediate) requestAnimationFrame(() => { track.style.transition = ''; });
  }
  const ctr = document.getElementById('gcCounter');
  if (ctr) ctr.textContent = `${gcCur + 1} / ${gcImages.length}`;
  document.querySelectorAll('.gcDot').forEach((d, i) => d.classList.toggle('on', i === gcCur));
  document.querySelectorAll('.gcThumb').forEach((th, i) => {
    th.classList.toggle('on', i === gcCur);
    if (i === gcCur) th.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  });
  gcStartProgress();
  gcStartAuto();
}

function gcNav(dir) { gcGoTo(gcCur + dir); }

// Recalculate position on window resize (pixel-based offset must stay correct)
window.addEventListener('resize', () => {
  if (gcImages.length > 0) gcGoTo(gcCur, true);
});

function gcStartProgress() {
  const bar = document.getElementById('gcProgress');
  if (!bar || gcImages.length <= 1) return;
  bar.style.transition = 'none';
  bar.style.width = '0%';
  requestAnimationFrame(() => {
    bar.style.transition = 'width 6s linear';
    bar.style.width = '100%';
  });
}

function gcStartAuto() {
  clearInterval(gcAuto);
  if (gcImages.length > 1) gcAuto = setInterval(() => gcNav(1), 6000); // 4.5s + 1.5s = 6s
}

/* ── 4. API helper ──────────────────────────────────────── */
const API = location.origin;
let token = localStorage.getItem('dvd_token');
let me    = null;
const ADMINS = new Set(['dvd', 'nina', 'victor', 'yu','roy', 'admin','aitor']);

// Token refresh tracking
let _tokenRefreshInProgress = false;
let _tokenRefreshTime = parseInt(localStorage.getItem('dvd_token_refreshed_at') || '0');

async function refreshTokenIfNeeded() {
  if (!token || _tokenRefreshInProgress) return;

  // Check if token needs refresh (every 1 hour)
  const now = Date.now();
  const hourInMs = 3600000;
  if (now - _tokenRefreshTime < hourInMs) return;

  _tokenRefreshInProgress = true;
  try {
    // FIX: correct path is /bank/api/me/refresh-token (was missing /bank prefix)
    const ctrl = new AbortController();
    const tid = setTimeout(() => ctrl.abort(), 8000);
    const r = await fetch(API + '/bank/api/me/refresh-token', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token },
      signal: ctrl.signal
    });
    clearTimeout(tid);

    if (r.ok) {
      const d = await r.json();
      token = d.token;
      localStorage.setItem('dvd_token', token);
      _tokenRefreshTime = Date.now();
      localStorage.setItem('dvd_token_refreshed_at', _tokenRefreshTime.toString());
      console.log('[Token] Refreshed successfully');
    } else if (r.status === 401) {
      console.log('[Token] Expired, logging out');
      token = null;
      localStorage.removeItem('dvd_token');
      localStorage.removeItem('dvd_token_refreshed_at');
      doLogout();
    }
    // Any other status (404, 500…) → silently skip, keep existing token
  } catch (e) {
    // AbortError (timeout) or network error → skip refresh, keep existing token
    console.warn('[Token] Refresh skipped:', e.name === 'AbortError' ? 'timeout' : e.message);
  } finally {
    _tokenRefreshInProgress = false;
  }
}

async function req(method, path, body, timeoutMs) {
  // Refresh token if needed before making API call (skip for login/register)
  const isAuthCall = path === '/bank/api/login' || path === '/bank/api/register';
  if (!isAuthCall) await refreshTokenIfNeeded();

  // Abort after timeoutMs (default 15s) so the spinner never hangs forever
  const ms = timeoutMs || 15000;
  const ctrl = new AbortController();
  const tid = setTimeout(() => ctrl.abort(), ms);

  let r;
  try {
    r = await fetch(API + path, {
      method,
      headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': '1', ...(token ? { 'Authorization': 'Bearer ' + token } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
      signal: ctrl.signal
    });
  } catch (e) {
    clearTimeout(tid);
    if (e.name === 'AbortError') throw new Error('El servidor tardó demasiado. Inténtalo de nuevo.');
    throw new Error('No se pudo conectar al servidor. Comprueba tu conexión.');
  }
  clearTimeout(tid);

  let d;
  try { d = await r.json(); } catch(e) {
    throw new Error('Error del servidor (' + r.status + '). Comprueba que el servidor está activo.');
  }
  if (!r.ok) {
    // If 401, token is invalid — logout
    if (r.status === 401) {
      token = null;
      localStorage.removeItem('dvd_token');
      localStorage.removeItem('dvd_token_refreshed_at');
      doLogout();
    }
    throw new Error(d.detail || t('errorLoading'));
  }
  return d;
}

function showAlert(id, msg, type) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'alert on a' + (type || 'e');
  el.textContent = msg;
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('on'), 6500);
}

const fmtDate = s => !s ? '—' : new Date(s + 'Z').toLocaleString('fr-FR', {
  day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false
});
const fmtC = n => (+n).toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 4 });
function fmtDuration(s) {
  if (!s || s < 60) return s ? s + 's' : '—';
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function setLoading(id, label) {
  const b = document.getElementById(id);
  if (!b) return () => {};
  b.disabled = true;
  b.innerHTML = `<span class="sp"></span>${t('btnProcessing')}`;
  return () => { b.disabled = false; b.textContent = label; };
}

/* ── 5. Auth functions ──────────────────────────────────── */
function authTab(which, el) {
  document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('on'));
  el.classList.add('on');
  document.getElementById('fLogin').classList.toggle('hidden', which !== 'login');
  document.getElementById('fReg').classList.toggle('hidden', which !== 'reg');
  document.getElementById('authAlert').classList.remove('on');
  const ft = document.getElementById('formTitle');
  const fs = document.getElementById('formSub');
  ft.textContent = t(which === 'login' ? 'formTitleLogin' : 'formTitleRegister');
  fs.textContent = t(which === 'login' ? 'formSubLogin'   : 'formSubRegister');
  ft.dataset.manuallySet = '1';
}

async function doLogin() {
  console.log('[DEBUG] doLogin called');
  const u = (document.getElementById('lU').value || '').trim().toLowerCase();
  const p = document.getElementById('lP').value || '';
  console.log('[DEBUG] Username:', u, 'Password length:', p.length);
  if (!u || !p) return showAlert('authAlert', t('errorUsernamePassword'));
  const done = setLoading('btnL', t('btnLogin'));
  try {
    console.log('[DEBUG] Calling API:', '/bank/api/login');
    const d = await req('POST', '/bank/api/login', { username: u, password: p });
    console.log('[DEBUG] Login response:', d);
    token = d.token;
    localStorage.setItem('dvd_token', token);
    await loadApp();
    // Solo solicitar permisos de notificaciones, NO audio/video
    _requestNotificationPermission();
  } catch (e) { 
    console.error('[DEBUG] Login error:', e);
    showAlert('authAlert', e.message); 
  }
  finally { done(); }
}

async function doReg() {
  console.log('[DEBUG] doReg called');
  
  // Obtener valores
  const u = (document.getElementById('rU').value || '').trim().toLowerCase();
  const p = document.getElementById('rP').value || '';
  const pConfirm = document.getElementById('rPConfirm').value || '';
  const email = (document.getElementById('rEmail').value || '').trim();
  const fullName = (document.getElementById('rFullName').value || '').trim();
  const phone = (document.getElementById('rPhone').value || '').trim();
  const opoInterest = document.getElementById('rOpoInterest').checked;
  const terms = document.getElementById('rTerms').checked;
  
  // Validaciones
  if (!u || !p || !email) {
    return showAlert('authAlert', 'Por favor completa todos los campos obligatorios (*)');
  }
  
  if (!terms) {
    return showAlert('authAlert', 'Debes aceptar los términos y condiciones');
  }
  
  if (p.length < 4) {
    return showAlert('authAlert', 'La contraseña debe tener al menos 4 caracteres');
  }
  
  if (p !== pConfirm) {
    return showAlert('authAlert', 'Las contraseñas no coinciden');
  }
  
  // Validar email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return showAlert('authAlert', 'Por favor ingresa un email válido');
  }
  
  const done = setLoading('btnR', t('btnRegister'));
  
  try {
    console.log('[DEBUG] Calling API:', '/bank/api/register');
    const d = await req('POST', '/bank/api/register', { 
      username: u, 
      password: p,
      email: email,
      full_name: fullName,
      phone: phone,
      opo_interest: opoInterest
    });
    console.log('[DEBUG] Register response:', d);
    
    // Si el registro requiere verificación de email
    if (d.requires_verification) {
      showAlert('authAlert', 
        '✅ Cuenta creada! Revisa tu email para verificar tu cuenta.', 
        's'
      );
      // Cambiar a tab de login después de 3 segundos
      setTimeout(() => {
        authTab('login', document.querySelector('.tab'));
      }, 3000);
    } else {
      // Login automático si no requiere verificación
      token = d.token;
      localStorage.setItem('dvd_token', token);
      await loadApp();
      _requestNotificationPermission();
    }
  } catch (e) { 
    console.error('[DEBUG] Register error:', e);
    showAlert('authAlert', e.message); 
  }
  finally { done(); }
}

function doLogout() {
  stopHeartbeat(); stopAdmRefresh();
  token = null; me = null;
  localStorage.removeItem('dvd_token');
  document.getElementById('authWrap').classList.remove('hidden');
  document.getElementById('authHdr').classList.remove('hidden');  // show auth header
  document.getElementById('app').classList.add('hidden');
  document.getElementById('lU').value = '';
  document.getElementById('lP').value = '';
  const ft = document.getElementById('formTitle');
  if (ft) { ft.textContent = t('formTitleLogin'); delete ft.dataset.manuallySet; }
}

/* ── 6. App loader ──────────────────────────────────────── */
async function loadApp() {
  try {
    me = await req('GET', '/bank/api/me', null, 12000);  // 12s timeout — never hang
    // Load language preference from DB (overrides localStorage)
    if (me.lang && me.lang !== curLang) {
      await loadLang(me.lang);
    }
    document.getElementById('authWrap').classList.add('hidden');
    document.getElementById('authHdr').classList.add('hidden');   // hide auth header
    document.getElementById('app').classList.remove('hidden');
    document.getElementById('hUser').textContent   = '@' + me.username;
    document.getElementById('hBal').textContent    = fmtC(me.balance) + ' ◆';
    document.getElementById('dBal').textContent    = fmtC(me.balance);
    document.getElementById('dUser').textContent   = me.username;
    document.getElementById('dSince').textContent  = fmtDate(me.created_at).split(',')[0];
    document.getElementById('dType').textContent   = me.is_admin ? t('dashTypeAdmin') : t('dashTypeStandard');
    document.getElementById('dashGreet').textContent = t('dashGreet') + ', ' + me.username;

    try {
      const mn = document.getElementById('mobileNav');

      // Social tab visible for ALL members
      ['navSocial','mobileNavSocial'].forEach(id =>
        document.getElementById(id)?.classList.remove('hidden')
      );

      // OPO tab visible for users with opo_interest or opo_access
      if (me.opo_interest || me.opo_access) {
        document.getElementById('navOpo')?.classList.remove('hidden');
      }

      if (me.is_admin) {
        // ── ADMIN / SUPERADMIN ─────────────────────────────────────
        ['hAdm', 'navAdm', 'mobileNavAdm'].forEach(id =>
          document.getElementById(id)?.classList.remove('hidden')
        );
        document.getElementById('navHist')?.classList.add('hidden');
        document.getElementById('mobileNavHist')?.classList.add('hidden');
        document.getElementById('dashRecentSection')?.classList.add('hidden');
        if (me.is_superadmin) {
          document.getElementById('navStats')?.classList.remove('hidden');
          document.getElementById('histAdvancedStatsPanel')?.style.setProperty('display','');
          document.getElementById('socialAdminPanel')?.style.setProperty('display','');
        }
        if (mn) mn.style.gridTemplateColumns = 'repeat(5,1fr)';
      } else {
        // ── MEMBER ────────────────────────────────────────────────
        // Historial oculto para todos los miembros
        document.getElementById('navHist')?.classList.add('hidden');
        document.getElementById('mobileNavHist')?.classList.add('hidden');
        ['hAdm','navAdm','mobileNavAdm','navStats'].forEach(id =>
          document.getElementById(id)?.classList.add('hidden')
        );
        document.getElementById('view-adm')?.classList.remove('on');
        if (mn) mn.style.gridTemplateColumns = 'repeat(5,1fr)';
      }
    } catch(e) { console.warn('nav setup error', e); }
    // Recalcular columnas del nav móvil según botones visibles
    setTimeout(_recalcMobileNav, 200);

    startHeartbeat();
    if (me.is_admin) startAdmRefresh();
    startGameStatusPolling();
    _startUnreadPolling();

    // Conectar WS de salas (dedicado, siempre activo) y WS de mensajes
    _roomsWsConnect();
    _roomsSseConnect();   // SSE — tiempo real garantizado
    socialConnectWS().catch(()=>{});
    _startRoomsPolling();
    // Use server-side rendered rooms immediately (no waiting for polling)
    if(window._pendingRooms && window._pendingRooms.length > 0){
      _renderRoomsList(window._pendingRooms);
      window._pendingRooms = null;
    }
    // Fetch inmediato de salas por REST como primer dato visible
    _refreshRoomsList();

    // Fire status checks — all wrapped, no crash propagation
    // Members only get game tabs when games are ENABLED (handled inside each check fn)
    await Promise.all([
      loadDropdown().catch(()=>{}),
      checkGameStatus().catch(()=>{}),
      checkMillonarioStatus().catch(()=>{}),
      checkQuienSoyStatus().catch(()=>{}),
      checkCifrasLetrasStatus().catch(()=>{}),
      checkHundirLaFlotaStatus().catch(()=>{}),
      checkRoomsStatus().catch(()=>{}),
      checkCuentosStatus().catch(()=>{}),
      ...(me.is_admin ? [] : [loadHist('dashH', 10).catch(()=>{}), loadUserApuestas().catch(()=>{})])
    ]);

    // Show admin-only panels
    try {
      if (me.is_superadmin) {
        document.getElementById('panelGameBtns')?.style.setProperty('display', '');
        document.getElementById('panelActivity')?.style.setProperty('display', '');
        document.getElementById('panelAdminMgmt')?.style.setProperty('display', '');
        loadAdminMgmt().catch(()=>{});
        document.getElementById('dashDvdStats')?.style.setProperty('display', '');
        loadOpoDash().catch(()=>{});
        loadDvdStats().catch(()=>{});
      }
      // Change password — all users
      document.getElementById('dashChangePwd')?.style.setProperty('display', '');
      // Contact & notifications panel — all users
      document.getElementById('dashContactPanel')?.style.setProperty('display', '');
      loadContactInfo();
      // Social admin panel for superadmin
      if (me.is_superadmin) document.getElementById('socialAdminPanel')?.style.setProperty('display','');
    } catch(e) { console.warn('panel setup error', e); }

    // Handle ?join=room_key in URL — auto-join a room from a direct link
    const _joinKey = new URLSearchParams(location.search).get('join');
    if(_joinKey){
      // Remove the param from URL without reload
      history.replaceState({}, '', location.pathname);
      // Navigate to Social and join after a short delay
      setTimeout(async ()=>{
        nav('social', document.getElementById('navSocial'));
        await new Promise(r=>setTimeout(r,400));
        // Get room title from active rooms
        try{
          const d = await req('GET', '/api/rooms/active');
          const room = (d.rooms||[]).find(r=>r.key===_joinKey);
          if(room) socialJoinRoom(_joinKey, room.title||_joinKey);
          else socialJoinRoom(_joinKey, _joinKey);
        }catch(e){ socialJoinRoom(_joinKey, _joinKey); }
      }, 600);
    }

  } catch (e) {
    console.error('loadApp error:', e);
    // Only logout if we never managed to get user data
    if (!me) doLogout();
  }
}

/* ── 7. Transfer ────────────────────────────────────────── */
/* ── 7. Transfer — autocomplete recipient search ─────────── */

// In-memory user list, loaded once per session and refreshed after each transfer
let acAllUsers = [];   // [{name, isAdmin}]
let acFocusIdx = -1;   // keyboard navigation index in dropdown

// Load all users into memory (called on nav to transfer tab and after transfers)
async function loadDropdown() {
  try {
    const users = await req('GET', '/api/users');
    acAllUsers = users.map(u => ({ name: u, isAdmin: ADMINS.has(u) }));
  } catch (e) { /* silent — list stays stale */ }
}

// Highlight matching substring inside a name
function acHighlight(name, query) {
  if (!query) return name;
  const idx = name.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return name;
  return name.slice(0, idx)
    + '<mark>' + name.slice(idx, idx + query.length) + '</mark>'
    + name.slice(idx + query.length);
}

// Render dropdown results for current input value
function acRender() {
  const query   = (document.getElementById('acInput').value || '').trim().toLowerCase();
  const dropdown = document.getElementById('acDropdown');
  acFocusIdx = -1;

  if (!query) { dropdown.classList.remove('open'); return; }

  const matches = acAllUsers.filter(u => u.name.toLowerCase().includes(query));

  if (!matches.length) {
    dropdown.innerHTML = `<div class="acNoResult">${t('txNoResults') || 'No users found'}</div>`;
    dropdown.classList.add('open');
    return;
  }

  dropdown.innerHTML = matches.map((u, i) => `
    <div class="acItem" data-idx="${i}" data-name="${u.name}"
      onmousedown="acPick('${u.name}')"
      onmouseover="acHover(${i})">
      <span class="acItemAt">@</span>
      <span class="acItemName">${acHighlight(u.name, query)}</span>
      ${u.isAdmin ? `<span class="acItemBadge">Admin ◆</span>` : ''}
    </div>
  `).join('');
  dropdown.classList.add('open');
}

// Called every time the user types
function acOnInput() {
  const input = document.getElementById('acInput');
  const clear = document.getElementById('acClear');
  // If there's a confirmed selection, reset it when user starts typing again
  acClearSelection(false);
  clear.style.display = input.value ? 'block' : 'none';
  acRender();
}

// Called on input focus — re-show dropdown if text is present
function acOnFocus() {
  if (document.getElementById('acInput').value) acRender();
}

// Keyboard navigation: arrows move focus, Enter selects, Escape closes
function acOnKey(e) {
  const dropdown = document.getElementById('acDropdown');
  const items = dropdown.querySelectorAll('.acItem');
  if (!items.length) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    acFocusIdx = Math.min(acFocusIdx + 1, items.length - 1);
    acUpdateFocus(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    acFocusIdx = Math.max(acFocusIdx - 1, 0);
    acUpdateFocus(items);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (acFocusIdx >= 0 && items[acFocusIdx]) {
      acPick(items[acFocusIdx].dataset.name);
    } else if (items.length === 1) {
      acPick(items[0].dataset.name); // auto-pick if only one result
    }
  } else if (e.key === 'Escape') {
    acClose();
  }
}

function acHover(idx) {
  acFocusIdx = idx;
  const items = document.getElementById('acDropdown').querySelectorAll('.acItem');
  acUpdateFocus(items);
}

function acUpdateFocus(items) {
  items.forEach((item, i) => item.classList.toggle('focused', i === acFocusIdx));
  if (items[acFocusIdx]) items[acFocusIdx].scrollIntoView({ block: 'nearest' });
}

// Confirm a user selection
function acPick(name) {
  document.getElementById('txTo').value = name;

  // Show confirmed badge
  const user = acAllUsers.find(u => u.name === name);
  const selectedEl   = document.getElementById('acSelected');
  const selectedName = document.getElementById('acSelectedName');
  selectedName.innerHTML = '@' + name
    + (user?.isAdmin ? ' <span class="acSelectedAdmin">Admin ◆</span>' : '');
  selectedEl.style.display = 'flex';

  // Hide and clear the search input
  const input = document.getElementById('acInput');
  input.value = '';
  input.style.display = 'none';
  document.getElementById('acClear').style.display = 'none';
  acClose();

  // Move focus to amount field
  setTimeout(() => document.getElementById('txAmt').focus(), 50);
}

// Clear the confirmed selection and restore search input
function acReset() {
  acClearSelection(true);
  document.getElementById('acInput').focus();
}

function acClearSelection(restoreInput) {
  document.getElementById('txTo').value = '';
  document.getElementById('acSelected').style.display = 'none';
  if (restoreInput) {
    const input = document.getElementById('acInput');
    input.style.display = '';
    input.value = '';
    document.getElementById('acClear').style.display = 'none';
  }
}

function acClose() {
  document.getElementById('acDropdown').classList.remove('open');
  acFocusIdx = -1;
}

// Close dropdown when clicking outside
document.addEventListener('click', e => {
  if (!document.getElementById('acWrap')?.contains(e.target)) acClose();
});

async function doTransfer() {
  const to  = (document.getElementById('txTo').value || '').trim();
  // Accept both comma and dot as decimal separator (type=number always uses dot)
  const rawAmt = String(document.getElementById('txAmt').value || '').trim().replace(',', '.');
  const amt = parseFloat(rawAmt);
  const con = (document.getElementById('txCon').value || '').trim();
  if (!to)                    return showAlert('txAlert', t('errorSelectRecipient'));
  if (!amt || amt <= 0 || isNaN(amt)) return showAlert('txAlert', t('errorValidAmount'));
  const done = setLoading('btnTx', t('txBtn'));
  try {
    const d = await req('POST', '/api/transfer', { to_user: to, amount: amt, concept: con });
    showAlert('txAlert', d.message, 's');
    // Clear fields and reset autocomplete
    document.getElementById('txAmt').value = '';
    document.getElementById('txCon').value = '';
    acReset();
    document.getElementById('acInput').style.display = '';
    document.getElementById('hBal').textContent = fmtC(d.new_balance) + ' ◆';
    document.getElementById('dBal').textContent = fmtC(d.new_balance);
    if (d.auto_created) await loadDropdown(); // refresh user list if new user was created
  } catch (e) { showAlert('txAlert', e.message); }
  finally { done(); }
}

/* ── 8. Transactions ────────────────────────────────────── */
function renderTx(id, txs) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!txs?.length) { el.innerHTML = `<div class="empty">${t('histEmpty')}</div>`; return; }
  el.innerHTML = txs.map(tx => {
    const fromAdmin = ADMINS.has(tx.from_user);
    const isIn = tx.to_user === me.username;

    // Detectar transacciones de apuestas
    const isApuesta = tx.concept && tx.concept.includes('Apuesta porra');
    const isPremio = tx.concept && tx.concept.includes('Ganador porra');

    let cls, ico, sign;

    if (isApuesta) {
      // Apuesta realizada (salida de dinero)
      cls = 'out';
      ico = '🎲';
      sign = '−';
    } else if (isPremio) {
      // Premio ganado (entrada de dinero)
      cls = 'in';
      ico = '🏆';
      sign = '+';
    } else {
      // Transacción normal
      cls  = fromAdmin && !isIn ? 'adm' : isIn ? 'in' : 'out';
      ico  = cls === 'adm' ? '◆' : cls === 'in' ? '↙' : '↗';
      sign = isIn ? '+' : '−';
    }

    return `<div class="txItem">
      <div class="txBadge ${cls}">${ico}</div>
      <div class="txInfo">
        <div class="txPair">${tx.from_user}<span class="txArrow">→</span>${tx.to_user}</div>
        <div class="txCon">${tx.concept || t('histNoRef')}</div>
        <div class="txDt">${fmtDate(tx.created_at)}</div>
      </div>
      <div class="txAmt ${cls}">${sign}${fmtC(tx.amount)} ◆</div>
    </div>`;
  }).join('');
}

async function loadHist(id, limit) {
  try {
    const txs = await req('GET', '/api/history?limit=' + Math.min(limit || 100, 1000));
    renderTx(id, txs);
  } catch (e) {
    document.getElementById(id).innerHTML = `<div class="empty">${t('errorLoading')}</div>`;
  }
}

/* ── Load user betting stats for dashboard ─────────────────────────────── */
async function loadUserApuestas() {
  const section = document.getElementById('dashApuestasSection');
  const el = document.getElementById('dashApuestas');
  if (!el || !section) return;

  try {
    const stats = await req('GET', '/api/porras/mis-estadisticas');

    // Show section only if user has betting activity
    if (stats.total_apostado > 0 || stats.apuestas_activas > 0) {
      section.style.display = '';

      const gananciaColor = stats.ganancia_neta >= 0 ? 'var(--green)' : 'var(--red)';
      const gananciaSign = stats.ganancia_neta >= 0 ? '+' : '';

      el.innerHTML = `
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Apostado</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--gold2)">${fmtC(stats.total_apostado)} ◆</div>
        </div>
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Ganancia</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:${gananciaColor}">${gananciaSign}${fmtC(stats.ganancia_neta)} ◆</div>
        </div>
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Activas</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--gold2)">${stats.apuestas_activas}</div>
        </div>
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Ganadas</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--green)">${stats.porras_ganadas}</div>
        </div>
      `;
    } else {
      section.style.display = 'none';
    }
  } catch (e) {
    section.style.display = 'none';
  }
}

/* ── 9. Admin panel ─────────────────────────────────────── */
/* ── Heartbeat: POST /api/ping every 30 s ─────────────────────────────── */
let _pingIv = null;
function startHeartbeat() {
  if (_pingIv) return;
  const doPing = () => { if (me) req('POST', '/api/ping').catch(() => {}); };
  doPing();
  _pingIv = setInterval(doPing, 30000);
}
function stopHeartbeat() { if (_pingIv) { clearInterval(_pingIv); _pingIv = null; } }

/* ── Auto-refresh admin table every 30 s ──────────────────────────────── */
let _admIv = null;
function startAdmRefresh() {
  if (_admIv) return;
  _admIv = setInterval(() => {
    if (document.getElementById('view-adm')?.classList.contains('on')) loadAdmin();
  }, 30000);
}

// Poll game status every 10 s so navGame tab appears when admin enables a game
let _gameStatusIv = null;
function startGameStatusPolling() {
  if (_gameStatusIv) return;
  _gameStatusIv = setInterval(() => {
    checkGameStatus().catch(()=>{});
    checkMillonarioStatus().catch(()=>{});
    checkQuienSoyStatus().catch(()=>{});
    checkCifrasLetrasStatus().catch(()=>{});
    checkHundirLaFlotaStatus().catch(()=>{});
    checkRoomsStatus().catch(()=>{});   // salas — mismo patrón que juegos
  }, 10000);
}
function stopAdmRefresh() { if (_admIv) { clearInterval(_admIv); _admIv = null; } }

/* ── Admin table sort state ─────────────────────────────────────────────── */
let _admUsers   = [];   // full user list from last fetch
let _admSortCol = 'username';
let _admSortDir = 1;    // 1 = asc, -1 = desc

function admSort(col) {
  if (_admSortCol === col) {
    _admSortDir = -_admSortDir;
  } else {
    _admSortCol = col;
    _admSortDir = col === 'balance' ? -1 : 1;
  }
  _admRender();
  // Update header arrows
  document.querySelectorAll('.tbl th.sortable').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.col === col) th.classList.add(_admSortDir === 1 ? 'sort-asc' : 'sort-desc');
  });
  // Sync sort pills
  const pillMap = {username:'admPillName', balance:'admPillBalance', role:'admPillRole', status:'admPillStatus', joined:'admPillJoined'};
  document.querySelectorAll('[id^="admPill"]').forEach(p => p.classList.remove('on'));
  const pill = pillMap[col];
  if (pill) document.getElementById(pill)?.classList.add('on');
}

function _admSortValue(u, col) {
  switch (col) {
    case 'username':  return u.username.toLowerCase();
    case 'balance':   return u.balance;
    case 'role':      return u.is_admin ? 0 : 1;
    case 'status':    return u.is_blocked ? 2 : (u.locked_until && new Date(u.locked_until+'Z') > new Date() ? 1 : 0);
    case 'failed':    return u.failed_attempts || 0;
    case 'joined':    return u.created_at || '';
    case 'lastseen':  return u.last_ping_at || 0;
    default:          return '';
  }
}

function fmtLastSeen(epoch) {
  if (!epoch) return '<span style="color:var(--text3);font-size:.7rem">—</span>';
  // Ensure epoch is a number (handle both seconds and milliseconds)
  const timestamp = typeof epoch === 'string' ? parseFloat(epoch) : epoch;
  if (!timestamp || isNaN(timestamp)) return '<span style="color:var(--text3);font-size:.7rem">—</span>';

  // If timestamp is in milliseconds (> year 2100 in seconds), convert to seconds
  const epochSeconds = timestamp > 4102444800 ? Math.floor(timestamp / 1000) : timestamp;

  const diff = Math.floor((Date.now()/1000) - epochSeconds);
  const d = new Date(epochSeconds * 1000);
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  const date = d.toLocaleDateString([], { day: '2-digit', month: '2-digit' });
  const isToday = new Date().toDateString() === d.toDateString();
  const label   = isToday ? time : `${date} ${time}`;
  if (diff < 90)   return `<span style="color:var(--green);font-size:.72rem">● ${label}</span>`;
  if (diff < 3600) return `<span style="font-size:.72rem;color:var(--text2)">${label} <span style="opacity:.6">(${Math.floor(diff/60)}m)</span></span>`;
  return `<span style="font-size:.72rem;color:var(--text3)">${label}</span>`;
}

function _admRender() {
  const isSuperAdmin = !!(me.is_superadmin);
  const searchQ = (document.getElementById('admSearch')?.value || '').trim().toLowerCase();
  // Regular admins only see non-admin members; superadmins see everyone
  const visible = isSuperAdmin ? _admUsers : _admUsers.filter(u => !u.is_admin && !u.is_ghost);
  const filtered = searchQ ? visible.filter(u => u.username.toLowerCase().includes(searchQ)) : visible;
  const sorted = [...filtered].sort((a, b) => {
    const av = _admSortValue(a, _admSortCol);
    const bv = _admSortValue(b, _admSortCol);
    if (av < bv) return -_admSortDir;
    if (av > bv) return  _admSortDir;
    return 0;
  });
  const countEl = document.getElementById('admCount');
  if (countEl) countEl.textContent = searchQ ? `${sorted.length} / ${visible.length}` : `${visible.length} miembros`;
  const isDvd = isSuperAdmin;

  document.getElementById('admTbl').innerHTML = sorted.map(u => {
    const isBlocked  = !!u.is_blocked;
    const isLocked   = !isBlocked && u.locked_until && new Date(u.locked_until + 'Z') > new Date();
    const canUnblock = isBlocked || isLocked;
    const isReg      = u.registered !== false;
    const isGhost    = !!u.is_ghost;  // ghost admin — only dvd can see & manage

    const dot = u.online
      ? `<span class="onlineDot"  title="Online"></span>`
      : `<span class="offlineDot" title="Offline"></span>`;

    const nameCell = isGhost
      ? `<td style="color:var(--gold);font-weight:500;opacity:.7">${u.username} <span style="font-size:.6rem;opacity:.6">👻</span></td>`
      : isReg
        ? `<td style="color:var(--text);font-weight:500">${u.username}</td>`
        : `<td style="color:var(--text3);font-style:italic">${u.username} <span style="font-size:.68rem">(unregistered)</span></td>`;

    const statusBadge = isBlocked
      ? `<span class="bdg bdgR">${t('admStatusBlocked')}</span>`
      : isLocked
        ? `<span class="bdg bdgR">${t('admStatusLocked')}</span>`
        : `<span class="bdg bdgG">${t('admStatusActive')}</span>`;

    const notSelf  = u.username !== me.username;
    // dvd can fully manage ghost (admin user) just like any other user
    const blockBtn = isDvd && canUnblock
      ? `<button class="btn btnO btnSm" onclick="admAct('unblock','${u.username}')">${t('admBtnUnblock')}</button>`
      : isDvd && notSelf
        ? `<button class="btn btnD btnSm" onclick="admAct('block','${u.username}')">${t('admBtnBlock')}</button>`
        : '';
    const resetBtn  = isDvd && notSelf
      ? `<button class="btn btnS btnSm" onclick="admAct('reset-pwd','${u.username}')">${t('admBtnResetPwd')}</button>`
      : '';
    const deleteBtn = isDvd && !u.is_admin && !isGhost && notSelf
      ? `<button class="btn btnDel btnSm" onclick="admDelete('${u.username}')">Delete</button>`
      : '';

    return `<tr style="${isGhost ? 'opacity:.55' : (isReg ? '' : 'opacity:.5')}">
      <td style="padding:4px 2px;text-align:center">${dot}</td>
      ${nameCell}
      <td style="font-family:'Playfair Display',serif;color:var(--gold2)">${fmtC(u.balance)} ◆</td>
      ${isSuperAdmin ? `<td>${u.is_superadmin ? '<span class="bdg bdgY" style="background:rgba(212,168,67,.2)">⭐ super</span>' : u.is_admin || isGhost ? '<span class="bdg bdgY">'+t('admRoleAdmin')+'</span>' : '<span class="bdg bdgG">'+t('admRoleMember')+'</span>'}</td>` : ''}
      <td>${isGhost ? '<span class="bdg" style="color:var(--gold);border-color:rgba(212,168,67,.3);background:rgba(212,168,67,.07)">👻 ghost</span>' : statusBadge}</td>
      <td style="color:var(--text3);text-align:center">${u.failed_attempts || 0}</td>
      <td style="color:var(--text3)">${fmtDate(u.created_at).split(',')[0]}</td>
      ${isSuperAdmin ? `<td>${fmtLastSeen(u.last_ping_at)}</td>` : ''}
      <td style="display:flex;gap:5px;flex-wrap:wrap">${blockBtn}${resetBtn}${deleteBtn}</td>
    </tr>`;
  }).join('');
}

async function loadAdmin() {
  try {
    _admUsers = await req('GET', '/api/admin/users');
    // Show/hide Last seen column + fix colspan (dvd only)
    const isDvdUser = !!(me.is_superadmin);
    const thLS = document.getElementById('thLastSeen');
    if (thLS) thLS.style.display = isDvdUser ? '' : 'none';
    const emptyRow = document.querySelector('#admTbl td[colspan]');
    if (emptyRow) emptyRow.setAttribute('colspan', isDvdUser ? '9' : '8');
    _admRender();
    // Restore sort arrow after re-render
    document.querySelectorAll('.tbl th.sortable').forEach(th => {
      th.classList.remove('sort-asc', 'sort-desc');
      if (th.dataset.col === _admSortCol)
        th.classList.add(_admSortDir === 1 ? 'sort-asc' : 'sort-desc');
    });
    try { renderActivity(await req('GET', '/api/admin/activity')); } catch(e) {}
    _ldgAll = await req('GET', '/api/admin/ledger?limit=1000');
    ldgApply();
  } catch (e) { showAlert('admAlert', e.message); }
}

/* ── Ledger filter + sort ─────────────────────────────────────── */
let _ldgAll    = [];          // full ledger from last fetch
let _ldgSortCol = 'date';     // 'date' | 'amount' | 'from' | 'to'
let _ldgSortDir = -1;         // -1 = desc (newest first), 1 = asc

function ldgSortBy(col) {
  if (_ldgSortCol === col) {
    _ldgSortDir = -_ldgSortDir;
  } else {
    _ldgSortCol = col;
    // Default directions
    _ldgSortDir = col === 'date' ? -1 : col === 'amount' ? -1 : 1;
  }
  // Update pill styles
  ['Date','Amt','From','To'].forEach(n => {
    const el = document.getElementById('ldgSort' + n.charAt(0).toUpperCase() + n.slice(1).toLowerCase());
    if (el) el.classList.toggle('on', el.id === 'ldgSort' + col.charAt(0).toUpperCase() + col.slice(1).toLowerCase());
  });
  // Easier: just update all pills
  document.querySelectorAll('.sortPill').forEach(p => p.classList.remove('on'));
  const active = {date:'ldgSortDate', amount:'ldgSortAmt', from:'ldgSortFrom', to:'ldgSortTo'}[col];
  if (active) document.getElementById(active)?.classList.add('on');
  ldgApply();
}

function ldgApply() {
  const fromF = (document.getElementById('ldgFrom')?.value  || '').trim().toLowerCase();
  const toF   = (document.getElementById('ldgTo')?.value    || '').trim().toLowerCase();
  const minF  = parseFloat(document.getElementById('ldgMin')?.value) || 0;
  const maxF  = parseFloat(document.getElementById('ldgMax')?.value) || Infinity;

  let filtered = _ldgAll.filter(tx => {
    if (fromF && !tx.from_user.toLowerCase().includes(fromF)) return false;
    if (toF   && !tx.to_user.toLowerCase().includes(toF))     return false;
    if (tx.amount < minF || tx.amount > maxF)                  return false;
    return true;
  });

  filtered.sort((a, b) => {
    let av, bv;
    switch (_ldgSortCol) {
      case 'date':   av = a.created_at; bv = b.created_at; break;
      case 'amount': av = a.amount;     bv = b.amount;     break;
      case 'from':   av = a.from_user;  bv = b.from_user;  break;
      case 'to':     av = a.to_user;    bv = b.to_user;    break;
      default:       av = a.created_at; bv = b.created_at;
    }
    if (av < bv) return -_ldgSortDir;
    if (av > bv) return  _ldgSortDir;
    return 0;
  });

  // Render with ledger mode (always show from→to, no "me" context)
  const el = document.getElementById('ledger');
  if (!el) return;
  const count = document.getElementById('ldgCount');
  if (count) count.textContent = filtered.length
    ? `${filtered.length} / ${_ldgAll.length}`
    : _ldgAll.length ? '0 results' : '';

  if (!filtered.length) {
    el.innerHTML = `<div class="empty">${_ldgAll.length ? 'No matches' : t('histEmpty')}</div>`;
    return;
  }

  el.innerHTML = filtered.map(tx => {
    const fromAdmin = ADMINS.has(tx.from_user);
    const cls  = fromAdmin ? 'adm' : 'out';
    const ico  = fromAdmin ? '◆' : '↗';
    return `<div class="txItem">
      <div class="txBadge ${cls}">${ico}</div>
      <div class="txInfo">
        <div class="txPair"><strong style="color:var(--text)">${tx.from_user}</strong><span class="txArrow">→</span><strong style="color:var(--text)">${tx.to_user}</strong></div>
        <div class="txCon">${tx.concept || t('histNoRef')}</div>
        <div class="txDt">${fmtDate(tx.created_at)}</div>
      </div>
      <div class="txAmt ${cls}">${fmtC(tx.amount)} ◆</div>
    </div>`;
  }).join('');
}

function ldgClear() {
  ['ldgFrom','ldgTo','ldgMin','ldgMax'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  _ldgSortCol = 'date';
  _ldgSortDir = -1;
  document.querySelectorAll('.sortPill').forEach(p => p.classList.remove('on'));
  document.getElementById('ldgSortDate')?.classList.add('on');
  ldgApply();
}

function renderActivity(log) {
  const el = document.getElementById('activityList');
  if (!el) return;
  if (!log || !log.length) { el.innerHTML = '<div class="empty">Sin actividad registrada</div>'; return; }
  const ICONS  = {bank:'⌂', cuentos:'📖', pasapalabra:'🔤', millonario:'💰'};
  const COLORS = {bank:'var(--gold2)', cuentos:'#38B87A', pasapalabra:'#4878D8', millonario:'var(--gold)'};
  el.innerHTML = log.map(a => {
    const icon  = ICONS[a.section]  || '●';
    const color = COLORS[a.section] || 'var(--text2)';
    const dt    = new Date(a.ts * 1000);
    const isToday = new Date().toDateString() === dt.toDateString();
    const tStr  = dt.toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
    const dStr  = dt.toLocaleDateString('fr-FR', {day:'2-digit',month:'2-digit',year:'2-digit'});
    const label = isToday ? tStr : dStr + ' ' + tStr;
    return `<div class="txItem" style="gap:10px">
      <div style="width:28px;height:28px;border-radius:50%;background:rgba(0,0,0,.3);
        border:1px solid ${color};display:flex;align-items:center;justify-content:center;
        font-size:.8rem;flex-shrink:0">${icon}</div>
      <div style="flex:1;min-width:0">
        <div style="font-size:.78rem;color:var(--text);font-weight:500">@${a.username}</div>
        <div style="font-size:.62rem;color:var(--text3);text-transform:uppercase;letter-spacing:.08em">${a.section}</div>
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:.65rem;color:var(--text3);white-space:nowrap">${label}</div>
    </div>`;
  }).join('');
}

async function checkCuentosStatus() {
  try {
    const d = await req('GET', '/api/cuentos/status');
    const on = d.enabled;
    // Show Cuentos tab only for members when enabled; admins use admin panel
    if (!me?.is_admin) {
      ['navCuentos','mobileNavCuentos'].forEach(id =>
        document.getElementById(id)?.classList.toggle('hidden', !on)
      );
    } else {
      ['navCuentos','mobileNavCuentos'].forEach(id =>
        document.getElementById(id)?.classList.add('hidden')
      );
    }
    // Admin panel controls (kept for ctLoad in drawer)
    const sub = document.getElementById('cuentosStatusSub');
    if (sub) sub.textContent = on ? 'Activado — visible para todos' : 'Desactivado';
    const btnOn  = document.getElementById('btnCuentosOn');
    const btnOff = document.getElementById('btnCuentosOff');
    if (btnOn)  btnOn.style.display  = on ? 'none' : '';
    if (btnOff) btnOff.style.display = on ? '' : 'none';
    // Nav tabs: show only when enabled
    ['navCuentos','mobileNavCuentos'].forEach(id => {
      const el = document.getElementById(id);
      if (el) { on ? el.classList.remove('hidden') : el.classList.add('hidden'); }
    });
  } catch(e) {}
}

async function toggleCuentos(enable) {
  try {
    await req('POST', '/api/cuentos/toggle');
    await checkCuentosStatus();
    showAlert('cuentosAlert', enable ? 'Cuentos activados ✓' : 'Cuentos desactivados', 's');
  } catch(e) { showAlert('cuentosAlert', e.message); }
}

/* ── Cuentos view (member + admin) ─────────────────────────────────── */
async function loadCuentosView() {
  const el = document.getElementById('cuentosViewList');
  if (!el) return;
  el.innerHTML = '<div class="empty">Cargando…</div>';
  // Show upload panel for admins
  if (me?.is_admin) document.getElementById('cuentosUploadPanel')?.style.setProperty('display','');
  try {
    const items = await req('GET', '/api/cuentos');
    if (!items.length) {
      el.innerHTML = '<div class="empty">Sin cuentos disponibles.</div>';
      return;
    }
    el.innerHTML = items.map(c => {
      const name  = c.filename || '';
      const label = (c.title || name).replace(/_/g,' ').replace(/\.(docx|odt)$/i,'');
      const masked = c.masked || false;
      if (masked && !me?.is_admin) return '';
      return `<div class="panel" style="display:flex;align-items:center;gap:12px;padding:14px 16px;${masked?'opacity:.5':''}">
        <span style="font-size:1.4rem;flex-shrink:0">📖</span>
        <div style="flex:1;min-width:0">
          <div style="font-size:.84rem;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(label)}</div>
          ${c.date ? `<div style="font-size:.58rem;color:var(--text3);margin-top:2px">${esc(c.date)}</div>` : ''}
          ${masked ? '<div style="font-size:.58rem;color:var(--red);margin-top:2px">🔒 Oculto para miembros</div>' : ''}
        </div>
        ${!masked ? `<a href="/bank/cuento/${encodeURIComponent(name)}?token=${encodeURIComponent(localStorage.getItem("dvd_token')||'')}" target="_blank"
          class="btn btnG btnSm" style="text-decoration:none;flex-shrink:0">Leer →</a>` : ''}
      </div>`;
    }).filter(Boolean).join('');
  } catch(e) {
    el.innerHTML = `<div class="empty">Error: ${esc(e.message)}</div>`;
  }
}

async function cuentosUpload() {
  const inp = document.getElementById('cuentosFileInput');
  const file = inp?.files?.[0];
  if (!file) { showAlert('cuentosUploadAlert', 'Selecciona un archivo .docx o .txt'); return; }
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['docx','odt','txt'].includes(ext)) { showAlert('cuentosUploadAlert', 'Solo .docx, .odt o .txt'); return; }
  const fd = new FormData();
  fd.append('file', file);
  try {
    const r = await fetch(\'/bank/api/cuentos/upload\', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('dvd_token')||''), 'ngrok-skip-browser-warning': '1' },
      body: fd,
    });
    const d = await r.json().catch(()=>({}));
    if (!r.ok) throw new Error(d.detail || 'Error al subir');
    showAlert('cuentosUploadAlert', '✓ Subido: ' + esc(d.filename || file.name), 's');
    inp.value = '';
    await loadCuentosView();
  } catch(e) { showAlert('cuentosUploadAlert', e.message); }
}

async function admAct(action, username) {
  if (action === 'reset-pwd' && !confirm(t('admConfirmReset', { user: username }))) return;
  try {
    const d = await req('POST', `/api/admin/${action}/${username}`);
    showAlert('admAlert', d.message, 's');
    await Promise.all([loadAdmin(), loadDropdown()]);
  } catch (e) { showAlert('admAlert', e.message); }
}

async function admDelete(username) {
  // Solo dvd puede borrar - confirmación simple
  if (!confirm(`¿Estás seguro de que quieres eliminar permanentemente a @${username}?\n\nEsta acción NO se puede deshacer.`)) {
    return;
  }

  try {
    const d = await req('POST', `/api/admin/delete/${username}`);
    showAlert('admAlert', d.message || 'Usuario eliminado correctamente', 's');
    await Promise.all([loadAdmin(), loadDropdown()]);
  } catch(e) {
    showAlert('admAlert', e.message || 'Error al eliminar usuario');
  }
}

/* ── 9b. Pasapalabra game ───────────────────────────────── */
let gameEnabled = false;

async function checkGameStatus() {
  try {
    const d = await req('GET', '/api/pasapalabra/status');
    gameEnabled = !!d.enabled;
  } catch (_) { gameEnabled = false; }
  // Members: show Pasapalabra tab only when enabled
  // Admins: never show it (they use admin panel)
  if (!me?.is_admin) {
    ['navGame', 'mobileNavGame'].forEach(id =>
      document.getElementById(id)?.classList.toggle('hidden', !gameEnabled)
    );
  } else {
    ['navGame', 'mobileNavGame'].forEach(id =>
      document.getElementById(id)?.classList.add('hidden')
    );
  }
  _recalcMobileNav();
}

async function toggleGame(enable) {
  try {
    await req('POST', '/api/pasapalabra/toggle', { enabled: enable });
    await checkGameStatus();
    showAlert('gameAlert', enable ? 'Game enabled — the Games tab is now visible to all users.' : 'Game disabled.', 's');
  } catch (e) { showAlert('gameAlert', e.message); }
}

function openGame() {
  const token = localStorage.getItem('dvd_token');
  const url   = token ? '/pasapalabra?token=' + encodeURIComponent(token) : '/pasapalabra';
  window.open(url, '_blank');
}

async function openVideo() {
  const username = localStorage.getItem('dvd_username');
  const token = localStorage.getItem('dvd_token');
  if (!username || !token) {
    alert('Debes iniciar sesión primero');
    return;
  }

  // Refresh token if needed
  await refreshTokenIfNeeded();

  const freshToken = localStorage.getItem('dvd_token');
  window.location.href = '/video?token=' + encodeURIComponent(freshToken);
}

function openVideoAsync() {
  openVideo().catch(err => {
    console.error('Error opening video:', err);
    alert('Error al abrir videollamadas');
  });
}

/* ── 9c. Millonario game ────────────────────────────────── */
let millonarioEnabled = false;

async function checkMillonarioStatus() {
  try {
    const d = await req('GET', '/api/millonario/status');
    millonarioEnabled = !!d.enabled;
  } catch (_) { millonarioEnabled = false; }
  // Members: show tab only when enabled; admins: always hidden (use admin panel)
  if (!me?.is_admin) {
    ['navMillonario', 'mobileNavMillonario'].forEach(id =>
      document.getElementById(id)?.classList.toggle('hidden', !millonarioEnabled)
    );
  } else {
    ['navMillonario', 'mobileNavMillonario'].forEach(id =>
      document.getElementById(id)?.classList.add('hidden')
    );
  }
}

async function toggleMillonario(enable) {
  try {
    await req('POST', '/api/millonario/toggle', { enabled: enable });
    await checkMillonarioStatus();
    showAlert('millonarioAlert', enable ? 'Millonario enabled.' : 'Millonario disabled.', 's');
  } catch (e) { showAlert('millonarioAlert', e.message); }
}

function openMillonario() {
  window.open('/millonario', '_blank');
}

function openApuestas() {
  const t = localStorage.getItem('dvd_token');
  window.location.href = t ? '/apuestas?token=' + encodeURIComponent(t) : '/apuestas';
}

function openVotaciones() {
  const t = localStorage.getItem('dvd_token');
  window.location.href = t ? '/votaciones?token=' + encodeURIComponent(t) : '/votaciones';
}

function openOpo() {
  const t = localStorage.getItem('dvd_token');
  window.location.href = t ? '/opo?token=' + encodeURIComponent(t) : '/opo';
}

/* ── 9d. ¿Quién soy? game ─────────────────────── */
let quienSoyEnabled  = false;
let qsPlayers        = [];
let qsAcAllUsers     = [];
let qsAcIdx          = -1;
let qsCharVerified   = false;   // true after successful verify

/* ── Status / toggle ── */
async function checkQuienSoyStatus() {
  try {
    const d = await req('GET', '/api/quiensoy/status');
    quienSoyEnabled = !!d.enabled;
  } catch (_) { quienSoyEnabled = false; }

  // Members: show tab only when enabled; admins: always hidden
  if (!me?.is_admin) {
    ['navQuienSoy','mobileNavQuienSoy'].forEach(id =>
      document.getElementById(id)?.classList.toggle('hidden', !quienSoyEnabled)
    );
  } else {
    ['navQuienSoy','mobileNavQuienSoy'].forEach(id =>
      document.getElementById(id)?.classList.add('hidden')
    );
  }
}

async function qsEnable() {
  try {
    await req('POST', '/api/quiensoy/toggle', { enabled: true });
    await checkQuienSoyStatus();
    showAlert('quienSoyAlert', '¿Quién soy? activado.', 's');
  } catch(e) { showAlert('quienSoyAlert', e.message); }
}

async function toggleQuienSoy(enable) {
  try {
    await req('POST', '/api/quiensoy/toggle', { enabled: enable });
    await checkQuienSoyStatus();
    showAlert('quienSoyAlert', enable ? 'Activado.' : 'Desactivado.', enable ? 's' : '');
  } catch(e) { showAlert('quienSoyAlert', e.message); }
}

function openQuienSoy() {
  const t = localStorage.getItem('dvd_token');
  window.open(t ? '/quiensoy?token=' + encodeURIComponent(t) : '/quiensoy', '_blank');
}

/* ── 9e. Cifras y Letras ─────────────────────────── */
let clEnabled   = false;
let clPlayers   = [];
let clAcUsers   = [];
let clAcIdx     = -1;

async function checkCifrasLetrasStatus() {
  try {
    const d = await req('GET', '/api/cifrasletras/status');
    clEnabled = !!d.enabled;
  } catch (_) { clEnabled = false; }
  // Members: show tab only when enabled; admins: always hidden
  if (!me?.is_admin) {
    ['navCifrasLetras','mobileNavCifrasLetras'].forEach(id =>
      document.getElementById(id)?.classList.toggle('hidden', !clEnabled)
    );
  } else {
    ['navCifrasLetras','mobileNavCifrasLetras'].forEach(id =>
      document.getElementById(id)?.classList.add('hidden')
    );
  }
}

/* ══════════════════════════════════════════════════════════════════════════
   ROOMS STATUS — mismo patrón que los juegos.
   Se llama cada 10s desde startGameStatusPolling() y también al entrar
   a la vista Social. Actualiza la pantalla directamente sin que el usuario
   haga nada.
══════════════════════════════════════════════════════════════════════════ */
async function checkRoomsStatus() {
  let rooms = [];
  try {
    const d = await req('GET', '/api/rooms/status');
    rooms = d.rooms || [];
  } catch (_) { rooms = []; }
  // Actualizar la pantalla social directamente
  _renderRoomsList(rooms);
}

async function clLoadUsers() {
  try { clAcUsers = await req('GET', '/api/cifrasletras/users'); } catch(_) { clAcUsers = []; }
}

async function toggleCifrasLetras(enable) {
  try {
    await req('POST', '/api/cifrasletras/toggle', { enabled: enable });
    await checkCifrasLetrasStatus();
    showAlert('clAlert', enable ? 'Cifras y Letras activado.' : 'Desactivado.', enable?'s':'');
  } catch(e) { showAlert('clAlert', e.message); }
}

function openCifrasLetras() {
  const t = localStorage.getItem('dvd_token');
  window.open(t ? '/cifrasletras?token=' + encodeURIComponent(t) : '/cifrasletras', '_blank');
}

/* ── 9f. Hundir la Flota game ─────────────────────── */
let hundirLaFlotaEnabled = false;

async function checkHundirLaFlotaStatus() {
  try {
    const d = await req('GET', '/api/hundirlaflota/status');
    hundirLaFlotaEnabled = !!d.enabled;
  } catch (_) { hundirLaFlotaEnabled = false; }

  // Members: show tab only when enabled; admins: always hidden
  if (!me?.is_admin) {
    ['navHundirLaFlota', 'mobileNavHundirLaFlota'].forEach(id =>
      document.getElementById(id)?.classList.toggle('hidden', !hundirLaFlotaEnabled)
    );
  } else {
    ['navHundirLaFlota', 'mobileNavHundirLaFlota'].forEach(id =>
      document.getElementById(id)?.classList.add('hidden')
    );
  }
}

async function toggleHundirLaFlota(enable) {
  try {
    await req('POST', '/api/hundirlaflota/toggle', { enabled: enable });
    await checkHundirLaFlotaStatus();
    showAlert('hundirLaFlotaAlert', enable ? 'Hundir la Flota activado.' : 'Hundir la Flota desactivado.', enable ? 's' : '');
  } catch(e) { showAlert('hundirLaFlotaAlert', e.message); }
}

function openHundirLaFlota() {
  const t = localStorage.getItem('dvd_token');
  window.open(t ? '/hundirlaflota/game.html?token=' + encodeURIComponent(t) : '/hundirlaflota/game.html', '_blank');
}

function clAcType() {
  const q = document.getElementById('clAcInput').value.trim().toLowerCase();
  const dd = document.getElementById('clAcDrop');
  clAcIdx = -1;
  if (!q) { dd.style.display='none'; return; }
  const hits = clAcUsers.filter(u => !clPlayers.includes(u) && u.toLowerCase().includes(q)).slice(0,8);
  if (!hits.length) { dd.style.display='none'; return; }
  dd.innerHTML = '';
  hits.forEach(u => {
    const lo=u.toLowerCase(), pos=lo.indexOf(q);
    const div=document.createElement('div');
    div.style.cssText='padding:8px 12px;font-size:.72rem;cursor:pointer;color:var(--text);border-bottom:1px solid var(--border)';
    div.innerHTML='@'+(pos>=0?esc(u.slice(0,pos))+'<b style="color:var(--gold)">'+esc(u.slice(pos,pos+q.length))+'</b>'+esc(u.slice(pos+q.length)):esc(u));
    div.addEventListener('mouseover',()=>div.style.background='var(--n4)');
    div.addEventListener('mouseout', ()=>div.style.background='');
    div.addEventListener('mousedown',ev=>{ev.preventDefault();clAddPlayer(u);});
    dd.appendChild(div);
  });
  dd.style.display='';
}

function clAcKey(e) {
  const dd=document.getElementById('clAcDrop');
  const rows=[...dd.querySelectorAll('div')];
  if(e.key==='ArrowDown'){e.preventDefault();clAcIdx=Math.min(clAcIdx+1,rows.length-1);rows.forEach((r,i)=>r.style.background=i===clAcIdx?'var(--n4)':'');}
  else if(e.key==='ArrowUp'){e.preventDefault();clAcIdx=Math.max(clAcIdx-1,0);rows.forEach((r,i)=>r.style.background=i===clAcIdx?'var(--n4)':'');}
  else if(e.key==='Enter'){e.preventDefault();if(clAcIdx>=0&&rows[clAcIdx])rows[clAcIdx].dispatchEvent(new Event('mousedown'));}
  else if(e.key==='Escape')dd.style.display='none';
}

function clAddPlayer(u) {
  if(!u||clPlayers.includes(u)||clPlayers.length>=10)return;
  clPlayers.push(u);
  document.getElementById('clAcInput').value='';
  document.getElementById('clAcDrop')?.style.setProperty('display','none');
  clRenderPills();
}

function clRemovePlayer(i) { clPlayers.splice(i,1); clRenderPills(); }

function clRenderPills() {
  const el=document.getElementById('clPills');
  if(!clPlayers.length){
    el.innerHTML='<span style="font-size:.62rem;color:var(--text2)">Añade jugadores…</span>';
  } else {
    el.innerHTML=clPlayers.map((n,i)=>
      `<span style="display:inline-flex;align-items:center;gap:4px;background:var(--n4);border:1px solid var(--border2);border-radius:16px;padding:3px 9px 3px 10px;font-size:.66rem;color:var(--text);margin:1px">@${esc(n)}<button onclick="clRemovePlayer(${i})" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:.75rem;line-height:1;margin-left:2px">✕</button></span>`
    ).join('');
  }
  document.getElementById('clPCount').textContent=clPlayers.length+' / 10 jugadores';
  document.getElementById('btnClStart').disabled=!clPlayers.length;
}

async function clStartGame() {
  const maxRounds = parseInt(document.getElementById('clRounds')?.value||'5');
  const roundTime = parseInt(document.getElementById('clSeconds')?.value||'30');
  if(!clPlayers.length){showAlert('clAlert','Añade al menos un jugador.');return;}
  try {
    await req('POST','/api/cifrasletras/setup',{players:clPlayers,max_rounds:maxRounds,round_time:roundTime});
    await checkCifrasLetrasStatus();
    showAlert('clAlert','¡Partida iniciada! Abre la pantalla del juego.','s');
    clPlayers=[]; clRenderPills();
  } catch(e){showAlert('clAlert',e.message);}
}

async function clResetGame() {
  if(!confirm('¿Reiniciar la partida? Se perderán los datos actuales.')) return;
  try {
    await req('POST','/api/cifrasletras/toggle',{enabled:false});
    await checkCifrasLetrasStatus();
    showAlert('clAlert','Partida reiniciada.','s');
  } catch(e){showAlert('clAlert',e.message);}
}

/* ── Load members list ── */
async function qsLoadUsers() {
  try {
    qsAcAllUsers = await req('GET', '/api/quiensoy/users');
  } catch(_) { qsAcAllUsers = []; }
}

/* ── Character verify ── */
function qsCharChanged() {
  qsCharVerified = false;
  document.getElementById('qsCharInfo')?.style.setProperty('display','none');
  qsChkStart();
}

async function qsVerifyChar() {
  const name = document.getElementById('qsCharInput').value.trim();
  if (!name) { showAlert('quienSoyAlert', 'Escribe un personaje primero.'); return; }
  const btn = document.getElementById('btnQsVerify');
  btn.textContent = '⏳'; btn.disabled = true;
  try {
    const d = await req('GET', '/api/quiensoy/verify-character?name=' + encodeURIComponent(name));
    const box    = document.getElementById('qsCharInfo');
    const status = document.getElementById('qsCharStatus');
    const hint   = document.getElementById('qsCharHint');
    const suggs  = document.getElementById('qsCharSuggs');
    box.style.display = '';

    if (d.valid) {
      // Use canonical name and store photo
      document.getElementById('qsCharInput').value = d.canonical || name;
      window.qsCharPhoto = d.photo || null;

      // Show large photo if available
      let photoHtml = '';
      if (d.photo) {
        photoHtml = `
          <div style="margin:12px 0;text-align:center">
            <img src="${esc(d.photo)}" style="
              width:150px;
              height:150px;
              object-fit:cover;
              border-radius:12px;
              border:3px solid var(--gold);
              box-shadow:0 4px 12px rgba(212,168,67,.3);
            " onerror="this.style.display='none'">
          </div>
        `;
      }

      status.innerHTML = '<span style="color:var(--green);font-size:.9rem">✓ Personaje reconocido: <strong>' + esc(d.canonical || name) + '</strong></span>' + photoHtml;
      hint.textContent  = d.hint || '';
      qsCharVerified = true;
    } else {
      status.innerHTML = '<span style="color:var(--red)">⚠ No reconocido como personaje famoso. ¿Quisiste decir…?</span>';
      hint.textContent  = '';
      qsCharVerified = false;
      window.qsCharPhoto = null;
    }

    // Show suggestions with photos
    if (d.suggestions && d.suggestions.length) {
      suggs.innerHTML = '<div style="color:var(--text2);font-size:.62rem;margin-bottom:8px;font-weight:600">Sugerencias:</div>' +
        d.suggestions.map(s => {
          const photoImg = s.photo ? `<img src="${esc(s.photo)}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;margin-right:10px;border:2px solid var(--border2)" onerror="this.style.display='none'">` : '';
          return `<button onclick="qsUseSuggestion('${esc(s.name)}', '${esc(s.photo||'')}')"
            style="display:flex;align-items:center;margin:6px 0;padding:10px 12px;border-radius:10px;background:var(--n3);border:1px solid var(--border2);color:var(--gold);font-size:.75rem;cursor:pointer;width:100%;text-align:left;transition:all .2s"
            onmouseover="this.style.borderColor='var(--gold)';this.style.background='var(--n4)';this.style.transform='translateX(4px)'"
            onmouseout="this.style.borderColor='var(--border2)';this.style.background='var(--n3)';this.style.transform='translateX(0)'">
            ${photoImg}<strong>${esc(s.name)}</strong>
          </button>`;
        }).join('');
    } else {
      suggs.innerHTML = '';
    }
    box.style.borderColor = d.valid ? 'rgba(56,184,122,.4)' : 'rgba(200,48,96,.4)';
  } catch(e) {
    showAlert('quienSoyAlert', 'Error verificando: ' + e.message);
  } finally {
    btn.textContent = '🔍 Verificar'; btn.disabled = false;
    qsChkStart();
  }
}

function qsUseSuggestion(name, photo) {
  document.getElementById('qsCharInput').value = name;
  window.qsCharPhoto = photo || null;
  qsCharChanged();
  qsVerifyChar();
}

/* ── Autocomplete players ── */
function qsAcType() {
  const q  = document.getElementById('qsAcInput').value.trim().toLowerCase();
  const dd = document.getElementById('qsAcDrop');
  qsAcIdx  = -1;
  if (!q) { dd.style.display = 'none'; return; }
  const hits = qsAcAllUsers.filter(u => !qsPlayers.includes(u) && u.toLowerCase().includes(q)).slice(0,8);
  if (!hits.length) { dd.style.display = 'none'; return; }
  dd.innerHTML = '';
  hits.forEach((u, i) => {
    const div = document.createElement('div');
    div.style.cssText = 'padding:8px 12px;font-size:.72rem;cursor:pointer;color:var(--text);border-bottom:1px solid var(--border)';
    const lo = u.toLowerCase(), pos = lo.indexOf(q);
    div.innerHTML = '@' + (pos >= 0
      ? esc(u.slice(0,pos)) + '<b style="color:var(--gold)">' + esc(u.slice(pos,pos+q.length)) + '</b>' + esc(u.slice(pos+q.length))
      : esc(u));
    div.addEventListener('mouseover',  () => div.style.background = 'var(--n4)');
    div.addEventListener('mouseout',   () => div.style.background = '');
    div.addEventListener('mousedown',  ev => { ev.preventDefault(); qsAddPlayer(u); });
    dd.appendChild(div);
  });
  dd.style.display = '';
}

function qsAcKey(e) {
  const dd = document.getElementById('qsAcDrop');
  const rows = [...dd.querySelectorAll('div')];
  if      (e.key === 'ArrowDown')  { e.preventDefault(); qsAcIdx = Math.min(qsAcIdx+1, rows.length-1); rows.forEach((r,i)=>r.style.background=i===qsAcIdx?'var(--n4)':''); }
  else if (e.key === 'ArrowUp')    { e.preventDefault(); qsAcIdx = Math.max(qsAcIdx-1,0); rows.forEach((r,i)=>r.style.background=i===qsAcIdx?'var(--n4)':''); }
  else if (e.key === 'Enter')      { e.preventDefault(); if(qsAcIdx>=0&&rows[qsAcIdx]) rows[qsAcIdx].dispatchEvent(new Event('mousedown')); }
  else if (e.key === 'Escape')     { dd.style.display = 'none'; }
}

function qsAddPlayer(u) {
  if (!u || qsPlayers.includes(u) || qsPlayers.length >= 10) return;
  qsPlayers.push(u);
  document.getElementById('qsAcInput').value = '';
  document.getElementById('qsAcDrop')?.style.setProperty('display','none');
  qsRenderPills();
}

function qsRemovePlayer(i) {
  qsPlayers.splice(i, 1);
  qsRenderPills();
}

function qsRenderPills() {
  const el = document.getElementById('qsPills');
  if (!qsPlayers.length) {
    el.innerHTML = '<span style="font-size:.62rem;color:var(--text2)">Añade jugadores…</span>';
  } else {
    el.innerHTML = qsPlayers.map((n, i) =>
      `<span style="display:inline-flex;align-items:center;gap:4px;background:var(--n4);border:1px solid var(--border2);border-radius:16px;padding:3px 9px 3px 10px;font-size:.66rem;color:var(--text);margin:1px">@${esc(n)}<button onclick="qsRemovePlayer(${i})" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:.75rem;line-height:1;padding:0 1px;margin-left:2px">✕</button></span>`
    ).join('');
  }
  document.getElementById('qsPCount').textContent = qsPlayers.length + ' / 10 jugadores';
  qsChkStart();
}

function qsChkStart() {
  const charOk   = !!document.getElementById('qsCharInput')?.value.trim() && qsCharVerified;
  const playersOk = qsPlayers.length >= 1;
  const btn = document.getElementById('btnQsStart');
  if (btn) btn.disabled = !charOk || !playersOk;
}

/* ── Start game ── */
async function qsStartGame() {
  const character = document.getElementById('qsCharInput')?.value.trim();
  if (!character) { showAlert('quienSoyAlert', 'Escribe el personaje.'); return; }
  if (!qsPlayers.length) { showAlert('quienSoyAlert', 'Añade al menos un jugador.'); return; }
  try {
    // Enable + setup via HTTP (no WS needed from admin panel)
    await req('POST', '/api/quiensoy/setup', {
      character,
      character_photo: window.qsCharPhoto || null,
      players: qsPlayers
    });
    await checkQuienSoyStatus();
    showAlert('quienSoyAlert', '¡Partida iniciada! Abre la pantalla del juego.', 's');
    // Reset form
    document.getElementById('qsCharInput').value = '';
    document.getElementById('qsCharInfo')?.style.setProperty('display','none');
    window.qsCharPhoto = null;
    qsPlayers = [];
    qsRenderPills();
    qsCharVerified = false;
    qsChkStart();
  } catch(e) { showAlert('quienSoyAlert', e.message); }
}

/* ══════════════════════════════════════════════════════════
   GAME MANAGEMENT DRAWER
   openGamePanel(name) → shows the drawer for that game
   closeGamePanel()    → hides drawer, shows button grid
══════════════════════════════════════════════════════════ */

let _curGamePanel = null;

// User lists cached per game
let ppAllUsers = [], ppPlayers = [], ppAcIdx = -1;
let mlAllUsers = [], mlSelected = '', mlAcIdx = -1;
let qs2Players = [], qs2AcAllUsers = [], qs2AcIdx = -1, qs2CharVerified = false;
let cl2Players = [], cl2AllUsers = [], cl2AcIdx = -1;

const GAME_META = {
  pasapalabra:  { icon:'🎯', get label(){ return t('navPasapalabra','Pasapalabra'); } },
  millonario:   { icon:'💰', get label(){ return t('navMillonario','Millonario'); } },
  quiensoy:     { icon:'🎭', get label(){ return t('navQuienSoy','¿Quién soy?'); } },
  cifrasletras: { icon:'🔤', get label(){ return t('navCifrasLetras','Cifras y Letras'); } },
  hundirlaflota:{ icon:'⚓', get label(){ return t('navHundirLaFlota','Hundir la Flota'); } },
  cuentos:      { icon:'📖', get label(){ return t('navCuentos','Cuentos'); } },
  opo:          { icon:'📝', label:'OPO' },
  mensajes:     { icon:'💬', get label(){ return t('socialTitle','Mensajes'); } },
};

async function openGamePanel(name) {
  _curGamePanel = name;
  const meta = GAME_META[name] || { icon:'🎮', label: name };
  document.getElementById('drawerTitle').textContent = meta.icon + ' ' + meta.label;
  // NO ocultar el panel de botones de juegos
  // document.getElementById('gameBtnGrid').style.display = 'none';
  document.getElementById('gameDrawer').style.display = '';
  document.querySelectorAll('.gamePanel').forEach(p => p.style.display = 'none');
  const panel = document.getElementById('gp-' + name);
  if (panel) panel.style.display = '';
  // Load game-specific data
  if (name === 'pasapalabra')  await ppLoad();
  if (name === 'millonario')   await mlLoad();
  if (name === 'quiensoy')     await qs2Load();
  if (name === 'cifrasletras') await cl2Load();
  if (name === 'hundirlaflota') await hlfLoad();
  if (name === 'cuentos')      await ctLoad();
  if (name === 'opo')          await opoLoad2();
  if (name === 'mensajes')     await msgLoad();
}

function closeGamePanel() {
  document.getElementById('gameDrawer').style.display = 'none';
  // NO mostrar el panel de botones porque ya está visible
  // document.getElementById('gameBtnGrid').style.display = '';
  _curGamePanel = null;
  // Volver a la pestaña admin (que es donde están los botones de juegos)
  // No necesitamos cambiar de pestaña porque ya estamos en admin
}

/* ──────────────────────────────────────────────────────────
   PASAPALABRA DRAWER
────────────────────────────────────────────────────────── */
let _ppWs = null;

async function ppLoad() {
  try {
    const [st, users] = await Promise.all([
      req('GET', '/api/pasapalabra/status'),
      req('GET', '/api/pasapalabra/users'),
    ]);
    ppAllUsers = users || [];
    ppUpdateStatus(st.enabled);
    ppConnectWS();
  } catch(e) { showAlert('ppAlert1', e.message); }
}

function ppUpdateStatus(enabled) {
  const sub = document.getElementById('ppStatusSub');
  if (sub) sub.textContent = enabled ? '🟢 Juego activo' : '⚫ Juego desactivado';
  document.getElementById('ppBtnOff')?.style.setProperty('display', enabled ? '' : 'none');
  document.getElementById('ppBtnReset')?.style.setProperty('display', enabled ? '' : 'none');
  document.getElementById('ppBtnOpen')?.style.setProperty('display', enabled ? '' : 'none');
  const badge = document.getElementById('drawerBadge');
  if (badge && _curGamePanel === 'pasapalabra') {
    badge.textContent = enabled ? '🟢 Activo' : '⚫ Off';
    badge.style.color = enabled ? 'var(--green)' : 'var(--text3)';
  }
}

function ppConnectWS() {
  if (_ppWs && _ppWs.readyState < 2) return;
  const wsBase = location.protocol === 'https:' ? 'wss://' + location.host : 'ws://' + location.host;
  _ppWs = new WebSocket(wsBase + '/ws/pasapalabra?token=' + encodeURIComponent(localStorage.getItem('dvd_token')||''));
  _ppWs.onmessage = e => { try { ppHandleState(JSON.parse(e.data)); } catch(_){} };
  _ppWs.onclose   = () => { if (_curGamePanel === 'pasapalabra') setTimeout(ppConnectWS, 3000); };
}

function ppHandleState(data) {
  if (data.type !== 'state') return;
  ppUpdateStatus(data.enabled);
  const ps = data.players || [];
  const sec = document.getElementById('ppLivePlayers');
  const grid = document.getElementById('ppPlayersGrid');
  if (ps.length && data.status !== 'waiting') {
    sec.style.display = '';
    const cur = data.current_player_idx ?? -1;
    grid.innerHTML = ps.map((p, i) => {
      const active = i === cur && !p.done;
      const t = p.time_remaining != null ? (Math.floor(p.time_remaining/60)+':'+(p.time_remaining%60+'').padStart(2,'0')) : '—';
      const done = Object.values(p.letters||{}).filter(v=>v!=='pending').length;
      return `<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;background:${active?'rgba(56,184,122,.07)':'var(--glass)'};border:1px solid ${active?'rgba(56,184,122,.35)':'var(--border)'};border-radius:8px">
        <span style="font-size:.85rem">${active?'▶':p.done?'✓':'○'}</span>
        <span style="flex:1;font-size:.78rem;color:var(--text)">@${esc(p.username)}</span>
        <span style="font-size:.62rem;color:var(--text3)">${done}/26</span>
        <span style="font-family:'Playfair Display',serif;color:var(--gold2)">${p.score}✓</span>
        <span style="font-size:.62rem;color:var(--text3)">⏱${t}</span>
      </div>`;
    }).join('');
  } else { sec.style.display = 'none'; }
}

async function ppToggle(on) {
  try {
    await req('POST', '/api/pasapalabra/toggle', { enabled: on });
    ppUpdateStatus(on);
    showAlert('ppAlert1', on ? '✓ Activado' : 'Desactivado', on?'s':'');
  } catch(e) { showAlert('ppAlert1', e.message); }
}

async function ppReset() {
  if (!confirm('¿Reiniciar la partida?')) return;
  try { await req('POST', '/api/pasapalabra/reset'); showAlert('ppAlert1','✓ Reiniciada','s'); } catch(e){ showAlert('ppAlert1',e.message); }
}

function ppOpen() { window.open('/pasapalabra?token='+encodeURIComponent(localStorage.getItem('dvd_token')||''), '_blank'); }

function ppAcFilter() {
  const q = document.getElementById('ppAcIn').value.trim().toLowerCase();
  const dd = document.getElementById('ppAcDrop'); ppAcIdx = -1;
  if (!q) { dd.style.display='none'; return; }
  const hits = ppAllUsers.filter(u => !ppPlayers.includes(u) && u.toLowerCase().includes(q)).slice(0,8);
  if (!hits.length) { dd.style.display='none'; return; }
  dd.innerHTML = hits.map(u => { const p=u.toLowerCase().indexOf(q); const h=p>=0?esc(u.slice(0,p))+'<b style="color:var(--gold)">'+esc(u.slice(p,p+q.length))+'</b>'+esc(u.slice(p+q.length)):esc(u); return `<div style="padding:8px 12px;font-size:.75rem;cursor:pointer;color:var(--text);border-bottom:1px solid var(--border)" onmouseover="this.style.background='var(--n4)'" onmouseout="this.style.background=''" onmousedown="event.preventDefault();ppAddPlayer('${u}')">@${h}</div>`; }).join('');
  dd.style.display = '';
}
function ppAcKey(e) { const rows=[...document.getElementById('ppAcDrop').querySelectorAll('div')]; if(e.key==='ArrowDown'){e.preventDefault();ppAcIdx=Math.min(ppAcIdx+1,rows.length-1);rows.forEach((r,i)=>r.style.background=i===ppAcIdx?'var(--n4)':'')}else if(e.key==='ArrowUp'){e.preventDefault();ppAcIdx=Math.max(ppAcIdx-1,0);rows.forEach((r,i)=>r.style.background=i===ppAcIdx?'var(--n4)':'')}else if(e.key==='Enter'){e.preventDefault();if(ppAcIdx>=0&&rows[ppAcIdx])rows[ppAcIdx].dispatchEvent(new Event('mousedown'))}else if(e.key==='Escape')document.getElementById('ppAcDrop').style.display='none'; }
function ppAddPlayer(u) { if(!u||ppPlayers.includes(u)||ppPlayers.length>=10)return; ppPlayers.push(u); document.getElementById('ppAcIn').value=''; document.getElementById('ppAcDrop').style.display='none'; ppRenderPills(); }
function ppRemovePlayer(i) { ppPlayers.splice(i,1); ppRenderPills(); }
function ppRenderPills() {
  const el = document.getElementById('ppPills');
  el.innerHTML = ppPlayers.length ? ppPlayers.map((u,i)=>`<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(212,168,67,.1);border:1px solid rgba(212,168,67,.25);border-radius:16px;padding:2px 8px 2px 9px;font-size:.66rem;color:var(--gold2)">@${esc(u)}<button onclick="ppRemovePlayer(${i})" style="background:none;border:none;color:var(--gold3);cursor:pointer;font-size:.75rem;line-height:1;padding:0 1px">✕</button></span>`).join('') : '<span style="font-size:.62rem;color:var(--text2)">Añade jugadores…</span>';
  document.getElementById('ppPCount').textContent = ppPlayers.length+' / 10';
  document.getElementById('ppBtnStart').disabled = !ppPlayers.length;
}
async function ppStartGame() {
  if (!ppPlayers.length) { showAlert('ppAlert2','Añade al menos un jugador'); return; }
  const rt = parseInt(document.getElementById('ppRoscoTime').value);
  const btn = document.getElementById('ppBtnStart'); btn.disabled=true; btn.textContent='⏳…';
  try {
    await req('POST', '/api/pasapalabra/setup', { players: ppPlayers.slice(), rosco_time: rt });
    ppUpdateStatus(true);
    showAlert('ppAlert2','✓ Partida iniciada — abriendo juego…','s');
    ppPlayers=[]; ppRenderPills();
    setTimeout(ppOpen, 700);
  } catch(e){ showAlert('ppAlert2',e.message); }
  finally { btn.disabled=!ppPlayers.length; btn.textContent='▶ Iniciar partida'; }
}

/* ──────────────────────────────────────────────────────────
   MILLONARIO DRAWER
────────────────────────────────────────────────────────── */
let _mlWs = null;

async function mlLoad() {
  try {
    const [st, users] = await Promise.all([
      req('GET', '/api/millonario/status'),
      req('GET', '/api/millonario/users'),
    ]);
    mlAllUsers = users || [];
    mlUpdateStatus(st.enabled);
    mlConnectWS();
  } catch(e) { showAlert('mlAlert1', e.message); }
}

function mlUpdateStatus(enabled) {
  document.getElementById('mlStatusSub').textContent = enabled ? '🟢 Juego activo' : '⚫ Juego desactivado';
  document.getElementById('mlBtnOn')?.style.setProperty('display', enabled?'none':'');
  document.getElementById('mlBtnOff')?.style.setProperty('display', enabled?'':'none');
  document.getElementById('mlBtnReset')?.style.setProperty('display', enabled?'':'none');
  document.getElementById('mlBtnOpen')?.style.setProperty('display', enabled?'':'none');
  const badge = document.getElementById('drawerBadge');
  if (badge && _curGamePanel === 'millonario') { badge.textContent = enabled?'🟢 Activo':'⚫ Off'; badge.style.color = enabled?'var(--green)':'var(--text3)'; }
}

function mlConnectWS() {
  if (_mlWs && _mlWs.readyState < 2) return;
  const wsBase = location.protocol === 'https:' ? 'wss://' + location.host : 'ws://' + location.host;
  _mlWs = new WebSocket(wsBase + '/ws/millonario?token=' + encodeURIComponent(localStorage.getItem('dvd_token')||''));
  _mlWs.onmessage = e => { try { mlHandleState(JSON.parse(e.data)); } catch(_){} };
  _mlWs.onclose   = () => { if (_curGamePanel === 'millonario') setTimeout(mlConnectWS, 3000); };
}
function mlHandleState(data) {
  if (data.type !== 'state') return;
  mlUpdateStatus(data.enabled);
  const card = document.getElementById('mlLiveCard');
  if (data.status === 'playing' && data.player) {
    card.style.display = '';
    document.getElementById('mlLivePlayer').textContent = '👤 @' + data.player;
    document.getElementById('mlLiveLevel').textContent  = 'Nivel ' + data.nivel + ' / 15' + (data.pregunta ? ' — ' + data.pregunta.premio : '');
  } else { card.style.display = 'none'; }
}
async function mlToggle(on) { try { await req('POST','/api/millonario/toggle',{enabled:on}); mlUpdateStatus(on); showAlert('mlAlert1',on?'✓ Activado':'Desactivado',on?'s':''); } catch(e){showAlert('mlAlert1',e.message);} }
async function mlReset() { if(!confirm('¿Reiniciar?'))return; try{await req('POST','/api/millonario/reset');showAlert('mlAlert1','✓ Reiniciada','s');}catch(e){showAlert('mlAlert1',e.message);} }
function mlOpen() { window.open('/millonario?token='+encodeURIComponent(localStorage.getItem('dvd_token')||''),'_blank'); }

function mlAcFilter() {
  const q = document.getElementById('mlAcIn').value.trim().toLowerCase();
  const dd = document.getElementById('mlAcDrop'); mlAcIdx=-1;
  if (!q) { dd.style.display='none'; return; }
  const hits = mlAllUsers.filter(u=>u.toLowerCase().includes(q)).slice(0,8);
  if (!hits.length) { dd.style.display='none'; return; }
  dd.innerHTML = hits.map(u=>{ const p=u.toLowerCase().indexOf(q); const h=p>=0?esc(u.slice(0,p))+'<b style="color:var(--gold)">'+esc(u.slice(p,p+q.length))+'</b>'+esc(u.slice(p+q.length)):esc(u); return `<div style="padding:8px 12px;font-size:.75rem;cursor:pointer;color:var(--text);border-bottom:1px solid var(--border)" onmouseover="this.style.background='var(--n4)'" onmouseout="this.style.background=''" onmousedown="event.preventDefault();mlSelectUser('${u}')">@${h}</div>`; }).join('');
  dd.style.display='';
}
function mlAcKey(e){const rows=[...document.getElementById('mlAcDrop').querySelectorAll('div')];if(e.key==='ArrowDown'){e.preventDefault();mlAcIdx=Math.min(mlAcIdx+1,rows.length-1);rows.forEach((r,i)=>r.style.background=i===mlAcIdx?'var(--n4)':'')}else if(e.key==='ArrowUp'){e.preventDefault();mlAcIdx=Math.max(mlAcIdx-1,0);rows.forEach((r,i)=>r.style.background=i===mlAcIdx?'var(--n4)':'')}else if(e.key==='Enter'){e.preventDefault();if(mlAcIdx>=0&&rows[mlAcIdx])rows[mlAcIdx].dispatchEvent(new Event('mousedown'))}else if(e.key==='Escape')document.getElementById('mlAcDrop').style.display='none';}
function mlSelectUser(u) { mlSelected=u; document.getElementById('mlAcIn').value='@'+u; document.getElementById('mlAcDrop').style.display='none'; const si=document.getElementById('mlSelected'); si.textContent='✓ @'+u; si.style.color='var(--gold2)'; document.getElementById('mlBtnStart').disabled=false; }
async function mlStartGame() {
  if(!mlSelected){showAlert('mlAlert2','Selecciona un jugador');return;}
  const btn=document.getElementById('mlBtnStart'); btn.disabled=true; btn.textContent='⏳…';
  try { await req('POST','/api/millonario/setup',{player:mlSelected}); mlUpdateStatus(true); showAlert('mlAlert2','✓ Partida iniciada — abriendo juego…','s'); mlSelected=''; document.getElementById('mlAcIn').value=''; document.getElementById('mlSelected').textContent='Ningún jugador seleccionado'; document.getElementById('mlSelected').style.color=''; setTimeout(mlOpen,700); }
  catch(e){showAlert('mlAlert2',e.message);}
  finally{btn.disabled=!mlSelected;btn.textContent='▶ Iniciar partida';}
}

/* ──────────────────────────────────────────────────────────
   ¿QUIÉN SOY? DRAWER  (uses qs2* variables / elements)
────────────────────────────────────────────────────────── */
async function qs2Load() {
  try {
    const [st, users] = await Promise.all([
      req('GET', '/api/quiensoy/status'),
      req('GET', '/api/quiensoy/users'),
    ]);
    qs2AcAllUsers = users || [];
    qs2UpdateStatus(st.enabled);
  } catch(e) { showAlert('qsAlert2', e.message); }
}
function qs2UpdateStatus(en) {
  document.getElementById('qsStatusSub2').textContent = en ? '🟢 Partida activa' : '⚫ Juego desactivado';
  document.getElementById('qsBtnOff2')?.style.setProperty('display', en?'':'none');
  document.getElementById('qsBtnOpen2')?.style.setProperty('display', en?'':'none');
  const badge = document.getElementById('drawerBadge');
  if (badge && _curGamePanel === 'quiensoy') { badge.textContent = en?'🟢 Activo':'⚫ Off'; badge.style.color=en?'var(--green)':'var(--text3)'; }
}
function qsCharChanged2() { qs2CharVerified=false; document.getElementById('qsCharInfo2').style.display='none'; qs2ChkStart(); }
async function qsVerifyChar2() {
  const name = document.getElementById('qsCharInput2').value.trim();
  if (!name) { showAlert('qsAlert3','Escribe un personaje primero.'); return; }
  const btn = document.getElementById('btnQsVerify2'); btn.textContent='⏳'; btn.disabled=true;
  try {
    const d = await req('GET', '/api/quiensoy/verify-character?name=' + encodeURIComponent(name));
    const box = document.getElementById('qsCharInfo2'); box.style.display='';

    if (d.valid) {
      document.getElementById('qsCharInput2').value=d.canonical||name;
      window.qs2CharPhoto = d.photo || null;

      let photoHtml = '';
      if (d.photo) {
        photoHtml = `<div style="margin:8px 0;text-align:center"><img src="${esc(d.photo)}" style="width:120px;height:120px;object-fit:cover;border-radius:10px;border:3px solid var(--gold);box-shadow:0 4px 12px rgba(212,168,67,.3)" onerror="this.style.display='none'"></div>`;
      }

      document.getElementById('qsCharStatus2').innerHTML = `<span style="color:var(--green);font-size:.85rem">✓ ${esc(d.canonical||name)}</span>${photoHtml}`;
      qs2CharVerified=true;
    } else {
      document.getElementById('qsCharStatus2').innerHTML = `<span style="color:var(--red)">⚠ No reconocido</span>`;
      window.qs2CharPhoto = null;
    }

    document.getElementById('qsCharHint2').textContent = d.hint||'';

    if (d.suggestions?.length) {
      document.getElementById('qsCharSuggs2').innerHTML='<div style="font-size:.62rem;color:var(--text2);margin-bottom:6px;font-weight:600">Sugerencias:</div>'+
        d.suggestions.map(s=>{
          const photoImg = s.photo ? `<img src="${esc(s.photo)}" style="width:40px;height:40px;object-fit:cover;border-radius:6px;margin-right:8px;border:2px solid var(--border2)" onerror="this.style.display='none'">` : '';
          return `<button onclick="qs2UseSugg('${esc(s.name)}','${esc(s.photo||'')}')"
            style="display:flex;align-items:center;margin:5px 0;padding:8px 10px;border-radius:8px;background:var(--n3);border:1px solid var(--border2);color:var(--gold);font-size:.7rem;cursor:pointer;width:100%;transition:all .2s"
            onmouseover="this.style.borderColor='var(--gold)';this.style.transform='translateX(4px)'" onmouseout="this.style.borderColor='var(--border2)';this.style.transform='translateX(0)'">
            ${photoImg}<strong>${esc(s.name)}</strong>
          </button>`;
        }).join('');
    }

    box.style.borderColor=d.valid?'rgba(56,184,122,.4)':'rgba(200,48,96,.4)';
  } catch(e) { showAlert('qsAlert3','Error: '+e.message); }
  finally { btn.textContent='🔍 Verificar'; btn.disabled=false; qs2ChkStart(); }
}
function qs2UseSugg(n, p) {
  document.getElementById('qsCharInput2').value=n;
  window.qs2CharPhoto = p || null;
  qsCharChanged2();
  qsVerifyChar2();
}
function qs2ChkStart() { const ok=!!document.getElementById('qsCharInput2')?.value.trim()&&qs2CharVerified&&qs2Players.length>=1; document.getElementById('btnQsStart2').disabled=!ok; }
function qsAcType2() {
  const q=document.getElementById('qsAcInput2').value.trim().toLowerCase();
  const dd=document.getElementById('qsAcDrop2'); qs2AcIdx=-1;
  if(!q){dd.style.display='none';return;}
  const hits=qs2AcAllUsers.filter(u=>!qs2Players.includes(u)&&u.toLowerCase().includes(q)).slice(0,8);
  if(!hits.length){dd.style.display='none';return;}
  dd.innerHTML=hits.map(u=>{const p=u.toLowerCase().indexOf(q);const h=p>=0?esc(u.slice(0,p))+'<b style="color:var(--gold)">'+esc(u.slice(p,p+q.length))+'</b>'+esc(u.slice(p+q.length)):esc(u);return`<div style="padding:8px 12px;font-size:.72rem;cursor:pointer;color:var(--text);border-bottom:1px solid var(--border)" onmouseover="this.style.background='var(--n4)'" onmouseout="this.style.background=''" onmousedown="event.preventDefault();qs2AddPlayer('${u}')">@${h}</div>`}).join('');
  dd.style.display='';
}
function qsAcKey2(e){const rows=[...document.getElementById('qsAcDrop2').querySelectorAll('div')];if(e.key==='ArrowDown'){e.preventDefault();qs2AcIdx=Math.min(qs2AcIdx+1,rows.length-1);rows.forEach((r,i)=>r.style.background=i===qs2AcIdx?'var(--n4)':'')}else if(e.key==='ArrowUp'){e.preventDefault();qs2AcIdx=Math.max(qs2AcIdx-1,0);rows.forEach((r,i)=>r.style.background=i===qs2AcIdx?'var(--n4)':'')}else if(e.key==='Enter'){e.preventDefault();if(qs2AcIdx>=0&&rows[qs2AcIdx])rows[qs2AcIdx].dispatchEvent(new Event('mousedown'))}else if(e.key==='Escape')document.getElementById('qsAcDrop2').style.display='none';}
function qs2AddPlayer(u){if(!u||qs2Players.includes(u)||qs2Players.length>=10)return;qs2Players.push(u);document.getElementById('qsAcInput2').value='';document.getElementById('qsAcDrop2').style.display='none';qs2RenderPills();}
function qs2RemovePlayer(i){qs2Players.splice(i,1);qs2RenderPills();}
function qs2RenderPills(){const el=document.getElementById('qsPills2');el.innerHTML=qs2Players.length?qs2Players.map((u,i)=>`<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(212,168,67,.1);border:1px solid rgba(212,168,67,.25);border-radius:16px;padding:2px 8px 2px 9px;font-size:.66rem;color:var(--gold2)">@${esc(u)}<button onclick="qs2RemovePlayer(${i})" style="background:none;border:none;color:var(--gold3);cursor:pointer;font-size:.75rem;line-height:1">✕</button></span>`).join(''):'<span style="font-size:.62rem;color:var(--text2)">Añade jugadores…</span>';document.getElementById('qsPCount2').textContent=qs2Players.length+' / 10 jugadores';qs2ChkStart();}
async function qsStartGame2(){
  const character=document.getElementById('qsCharInput2')?.value.trim();
  if(!character){showAlert('qsAlert3','Escribe el personaje.');return;}
  if(!qs2Players.length){showAlert('qsAlert3','Añade al menos un jugador.');return;}
  try {
    await req('POST','/api/quiensoy/setup',{
      character,
      character_photo: window.qs2CharPhoto || null,
      players:qs2Players
    });
    qs2UpdateStatus(true);
    showAlert('qsAlert3','¡Partida iniciada!','s');
    document.getElementById('qsCharInput2').value=''; document.getElementById('qsCharInfo2').style.display='none';
    qs2Players=[]; qs2RenderPills(); qs2CharVerified=false; qs2ChkStart();
    window.qs2CharPhoto = null;
    setTimeout(openQuienSoy, 700);
  } catch(e){showAlert('qsAlert3',e.message);}
}

/* ──────────────────────────────────────────────────────────
   CIFRAS Y LETRAS DRAWER (cl2* variables / elements)
────────────────────────────────────────────────────────── */
async function cl2Load() {
  try {
    const [st, users] = await Promise.all([
      req('GET', '/api/cifrasletras/status'),
      req('GET', '/api/cifrasletras/users'),
    ]);
    cl2AllUsers = users || [];
    cl2UpdateStatus(st.enabled, st);
    cl2ConnectWS();
  } catch(e) { showAlert('clAlert2', e.message); }
}
function cl2UpdateStatus(en, data) {
  document.getElementById('clStatusSub2').textContent = en ? '🟢 Juego activo' : '⚫ Juego desactivado';
  document.getElementById('clBtnOff2')?.style.setProperty('display', en?'':'none');
  document.getElementById('clBtnReset2')?.style.setProperty('display', en?'':'none');
  document.getElementById('clBtnOpen2')?.style.setProperty('display', en?'':'none');
  const badge = document.getElementById('drawerBadge');
  if (badge && _curGamePanel === 'cifrasletras') { badge.textContent = en?'🟢 Activo':'⚫ Off'; badge.style.color=en?'var(--green)':'var(--text3)'; }
}
let _cl2Ws = null;
function cl2ConnectWS() {
  if (_cl2Ws && _cl2Ws.readyState < 2) return;
  const wsBase = location.protocol === 'https:' ? 'wss://' + location.host : 'ws://' + location.host;
  _cl2Ws = new WebSocket(wsBase + '/ws/cifrasletras?token=' + encodeURIComponent(localStorage.getItem('dvd_token')||''));
  _cl2Ws.onmessage = e => { try { cl2HandleState(JSON.parse(e.data)); } catch(_){} };
  _cl2Ws.onclose   = () => { if (_curGamePanel === 'cifrasletras') setTimeout(cl2ConnectWS, 3000); };
}
function cl2HandleState(data) {
  if (data.type !== 'state') return;
  cl2UpdateStatus(data.enabled);
  const ps = data.players || [];
  const sec = document.getElementById('clLiveScores');
  if (ps.length) { sec.style.display=''; document.getElementById('clScoreList').innerHTML=[...ps].sort((a,b)=>b.score-a.score).map(p=>`<div style="display:flex;align-items:center;gap:8px;padding:5px 8px;font-size:.75rem"><span style="flex:1;color:var(--text)">@${esc(p.username)}</span><span style="font-family:'Playfair Display',serif;color:var(--gold2)">${p.score} pts</span></div>`).join(''); } else { sec.style.display='none'; }
}
function clAcFilter2() {
  const q=document.getElementById('clAcIn2').value.trim().toLowerCase();
  const dd=document.getElementById('clAcDrop2'); cl2AcIdx=-1;
  if(!q){dd.style.display='none';return;}
  const hits=cl2AllUsers.filter(u=>!cl2Players.includes(u)&&u.toLowerCase().includes(q)).slice(0,8);
  if(!hits.length){dd.style.display='none';return;}
  dd.innerHTML=hits.map(u=>{const p=u.toLowerCase().indexOf(q);const h=p>=0?esc(u.slice(0,p))+'<b style="color:var(--gold)">'+esc(u.slice(p,p+q.length))+'</b>'+esc(u.slice(p+q.length)):esc(u);return`<div style="padding:8px 12px;font-size:.75rem;cursor:pointer;color:var(--text);border-bottom:1px solid var(--border)" onmouseover="this.style.background='var(--n4)'" onmouseout="this.style.background=''" onmousedown="event.preventDefault();cl2AddPlayer('${u}')">@${h}</div>`}).join('');
  dd.style.display='';
}
function clAcKey2(e){const rows=[...document.getElementById('clAcDrop2').querySelectorAll('div')];if(e.key==='ArrowDown'){e.preventDefault();cl2AcIdx=Math.min(cl2AcIdx+1,rows.length-1);rows.forEach((r,i)=>r.style.background=i===cl2AcIdx?'var(--n4)':'')}else if(e.key==='ArrowUp'){e.preventDefault();cl2AcIdx=Math.max(cl2AcIdx-1,0);rows.forEach((r,i)=>r.style.background=i===cl2AcIdx?'var(--n4)':'')}else if(e.key==='Enter'){e.preventDefault();if(cl2AcIdx>=0&&rows[cl2AcIdx])rows[cl2AcIdx].dispatchEvent(new Event('mousedown'))}else if(e.key==='Escape')document.getElementById('clAcDrop2').style.display='none';}
function cl2AddPlayer(u){if(!u||cl2Players.includes(u)||cl2Players.length>=10)return;cl2Players.push(u);document.getElementById('clAcIn2').value='';document.getElementById('clAcDrop2').style.display='none';cl2RenderPills();}
function cl2RemovePlayer(i){cl2Players.splice(i,1);cl2RenderPills();}
function cl2RenderPills(){const el=document.getElementById('clPills2');el.innerHTML=cl2Players.length?cl2Players.map((u,i)=>`<span style="display:inline-flex;align-items:center;gap:4px;background:rgba(212,168,67,.1);border:1px solid rgba(212,168,67,.25);border-radius:16px;padding:2px 8px 2px 9px;font-size:.66rem;color:var(--gold2)">@${esc(u)}<button onclick="cl2RemovePlayer(${i})" style="background:none;border:none;color:var(--gold3);cursor:pointer;font-size:.75rem;line-height:1">✕</button></span>`).join(''):'<span style="font-size:.62rem;color:var(--text2)">Añade jugadores…</span>';document.getElementById('clPCount2').textContent=cl2Players.length+' / 10';document.getElementById('clBtnStart2').disabled=!cl2Players.length;}
async function clStartGame2(){
  if(!cl2Players.length){showAlert('clAlert3','Añade al menos un jugador.');return;}
  const maxRounds=parseInt(document.getElementById('clRounds2').value);
  const roundTime=parseInt(document.getElementById('clSeconds2').value);
  const btn=document.getElementById('clBtnStart2');btn.disabled=true;btn.textContent='⏳…';
  try{await req('POST','/api/cifrasletras/setup',{players:cl2Players.slice(),max_rounds:maxRounds,round_time:roundTime});cl2UpdateStatus(true);showAlert('clAlert3','✓ Partida iniciada','s');cl2Players=[];cl2RenderPills();setTimeout(openCifrasLetras,600);}catch(e){showAlert('clAlert3',e.message);}
  finally{btn.disabled=!cl2Players.length;btn.textContent='▶ Iniciar partida';}
}

/* ──────────────────────────────────────────────────────────
   HUNDIR LA FLOTA DRAWER
────────────────────────────────────────────────────────── */
async function hlfLoad() {
  try {
    const d = await req('GET', '/api/hundirlaflota/status');
    const en = !!d.enabled;
    document.getElementById('hlfStatusSub').textContent = en ? '🟢 Juego activo' : '⚫ Juego desactivado';
    document.getElementById('hlfBtnOn')?.style.setProperty('display', en?'none':'');
    document.getElementById('hlfBtnOff')?.style.setProperty('display', en?'':'none');
    const badge = document.getElementById('drawerBadge');
    if (badge && _curGamePanel === 'hundirlaflota') {
      badge.textContent = en?'🟢 Activo':'⚫ Off';
      badge.style.color=en?'var(--green)':'var(--text3)';
    }
  } catch(e) { showAlert('hlfAlert1', e.message); }
}

async function hlfToggle(enable) {
  try {
    await req('POST', '/api/hundirlaflota/toggle', { enabled: enable });
    await hlfLoad();
    await checkHundirLaFlotaStatus();
    showAlert('hlfAlert1', enable ? '✓ Hundir la Flota activado' : 'Hundir la Flota desactivado', enable?'s':'');
  } catch(e) { showAlert('hlfAlert1', e.message); }
}

/* ──────────────────────────────────────────────────────────
   CUENTOS DRAWER
────────────────────────────────────────────────────────── */
async function ctLoad() {
  try {
    const d = await req('GET', '/api/cuentos/status');
    const en = !!d.enabled;
    document.getElementById('ctStatusSub').textContent = en ? '🟢 Visible para todos' : '⚫ Solo admins';
    document.getElementById('ctBtnOn')?.style.setProperty('display', en?'none':'');
    document.getElementById('ctBtnOff')?.style.setProperty('display', en?'':'none');
    const badge = document.getElementById('drawerBadge');
    if (badge && _curGamePanel === 'cuentos') { badge.textContent = en?'🟢 Activo':'⚫ Off'; badge.style.color=en?'var(--green)':'var(--text3)'; }
  } catch(e) { showAlert('ctAlert', e.message); }
}
async function toggleCuentos(en) {
  try {
    await req('POST', '/api/cuentos/toggle');
    await ctLoad();
    showAlert('ctAlert', en ? '✓ Cuentos visibles para todos' : 'Cuentos ocultos', en?'s':'');
  } catch(e) { showAlert('ctAlert', e.message); }
}

/* ──────────────────────────────────────────────────────────
   OPO DRAWER (reuses existing OPO logic with new element IDs)
────────────────────────────────────────────────────────── */
let _opoAllUsers2 = [];
async function opoLoad2() {
  try {
    const [players, connected] = await Promise.all([
      req('GET', '/api/opo/players'),
      req('GET', '/api/admin/connected').catch(()=>[])
    ]);
    _opoPlayers = players;
    _ONLINE_MAP = {};
    (connected||[]).forEach(u => { _ONLINE_MAP[u] = true; });
    renderOpoPlayers2();
  } catch(e) { showAlert('opoAlert2', e.message); }
}
function renderOpoPlayers2() {
  const el = document.getElementById('opoPlayersList2');
  if (!el) return;
  if (!_opoPlayers.length) { el.innerHTML = '<div style="font-size:.72rem;color:var(--text3);padding:8px 0">Sin jugadores OPO registrados</div>'; return; }
  el.innerHTML = _opoPlayers.map(p => {
    const online = !!_ONLINE_MAP[p.username];
    const isSuperadmin = p.username === 'dvd';
    return `<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;background:var(--glass);border:1px solid var(--border);border-radius:8px">
      <span style="width:8px;height:8px;border-radius:50%;background:${online?'var(--green)':'var(--text3)'};flex-shrink:0"></span>
      <span style="flex:1;font-size:.78rem;color:var(--text)">@${esc(p.username)}</span>
      ${!isSuperadmin ? `<button onclick="opoRemovePlayer2('${esc(p.username)}')" class="btn btnD btnSm" style="padding:3px 8px;font-size:.6rem">✕</button>` : ''}
    </div>`;
  }).join('');
}
async function opoAddPlayer2() {
  const inp = document.getElementById('opoAddInput2');
  const uname = (inp?.value||'').trim().toLowerCase();
  if (!uname) return;
  try { await req('POST', '/api/opo/players', { username: uname }); inp.value=''; document.getElementById('opoSuggestBox2').style.display='none'; showAlert('opoAlert2','@'+uname+' añadido al OPO','s'); await opoLoad2(); }
  catch(e) { showAlert('opoAlert2', e.message||'Error'); }
}
async function opoRemovePlayer2(uname) {
  if (!confirm('¿Quitar a @'+uname+' del OPO?')) return;
  try { await req('DELETE', '/api/opo/players/'+uname); showAlert('opoAlert2','@'+uname+' eliminado','s'); await opoLoad2(); }
  catch(e) { showAlert('opoAlert2', e.message); }
}
async function opoSuggest2(val) {
  const box = document.getElementById('opoSuggestBox2'); if (!box) return;
  if (!val || val.length < 2) { box.style.display='none'; return; }
  if (!_opoAllUsers2.length) {
    try { const d = await req('GET', '/api/admin/users'); _opoAllUsers2 = (d||[]).filter(u=>!u.is_admin&&!u.is_ghost).map(u=>u.username); } catch(_){}
  }
  const q = val.toLowerCase();
  const matches = _opoAllUsers2.filter(u => u.includes(q)).slice(0,8);
  if (!matches.length) { box.style.display='none'; return; }
  box.style.display='block';
  box.innerHTML = matches.map(u => `<div style="padding:6px 10px;cursor:pointer;font-size:.72rem;color:var(--text);border-bottom:1px solid var(--border)" onmouseover="this.style.background='var(--n4)'" onmouseout="this.style.background=''" onmousedown="document.getElementById('opoAddInput2').value='${u}';document.getElementById('opoSuggestBox2').style.display='none'">@${esc(u)}</div>`).join('');
}

/* ── Change password ───────────────────────────────────── */
async function changePwd() {
  const old_p = (document.getElementById('pwdOld')?.value || '').trim();
  const new_p = (document.getElementById('pwdNew')?.value || '').trim();
  if (!old_p || !new_p) { showAlert('pwdAlert', 'Rellena ambos campos'); return; }
  if (new_p.length < 4)  { showAlert('pwdAlert', 'La nueva contraseña debe tener al menos 4 caracteres'); return; }
  try {
    await req('POST', '/api/me/change-password', { old_password: old_p, new_password: new_p });
    showAlert('pwdAlert', '✓ Contraseña actualizada correctamente', 's');
    document.getElementById('pwdOld').value = '';
    document.getElementById('pwdNew').value = '';
  } catch(e) {
    showAlert('pwdAlert', e.message || 'Error al cambiar contraseña');
  }
}

/* ── Contact & Notifications ───────────────────────────────────── */
async function loadContactInfo() {
  if (!me) return;
  try {
    // Los datos ya vienen en el objeto 'me' desde /api/me
    document.getElementById('profileEmail').value = me.email || '';
    document.getElementById('profilePhone').value = me.phone || '';
    document.getElementById('profileWhatsapp').value = me.whatsapp || '';
    document.getElementById('notifEmail').checked = me.notifications_email !== false;
    document.getElementById('notifSMS').checked = me.notifications_sms === true;
    document.getElementById('notifWhatsApp').checked = me.notifications_whatsapp === true;
  } catch(e) {
    console.warn('Error loading contact info:', e);
  }
}

async function saveContactInfo() {
  const email = (document.getElementById('profileEmail')?.value || '').trim();
  const phone = (document.getElementById('profilePhone')?.value || '').trim();
  const whatsapp = (document.getElementById('profileWhatsapp')?.value || '').trim();
  const notifEmail = document.getElementById('notifEmail')?.checked;
  const notifSMS = document.getElementById('notifSMS')?.checked;
  const notifWhatsApp = document.getElementById('notifWhatsApp')?.checked;
  
  try {
    await req('POST', '/api/me/update-profile', {
      email: email || null,
      phone: phone || null,
      whatsapp: whatsapp || null,
      notifications_email: notifEmail,
      notifications_sms: notifSMS,
      notifications_whatsapp: notifWhatsApp
    });
    
    // Update local me object
    me.email = email || null;
    me.phone = phone || null;
    me.whatsapp = whatsapp || null;
    me.notifications_email = notifEmail;
    me.notifications_sms = notifSMS;
    me.notifications_whatsapp = notifWhatsApp;
    
    showAlert('contactAlert', '✓ Configuración guardada correctamente', 's');
  } catch(e) {
    showAlert('contactAlert', e.message || 'Error al guardar configuración');
  }
}

/* ── 10. Navigation ─────────────────────────────────────── */
let _previousPanel = null; // Variable para guardar la pestaña anterior

function nav(name, el) {
  // Guardar la pestaña actual antes de cambiar
  const currentView = document.querySelector('.view.on');
  if (currentView && currentView.id !== 'view-' + name) {
    _previousPanel = currentView.id.replace('view-', '');
  }

  document.querySelectorAll('.view').forEach(v => v.classList.remove('on'));
  document.getElementById('view-' + name)?.classList.add('on');
  document.querySelectorAll('.navTab').forEach(tab => tab.classList.remove('on'));
  document.querySelectorAll('.mNavBtn').forEach(b => b.classList.toggle('on', b.dataset.view === name));
  if (el?.classList.contains('navTab')) {
    el.classList.add('on');
  } else {
    document.querySelectorAll('.navTab').forEach(tab => {
      if (tab.getAttribute('onclick')?.includes(`'${name}'`)) tab.classList.add('on');
    });
  }
  if (name === 'hist')    { loadHist('fullH', 1000); }
  if (name === 'adm') {
    // Block non-admins from accessing admin view
    if (!me?.is_admin) {
      nav('dash', null);
      return;
    }
    // Always reset game drawer when returning to admin tab
    const drawer = document.getElementById('gameDrawer');
    const grid   = document.getElementById('gameBtnGrid');
    if (drawer) drawer.style.display = 'none';
    if (grid)   grid.style.display   = '';
    _curGamePanel = null;
    if (me?.is_superadmin) {
      document.getElementById('panelGameBtns')?.style.setProperty('display', '');
    }
    loadAdmin();
  }
  if (name === 'dash')    { loadHist('dashH', 10); loadUserApuestas(); }
  if (name === 'tx')      { loadDropdown(); }
  if (name === 'gallery') loadGallery();
  // NO solicitar permisos automáticamente al abrir Social
  // Los permisos se solicitarán cuando el usuario inicie/se una a una videollamada
}

/* ── Request media permissions REMOVED ─────────────────────
   Media permissions (audio/video) are now requested on-demand:
   - When joining/creating a video call (_enterRoom function)
   - When recording audio messages (chat)
   - When playing games that require audio
   This improves UX by not asking for permissions unnecessarily.
─────────────────────────────────────────────────────────── */

/* ── 11. Boot sequence ──────────────────────────────────── */
window.addEventListener('DOMContentLoaded', async () => {
  await loadLang(curLang);   // Language must load first (all text depends on it)
  if (token) {
    try {
      await loadApp(); // Resume session if token exists in localStorage
    } catch (e) {
      // Token expired or invalid — clear it and show login screen
      token = null;
      localStorage.removeItem('dvd_token');
      document.getElementById('authWrap').classList.remove('hidden');
      document.getElementById('authHdr').classList.remove('hidden');
      document.getElementById('app').classList.add('hidden');
    }
  }
});

/* ── OPO Dashboard ─────────────────────────────────────── */
const escHtml = s => String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
let _opoPlayers = [];

// Map of username → online status (populated from /api/admin/connected)
let _ONLINE_MAP = {};

async function loadOpoDash() {
  try {
    const [players, connected] = await Promise.all([
      req('GET', '/api/opo/players'),
      req('GET', '/api/admin/connected').catch(()=>[])
    ]);
    _opoPlayers = players;
    _ONLINE_MAP = {};
    (connected||[]).forEach(u => { _ONLINE_MAP[u] = true; });
    renderOpoPlayers();
  } catch(e) { console.error('OPO dash error', e); }
}

function renderOpoPlayers() {
  const el = document.getElementById('opoPlayersList');
  if (!el) return;
  if (!_opoPlayers.length) {
    el.innerHTML = '<div style="font-size:.7rem;color:var(--text3);padding:10px 0">Sin jugadores añadidos.</div>';
    return;
  }
  const totalAllS = _opoPlayers.reduce((s,p)=>s+(p.total_s||0),0);
  const rows = _opoPlayers.map(p => {
    const isDvdNeb = p.username==='dvd' || p.username==='nebulosa';
    const isOnline = !!(_ONLINE_MAP && _ONLINE_MAP[p.username]);
    const dot = isOnline
      ? '<span class="onlineDot" title="Online"></span>'
      : '<span class="offlineDot" title="Offline"></span>';
    const lastC  = p.last_conn ? fmtDate(p.last_conn) : '—';
    const totalH = p.total_s  > 0 ? fmtDuration(p.total_s) : '—';
    const removeBtn = !isDvdNeb
      ? `<button class="btn btnD btnSm" onclick="opoRemovePlayer('${escHtml(p.username)}')">✕ Quitar</button>`
      : '';
    return `<tr>
      <td style="padding:4px 2px;text-align:center">${dot}</td>
      <td style="font-weight:500;color:var(--text)">@${escHtml(p.username)}</td>
      <td style="color:var(--gold3)">${p.tests_done} test${p.tests_done!==1?'s':''}</td>
      <td style="color:var(--text3)">${lastC}</td>
      <td style="color:var(--text3)">${totalH}</td>
      <td style="display:flex;gap:5px;flex-wrap:wrap">${removeBtn}</td>
    </tr>`;
  }).join('');
  el.innerHTML = `
    <table class="tbl" style="margin-top:4px">
      <thead><tr>
        <th style="width:18px;padding:4px 2px"></th>
        <th>Usuario</th><th>Tests</th><th>Última conexión</th>
        <th>Tiempo total</th><th>Acciones</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <div style="padding:5px 2px;font-size:.62rem;color:var(--text3);text-align:right;border-top:1px solid var(--border);margin-top:4px">
      Tiempo total OPO: <strong style="color:var(--gold2)">${fmtDuration(totalAllS)}</strong>
    </div>`;
}

async function opoAddPlayer() {
  const inp = document.getElementById('opoAddInput');
  const uname = (inp?.value || '').trim().toLowerCase();
  if (!uname) return;
  try {
    await req('POST', '/api/opo/players', { username: uname });
    inp.value = '';
    document.getElementById('opoSuggestBox').innerHTML = '';
    document.getElementById('opoSuggestBox').style.display = 'none';
    showAlert('opoAddAlert', `@${uname} puede acceder al OPO`, 's');
    await loadOpoDash();
  } catch(e) {
    showAlert('opoAddAlert', e.message || 'Error al añadir');
  }
}

async function opoRemovePlayer(uname) {
  if (!confirm(`¿Quitar a @${uname} del OPO?`)) return;
  try {
    await req('DELETE', `/api/opo/players/${uname}`);
    await loadOpoDash();
  } catch(e) { showAlert('opoAddAlert', e.message || 'Error'); }
}

// Autocomplete for OPO add input
let _opoAllUsers = [];
async function opoSuggest(val) {
  const box = document.getElementById('opoSuggestBox');
  if (!box) return;
  if (!val || val.length < 1) { box.style.display = 'none'; box.innerHTML = ''; return; }
  // Load users if not loaded
  if (!_opoAllUsers.length) {
    try {
      const d = await req('GET', '/api/admin/users');
      _opoAllUsers = (d || []).filter(u => !u.is_admin && !u.is_ghost).map(u => u.username);
    } catch(e) { return; }
  }
  const q = val.toLowerCase();
  const matches = _opoAllUsers.filter(u => u.includes(q)).slice(0, 8);
  if (!matches.length) { box.style.display = 'none'; return; }
  box.style.display = 'block';
  box.innerHTML = matches.map(u =>
    `<div style="padding:6px 10px;cursor:pointer;font-size:.72rem;color:var(--text);
      border-bottom:1px solid var(--border)"
      onmousedown="document.getElementById('opoAddInput').value='${u}';
        document.getElementById('opoSuggestBox').style.display='none'"
    >@${escHtml(u)}</div>`
  ).join('');
}

async function checkOpoAccess() {
  // Superadmins have full OPO management in dashDvdStats already
  if (me.is_superadmin) return;
  // Regular admins: no OPO member panel
  if (me.is_admin) return;
  try {
    const st = await req('GET', '/api/opo/status');
    if (st.is_opo_user) {
      // Show OPO panel on member home (2 buttons: advanced stats + select questionnaire)
      const panel = document.getElementById('dashMemberOpo');
      if (panel) panel.style.display = '';
    }
  } catch(e) {}
}

async function loadDvdStats() {
  const el = document.getElementById('dvdStatsContent');
  if (!el) return;
  try {
    const [summary, txSummary, apuestasSummary] = await Promise.all([
      req('GET', '/api/stats/summary').catch(() => []),
      req('GET', '/api/stats/transactions-summary').catch(() => ({})),
      req('GET', '/api/stats/apuestas-summary').catch(() => ({})),
    ]);
    const totalUsers = summary.length;
    const totalSessions = summary.reduce((s,u) => s + (u.total_sessions||0), 0);
    const totalTx  = txSummary.total_tx  || 0;
    const totalVol = txSummary.total_vol || 0;
    const totalApostado = apuestasSummary.total_apostado || 0;
    const totalPremios = apuestasSummary.total_premios || 0;
    const porrasAbiertas = apuestasSummary.porras_abiertas || 0;
    const porrasFinalizadas = apuestasSummary.porras_finalizadas || 0;

    el.innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin-bottom:10px">
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Usuarios</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${totalUsers}</div>
        </div>
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Sesiones</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${totalSessions}</div>
        </div>
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Transferencias</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${totalTx}</div>
        </div>
        <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
          <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Volumen ◆</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${fmtC(totalVol)}</div>
        </div>
      </div>

      <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
        <div style="font-size:.7rem;color:var(--gold2);text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;display:flex;align-items:center;gap:6px">
          <span>🎲</span> Estadísticas de Apuestas
        </div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px">
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
            <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Apostado</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${fmtC(totalApostado)} ◆</div>
          </div>
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
            <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Premios</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${fmtC(totalPremios)} ◆</div>
          </div>
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
            <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Abiertas</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${porrasAbiertas}</div>
          </div>
          <div style="background:var(--glass);border:1px solid var(--border);border-radius:var(--r);padding:10px 12px">
            <div style="font-size:.58rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em">Finalizadas</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--gold2)">${porrasFinalizadas}</div>
          </div>
        </div>
      </div>

      <div style="font-size:.62rem;color:var(--text3);text-align:right;margin-top:10px">
        <a href="/bank/stats" style="color:var(--gold3);text-decoration:none">Ver estadísticas completas →</a>
      </div>`;
    document.getElementById('dvdStatsSub').textContent = `${totalUsers} miembros · ${totalSessions} sesiones · ${porrasAbiertas} porras activas`;
  } catch(e) {
    el.innerHTML = '<div class="empty">No se pudieron cargar las estadísticas</div>';
  }
}

function showMemberOpoSelect() {
  // Open OPO with block selection visible — just navigate to the game
  window.open('/opo?token=' + encodeURIComponent(localStorage.getItem('dvd_token')), '_blank');
}

async function showOpoResults() {
  const modal = document.getElementById('opoResultsModal');
  const body = document.getElementById('opoResultsBody');
  if (!modal || !body) return;
  modal.style.display = 'block';
  body.innerHTML = 'Cargando…';
  try {
    const results = await req('GET', '/api/opo/results');
    if (!results.length) { body.innerHTML = '<div class="empty">Sin resultados</div>'; return; }
    // Group by user for summary
    const byUser = {};
    results.forEach(r => {
      if (!byUser[r.username]) byUser[r.username] = {correct:0, wrong:0, tests:0};
      byUser[r.username].correct += r.correct;
      byUser[r.username].wrong   += r.wrong;
      byUser[r.username].tests++;
    });
    const summaryRows = Object.entries(byUser)
      .sort((a,b) => b[1].correct - a[1].correct)
      .map(([u,s]) => {
        const total = s.correct + s.wrong;
        const pct = total > 0 ? Math.round(s.correct/total*100) : 0;
        return `<div style="display:flex;gap:10px;align-items:center;padding:5px 8px;
          background:var(--n4);border-radius:7px;border:1px solid var(--border);font-size:.7rem">
          <span style="flex:1;color:var(--text)">@${escHtml(u)}</span>
          <span style="color:var(--text3)">${s.tests} test${s.tests!==1?'s':''}</span>
          <span style="color:var(--green)">✓ ${s.correct}</span>
          <span style="color:var(--red)">✗ ${s.wrong}</span>
          <span style="color:var(--gold2);font-weight:700">${pct}%</span>
        </div>`;
      }).join('');

    body.innerHTML = `
      <div style="margin-bottom:14px">
        <div style="font-size:.6rem;color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">Resumen por usuario</div>
        <div style="display:flex;flex-direction:column;gap:4px">${summaryRows}</div>
      </div>
      <div style="font-size:.6rem;color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">Todos los resultados</div>
      <table style="width:100%;border-collapse:collapse;font-size:.68rem">
        <thead><tr style="color:var(--text3);font-size:.58rem;letter-spacing:.08em;
          text-transform:uppercase;border-bottom:1px solid var(--border)">
          <th style="padding:5px 6px;text-align:left">Usuario</th>
          <th style="padding:5px 6px;text-align:center">Test</th>
          <th style="padding:5px 6px;text-align:center">Fecha y hora</th>
          <th style="padding:5px 6px;text-align:center">✓</th>
          <th style="padding:5px 6px;text-align:center">✗</th>
        </tr></thead>
        <tbody>
          ${results.map(r => {
            const total = r.correct + r.wrong;
            const pct = total > 0 ? Math.round(r.correct/total*100) : 0;
            return `<tr style="border-bottom:1px solid var(--border)">
              <td style="padding:5px 6px;color:var(--text)">@${escHtml(r.username)}</td>
              <td style="padding:5px 6px;text-align:center;color:var(--gold2);font-family:'Oswald',sans-serif;font-weight:600">
                Test ${r.block_n}</td>
              <td style="padding:5px 6px;text-align:center;color:var(--text3)">${fmtDate(r.played_at)}</td>
              <td style="padding:5px 6px;text-align:center;color:var(--green)">${r.correct}</td>
              <td style="padding:5px 6px;text-align:center;color:var(--red)">${r.wrong}</td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>`;
  } catch(e) {
    body.innerHTML = '<div class="empty">Error cargando resultados</div>';
  }
}

/* ── Admin Management (superadmin only) ─────────────────────────────── */
async function loadAdminMgmt() {
  try {
    const admins = await req('GET', '/api/admin/list-admins');
    renderAdminsList(admins);
  } catch(e) { console.error('loadAdminMgmt', e); }
}

function renderAdminsList(admins) {
  const el = document.getElementById('adminsList');
  if (!el) return;
  if (!admins.length) {
    el.innerHTML = '<div class="empty">Sin admins adicionales</div>';
    return;
  }
  el.innerHTML = admins.map(a => {
    const isSuperadmin = a.is_superadmin;
    const canRemove = !isSuperadmin;
    const badge = isSuperadmin
      ? '<span style="font-size:.58rem;color:var(--gold2);border:1px solid var(--border);border-radius:20px;padding:1px 7px">superadmin</span>'
      : '<span style="font-size:.58rem;color:var(--text3);border:1px solid var(--border);border-radius:20px;padding:1px 7px">admin</span>';
    return `<div style="display:flex;align-items:center;gap:8px;padding:8px 10px;
      background:var(--n4);border:1px solid var(--border);border-radius:8px">
      <div style="flex:1;font-size:.75rem;color:var(--text)">@${escHtml(a.username)}</div>
      ${badge}
      <div style="display:flex;gap:5px">
        <button class="btn btnN btnSm" style="font-size:.6rem;padding:3px 8px"
          onclick="resetAdminPwd('${escHtml(a.username)}')">🔑 Reset pwd</button>
        ${canRemove ? `<button class="btn btnD btnSm" style="font-size:.6rem;padding:3px 8px"
          onclick="deleteAdmin('${escHtml(a.username)}')">✕ Quitar</button>` : ''}
      </div>
    </div>`;
  }).join('');
}

async function createAdmin() {
  const uname = (document.getElementById('newAdminUser')?.value || '').trim().toLowerCase();
  const pwd   = (document.getElementById('newAdminPwd')?.value || '').trim();
  if (!uname) { showAlert('adminMgmtAlert', 'Introduce un nombre de usuario'); return; }
  try {
    await req('POST', '/api/admin/create-admin', { username: uname, password: pwd });
    document.getElementById('newAdminUser').value = '';
    document.getElementById('newAdminPwd').value = '';
    showAlert('adminMgmtAlert', `@${uname} es ahora admin`, 's');
    await loadAdminMgmt();
  } catch(e) { showAlert('adminMgmtAlert', e.message || 'Error al crear admin'); }
}

async function deleteAdmin(uname) {
  if (!confirm(`¿Quitar permisos de admin a @${uname}?`)) return;
  try {
    await req('DELETE', `/api/admin/delete-admin/${uname}`);
    showAlert('adminMgmtAlert', `@${uname} ya no es admin`, 's');
    await loadAdminMgmt();
  } catch(e) { showAlert('adminMgmtAlert', e.message || 'Error'); }
}

async function resetAdminPwd(uname) {
  if (!confirm(`¿Resetear la contraseña de @${uname}? Deberá registrarse de nuevo.`)) return;
  try {
    await req('POST', `/api/admin/reset-admin-pwd/${uname}`);
    showAlert('adminMgmtAlert', `Contraseña de @${uname} reseteada`, 's');
  } catch(e) { showAlert('adminMgmtAlert', e.message || 'Error'); }
}

/* ──────────────────────────────────────────────────────────
   MENSAJES DRAWER
────────────────────────────────────────────────────────── */
async function msgLoad() {
  try {
    const status = await req('GET', '/api/messages/status');
    const enabled = !!status.enabled;
    const online = status.online || [];
    msgUpdateStatus(enabled, online);
    await msgLoadStats();
  } catch(e) { showAlert('msgAlert1', e.message); }
}

function msgUpdateStatus(enabled, online) {
  const onlineCount = (online || []).filter(u => u !== (me?.username||'')).length;
  document.getElementById('msgStatusSub').textContent = enabled
    ? ('🟢 Mensajería activa' + (onlineCount > 0 ? ` · ${onlineCount} en línea` : ''))
    : '⚫ Mensajería desactivada';
  document.getElementById('msgBtnOn')?.style.setProperty('display',  enabled ? 'none' : '');
  document.getElementById('msgBtnOff')?.style.setProperty('display', enabled ? ''     : 'none');
  document.getElementById('msgBtnOpen')?.style.setProperty('display',enabled ? ''     : 'none');
  const badge = document.getElementById('drawerBadge');
  if (badge && _curGamePanel === 'mensajes') {
    badge.textContent = enabled ? '🟢 Activo' : '⚫ Off';
    badge.style.color = enabled ? 'var(--green)' : 'var(--text3)';
  }
}

async function msgToggle(on) {
  try {
    await req('POST', '/api/messages/toggle', { enabled: on });
    msgUpdateStatus(on, []);
    showAlert('msgAlert1', on ? '✓ Mensajería activada' : 'Mensajería desactivada', on ? 's' : '');
    if (on) await msgLoadStats();
  } catch(e) { showAlert('msgAlert1', e.message); }
}

function msgOpen() {
  window.open('/messages?token=' + encodeURIComponent(localStorage.getItem('dvd_token') || ''), '_blank');
}

async function msgLoadStats() {
  try {
    const d = await req('GET', '/api/messages/admin/stats');
    document.getElementById('msgStatTotal').textContent  = d.total_messages  ?? '—';
    document.getElementById('msgStatToday').textContent  = d.messages_today  ?? '—';
    document.getElementById('msgStatUsers').textContent  = d.unique_senders  ?? '—';
    document.getElementById('msgStatRooms').textContent  = d.total_rooms     ?? '—';
    if (d.enabled !== undefined) msgUpdateStatus(!!d.enabled, []);
    msgRenderRecent(d.recent || []);
  } catch(e) {
    document.getElementById('msgRecentList').innerHTML =
      '<div style="font-size:.67rem;color:var(--text3);text-align:center;padding:12px">Sin datos aún</div>';
  }
}

function msgRenderRecent(msgs) {
  const el = document.getElementById('msgRecentList');
  if (!el) return;
  if (!msgs.length) {
    el.innerHTML = '<div style="font-size:.67rem;color:var(--text3);text-align:center;padding:12px">Sin mensajes aún</div>';
    return;
  }
  el.innerHTML = msgs.map(m => {
    const isAudio = m.msg_type === 'audio';
    const isImg   = m.msg_type === 'image';
    const preview = isAudio ? '🎤 Nota de voz' : isImg ? '🖼 Imagen' : esc(m.content || '').slice(0, 60);
    let timeStr = '';
    try {
      const d   = new Date((m.created_at?.includes('T') ? m.created_at : (m.created_at||'').replace(' ','T')) + 'Z');
      const now = new Date();
      const isToday = d.toDateString() === now.toDateString();
      timeStr = isToday
        ? d.toLocaleTimeString('es-ES', { hour:'2-digit', minute:'2-digit', hour12:false })
        : d.toLocaleDateString('es-ES', { day:'2-digit', month:'2-digit' }) + ' '
          + d.toLocaleTimeString('es-ES', { hour:'2-digit', minute:'2-digit', hour12:false });
    } catch(_) { timeStr = (m.created_at || '').slice(11, 16); }
    return `<div style="display:flex;gap:8px;padding:7px 2px;border-bottom:1px solid rgba(255,255,255,.04);font-size:.64rem;align-items:flex-start">
      <span style="color:var(--gold3);min-width:72px;flex-shrink:0;padding-top:1px">@${esc(m.from_user)}</span>
      <span style="flex:1;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${preview}</span>
      ${isAudio ? '<span style="font-size:.52rem;color:var(--blue);flex-shrink:0">audio</span>' : ''}
      ${isImg   ? '<span style="font-size:.52rem;color:var(--green);flex-shrink:0">img</span>'   : ''}
      <span style="font-size:.52rem;color:var(--text3);flex-shrink:0;white-space:nowrap">${timeStr}</span>
    </div>`;
  }).join('');
}

/* ══════════════════════════════════════════════════════════════
   SOCIAL & CHAT — WebRTC + WebSocket Messaging
   ══════════════════════════════════════════════════════════════ */
// Variables de estado de videollamada
let _socialWS=null, _socialRoom='group', _socialDMTarget='', _localStream=null,
    _currentVideoRoom='', _micEnabled=true, _camEnabled=true,
    _callInvited=new Set(), _callMembers=new Set();
let _permStream = null;  // stream de permisos — se obtiene al login, se reutiliza en llamadas

// WebSocket de video (señalización WebRTC)
let _videoWS = null;
// Peers WebRTC: username → RTCPeerConnection
const _rtcPeers = {};
// Streams remotos: username → MediaStream
const _remoteStreams = {};
// Queue de ICE candidates pendientes: username → [candidates]
const _pendingIceCandidates = {};

/* ══════════════════════════════════════════════════════════════════════════
   VIDEO — WebRTC con relay de señalización via servidor
   El servidor /ws/video reenvía offer/answer/ice entre peers.
   Cada peer envía su stream directamente al otro via WebRTC.
══════════════════════════════════════════════════════════════════════════ */

const _ICE_SERVERS = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  { urls: 'stun:stun2.l.google.com:19302' },
  { urls: 'stun:stun.cloudflare.com:3478' },
];

/** Conectar al WebSocket de señalización */
function _videoConnect(roomKey){
  if(_videoWS && _videoWS.readyState <= 1) return;
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const tok = localStorage.getItem('dvd_token') || '';
  _videoWS = new WebSocket(`${proto}//${location.host}/ws/video?token=${encodeURIComponent(tok)}`);
  _videoWS.binaryType = 'arraybuffer';

  _videoWS.onopen = () => {
    console.log('[VIDEO] WS connected, joining room:', roomKey);
    _videoWS.send(JSON.stringify({ action: 'join', room: roomKey }));
  };

  _videoWS.onmessage = async e => {
    // Ignorar mensajes binarios (relay legacy)
    if(typeof e.data !== 'string') return;

    let msg;
    try{ msg = JSON.parse(e.data); }catch{ return; }

    console.log('[VIDEO] WS message:', msg.type, 'from:', msg.from);

    if(msg.type === 'peer-joined'){
      const peer = msg.from;
      console.log('[VIDEO] 👤 peer-joined:', peer);
      _callMembers.add(peer);
      _updateParticipants(); _updatePeerCount();
      if(!document.getElementById('vtile-' + peer)) _addTile(peer, null, peer, false);
      // El que ya estaba en la sala inicia la oferta
      setTimeout(() => {
        console.log('[VIDEO] Initiating offer to', peer);
        _createPeerConnection(peer, true).catch(e => console.warn('[RTC] offer error:', e));
      }, 100);

    } else if(msg.type === 'peer-left'){
      const peer = msg.from;
      console.log('[VIDEO] 👋 peer-left:', peer);
      _callMembers.delete(peer);
      _removeTile(peer);
      _closePeer(peer);
      _updateParticipants(); _updatePeerCount();

    } else if(msg.type === 'webrtc-offer'){
      const peer = msg.from;
      console.log('[VIDEO] 📨 webrtc-offer from:', peer);
      if(!document.getElementById('vtile-' + peer)) _addTile(peer, null, peer, false);
      _callMembers.add(peer);

      // Manejar glare (ofertas simultáneas): el que tiene username "menor" gana
      const existingPc = _rtcPeers[peer];
      if(existingPc && existingPc.signalingState !== 'stable'){
        console.log('[RTC] ⚠️ Glare detected with', peer, '— resolving...');
        const myName = me?.username || '';
        if(myName < peer){
          // Yo gano, ignorar la oferta del otro
          console.log('[RTC] Ignoring offer from', peer, '(I win glare)');
          return;
        } else {
          // El otro gana, cerrar mi conexión y aceptar su oferta
          console.log('[RTC] Accepting offer from', peer, '(they win glare)');
          _closePeer(peer);
        }
      }

      // Manejar la oferta
      _handleOffer(peer, msg.sdp)
        .then(() => console.log('[RTC] ✅ Offer handled for', peer))
        .catch(e => console.warn('[RTC] ❌ answer error:', e));

    } else if(msg.type === 'webrtc-answer'){
      const pc = _rtcPeers[msg.from];
      console.log('[VIDEO] 📬 webrtc-answer from:', msg.from, 'has pc:', !!pc, 'state:', pc?.signalingState);
      if(pc){
        // Solo procesar answer si estamos en el estado correcto
        if(pc.signalingState === 'have-local-offer'){
          pc.setRemoteDescription({ type:'answer', sdp: msg.sdp })
            .then(() => {
              console.log('[RTC] ✅ Remote description set for', msg.from);
              // Procesar ICE candidates pendientes
              _processPendingIceCandidates(msg.from);
            })
            .catch(e => console.warn('[RTC] ❌ setRemoteDesc error:', e));
        } else {
          console.warn('[RTC] ⚠️ Ignoring answer from', msg.from, '— wrong state:', pc.signalingState);
        }
      } else {
        console.error('[RTC] ❌ No peer connection found for', msg.from);
      }

    } else if(msg.type === 'webrtc-ice'){
      const pc = _rtcPeers[msg.from];
      if(pc && msg.candidate){
        console.log('[VIDEO] 🧊 ICE candidate from:', msg.from);

        // Si la descripción remota no está lista, hacer queue del candidato
        if(!pc.remoteDescription || !pc.remoteDescription.type){
          console.log('[RTC] ⏳ Queueing ICE candidate for', msg.from, '(remote description not ready)');
          if(!_pendingIceCandidates[msg.from]) _pendingIceCandidates[msg.from] = [];
          _pendingIceCandidates[msg.from].push(msg.candidate);
        } else {
          // Descripción remota lista, añadir candidato inmediatamente
          pc.addIceCandidate(new RTCIceCandidate(msg.candidate))
            .then(() => console.log('[RTC] ✅ ICE candidate added for', msg.from))
            .catch(e => console.warn('[RTC] ❌ ICE candidate error:', e));
        }
      } else if(!pc) {
        console.warn('[RTC] ❌ No peer connection for ICE from', msg.from);
      }
    }
  };

  _videoWS.onclose = () => {
    console.log('[VIDEO] WS closed, current room:', _currentVideoRoom);
    if(_currentVideoRoom) setTimeout(() => _videoConnect(_currentVideoRoom), 2000);
  };
  _videoWS.onerror = (err) => {
    console.error('[VIDEO] WS error:', err);
    _videoWS?.close();
  };
}

/** Crear RTCPeerConnection para un peer */
async function _createPeerConnection(peer, isInitiator){
  _closePeer(peer);
  const pc = new RTCPeerConnection({ iceServers: _ICE_SERVERS });
  _rtcPeers[peer] = pc;

  // Añadir tracks locales — CRITICAL: verificar que el stream existe y tiene tracks
  if(_localStream && _localStream.getTracks().length > 0){
    console.log('[RTC] Adding local tracks to PC for', peer, '— tracks:', _localStream.getTracks().map(t => t.kind + ':' + t.enabled));
    _localStream.getTracks().forEach(t => {
      try {
        const sender = pc.addTrack(t, _localStream);
        console.log('[RTC] Track added:', t.kind, 'enabled:', t.enabled, 'readyState:', t.readyState);

        // Configurar bitrate para video de alta calidad
        if(t.kind === 'video' && sender){
          const params = sender.getParameters();
          if(!params.encodings || params.encodings.length === 0){
            params.encodings = [{}];
          }
          // Bitrate máximo de 2.5 Mbps para HD
          params.encodings[0].maxBitrate = 2500000;
          sender.setParameters(params).catch(e => console.warn('[RTC] Failed to set bitrate:', e));
        }
      } catch(e) {
        console.error('[RTC] Failed to add track:', e);
      }
    });
  } else {
    console.warn('[RTC] No local stream or tracks available when creating PC for', peer);
  }

  // Recibir tracks remotos → mostrar en tile
  pc.ontrack = e => {
    console.log('[RTC] ✅ ontrack from', peer, 'track:', e.track.kind, 'enabled:', e.track.enabled, 'readyState:', e.track.readyState);

    // Usar el stream del evento o crear uno nuevo
    let stream = _remoteStreams[peer];
    if(!stream){
      stream = e.streams[0] || new MediaStream();
      _remoteStreams[peer] = stream;
    }

    // Añadir el track al stream si no está ya
    if(!stream.getTracks().find(t => t.id === e.track.id)){
      stream.addTrack(e.track);
    }

    console.log('[RTC] Stream tracks:', stream.getTracks().map(t => t.kind + ':' + t.enabled));

    const vid = document.getElementById('vvid-' + peer);
    if(vid){
      // Solo actualizar srcObject si cambió
      if(vid.srcObject !== stream){
        vid.srcObject = stream;
        console.log('[RTC] Video element srcObject set for', peer);
      }

      // Intentar reproducir con muted primero para evitar errores de autoplay
      vid.muted = true;
      vid.play().then(() => {
        console.log('[RTC] ✅ Video playing for', peer, '(muted)');
        // Después de 100ms, intentar unmute
        setTimeout(() => {
          vid.muted = false;
          console.log('[RTC] Video unmuted for', peer);
        }, 100);
      }).catch(err => {
        console.warn('[VIDEO] play error for', peer, ':', err);
      });

      vid.style.display = 'block';
      const camoff = document.getElementById('vcamoff-' + peer);
      if(camoff) camoff.style.display = 'none';
      _refreshTileVis(peer, stream);
    } else {
      console.warn('[RTC] Video element not found for', peer);
    }
  };

  // Enviar candidatos ICE al peer via servidor
  pc.onicecandidate = e => {
    if(e.candidate && _videoWS?.readyState === WebSocket.OPEN){
      console.log('[RTC] Sending ICE candidate to', peer);
      _videoWS.send(JSON.stringify({ action:'ice', to:peer, candidate:e.candidate.toJSON() }));
    } else if(!e.candidate) {
      console.log('[RTC] ICE gathering complete for', peer);
    }
  };

  // Monitor connection state
  pc.onconnectionstatechange = () => {
    console.log('[RTC] Connection state with', peer, ':', pc.connectionState);
    if(pc.connectionState === 'connected'){
      console.log('[RTC] ✅ Connected to', peer);
    } else if(pc.connectionState === 'failed'){
      console.warn('[RTC] ❌ Connection failed with', peer, '— retrying');
      setTimeout(() => _createPeerConnection(peer, isInitiator).catch(()=>{}), 2000);
    }
  };

  // Monitor ICE connection state
  pc.oniceconnectionstatechange = () => {
    console.log('[RTC] ICE connection state with', peer, ':', pc.iceConnectionState);
  };

  if(isInitiator){
    try{
      const offer = await pc.createOffer({ offerToReceiveAudio:true, offerToReceiveVideo:true });
      await pc.setLocalDescription(offer);
      console.log('[RTC] ✅ Offer created for', peer, '— sending...');
      if(_videoWS?.readyState === WebSocket.OPEN){
        _videoWS.send(JSON.stringify({ action:'offer', to:peer, sdp:pc.localDescription.sdp }));
      } else {
        console.error('[RTC] Cannot send offer — WebSocket not open');
      }
    }catch(e){
      console.error('[RTC] ❌ Offer creation error:', e);
      throw e;
    }
  }
  return pc;
}

async function _handleOffer(peer, sdp){
  try{
    console.log('[RTC] Handling offer from', peer);
    const pc = await _createPeerConnection(peer, false);
    await pc.setRemoteDescription({ type:'offer', sdp });
    console.log('[RTC] Remote description set for', peer);

    // Procesar ICE candidates pendientes
    _processPendingIceCandidates(peer);

    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    console.log('[RTC] ✅ Answer created for', peer, '— sending...');
    if(_videoWS?.readyState === WebSocket.OPEN){
      _videoWS.send(JSON.stringify({ action:'answer', to:peer, sdp:pc.localDescription.sdp }));
    } else {
      console.error('[RTC] Cannot send answer — WebSocket not open');
    }
  }catch(e){
    console.error('[RTC] ❌ handleOffer error:', e);
    throw e;
  }
}

function _processPendingIceCandidates(peer){
  const pc = _rtcPeers[peer];
  const pending = _pendingIceCandidates[peer];

  if(!pc || !pending || pending.length === 0) return;

  console.log('[RTC] 📦 Processing', pending.length, 'pending ICE candidates for', peer);

  pending.forEach(candidate => {
    pc.addIceCandidate(new RTCIceCandidate(candidate))
      .then(() => console.log('[RTC] ✅ Queued ICE candidate added for', peer))
      .catch(e => console.warn('[RTC] ❌ Queued ICE candidate error:', e));
  });

  // Limpiar queue
  delete _pendingIceCandidates[peer];
}

function _closePeer(peer){
  const pc = _rtcPeers[peer];
  if(pc){ try{ pc.close(); }catch{} delete _rtcPeers[peer]; }
  delete _remoteStreams[peer];
  delete _pendingIceCandidates[peer]; // Limpiar queue de ICE candidates
}

function _videoDisconnect(){
  Object.keys(_rtcPeers).forEach(p => _closePeer(p));
  if(_videoWS){
    if(_videoWS.readyState === WebSocket.OPEN)
      _videoWS.send(JSON.stringify({ action:'leave', room:_currentVideoRoom }));
    _videoWS.onclose = null;
    _videoWS.close();
    _videoWS = null;
  }
}

// Diagnostic function for debugging video issues
window._videoDiagnostic = function(){
  console.log('═══════════════════════════════════════════════════════════');
  console.log('VIDEO DIAGNOSTIC REPORT');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('Current room:', _currentVideoRoom);
  console.log('Local stream:', _localStream);
  if(_localStream){
    console.log('  - Active:', _localStream.active);
    console.log('  - Tracks:', _localStream.getTracks().map(t => ({
      kind: t.kind,
      enabled: t.enabled,
      readyState: t.readyState,
      muted: t.muted,
      label: t.label
    })));
  }
  console.log('WebSocket state:', _videoWS?.readyState, '(1=OPEN)');
  console.log('Call members:', Array.from(_callMembers));
  console.log('Peer connections:', Object.keys(_rtcPeers));
  Object.entries(_rtcPeers).forEach(([peer, pc]) => {
    console.log(`  - ${peer}:`, {
      connectionState: pc.connectionState,
      iceConnectionState: pc.iceConnectionState,
      iceGatheringState: pc.iceGatheringState,
      signalingState: pc.signalingState,
      hasRemoteDescription: !!pc.remoteDescription,
      localTracks: pc.getSenders().map(s => s.track ? s.track.kind + ':' + s.track.enabled : 'null'),
      remoteTracks: pc.getReceivers().map(r => r.track ? r.track.kind + ':' + r.track.enabled : 'null')
    });
  });
  console.log('Remote streams:', Object.keys(_remoteStreams));
  Object.entries(_remoteStreams).forEach(([peer, stream]) => {
    console.log(`  - ${peer}:`, {
      active: stream.active,
      tracks: stream.getTracks().map(t => ({
        kind: t.kind,
        enabled: t.enabled,
        readyState: t.readyState,
        muted: t.muted
      }))
    });
  });
  console.log('Pending ICE candidates:', Object.keys(_pendingIceCandidates));
  Object.entries(_pendingIceCandidates).forEach(([peer, candidates]) => {
    console.log(`  - ${peer}: ${candidates.length} pending`);
  });
  console.log('═══════════════════════════════════════════════════════════');
  return 'Diagnostic complete — check console above';
};

// Stubs para compatibilidad con código que llama estas funciones
function _cleanVideoDecoder(peer){}
function _startVideoSend(){}
function _restartVideoSend(){}
const _videoDecoders = {};

/* ══════════════════════════════════════════════════════════════════════════
   socialInit / socialConnectWS
══════════════════════════════════════════════════════════════════════════ */

/* ── Rooms-dedicated WebSocket — siempre activo, independiente de mensajes ── */
let _roomsWS     = null;
let _roomsWsRetry = null;

function _roomsWsConnect(){
  if(_roomsWS && _roomsWS.readyState <= 1) return;
  clearTimeout(_roomsWsRetry);
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const tok   = localStorage.getItem('dvd_token') || '';
  if(!tok) return;

  _roomsWS = new WebSocket(`${proto}//${location.host}/ws/rooms?token=${encodeURIComponent(tok)}`);

  _roomsWS.onopen = () => {
    _roomsWS.send(JSON.stringify({action:'get-rooms'}));
    if(_roomsWS._pingIv) clearInterval(_roomsWS._pingIv);
    _roomsWS._pingIv = setInterval(()=>{
      if(_roomsWS && _roomsWS.readyState === WebSocket.OPEN)
        _roomsWS.send(JSON.stringify({action:'ping'}));
    }, 25000);
  };

  _roomsWS.onmessage = (evt) => {
    let msg; try{ msg = JSON.parse(evt.data); }catch{ return; }
    if(msg.type === 'rooms-update') _renderRoomsList(msg.rooms || []);
    if(msg.type === 'room-invite')  _handleRoomInvite(msg);
  };

  _roomsWS.onclose = () => {
    if(_roomsWS?._pingIv) clearInterval(_roomsWS._pingIv);
    _roomsWsRetry = setTimeout(_roomsWsConnect, 3000);
  };

  _roomsWS.onerror = () => { _roomsWS?.close(); };
}

/* ── SSE — Server-Sent Events para notificaciones en tiempo real de salas ── */
let _roomsSSE = null;
let _roomsSseRetry = null;

function _roomsSseConnect(){
  if(_roomsSSE && _roomsSSE.readyState !== EventSource.CLOSED) return;
  clearTimeout(_roomsSseRetry);
  const tok = localStorage.getItem('dvd_token') || '';
  if(!tok) return;

  try {
    _roomsSSE = new EventSource(`/api/rooms/stream?token=${encodeURIComponent(tok)}`);

    _roomsSSE.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if(msg.type === 'rooms-update') {
          _renderRoomsList(msg.rooms || []);
          // También actualizar el FAB del script v7
          try{ if(typeof window._rpRenderFromApp==='function') window._rpRenderFromApp(msg.rooms||[]); }catch(e){}
        }
      } catch(e) {}
    };

    _roomsSSE.onerror = () => {
      _roomsSSE.close();
      _roomsSSE = null;
      // Reconectar en 4s
      _roomsSseRetry = setTimeout(_roomsSseConnect, 4000);
    };

    _roomsSSE.onopen = () => {
      // SSE conectado — limpiar retry
      clearTimeout(_roomsSseRetry);
    };
  } catch(e) {
    // EventSource no disponible (muy raro) — usar solo polling
    _roomsSseRetry = setTimeout(_roomsSseConnect, 10000);
  }
}

async function socialInit(){
  const sel=document.getElementById('socialDMUser');
  if(sel){
    const users=acAllUsers.length?acAllUsers.map(u=>u.name):await req('GET','/api/users').catch(()=>[]);
    sel.innerHTML='<option value="">— Seleccionar usuario —</option>'+
      [].concat(users).filter(u=>(typeof u==='string'?u:u.name)!==me.username)
        .map(u=>{
          const n=typeof u==='string'?u:u.name;
          const dmRoom = 'dm:' + [me.username, n].sort().join(':');
          const unread = _unreadCounts[dmRoom] || 0;
          const badge = unread > 0 ? ` 🔴 ${unread}` : '';
          return`<option value="${esc(n)}">${esc(n)}${badge}</option>`;
        }).join('');
  }
  await socialConnectWS();
  if(me.is_superadmin) socialLoadAllRooms().catch(()=>{});
  _startRoomsPolling();
  // Refrescar salas al entrar a Social — igual que los juegos
  if(!_currentVideoRoom) checkRoomsStatus().catch(()=>{});
}

async function socialConnectWS(){
  if(_socialWS&&_socialWS.readyState<=1)return;
  const proto=location.protocol==='https:'?'wss:':'ws:';
  const tok=localStorage.getItem('dvd_token')||'';
  _socialWS=new WebSocket(`${proto}//${location.host}/ws/messages?token=${encodeURIComponent(tok)}`);
  _socialWS.onopen=()=>{
    _socialWS.send(JSON.stringify({action:'join',room:'group'}));
    _socialWS.send(JSON.stringify({action:'history',room:'group',limit:60}));
    // Refresh rooms list immediately on connect
    setTimeout(_refreshRoomsList, 200);
  };
  _socialWS.onmessage=async(evt)=>{
    let msg; try{msg=JSON.parse(evt.data);}catch{return;}
    if     (msg.type==='status')        _handleStatusMsg(msg);
    else if(msg.type==='message')       _handleChatMsg(msg);
    else if(msg.type==='history')       _handleHistoryMsg(msg);
    else if(msg.type==='deleted')       _handleDeletedMsg(msg);
    else if(msg.type==='rooms-update')  _renderRoomsList(msg.rooms||[]);
    else if(msg.type==='room-invite')   _handleRoomInvite(msg);
    else if(msg.type==='webrtc-room-joined') _handleRoomJoined(msg);
    else if(msg.type==='webrtc-offer')  await _handleOffer(msg);
    else if(msg.type==='webrtc-answer') await _handleAnswer(msg);
    else if(msg.type==='webrtc-ice')    await _handleIce(msg);
    else if(msg.type==='webrtc-joined') await _handleJoined(msg);
    else if(msg.type==='webrtc-left')   _handleLeft(msg);
    else if(msg.type==='call-chat')     _handleCallChat(msg);
    else if(msg.type==='call-mute')     _handleCallMute(msg);
  };
  _socialWS.onclose=()=>setTimeout(()=>{
    socialConnectWS(); // reconectar siempre, no solo en vista Social
  },3000);
}

/* ── Chat message helpers ─────────────────────────────────────────────── */
function _handleStatusMsg(msg){
  const on=msg.online||[];
  const c=document.getElementById('socialOnlineCount');if(c)c.textContent=on.length+' en línea';
  const l=document.getElementById('socialOnlineList');
  if(l)l.innerHTML=on.map(u=>`<span style="background:var(--glass);border:1px solid var(--border);border-radius:20px;padding:3px 10px;font-size:.68rem;color:var(--text2)"><span style="display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;margin-right:4px"></span>${esc(u)}</span>`).join('');
}
function _handleChatMsg(msg){
  const r=msg.message?.room||'';
  const onSocial=document.getElementById('view-social')?.classList.contains('on');
  if(r==='group'&&_socialRoom==='group'&&onSocial){
    appendSocialMsg(document.getElementById('socialGroupMessages'),msg.message,true);
  } else if(r===_dmRoom()&&_socialRoom==='dm'&&onSocial){
    appendSocialMsg(document.getElementById('socialDMMessages'),msg.message,true);
  } else {
    // Not currently viewing this chat — increment unread
    if(!_unreadCounts[r])_unreadCounts[r]=0;
    _unreadCounts[r]++;
    _updateUnreadBadge();
  }
}
function _handleHistoryMsg(msg){
  const r=msg.room||'',msgs=msg.messages||[];
  const el=document.getElementById(r==='group'?'socialGroupMessages':'socialDMMessages');
  if(el){el.innerHTML='';msgs.forEach(m=>appendSocialMsg(el,m,true));el.scrollTop=el.scrollHeight;}
}
function _handleDeletedMsg(msg){
  document.querySelectorAll(`[data-msg-id="${msg.msg_id}"]`).forEach(el=>{
    const b=el.querySelector('._mb');
    if(b)b.innerHTML='<em style="color:var(--text3);font-size:.73rem">Mensaje eliminado</em>';
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   ROOMS LIST
══════════════════════════════════════════════════════════════════════════ */
// Pedir lista de salas activas via API REST — usa el endpoint simple y directo
async function _refreshRoomsList(){
  try{
    const d = await req('GET', '/api/rooms/status');
    _renderRoomsList(d.rooms || []);
  }catch(_){
    // fallback al endpoint legacy
    try{
      const d2 = await req('GET', '/api/rooms/list');
      _renderRoomsList(d2.rooms || []);
    }catch(__){ }
  }
}

// Polling de salas cada 10s — mismo intervalo que los juegos
let _roomsPollingIv = null;
function _startRoomsPolling(){
  if(_roomsPollingIv) return;
  _roomsPollingIv = setInterval(()=>{
    if(!_currentVideoRoom) checkRoomsStatus().catch(()=>{});
  }, 10000);
}
function _stopRoomsPolling(){
  if(_roomsPollingIv){ clearInterval(_roomsPollingIv); _roomsPollingIv=null; }
}

/* ── Header rooms pill ─────────────────────────────────────────────────── */
let _hdrRoomsData = [];
let _hdrDdOpen    = false;

function _updateHdrRooms(rooms){
  _hdrRoomsData = rooms || [];
  const pill  = document.getElementById('hdrRooms');
  const label = document.getElementById('hdrRoomsLabel');
  const list  = document.getElementById('hdrRoomsList');
  const count = document.getElementById('hdrDdCount');
  if(!pill || !label || !list) return;

  // Salas visibles: públicas + privadas donde el usuario está invitado o ya está dentro
  const visible = _hdrRoomsData.filter(r =>
    r.mode === 'public' || r.invited || r.members?.includes(me?.username)
  );

  if(!visible.length){
    pill.style.display = 'none';
    closeHdrRoomsDropdown();
    return;
  }

  // ¿El usuario está en alguna sala?
  const myRoom = visible.find(r => r.members?.includes(me?.username));
  pill.style.display = 'flex';
  pill.classList.toggle('in-call', !!myRoom);

  // Label: si estoy en llamada, mostrar nombre de sala; si no, número de salas
  if(myRoom){
    label.textContent = '🔴 ' + (myRoom.title || 'En llamada');
  } else {
    label.textContent = visible.length + ' sala' + (visible.length === 1 ? '' : 's');
  }

  if(count) count.textContent = visible.length;

  // Separar: salas donde estoy invitado primero, luego públicas
  const invited = visible.filter(r => r.invited && !r.members?.includes(me?.username));
  const others  = visible.filter(r => !r.invited || r.members?.includes(me?.username));
  const sorted  = [...invited, ...others];

  list.innerHTML = sorted.map(r => {
    const inRoom  = r.members?.includes(me?.username);
    const isInv   = !!r.invited && !inRoom;
    const cnt     = r.members?.length || 0;
    const host    = r.host || '';

    // Dot color
    const dotBg  = inRoom ? '#4ade80' : cnt > 0 ? '#4ade80' : 'var(--text3)';
    const dotSh  = cnt > 0 ? `0 0 7px ${dotBg}` : 'none';

    // Badges
    const privBadge = r.mode === 'private'
      ? `<span style="font-size:.5rem;background:rgba(255,255,255,.07);color:var(--text3);border-radius:6px;padding:1px 5px;letter-spacing:.04em">🔒 Privada</span>`
      : '';
    const invBadge = isInv
      ? `<span style="font-size:.5rem;background:rgba(212,168,67,.12);color:var(--gold2);border:1px solid rgba(212,168,67,.25);border-radius:6px;padding:1px 6px">✉ Invitado</span>`
      : '';

    // Action
    let action;
    if(inRoom){
      action = `<span style="font-size:.6rem;color:#4ade80;font-weight:700;flex-shrink:0;letter-spacing:.02em">● En llamada</span>`;
    } else {
      action = `<button class="hdrRoomJoinBtn"
        onclick="event.stopPropagation();_hdrJoinRoom('${esc(r.key)}','${esc(r.title||r.key)}',this)">
        ▶ Unirse
      </button>`;
    }

    // Participantes text
    const peersText = cnt === 0
      ? '<span style="color:var(--text3)">Sala vacía</span>'
      : `<span style="color:#4ade80">${cnt} en directo</span>`;

    return `<div class="hdrRoomItem${isInv?' invited':''}${inRoom?' in-call':''}">
      <span class="hdrRoomLiveDot" style="background:${dotBg};box-shadow:${dotSh}"></span>
      <div style="flex:1;min-width:0;overflow:hidden">
        <div style="display:flex;align-items:center;gap:4px;flex-wrap:wrap;margin-bottom:3px">
          <span style="font-size:.76rem;color:var(--text);font-family:'Playfair Display',serif;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px">${esc(r.title||r.key)}</span>
          ${privBadge}${invBadge}
        </div>
        <div style="font-size:.58rem;display:flex;align-items:center;gap:6px">
          ${peersText}
          ${host ? `<span style="color:var(--text3)">· @${esc(host)}</span>` : ''}
        </div>
      </div>
      ${action}
    </div>`;
  }).join('');

  // Si el dropdown está abierto, reposicionar por si cambió el tamaño
  if(_hdrDdOpen) _positionHdrDropdown();
}

function _hdrJoinRoom(key, title, btn){
  if(btn){ btn.disabled = true; btn.textContent = '…'; }
  closeHdrRoomsDropdown();
  // Navegar a Social y unirse
  nav('social', document.getElementById('navSocial'));
  // Pequeño delay para que la vista cargue antes de entrar a la sala
  setTimeout(() => socialJoinRoom(key, title), 120);
}

function _positionHdrDropdown(){
  const pill = document.getElementById('hdrRooms');
  const dd   = document.getElementById('hdrRoomsDropdown');
  if(!pill || !dd) return;
  const rect = pill.getBoundingClientRect();
  const ddW  = 300;
  // Alinear a la derecha del pill, sin salirse de la pantalla
  let left = rect.right - ddW;
  if(left < 8) left = 8;
  dd.style.top  = (rect.bottom + 8) + 'px';
  dd.style.left = left + 'px';
  dd.style.right = 'auto';
  dd.style.width = Math.min(ddW, window.innerWidth - 16) + 'px';
}

function toggleHdrRoomsDropdown(e){
  e.stopPropagation();
  _hdrDdOpen ? closeHdrRoomsDropdown() : openHdrRoomsDropdown();
}

function openHdrRoomsDropdown(){
  const pill = document.getElementById('hdrRooms');
  const dd   = document.getElementById('hdrRoomsDropdown');
  if(!dd || !pill) return;
  _positionHdrDropdown();
  _hdrDdOpen = true;
  pill.classList.add('open');
  pill.setAttribute('aria-expanded','true');
  // display:block primero, luego clase .open en el siguiente frame para activar la transición
  dd.style.display = 'block';
  requestAnimationFrame(()=> requestAnimationFrame(()=>{ dd.classList.add('open'); }));
}

function closeHdrRoomsDropdown(){
  const pill = document.getElementById('hdrRooms');
  const dd   = document.getElementById('hdrRoomsDropdown');
  if(!dd) return;
  _hdrDdOpen = false;
  pill?.classList.remove('open');
  pill?.setAttribute('aria-expanded','false');
  dd.classList.remove('open');
  // Esperar a que termine la transición de salida (200ms) antes de ocultar
  setTimeout(()=>{ if(!_hdrDdOpen) dd.style.display = 'none'; }, 220);
}

// Cerrar al hacer click fuera o al hacer scroll
document.addEventListener('click', e => {
  if(!document.getElementById('hdrRooms')?.contains(e.target) &&
     !document.getElementById('hdrRoomsDropdown')?.contains(e.target)){
    closeHdrRoomsDropdown();
  }
});
document.addEventListener('scroll', ()=>{ if(_hdrDdOpen) _positionHdrDropdown(); }, true);
window.addEventListener('resize',   ()=>{ if(_hdrDdOpen) _positionHdrDropdown(); });
function _renderRoomsList(rooms){
  const el  = document.getElementById('socialRoomsList');
  const sub = document.getElementById('socialRoomSub');

  // Normalizar: asegurar que cada sala tiene members como array
  const safeRooms = (rooms||[]).map(r => ({
    ...r,
    members: Array.isArray(r.members) ? r.members : [],
    key:     r.key || '',
    title:   r.title || r.key || 'Sala',
    host:    r.host || '',
    mode:    r.mode || 'public',
    invited: !!r.invited,
    join_url: r.join_url || `/join/${r.key||''}`,
  }));

  // Actualizar siempre el pill del header
  try{ _updateHdrRooms(safeRooms); }catch(e){}

  // Actualizar enlace de salas en header
  try{
    const salasLink  = document.getElementById('hdrSalasLink');
    const salasCount = document.getElementById('hdrSalasCount');
    if(salasLink && salasCount){
      const myN = me?.username || '';
      const vis = safeRooms.filter(r => r.mode==='public' || r.invited || r.members.includes(myN));
      salasLink.style.display = vis.length > 0 ? 'flex' : 'none';
      if(vis.length > 0) salasCount.textContent = vis.length + ' sala' + (vis.length===1?'':'s');
    }
  }catch(e){}

  // Actualizar el FAB (script v7)
  try{ if(typeof window._rpRenderFromApp === 'function') window._rpRenderFromApp(safeRooms); }catch(e){}

  if(!el) return;

  // Asegurar que la lista sea visible cuando no estamos en llamada
  if(!_currentVideoRoom) el.style.display = 'flex';

  if(!safeRooms.length){
    el.innerHTML = '<div style="padding:10px 0;font-size:.72rem;color:var(--text3);text-align:center">Sin salas activas</div>';
    if(sub && !_currentVideoRoom) sub.textContent = 'Sin salas activas';
    return;
  }

  if(sub && !_currentVideoRoom)
    sub.textContent = safeRooms.length + ' sala' + (safeRooms.length===1?'':'s') + ' activa' + (safeRooms.length===1?'':'s');

  el.innerHTML = safeRooms.map(r => {
    const myN         = me?.username || '';
    const inRoom      = r.members.includes(myN);
    const isInvited   = r.invited;
    const memberCount = r.members.length;
    const memberNames = r.members.slice(0,3).map(u => '@'+esc(u)).join(', ') + (r.members.length>3?' +':'');
    const isPrivate   = r.mode === 'private';

    const borderColor = inRoom    ? 'var(--green)'
                      : isInvited ? 'var(--gold)'
                      : 'var(--border)';

    const inviteBadge = isInvited && !inRoom
      ? `<span style="font-size:.55rem;background:rgba(212,168,67,.15);color:var(--gold2);
           border:1px solid rgba(212,168,67,.3);border-radius:10px;padding:1px 7px;flex-shrink:0">
           ✉ Invitado</span>`
      : '';

    const joinUrl = r.join_url || `/join/${esc(r.key)}`;
    const action = inRoom
      ? `<span style="font-size:.62rem;color:var(--green);font-weight:700;flex-shrink:0">● En llamada</span>`
      : `<button class="btn btnG btnSm" style="flex-shrink:0"
           onclick="socialJoinRoom('${esc(r.key)}','${esc(r.title||r.key)}')">
           ▶ Unirse
         </button>`;

    const shareLink = `<a href="${joinUrl}" target="_blank"
      style="font-size:.52rem;color:var(--text3);text-decoration:none;display:block;margin-top:3px;
        overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
      title="Enlace directo para unirse">🔗 ${location.origin}${joinUrl}</a>`;

    return `<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
        background:var(--glass);border:1px solid ${borderColor};
        border-radius:var(--r);transition:all .2s;
        ${isInvited&&!inRoom?'box-shadow:0 0 12px rgba(212,168,67,.12)':''}">
      <span style="width:10px;height:10px;border-radius:50%;flex-shrink:0;
        background:${memberCount?'var(--green)':'var(--text3)'};
        box-shadow:${memberCount?'0 0 8px var(--green)':'none'};
        transition:all .3s"></span>
      <div style="flex:1;min-width:0">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
          <span style="font-size:.8rem;color:var(--text);font-family:'Playfair Display',serif;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc(r.title||r.key)}</span>
          ${isPrivate?`<span style="font-size:.55rem;color:var(--text3)">🔒</span>`:''}
          ${inviteBadge}
        </div>
        <div style="font-size:.6rem;color:var(--text3);margin-top:2px">
          ${memberNames||'Sala vacía'} · ${memberCount} participante${memberCount===1?'':'s'}
        </div>
        ${!inRoom ? shareLink : ''}
      </div>
      ${action}
    </div>`;
  }).join('');
}

function _handleRoomInvite(msg){
  const title=msg.title||('Sala de '+(msg.host||'?'));
  const key=msg.room_key;
  if(!key)return;

  // Refrescar lista de salas para que aparezca la sala a la que se invita
  _refreshRoomsList();

  const banner=document.createElement('div');
  banner.style.cssText='position:fixed;top:56px;left:50%;transform:translateX(-50%);'+
    'background:var(--n3);border:1px solid var(--border2);border-radius:var(--r);'+
    'padding:10px 16px;z-index:9999;display:flex;align-items:center;gap:10px;'+
    'font-size:.78rem;box-shadow:0 4px 24px rgba(0,0,0,.6);max-width:340px';
  banner.innerHTML=`<span>📹 <strong>${esc(msg.host)}</strong> te invita a <em>${esc(title)}</em></span>
    <button class="btn btnG btnSm" onclick="socialJoinRoom('${esc(key)}','${esc(title)}');this.closest('div[style*=fixed]').remove()">Unirse</button>
    <button class="btn btnS btnSm" onclick="this.closest('div[style*=fixed]').remove()">✕</button>`;
  document.body.appendChild(banner);
  setTimeout(()=>banner.remove(),15000);
}

/* ══════════════════════════════════════════════════════════════════════════
   ROOM JOIN / LEAVE
══════════════════════════════════════════════════════════════════════════ */
async function socialStartRoom(){
  // Delegado al modal
  showCreateRoomModal();
}

/* ══════════════════════════════════════════════════════════════════════════
   MODAL: Crear sala
══════════════════════════════════════════════════════════════════════════ */
let _crSelectedInvites = new Set();

async function showCreateRoomModal(){
  _crSelectedInvites = new Set();
  const modal = document.getElementById('modalCreateRoom');
  if(!modal) return;
  modal.style.display = 'flex';
  // Reset form
  const titleEl = document.getElementById('crRoomTitle');
  if(titleEl) titleEl.value = '';
  document.querySelectorAll('input[name="crMode"]').forEach(r=>{ r.checked = r.value==='public'; });
  document.getElementById('crInviteSection').style.display = 'none';
  document.getElementById('crUserList').innerHTML =
    '<div style="font-size:.68rem;color:var(--text3,#666);text-align:center;padding:8px">Cargando usuarios…</div>';
  // Pre-load users
  try{
    const users = await req('GET','/api/users');
    _renderCrUserList(Array.isArray(users)?users:(users.users||[]));
  }catch(e){
    document.getElementById('crUserList').innerHTML =
      '<div style="font-size:.68rem;color:var(--text3,#666);text-align:center;padding:8px">Error al cargar usuarios</div>';
  }
}

function closeCreateRoomModal(){
  const modal = document.getElementById('modalCreateRoom');
  if(modal) modal.style.display = 'none';
}

function crTogglePrivate(val){
  document.getElementById('crInviteSection').style.display = val==='private' ? '' : 'none';
}

function _renderCrUserList(users){
  const el = document.getElementById('crUserList');
  if(!el) return;
  const others = users.filter(u=>(typeof u==='string'?u:u.name||u.username) !== me?.username);
  if(!others.length){
    el.innerHTML = '<div style="font-size:.68rem;color:var(--text3,#666);text-align:center;padding:8px">No hay otros usuarios</div>';
    return;
  }
  el.innerHTML = others.map(u=>{
    const name = typeof u==='string'?u:(u.name||u.username);
    return `<label style="display:flex;align-items:center;gap:8px;padding:5px 4px;cursor:pointer;
      border-radius:6px;font-size:.78rem;color:var(--text,#eee);transition:background .15s"
      onmouseover="this.style.background='rgba(255,255,255,.05)'" onmouseout="this.style.background=''">
      <input type="checkbox" value="${esc(name)}" onchange="crToggleInvite(this)"
        style="accent-color:var(--gold,#d4a843)">
      <span>@${esc(name)}</span>
    </label>`;
  }).join('');
}

function crToggleInvite(cb){
  if(cb.checked) _crSelectedInvites.add(cb.value);
  else _crSelectedInvites.delete(cb.value);
}

async function confirmCreateRoom(){
  const titleEl = document.getElementById('crRoomTitle');
  const title = (titleEl?.value||'').trim() || ('Sala de '+(me?.username||''));
  const modeEl = document.querySelector('input[name="crMode"]:checked');
  const mode = modeEl?.value || 'public';
  const invites = mode==='private' ? [..._crSelectedInvites] : [];
  closeCreateRoomModal();
  const key = Math.random().toString(36).slice(2,14);
  invites.forEach(u=>_callInvited.add(u));

  // PASO 1: Crear la sala en DB PRIMERO (antes de cualquier media)
  // Esto garantiza que la sala existe aunque falle la cámara
  let roomData = null;
  try{
    roomData = await req('POST', '/api/rooms/create', {room:key, title, mode, invites});
  }catch(e){
    console.error('Error creando sala:', e);
    // Intentar igualmente entrar — la sala puede estar en memoria
  }

  // PASO 2: Entrar a la sala localmente (inicia cámara/mic)
  try{
    await _enterRoom(key, title, true);
  }catch(e){
    console.error('Error entrando a sala:', e);
  }

  // PASO 3: Notificar via WS a peers ya conectados
  if(_socialWS?.readyState===WebSocket.OPEN){
    _socialWS.send(JSON.stringify({action:'webrtc-join', room:key, title, mode, invites}));
  }

  // PASO 4: Actualizar UI con la sala recién creada
  if(roomData){
    _handleRoomJoined({
      room:key, title:roomData.title, host:roomData.host,
      mode:roomData.mode, members:roomData.members||[me?.username], you:me?.username
    });
  }

  // PASO 5: Refrescar lista — la sala ya está en DB
  checkRoomsStatus().catch(()=>{});
}

/* ══════════════════════════════════════════════════════════════════════════
   MODAL: Invitar a sala activa
══════════════════════════════════════════════════════════════════════════ */
async function showInviteModal(){
  if(!_currentVideoRoom) return;
  const modal = document.getElementById('modalInviteRoom');
  if(!modal) return;
  modal.style.display = 'flex';
  const el = document.getElementById('inviteUserList');
  el.innerHTML = '<div style="font-size:.68rem;color:var(--text3,#666);text-align:center;padding:8px">Cargando…</div>';
  try{
    const users = await req('GET','/api/users');
    const all = Array.isArray(users)?users:(users.users||[]);
    const others = all.filter(u=>(typeof u==='string'?u:u.name||u.username) !== me?.username);
    if(!others.length){ el.innerHTML='<div style="font-size:.68rem;color:var(--text3);text-align:center;padding:8px">No hay otros usuarios</div>'; return; }
    el.innerHTML = others.map(u=>{
      const name = typeof u==='string'?u:(u.name||u.username);
      return `<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 4px;
        border-bottom:1px solid rgba(255,255,255,.04);font-size:.78rem;color:var(--text,#eee)">
        <span>@${esc(name)}</span>
        <button class="btn btnG btnSm" style="font-size:.62rem;padding:3px 10px"
          onclick="sendRoomInvite('${esc(name)}',this)">Invitar</button>
      </div>`;
    }).join('');
  }catch(e){
    el.innerHTML='<div style="font-size:.68rem;color:var(--text3);text-align:center;padding:8px">Error al cargar</div>';
  }
}

function closeInviteModal(){
  const modal = document.getElementById('modalInviteRoom');
  if(modal) modal.style.display = 'none';
}

async function sendRoomInvite(username, btn){
  if(!_currentVideoRoom) return;
  try{
    await req('POST','/api/rooms/invite',{room:_currentVideoRoom, username});
    if(btn){ btn.textContent='✓ Enviado'; btn.disabled=true; }
    _callInvited.add(username);
    _updateParticipants();
  }catch(e){
    if(btn) btn.textContent='Error';
  }
}

async function socialJoinRoom(key, title){
  await _enterRoom(key, title, false);
  if(_socialWS?.readyState===WebSocket.OPEN){
    _socialWS.send(JSON.stringify({action:'webrtc-join',room:key,title:title||key,mode:'join',invites:[]}));
  } else {
    // Fallback REST
    try{
      const d = await req('POST', '/api/rooms/join', {room:key, title:title||key});
      _handleRoomJoined({room:key, title:d.title, host:d.host, mode:d.mode, members:d.members, you:me?.username});
    }catch(e){ console.warn('REST room join failed:', e); }
  }
  _refreshRoomsList();
}

async function _enterRoom(key, title, isHost){
  try{
  if(_currentVideoRoom) await socialLeaveRoom();
  _currentVideoRoom = key;
  _callInvited = new Set();
  _callMembers = new Set();

  document.getElementById('socialVideoGrid').style.display='';
  document.getElementById('btnStartRoom').style.display='none';
  document.getElementById('btnLeaveRoom').style.display='';
  document.getElementById('socialRoomsList').style.display='none';
  const btnInvite=document.getElementById('btnInviteRoom');
  if(btnInvite) btnInvite.style.display=isHost?'':'none';
  const lbl=document.getElementById('socialCallLabel');
  if(lbl) lbl.textContent='🔴 '+esc(title||key);
  const cc=document.getElementById('callChatMessages');
  if(cc) cc.innerHTML='';

  // 1. Obtener media local — SOLICITAR PERMISOS AQUÍ (cuando el usuario inicia/se une a videollamada)
  console.log('[VIDEO] Requesting camera and microphone permissions...');
  try{
    // Solicitar permisos de audio y video cuando el usuario se une a la sala
    console.log('[VIDEO] Using standard getUserMedia to request permissions');
    _localStream = await navigator.mediaDevices.getUserMedia({
      video:{ facingMode:'user', width:{ideal:1280}, height:{ideal:720} },
      audio:{ echoCancellation:true, noiseSuppression:true, autoGainControl:true }
    });
    console.log('[VIDEO] ✅ Local stream obtained — tracks:', _localStream.getTracks().map(t => t.kind + ':' + t.enabled));
  }catch(e1){
    console.warn('[VIDEO] Video+audio failed, trying audio only:', e1);
    try{
      _localStream = await navigator.mediaDevices.getUserMedia({audio:true});
      console.log('[VIDEO] ✅ Audio-only stream obtained');
    }
    catch(e2){
      console.error('[VIDEO] ❌ All media failed, using empty stream:', e2);
      alert('⚠️ No se pudo acceder a la cámara o micrófono. Verifica los permisos del navegador.');
      _localStream = new MediaStream();
    }
  }

  // 2. Mostrar tile local
  _addTile('__local__', _localStream, (me?.username||'yo')+' (tú)', true);
  setTimeout(()=>_refreshTileVis('__local__', _localStream), 300);
  _updateParticipants();
  _updatePeerCount();

  // 3. CRITICAL: Wait a bit to ensure stream is fully ready before connecting
  await new Promise(resolve => setTimeout(resolve, 200));
  console.log('[VIDEO] Stream ready, connecting to room:', key);

  // 4. Conectar al relay de video
  _videoConnect(key);

  // 5. Actualizar pill del header
  _updateHdrRooms(_hdrRoomsData);
  }catch(err){
    console.error('[_enterRoom] error:', err);
  }
}

async function socialLeaveRoom(){
  if(!_currentVideoRoom)return;
  // Desconectar relay de video
  _videoDisconnect();
  const roomKey = _currentVideoRoom;
  if(_socialWS?.readyState===WebSocket.OPEN){
    _socialWS.send(JSON.stringify({action:'webrtc-leave',room:roomKey}));
  } else {
    // Fallback REST
    req('POST', '/api/rooms/leave', {room:roomKey}).catch(()=>{});
  }

  // Si el stream es el de permisos, solo deshabilitar tracks (no parar)
  // Si es un stream nuevo, pararlo completamente
  if(_localStream && _localStream !== _permStream){
    _localStream.getTracks().forEach(t=>t.stop());
  } else if(_localStream === _permStream){
    _localStream.getTracks().forEach(t=>{ t.enabled = false; });
  }
  _localStream=null;
  _currentVideoRoom='';
  _callInvited=new Set(); _callMembers=new Set();

  document.getElementById('socialVideoGrid').style.display='none';
  document.getElementById('socialVideoTiles').innerHTML='';
  document.getElementById('btnStartRoom').style.display='';
  document.getElementById('btnLeaveRoom').style.display='none';
  document.getElementById('socialRoomsList').style.display='';
  const btnInvite=document.getElementById('btnInviteRoom');
  if(btnInvite) btnInvite.style.display='none';
  ['callChatMessages','callChatMessagesMobile'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.innerHTML='';
  });
  ['callParticipantsList','callParticipantsListMobile'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.innerHTML='';
  });
  const sub=document.getElementById('socialRoomSub');
  if(sub) sub.textContent='Sin salas activas';
  // Refrescar lista al salir
  checkRoomsStatus().catch(()=>{});
  // Reset call chat state
  _callChatHistoryOpen = true;
  _callChatUnreadCount = 0;
}

/* ══════════════════════════════════════════════════════════════════════════
   SIGNALING — el relay de video usa /ws/video, no WebRTC P2P.
   Estos handlers mantienen compatibilidad con el WS de mensajes.
══════════════════════════════════════════════════════════════════════════ */
function _handleJoined(msg){
  // El relay de video gestiona la entrada de peers via peer-joined
  _callMembers.add(msg.from); _updateParticipants(); _updatePeerCount();
}
// Stubs eliminados - las funciones reales están definidas arriba
function _handleLeft(msg){
  const p=msg.from;
  _callMembers.delete(p); _removeTile(p); _cleanVideoDecoder(p);
  _updateParticipants(); _updatePeerCount();
}
function _handleRoomJoined(msg){
  const lbl=document.getElementById('socialCallLabel');
  if(lbl) lbl.textContent='🔴 '+esc(msg.title||msg.room||'');
  const btnInvite=document.getElementById('btnInviteRoom');
  if(btnInvite) btnInvite.style.display=(msg.host===me?.username)?'':'none';
  if(msg.members) msg.members.forEach(u=>{ if(u!==me?.username) _callMembers.add(u); });
  _updateParticipants(); _updatePeerCount();
}
function _addTracksToPC(){}
function _setIceStatus(){}

/* ══════════════════════════════════════════════════════════════════════════
   VIDEO TILE MANAGEMENT
══════════════════════════════════════════════════════════════════════════ */
function _addTile(id, stream, label, muted){
  const grid=document.getElementById('socialVideoTiles');
  if(!grid)return;
  let tile=document.getElementById('vtile-'+id);
  if(!tile){
    tile=document.createElement('div');
    tile.id='vtile-'+id;
    tile.style.cssText='position:relative;background:#08080F;border-radius:8px;overflow:hidden;aspect-ratio:16/9;min-height:110px;cursor:pointer';
    const initial=esc((label||'?')[0].toUpperCase());
    tile.innerHTML=`
      <video id="vvid-${esc(id)}" autoplay playsinline ${muted?'muted':''}
        style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:none"
        preload="auto"></video>
      <div id="vcamoff-${esc(id)}" style="position:absolute;inset:0;display:flex;flex-direction:column;
        align-items:center;justify-content:center;gap:6px;background:#0c0c1a">
        <div style="width:44px;height:44px;border-radius:50%;background:var(--glass);
          border:1px solid var(--border2);font-size:1.1rem;font-family:'Playfair Display',serif;
          color:var(--gold2);display:flex;align-items:center;justify-content:center">${initial}</div>
        <div style="font-size:.58rem;color:var(--text3)">Sin cámara</div>
      </div>
      <div style="position:absolute;bottom:5px;left:0;right:0;text-align:center;pointer-events:none">
        <span style="background:rgba(0,0,0,.7);padding:2px 8px;border-radius:20px;font-size:.6rem">${esc(label)}</span>
      </div>
      <button class="vf-expand-btn" onclick="event.stopPropagation();_expandTile('${esc(id)}','${esc(label)}')" title="Pantalla completa">⛶</button>`;
    tile.ondblclick = () => _expandTile(id, label);
    grid.appendChild(tile);
    _updateGrid();
  }
  // Solo asignar srcObject para el tile local (stream directo)
  // Los tiles remotos usan MediaSource via _initVideoDecoder
  if(stream && id === '__local__'){
    const vid=document.getElementById('vvid-'+id);
    if(vid){
      vid.srcObject = stream;
      vid.play().catch(()=>{});
      vid.onloadedmetadata = () => _refreshTileVis(id, stream);
    }
    _refreshTileVis(id, stream);
  }
}

function _refreshTileVis(id, stream){
  const s = stream || (id==='__local__' ? _localStream : _remoteStreams[id]);
  const vid=document.getElementById('vvid-'+id);
  const camoff=document.getElementById('vcamoff-'+id);
  if(!vid||!camoff||!s)return;
  const hasVideo=s.getVideoTracks().some(t=>t.enabled&&t.readyState==='live');
  vid.style.display=hasVideo?'block':'none';
  camoff.style.display=hasVideo?'none':'flex';
  // Forzar repaint para evitar flickering
  if(hasVideo) vid.offsetHeight;
}

/** Muestra el video inmediatamente si hay tracks de vídeo, sin esperar readyState */
function _showTileVideo(id, stream){
  const s = stream || (id==='__local__' ? _localStream : _remoteStreams[id]);
  const vid=document.getElementById('vvid-'+id);
  const camoff=document.getElementById('vcamoff-'+id);
  if(!vid||!camoff||!s)return;
  // Show video if there are any video tracks (enabled or not — they may not be live yet)
  const hasVideoTracks = s.getVideoTracks().length > 0;
  vid.style.display = hasVideoTracks ? 'block' : 'none';
  camoff.style.display = hasVideoTracks ? 'none' : 'flex';
}

function _removeTile(id){
  document.getElementById('vtile-'+id)?.remove();
  _updateGrid();
}

function _updateGrid(){
  const g=document.getElementById('socialVideoTiles');
  if(!g)return;
  const n=g.children.length;
  if(n===0)return;
  if(n===1)     { g.style.gridTemplateColumns='1fr';           g.style.gridTemplateRows='1fr'; }
  else if(n===2){ g.style.gridTemplateColumns='1fr 1fr';       g.style.gridTemplateRows='1fr'; }
  else if(n<=4) { g.style.gridTemplateColumns='1fr 1fr';       g.style.gridTemplateRows='1fr 1fr'; }
  else          { g.style.gridTemplateColumns='repeat(3,1fr)'; g.style.gridTemplateRows=''; }
  // Height: taller for fewer participants
  const isMobile = window.innerWidth <= 480;
  const tileH = isMobile ? (n<=2?200:140) : (n<=2?260:160);
  g.style.minHeight=(tileH*Math.ceil(n/2))+'px';
}

function _updatePeerCount(){
  const n=Object.keys(_rtcPeers).length+1;
  const el=document.getElementById('socialCallPeers');
  if(el)el.textContent=n+' participante'+(n===1?'':'s');
}

function _updateParticipants(){
  const myName=me?.username||'yo';
  const all=new Map();
  all.set(myName,{status:'connected',isMe:true});
  _callInvited.forEach(u=>{ if(!all.has(u)) all.set(u,{status:'invited',isMe:false}); });
  _callMembers.forEach(u=>{ if(u!==myName) all.set(u,{status:'connected',isMe:false}); });

  const rows=[...all.entries()].map(([u,info])=>{
    const dot=info.status==='connected'
      ?'<span style="width:7px;height:7px;border-radius:50%;background:var(--green);flex-shrink:0;box-shadow:0 0 5px var(--green)"></span>'
      :'<span style="width:7px;height:7px;border-radius:50%;background:var(--text3);flex-shrink:0"></span>';
    const lbl=info.isMe?`<b>${esc(u)}</b> <span style="color:var(--text3)">(tú)</span>`:esc(u);
    const sub=info.status==='invited'?'<div style="font-size:.55rem;color:var(--text3)">Invitado…</div>':'';
    return`<div style="display:flex;align-items:center;gap:6px;padding:3px 0">${dot}<div style="font-size:.7rem;color:var(--text)">${lbl}${sub}</div></div>`;
  }).join('');

  const el=document.getElementById('callParticipantsList');
  if(el)el.innerHTML=rows;

  // Mobile: compact chips
  const mob=document.getElementById('callParticipantsListMobile');
  if(mob){
    mob.innerHTML=[...all.entries()].map(([u,info])=>{
      const color=info.status==='connected'?'var(--green)':'var(--text3)';
      return`<span style="background:var(--glass);border:1px solid var(--border);border-radius:20px;padding:2px 8px;font-size:.62rem;color:var(--text);display:inline-flex;align-items:center;gap:4px"><span style="width:6px;height:6px;border-radius:50%;background:${color}"></span>${esc(u)}${info.isMe?' (tú)':''}</span>`;
    }).join('');
  }
}

function _setIceStatus(){
  const el=document.getElementById('socialIceStatus');
  if(!el)return;
  const statuses=Object.entries(_rtcPeers)
    .map(([p,pc])=>p+':'+pc.iceConnectionState)
    .filter(s=>!s.includes('connected')&&!s.includes('completed'));
  el.textContent=statuses.join(' · ');
  el.style.display=statuses.length?'':'none';
}

/* ══════════════════════════════════════════════════════════════════════════
   FULLSCREEN VIDEO — ampliar tile o toda la sala
══════════════════════════════════════════════════════════════════════════ */
/*
   Enfoque híbrido:
   1. Intenta requestFullscreen() nativo del navegador sobre el contenedor de video.
   2. Si no está disponible, usa overlay CSS fixed como fallback.
   ESC o botón ✕ para salir. Doble-click o ⛶ en cada tile para expandir uno.
*/
let _vfsActive     = false;
let _vfsSingleTile = null;
let _vfsFallback   = false; // true si usamos overlay CSS en lugar de API nativa
let _vfsSavedGridStyle = ''; // estilo original del grid antes de fullscreen

function _expandTile(id, label){
  if(_vfsActive){ _closeFullscreen(); }
  _vfsSingleTile = id;
  // Ocultar todos los tiles excepto el seleccionado
  const grid = document.getElementById('socialVideoTiles');
  if(!grid) return;
  [...grid.children].forEach(t => {
    if(t.id !== 'vtile-' + id){ t.dataset.vfsHidden='1'; t.style.display='none'; }
  });
  _openVfsOverlay();
}

function _expandAllTiles(){
  if(_vfsActive && !_vfsSingleTile){ _closeFullscreen(); return; }
  if(_vfsActive){ _closeFullscreen(); }
  _vfsSingleTile = null;
  const grid = document.getElementById('socialVideoTiles');
  if(!grid || !grid.children.length) return;
  [...grid.children].forEach(t => { t.style.display=''; delete t.dataset.vfsHidden; });
  _openVfsOverlay();
}

function _openVfsOverlay(){
  const grid = document.getElementById('socialVideoTiles');
  if(!grid) return;
  _vfsActive = true;
  _vfsSavedGridStyle = grid.getAttribute('style') || '';

  // Intentar fullscreen nativo primero sobre el contenedor de video
  const container = document.getElementById('socialVideoGrid');
  if(container && container.requestFullscreen){
    _vfsFallback = false;
    container.requestFullscreen().then(()=>{
      // En fullscreen nativo: expandir el grid de tiles para llenar la pantalla
      _applyFullscreenGridStyle(grid);
      _addVfsControls(true);
    }).catch(()=>{
      _vfsFallback = true;
      _applyFallbackFullscreen(grid);
    });
    // Escuchar salida de fullscreen nativo (botón ESC del navegador)
    const onFsChange = () => {
      if(!document.fullscreenElement && _vfsActive){ _closeFullscreen(); }
      document.removeEventListener('fullscreenchange', onFsChange);
    };
    document.addEventListener('fullscreenchange', onFsChange);
  } else {
    _vfsFallback = true;
    _applyFallbackFullscreen(grid);
  }
}

function _applyFullscreenGridStyle(grid){
  const visible = [...grid.children].filter(t => t.dataset.vfsHidden !== '1');
  const n = visible.length;
  let cols, rows;
  if     (n <= 1) { cols='1fr';           rows='1fr'; }
  else if(n === 2) { cols='1fr 1fr';       rows='1fr'; }
  else if(n <= 4)  { cols='1fr 1fr';       rows='1fr 1fr'; }
  else             { cols='repeat(3,1fr)'; rows=''; }
  // Ocultar sidebar y otros elementos del layout para que el grid llene la pantalla
  const sidebar = document.getElementById('callSidebar');
  if(sidebar){ sidebar.dataset.vfsHidden='sidebar'; sidebar.style.display='none'; }
  const mobileBottom = document.getElementById('callMobileBottom');
  if(mobileBottom){ mobileBottom.dataset.vfsHidden='mobile'; mobileBottom.style.display='none'; }
  // El grid ocupa todo el espacio del contenedor fullscreen
  grid.style.cssText =
    'display:grid;gap:2px;width:100%;height:100vh;background:#000;border-radius:0;min-height:0;flex:1;' +
    'grid-template-columns:'+cols+';' +
    (rows ? 'grid-template-rows:'+rows+';' : '');
  visible.forEach(t => { t.style.aspectRatio='unset'; t.style.minHeight='0'; t.style.height='100%'; });
}

function _applyFallbackFullscreen(grid){
  const visible = [...grid.children].filter(t => t.dataset.vfsHidden !== '1');
  const n = visible.length;
  let cols, rows;
  if     (n <= 1) { cols='1fr';           rows='1fr'; }
  else if(n === 2) { cols='1fr 1fr';       rows='1fr'; }
  else if(n <= 4)  { cols='1fr 1fr';       rows='1fr 1fr'; }
  else             { cols='repeat(3,1fr)'; rows=''; }
  grid.style.cssText =
    'position:fixed;inset:0;z-index:9999;background:#000;border-radius:0;' +
    'display:grid;gap:2px;' +
    'grid-template-columns:'+cols+';' +
    (rows ? 'grid-template-rows:'+rows+';' : '') +
    'min-height:0;';
  visible.forEach(t => { t.style.aspectRatio='unset'; t.style.minHeight='0'; });
  _addVfsControls(false);
}

function _addVfsControls(isNative){
  const ctrl = document.createElement('div');
  ctrl.id = '_vfControls';
  ctrl.style.cssText =
    'position:fixed;bottom:0;left:0;right:0;z-index:10000;' +
    'display:flex;align-items:center;justify-content:center;gap:10px;' +
    'padding:10px 16px calc(10px + env(safe-area-inset-bottom));' +
    'background:linear-gradient(transparent,rgba(0,0,0,.82));pointer-events:auto;';

  const bs =
    'background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);color:#fff;' +
    'border-radius:50%;width:46px;height:46px;font-size:1.15rem;cursor:pointer;' +
    'display:flex;align-items:center;justify-content:center;transition:background .18s;';
  const bsClose =
    'background:rgba(200,48,96,.55);border:1px solid rgba(200,48,96,.7);color:#fff;' +
    'border-radius:50%;width:46px;height:46px;font-size:1.15rem;cursor:pointer;' +
    'display:flex;align-items:center;justify-content:center;transition:background .18s;';

  ctrl.innerHTML =
    '<button id="_vfBtnMic" onclick="socialToggleMic()" style="'+bs+'" title="Micrófono">'+(_micEnabled?'🎤':'🔇')+'</button>' +
    '<button id="_vfBtnCam" onclick="socialToggleCam()" style="'+bs+'" title="Cámara">'+(_camEnabled?'📷':'🚫')+'</button>' +
    (_vfsSingleTile
      ? '<button onclick="_closeFullscreen();setTimeout(_expandAllTiles,50);" style="'+bs+'" title="Ver toda la sala">⊞</button>'
      : '') +
    '<button onclick="_closeFullscreen()" style="'+bsClose+'" title="Salir (Esc)">✕</button>';

  const kh = e => { if(e.key==='Escape') _closeFullscreen(); };
  ctrl._keyHandler = kh;
  document.addEventListener('keydown', kh);
  document.body.appendChild(ctrl);
}

function _closeFullscreen(){
  if(!_vfsActive) return;
  _vfsActive = false;

  const ctrl = document.getElementById('_vfControls');
  if(ctrl){ document.removeEventListener('keydown', ctrl._keyHandler); ctrl.remove(); }

  // Salir de fullscreen nativo si está activo
  if(!_vfsFallback && document.fullscreenElement){
    document.exitFullscreen().catch(()=>{});
  }

  const grid = document.getElementById('socialVideoTiles');
  if(grid){
    // Restaurar estilo original del grid
    if(_vfsSavedGridStyle){
      grid.setAttribute('style', _vfsSavedGridStyle);
    }
    // Restaurar tiles ocultos y sus estilos
    [...grid.children].forEach(t => {
      if(t.dataset.vfsHidden==='1'){ t.style.display=''; delete t.dataset.vfsHidden; }
      t.style.aspectRatio = '16/9';
      t.style.minHeight   = '110px';
      t.style.height      = '';
    });
    _updateGrid();
  }
  // Restaurar sidebar y elementos ocultos durante fullscreen nativo
  const sidebar = document.getElementById('callSidebar');
  if(sidebar && sidebar.dataset.vfsHidden==='sidebar'){ sidebar.style.display=''; delete sidebar.dataset.vfsHidden; }
  const mobileBottom = document.getElementById('callMobileBottom');
  if(mobileBottom && mobileBottom.dataset.vfsHidden==='mobile'){ mobileBottom.style.display=''; delete mobileBottom.dataset.vfsHidden; }
  _vfsSingleTile    = null;
  _vfsFallback      = false;
  _vfsSavedGridStyle = '';
}

function _renderVfMessages(){ /* no-op */ }
function _syncVfControls(){
  const bm=document.getElementById('_vfBtnMic'); if(bm) bm.textContent=_micEnabled?'🎤':'🔇';
  const bc=document.getElementById('_vfBtnCam'); if(bc) bc.textContent=_camEnabled?'📷':'🚫';
}

/* ══════════════════════════════════════════════════════════════════════════
   IN-CALL CHAT (ephemeral — only while call is active)
══════════════════════════════════════════════════════════════════════════ */
function callSendChat(){
  const inp=document.getElementById('callChatInput');
  const text=(inp?.value||'').trim();
  if(!text||!_currentVideoRoom||!_socialWS)return;
  inp.value='';
  _socialWS.send(JSON.stringify({action:'call-chat',room:_currentVideoRoom,text}));
  _appendCallChat(me?.username||'yo',text,true);
}

function callSendChatMobile(){
  const inp=document.getElementById('callChatInputMobile');
  const text=(inp?.value||'').trim();
  if(!text||!_currentVideoRoom||!_socialWS)return;
  inp.value='';
  _socialWS.send(JSON.stringify({action:'call-chat',room:_currentVideoRoom,text}));
  _appendCallChat(me?.username||'yo',text,true);
}

function _handleCallChat(msg){
  if(msg.room!==_currentVideoRoom)return;
  _appendCallChat(msg.from,msg.text,false);
}

function _handleCallMute(msg){
  if(msg.room!==_currentVideoRoom)return;
  _setMuteOverlay(msg.from, !!msg.muted);
}

/* ── Toggle call chat history panel ── */
let _callChatHistoryOpen = true;
function toggleCallChatHistory(){
  _callChatHistoryOpen = !_callChatHistoryOpen;
  const hist    = document.getElementById('callChatHistory');
  const chevron = document.getElementById('callChatChevron');
  const badge   = document.getElementById('callChatUnread');
  if(hist)    hist.style.display    = _callChatHistoryOpen ? '' : 'none';
  if(chevron) chevron.textContent   = _callChatHistoryOpen ? '▲' : '▼';
  if(!_callChatHistoryOpen && badge) { badge.style.display='none'; badge.textContent=''; }
}

let _callChatUnreadCount = 0;
function _appendCallChat(from,text,isSelf){
  const now=new Date();
  const hh=now.getHours().toString().padStart(2,'0');
  const mm=now.getMinutes().toString().padStart(2,'0');
  const html=`<div style="padding:4px 0;border-bottom:1px solid rgba(255,255,255,.04)">` +
    `<span style="color:${isSelf?'var(--gold2)':'var(--text2)'};font-weight:${isSelf?700:400}">${esc(from)}</span>` +
    `<span style="color:var(--text3)">: </span><span style="color:var(--text)">${esc(text)}</span>` +
    `<span style="color:var(--text3);font-size:.58rem;margin-left:4px">${hh}:${mm}</span></div>`;

  // Main chat messages container (new layout)
  const el = document.getElementById('callChatMessages');
  if(el){
    el.insertAdjacentHTML('beforeend', html);
    el.scrollTop = el.scrollHeight;
  }

  // If history is collapsed and message is from someone else, show unread badge
  if(!isSelf && !_callChatHistoryOpen){
    _callChatUnreadCount++;
    const badge = document.getElementById('callChatUnread');
    if(badge){ badge.textContent = _callChatUnreadCount; badge.style.display='inline'; }
  }

  // Reset unread when history is open
  if(_callChatHistoryOpen){ _callChatUnreadCount=0; }

  // Legacy mobile container (kept for compatibility)
  const mob = document.getElementById('callChatMessagesMobile');
  if(mob){ mob.insertAdjacentHTML('beforeend', html); mob.scrollTop=mob.scrollHeight; }
}

/* ── Controls ─────────────────────────────────────────────────────────── */
function socialToggleMic(){
  _micEnabled=!_micEnabled;
  _localStream?.getAudioTracks().forEach(t=>t.enabled=_micEnabled);
  const b=document.getElementById('btnSocialMic');
  if(b)b.innerHTML=(_micEnabled?'🎤':'🔇')+' Mic';
  // Show/hide mute overlay on own tile
  _setMuteOverlay('__local__', !_micEnabled);
  // Notify peers via call-chat channel (reuse WS, no extra endpoint needed)
  if(_socialWS?.readyState===WebSocket.OPEN && _currentVideoRoom)
    _socialWS.send(JSON.stringify({action:'call-mute', room:_currentVideoRoom, muted:!_micEnabled}));
}

function _setMuteOverlay(id, muted){
  let overlay=document.getElementById('vmute-'+id);
  const tile=document.getElementById('vtile-'+id);
  if(!tile)return;
  if(muted){
    if(!overlay){
      overlay=document.createElement('div');
      overlay.id='vmute-'+id;
      overlay.style.cssText='position:absolute;top:6px;right:6px;background:rgba(0,0,0,.65);'+
        'border-radius:50%;width:22px;height:22px;display:flex;align-items:center;'+
        'justify-content:center;font-size:.75rem;z-index:5';
      overlay.textContent='🔇';
      tile.appendChild(overlay);
    }
  } else {
    overlay?.remove();
  }
}
function socialToggleCam(){
  _camEnabled=!_camEnabled;
  _localStream?.getVideoTracks().forEach(t=>t.enabled=_camEnabled);
  const b=document.getElementById('btnSocialCam');
  if(b)b.innerHTML=(_camEnabled?'📷':'🚫')+' Cam';
  if(_localStream)_refreshTileVis('__local__',_localStream);
}
async function socialShareScreen(){
  try{
    const ss=await navigator.mediaDevices.getDisplayMedia({video:true});
    const tr=ss.getVideoTracks()[0];
    Object.values(_rtcPeers).forEach(pc=>{
      const s=pc.getSenders().find(s=>s.track?.kind==='video');
      if(s)s.replaceTrack(tr);
    });
    tr.onended=()=>{
      _localStream?.getVideoTracks().forEach(lt=>{
        Object.values(_rtcPeers).forEach(pc=>{
          const s=pc.getSenders().find(s=>s.track?.kind==='video');
          if(s)s.replaceTrack(lt);
        });
      });
    };
  }catch(e){}
}

/* ══════════════════════════════════════════════════════════════════════════
   SOCIAL CHAT — missing functions restored
══════════════════════════════════════════════════════════════════════════ */

function _dmRoom(){
  if(!_socialDMTarget)return'';
  const p=[me?.username||'',_socialDMTarget].sort();
  return'dm:'+p[0]+':'+p[1];
}

function socialChatTab(tab,el){
  document.getElementById('socialGroupChatDiv').style.display=tab==='group'?'':'none';
  document.getElementById('socialDMSection').style.display=tab==='dm'?'':'none';
  document.querySelectorAll('[id^=chatTab]').forEach(b=>b.classList.remove('on'));
  el?.classList.add('on');
  _socialRoom=tab;
  if(tab==='group'){
    if(_socialWS?.readyState===WebSocket.OPEN)
      _socialWS.send(JSON.stringify({action:'history',room:'group',limit:60}));
    // Marcar grupo como leído en el servidor
    _markRoomAsRead('group');
  }
}

function socialSendMessage(){
  const inp=document.getElementById('socialGroupInput'),txt=(inp?.value||'').trim();
  if(!txt||_socialWS?.readyState!==WebSocket.OPEN)return;
  _socialWS.send(JSON.stringify({action:'send',room:'group',content:txt,msg_type:'text'}));
  inp.value='';
}

function socialSendDM(){
  if(!_socialDMTarget)return;
  const inp=document.getElementById('socialDMInput'),txt=(inp?.value||'').trim();
  if(!txt||_socialWS?.readyState!==WebSocket.OPEN)return;
  _socialWS.send(JSON.stringify({action:'send',room:_dmRoom(),content:txt,msg_type:'text'}));
  inp.value='';
}

async function socialLoadDM(username){
  if(!username)return;
  _socialDMTarget=username;
  document.getElementById('socialDMInputRow').style.display='flex';
  const el=document.getElementById('socialDMMessages');
  if(el)el.innerHTML='<div style="text-align:center;color:var(--text3);font-size:.7rem;padding:12px">Cargando…</div>';
  if(_socialWS?.readyState===WebSocket.OPEN){
    const dr=_dmRoom();
    _socialWS.send(JSON.stringify({action:'join',room:dr}));
    _socialWS.send(JSON.stringify({action:'history',room:dr,limit:60}));
    // Marcar DM como leído en el servidor
    _markRoomAsRead(dr);
  }
}

function socialDeleteMsg(id,btn){
  if(_socialWS?.readyState!==WebSocket.OPEN)return;
  _socialWS.send(JSON.stringify({action:'delete_msg',msg_id:id}));
  const b=btn?.closest('div[data-msg-id]');
  if(b)b.querySelector('._mb').innerHTML='<em style="color:var(--text3);font-size:.73rem">Mensaje eliminado</em>';
}

function appendSocialMsg(container,msg,append=true){
  if(!container||!msg)return;
  const isMine=msg.from_user===me?.username;
  const isDeleted=!!msg.deleted;
  const canDelete=me?.is_superadmin||isMine;
  // Format timestamp with date + time
  let time='';
  if(msg.created_at){
    const d=new Date(msg.created_at+'Z');
    const dateStr=d.toLocaleDateString('es-ES',{day:'2-digit',month:'2-digit',year:'numeric'});
    const timeStr=d.toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});
    time=`${dateStr} ${timeStr}`;
  }
  let body='';
  if(isDeleted) body='<em style="color:var(--text3);font-size:.73rem">Mensaje eliminado</em>';
  else if(msg.msg_type==='audio') body=`<audio controls src="${esc(msg.content)}" style="height:28px;max-width:200px"></audio>`;
  else if(msg.msg_type==='image') body=`<img src="${esc(msg.content)}" style="max-width:200px;border-radius:6px;cursor:pointer" onclick="window.open(this.src)">`;
  else body=`<span style="white-space:pre-wrap;word-break:break-word">${esc(msg.content)}</span>`;
  const d=document.createElement('div');
  d.setAttribute('data-msg-id',msg.id||'');
  d.style.cssText=`display:flex;gap:8px;align-items:flex-start;padding:3px 0;${isMine?'flex-direction:row-reverse':''}`;
  d.innerHTML=`<div style="width:28px;height:28px;border-radius:50%;background:var(--glass);border:1px solid var(--border);
    display:flex;align-items:center;justify-content:center;font-size:.64rem;flex-shrink:0;
    color:var(--gold2);font-family:'Playfair Display',serif">${esc((msg.from_user[0]||'?').toUpperCase())}</div>
    <div style="max-width:76%">
      <div style="font-size:.55rem;color:var(--text3);margin-bottom:2px;${isMine?'text-align:right':''}">${isMine?'tú':esc(msg.from_user)} · ${time}</div>
      <div class="_mb" style="background:${isMine?'rgba(212,168,67,.1)':'var(--glass)'};border:1px solid ${isMine?'var(--border2)':'var(--border)'};
        border-radius:${isMine?'10px 2px 10px 10px':'2px 10px 10px 10px'};padding:6px 10px;font-size:.78rem;line-height:1.5">
        ${body}
        ${canDelete&&!isDeleted?`<button onclick="socialDeleteMsg(${msg.id},this)"
          style="display:block;margin-top:3px;background:none;border:none;color:var(--text3);font-size:.57rem;cursor:pointer;padding:0;opacity:.6">🗑 Eliminar</button>`:''}
      </div>
    </div>`;
  if(append)container.appendChild(d);else container.insertBefore(d,container.firstChild);
  if(append)container.scrollTop=container.scrollHeight;
}

/* ── Unread badge ─────────────────────────────────────────────────── */
let _unreadCounts={};

function _updateUnreadBadge(){
  // Social nav badge (desktop)
  const total=Object.values(_unreadCounts).reduce((s,n)=>s+n,0);
  let badge=document.getElementById('_socialNavBadge');
  const navBtn=document.getElementById('navSocial');
  if(navBtn){
    if(!badge){
      badge=document.createElement('span');
      badge.id='_socialNavBadge';
      badge.style.cssText='display:inline-flex;align-items:center;justify-content:center;'+
        'background:var(--red);color:#fff;border-radius:50%;width:14px;height:14px;'+
        'font-size:.55rem;font-weight:700;margin-left:4px;vertical-align:middle';
      navBtn.appendChild(badge);
    }
    badge.textContent=total>9?'9+':total;
    badge.style.display=total>0?'inline-flex':'none';
  }
  // Mobile Social badge
  const mBadge=document.getElementById('_mSocialBadge');
  if(mBadge){
    mBadge.textContent=total>9?'9+':total;
    mBadge.style.display=total>0?'':'none';
  }
  // Chat tab badges
  const groupCount=_unreadCounts['group']||0;
  const dmCount=Object.entries(_unreadCounts).filter(([k])=>k.startsWith('dm:')).reduce((s,[,n])=>s+n,0);
  _setTabBadge('chatTabGroup',groupCount);
  _setTabBadge('chatTabDM',dmCount);
}

/** Recalcula las columnas del nav móvil según los botones visibles */
function _recalcMobileNav(){
  const mn=document.getElementById('mobileNav');
  if(!mn)return;
  const visible=[...mn.querySelectorAll('.mNavBtn')].filter(b=>!b.classList.contains('hidden'));
  const n=Math.max(4,Math.min(visible.length,7));
  mn.style.gridTemplateColumns=`repeat(${n},1fr)`;
}

/** Navega a Social y salta directamente al primer mensaje no leído */
function _mobileNavSocial(){
  nav('social', document.getElementById('mobileNavSocial'));
  // Si hay no leídos en DM, abrir DM; si solo en grupo, abrir grupo
  const dmCount=Object.entries(_unreadCounts).filter(([k])=>k.startsWith('dm:')).reduce((s,[,n])=>s+n,0);
  const groupCount=_unreadCounts['group']||0;
  setTimeout(()=>{
    if(dmCount>0){
      socialChatTab('dm',document.getElementById('chatTabDM'));
    } else if(groupCount>0){
      socialChatTab('group',document.getElementById('chatTabGroup'));
    }
  },100);
}

function _setTabBadge(tabId,count){
  const tab=document.getElementById(tabId);
  if(!tab)return;
  let b=tab.querySelector('._tabBadge');
  if(!b){
    b=document.createElement('span');
    b.className='_tabBadge';
    b.style.cssText='display:inline-flex;align-items:center;justify-content:center;'+
      'background:var(--red);color:#fff;border-radius:50%;width:13px;height:13px;'+
      'font-size:.52rem;font-weight:700;margin-left:4px;vertical-align:middle';
    tab.appendChild(b);
  }
  b.textContent=count>9?'9+':count;
  b.style.display=count>0?'inline-flex':'none';
}

async function _pollUnread(){
  try{
    const d=await req('GET','/api/messages/unread');
    // Solo actualizar contadores que realmente tienen mensajes no leídos en el servidor
    // No sobrescribir todo - mantener los que ya fueron marcados como leídos localmente
    if(d && typeof d === 'object'){
      // Actualizar solo los rooms que tienen mensajes no leídos en el servidor
      Object.keys(d).forEach(room => {
        if(d[room] > 0){
          _unreadCounts[room] = d[room];
        }
      });

      // Limpiar rooms que ya no tienen mensajes no leídos en el servidor
      Object.keys(_unreadCounts).forEach(room => {
        if(!d[room] || d[room] === 0){
          delete _unreadCounts[room];
        }
      });
    }
    _updateUnreadBadge();
  }catch(_){}
}

/* ── All rooms (superadmin) ───────────────────────────────────────── */
async function socialLoadAllRooms(){
  try{
    const d=await req('GET','/api/messages/admin/all-rooms');
    const el=document.getElementById('socialAllRooms');if(!el)return;
    const rooms=d.rooms||[];
    if(!rooms.length){el.innerHTML='<div class="empty">Sin conversaciones</div>';return;}
    // Sort by last message time desc
    rooms.sort((a,b)=>(b.last_at||'').localeCompare(a.last_at||''));
    el.innerHTML=rooms.map(r=>{
      const label=r.room==='group'?'👥 Grupo':'💬 '+r.room.replace(/^dm:/,'').replace(/:/,' ↔ ');
      const unread=_unreadCounts[r.room]||0;
      return`<div style="padding:7px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;gap:8px">
        <div style="flex:1;min-width:0">
          <div style="font-size:.72rem;color:var(--text);display:flex;align-items:center;gap:6px">
            ${esc(label)}
            ${unread?`<span style="background:var(--red);color:#fff;border-radius:50%;width:14px;height:14px;display:inline-flex;align-items:center;justify-content:center;font-size:.52rem">${unread}</span>`:''}
          </div>
          <div style="font-size:.58rem;color:var(--text3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${esc((r.last_user||'')+(r.last_content?': '+(r.last_content||'').slice(0,38):''))} · ${r.total||0} msgs</div>
        </div>
        <button class="btn btnS btnSm" onclick="socialAdminOpen('${esc(r.room)}')">Ver</button>
      </div>`;
    }).join('');
  }catch(e){}
}

async function socialAdminOpen(room){
  if(room==='group'){
    socialChatTab('group',document.getElementById('chatTabGroup'));
  }else{
    const parts=room.replace('dm:','').split(':');
    const other=parts.find(p=>p!==me?.username)||parts[0];
    const sel=document.getElementById('socialDMUser');if(sel)sel.value=other;
    socialChatTab('dm',document.getElementById('chatTabDM'));
    await socialLoadDM(other);
  }
}

/* ── Unread polling (when social tab not open) ────────────────────── */
let _unreadIv=null;
function _startUnreadPolling(){
  if(_unreadIv)return;
  _pollUnread();
  _unreadIv=setInterval(()=>{
    if(!document.getElementById('view-social')?.classList.contains('on'))
      _pollUnread();
  },30000);
}

/* ── Panel de notificaciones pendientes ────────────────────────────── */
function _showPendingNotifications(){
  // Obtener todas las notificaciones pendientes
  const groupCount = _unreadCounts['group'] || 0;
  const dmEntries = Object.entries(_unreadCounts).filter(([k]) => k.startsWith('dm:'));
  const dmCount = dmEntries.reduce((s, [, n]) => s + n, 0);

  const totalUnread = groupCount + dmCount;

  // Si no hay notificaciones pendientes, no mostrar nada
  if (totalUnread === 0) return;

  // Crear el panel de notificaciones
  const panel = document.createElement('div');
  panel.id = '_pendingNotificationsPanel';
  panel.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10000;
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 20px;
    min-width: 320px;
    max-width: 90vw;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0,0,0,.5);
    animation: fadeInScale .3s ease;
  `;

  // Crear el contenido del panel
  let content = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h3 style="color:var(--gold);font-size:1.1rem;font-weight:600;margin:0">
        📬 Notificaciones Pendientes
      </h3>
      <button onclick="_closePendingNotifications()" style="
        background:none;border:none;color:var(--text3);
        cursor:pointer;font-size:1.3rem;padding:0;
        width:28px;height:28px;display:flex;align-items:center;justify-content:center;
        border-radius:50%;transition:all .2s
      " onmouseover="this.style.background='var(--bg4)';this.style.color='var(--text)'"
         onmouseout="this.style.background='none';this.style.color='var(--text3)'">✕</button>
    </div>

    <div style="color:var(--text2);font-size:.85rem;margin-bottom:16px">
      Tienes <strong style="color:var(--gold)">${totalUnread}</strong> mensaje${totalUnread !== 1 ? 's' : ''} sin leer
    </div>

    <div style="display:flex;flex-direction:column;gap:8px">
  `;

  // Agregar notificación del grupo si hay mensajes
  if (groupCount > 0) {
    content += `
      <div class="notification-item" onclick="_openNotification('group')" style="
        background:var(--bg3);
        border:1px solid var(--border);
        border-radius:var(--radius-sm);
        padding:12px;
        cursor:pointer;
        transition:all .2s;
        display:flex;
        align-items:center;
        gap:12px;
      " onmouseover="this.style.background='var(--bg4)';this.style.borderColor='var(--gold)'"
         onmouseout="this.style.background='var(--bg3)';this.style.borderColor='var(--border)'">
        <div style="font-size:1.8rem;flex-shrink:0">👥</div>
        <div style="flex:1;min-width:0">
          <div style="font-weight:600;color:var(--text);font-size:.9rem;margin-bottom:2px">
            Chat Grupal
          </div>
          <div style="color:var(--text3);font-size:.75rem">
            ${groupCount} mensaje${groupCount !== 1 ? 's' : ''} nuevo${groupCount !== 1 ? 's' : ''}
          </div>
        </div>
        <div style="
          background:var(--red);
          color:#fff;
          border-radius:50%;
          width:24px;
          height:24px;
          display:flex;
          align-items:center;
          justify-content:center;
          font-size:.7rem;
          font-weight:700;
          flex-shrink:0;
        ">${groupCount}</div>
      </div>
    `;
  }

  // Agregar notificaciones de DMs
  const currentUser = me?.username || '';
  dmEntries.forEach(([room, count]) => {
    const otherUser = room.replace('dm:', '').split(':').find(u => u !== currentUser);
    content += `
      <div class="notification-item" onclick="_openNotification('${room}')" style="
        background:var(--bg3);
        border:1px solid var(--border);
        border-radius:var(--radius-sm);
        padding:12px;
        cursor:pointer;
        transition:all .2s;
        display:flex;
        align-items:center;
        gap:12px;
      " onmouseover="this.style.background='var(--bg4)';this.style.borderColor='var(--gold)'"
         onmouseout="this.style.background='var(--bg3)';this.style.borderColor='var(--border)'">
        <div style="font-size:1.8rem;flex-shrink:0">💬</div>
        <div style="flex:1;min-width:0">
          <div style="font-weight:600;color:var(--text);font-size:.9rem;margin-bottom:2px">
            ${esc(otherUser)}
          </div>
          <div style="color:var(--text3);font-size:.75rem">
            ${count} mensaje${count !== 1 ? 's' : ''} nuevo${count !== 1 ? 's' : ''}
          </div>
        </div>
        <div style="
          background:var(--red);
          color:#fff;
          border-radius:50%;
          width:24px;
          height:24px;
          display:flex;
          align-items:center;
          justify-content:center;
          font-size:.7rem;
          font-weight:700;
          flex-shrink:0;
        ">${count}</div>
      </div>
    `;
  });

  content += `
    </div>

    <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border);display:flex;gap:8px">
      <button onclick="_showNotificationHistory()" class="btn btnSm" style="
        flex:1;
        background:var(--bg4);
        border:1px solid var(--border);
        color:var(--text2);
        padding:8px;
        border-radius:var(--radius-sm);
        cursor:pointer;
        font-size:.75rem;
        transition:all .2s;
      " onmouseover="this.style.background='var(--bg5)';this.style.borderColor='var(--gold)';this.style.color='var(--gold2)'"
         onmouseout="this.style.background='var(--bg4)';this.style.borderColor='var(--border)';this.style.color='var(--text2)'">
        📜 Ver historial
      </button>
      <button onclick="_markAllAsRead()" class="btn btnSm" style="
        flex:1;
        background:var(--bg4);
        border:1px solid var(--border);
        color:var(--text2);
        padding:8px;
        border-radius:var(--radius-sm);
        cursor:pointer;
        font-size:.75rem;
        transition:all .2s;
      " onmouseover="this.style.background='var(--bg5)';this.style.borderColor='var(--green)';this.style.color='var(--green)'"
         onmouseout="this.style.background='var(--bg4)';this.style.borderColor='var(--border)';this.style.color='var(--text2)'">
        ✓ Marcar leídos
      </button>
      <button onclick="_closePendingNotifications()" class="btn btnSm" style="
        flex:1;
        background:var(--gold);
        border:none;
        color:#1a1a22;
        padding:8px;
        border-radius:var(--radius-sm);
        cursor:pointer;
        font-size:.75rem;
        font-weight:600;
        transition:all .2s;
      " onmouseover="this.style.background='var(--gold2)';this.style.transform='translateY(-1px)'"
         onmouseout="this.style.background='var(--gold)';this.style.transform='translateY(0)'">
        Cerrar
      </button>
    </div>
  `;

  panel.innerHTML = content;

  // Crear overlay
  const overlay = document.createElement('div');
  overlay.id = '_pendingNotificationsOverlay';
  overlay.style.cssText = `
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.6);
    backdrop-filter: blur(4px);
    z-index: 9999;
    animation: fadeIn .3s ease;
  `;
  overlay.onclick = _closePendingNotifications;

  // Agregar al DOM
  document.body.appendChild(overlay);
  document.body.appendChild(panel);
}

function _closePendingNotifications(){
  document.getElementById('_pendingNotificationsPanel')?.remove();
  document.getElementById('_pendingNotificationsOverlay')?.remove();
}

/* ── Notification History Panel ────────────────────────────────────── */
let _notificationHistoryFilter = 'all';
let _notificationHistoryData = [];

async function _showNotificationHistory(){
  _closePendingNotifications();

  // Create or show panel
  let panel = document.getElementById('_notificationHistoryPanel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = '_notificationHistoryPanel';
    panel.style.cssText = `
      position:fixed;
      inset:0;
      background:rgba(4,4,10,.95);
      z-index:10001;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:24px;
    `;

    panel.innerHTML = `
      <div style="
        background:var(--bg2);
        border:1.5px solid var(--gold);
        border-radius:var(--radius);
        padding:20px;
        max-width:700px;
        width:100%;
        max-height:85vh;
        display:flex;
        flex-direction:column;
      ">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h3 style="color:var(--gold);font-size:1.1rem;font-weight:600;margin:0">
            📜 Historial de Notificaciones
          </h3>
          <button onclick="_closeNotificationHistory()" style="
            background:none;border:none;color:var(--text3);
            cursor:pointer;font-size:1.3rem;padding:0;
            width:28px;height:28px;display:flex;align-items:center;justify-content:center;
            border-radius:50%;transition:all .2s
          " onmouseover="this.style.background='var(--bg4)';this.style.color='var(--text)'"
             onmouseout="this.style.background='none';this.style.color='var(--text3)'">✕</button>
        </div>

        <div style="display:flex;gap:8px;margin-bottom:12px">
          <button id="historyFilterAll" class="btn btnSm" onclick="_filterNotificationHistory('all')" style="flex:1;background:rgba(212,168,67,.14);border-color:var(--gold);color:var(--gold2)">
            Todos
          </button>
          <button id="historyFilterGroup" class="btn btnSm btnN" onclick="_filterNotificationHistory('group')" style="flex:1">
            👥 Grupo
          </button>
          <button id="historyFilterDM" class="btn btnSm btnN" onclick="_filterNotificationHistory('dm')" style="flex:1">
            💬 DMs
          </button>
        </div>

        <div id="notificationHistoryContent" style="
          flex:1;
          overflow-y:auto;
          border:1px solid var(--border);
          border-radius:var(--radius);
          padding:12px;
          background:var(--bg3);
          min-height:300px;
          max-height:calc(85vh - 200px);
        ">
          <div style="text-align:center;color:var(--text3);padding:20px">
            Cargando historial...
          </div>
        </div>

        <div style="margin-top:12px;display:flex;gap:8px">
          <button class="btn btnN" onclick="_closeNotificationHistory()" style="flex:1">
            Cerrar
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(panel);
  } else {
    panel.style.display = 'flex';
  }

  // Load history
  try {
    const response = await fetch(\'/bank/api/messages/admin/all-rooms\', {
      headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('dvd_token') || localStorage.getItem('token')) }
    });

    if (!response.ok) throw new Error('Error cargando historial');

    const data = await response.json();
    _notificationHistoryData = data.rooms || [];

    // Sort by last message time
    _notificationHistoryData.sort((a, b) => (b.last_at || '').localeCompare(a.last_at || ''));

    _renderNotificationHistory();
  } catch (e) {
    document.getElementById('notificationHistoryContent').innerHTML =
      `<div style="text-align:center;color:var(--red);padding:20px">Error: ${esc(e.message)}</div>`;
  }
}

function _closeNotificationHistory(){
  const panel = document.getElementById('_notificationHistoryPanel');
  if (panel) panel.style.display = 'none';
}

function _filterNotificationHistory(filter){
  _notificationHistoryFilter = filter;

  // Update button styles
  const allBtn = document.getElementById('historyFilterAll');
  const groupBtn = document.getElementById('historyFilterGroup');
  const dmBtn = document.getElementById('historyFilterDM');

  [allBtn, groupBtn, dmBtn].forEach(btn => {
    btn.style.background = '';
    btn.style.borderColor = '';
    btn.style.color = '';
  });

  if (filter === 'all') {
    allBtn.style.background = 'rgba(212,168,67,.14)';
    allBtn.style.borderColor = 'var(--gold)';
    allBtn.style.color = 'var(--gold2)';
  } else if (filter === 'group') {
    groupBtn.style.background = 'rgba(212,168,67,.14)';
    groupBtn.style.borderColor = 'var(--gold)';
    groupBtn.style.color = 'var(--gold2)';
  } else if (filter === 'dm') {
    dmBtn.style.background = 'rgba(212,168,67,.14)';
    dmBtn.style.borderColor = 'var(--gold)';
    dmBtn.style.color = 'var(--gold2)';
  }

  _renderNotificationHistory();
}

function _renderNotificationHistory(){
  const content = document.getElementById('notificationHistoryContent');
  if (!content) return;

  let filtered = _notificationHistoryData;
  if (_notificationHistoryFilter === 'group') {
    filtered = _notificationHistoryData.filter(r => r.room === 'group');
  } else if (_notificationHistoryFilter === 'dm') {
    filtered = _notificationHistoryData.filter(r => r.room.startsWith('dm:'));
  }

  if (!filtered.length) {
    content.innerHTML = '<div style="text-align:center;color:var(--text3);padding:20px">Sin notificaciones</div>';
    return;
  }

  const currentUser = me?.username || '';

  content.innerHTML = filtered.map(r => {
    const isGroup = r.room === 'group';
    const icon = isGroup ? '👥' : '💬';
    let label = isGroup ? 'Chat Grupal' : r.room.replace('dm:', '').split(':').find(u => u !== currentUser) || 'DM';

    const lastMsg = r.last_msg || 'Sin mensajes';
    const lastAt = r.last_at ? new Date(r.last_at).toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }) : 'Nunca';

    const unread = _unreadCounts[r.room] || 0;
    const unreadBadge = unread > 0 ? `<div style="
      background:var(--red);
      color:#fff;
      border-radius:50%;
      width:22px;
      height:22px;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:.65rem;
      font-weight:700;
      flex-shrink:0;
    ">${unread}</div>` : '';

    return `
      <div onclick="_openNotificationFromHistory('${r.room}')" style="
        background:var(--bg4);
        border:1px solid var(--border);
        border-radius:var(--radius-sm);
        padding:12px;
        margin-bottom:8px;
        cursor:pointer;
        transition:all .2s;
      " onmouseover="this.style.borderColor='var(--gold)';this.style.background='var(--n3)'"
         onmouseout="this.style.borderColor='var(--border)';this.style.background='var(--bg4)'">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
          <div style="font-size:1.5rem">${icon}</div>
          <div style="flex:1;min-width:0">
            <div style="font-weight:600;color:var(--text);font-size:.85rem">
              ${esc(label)}
            </div>
            <div style="color:var(--text3);font-size:.65rem">
              ${lastAt}
            </div>
          </div>
          ${unreadBadge}
        </div>
        <div style="color:var(--text2);font-size:.72rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
          ${esc(lastMsg)}
        </div>
      </div>
    `;
  }).join('');
}

function _openNotificationFromHistory(room){
  _closeNotificationHistory();
  _openNotification(room);
}

function _openNotification(room){
  _closePendingNotifications();

  // First, navigate to the social view
  nav('social', document.getElementById('navSocial') || document.getElementById('mobileNavSocial'));

  // Wait for the social view to initialize, then open the specific chat
  setTimeout(() => {
    if (room === 'group') {
      // Abrir chat grupal
      const groupTab = document.getElementById('chatTabGroup');
      if (groupTab) {
        socialChatTab('group', groupTab);
      }

      // Marcar mensajes del grupo como leídos
      setTimeout(() => {
        _markRoomAsRead('group');
      }, 500);
    } else if (room.startsWith('dm:')) {
      // Abrir DM específico
      const currentUser = me?.username || '';
      const otherUser = room.replace('dm:', '').split(':').find(u => u !== currentUser);
      _socialDMTarget = otherUser;

      const dmTab = document.getElementById('chatTabDM');
      if (dmTab) {
        socialChatTab('dm', dmTab);
      }

      // Esperar un momento y luego cargar el historial del DM
      setTimeout(() => {
        if (_socialWS?.readyState === WebSocket.OPEN) {
          _socialWS.send(JSON.stringify({action: 'join', room: room}));
          _socialWS.send(JSON.stringify({action: 'history', room: room, limit: 60}));
        }

        // Marcar mensajes del DM como leídos
        _markRoomAsRead(room);
      }, 500);
    }
  }, 150);
}

function _markAllAsRead(){
  // Marcar todos los chats como leídos en la base de datos
  Object.keys(_unreadCounts).forEach(room => {
    _markRoomAsRead(room);
  });

  // Limpiar todos los contadores de no leídos localmente
  _unreadCounts = {};
  _updateUnreadBadge();
  _closePendingNotifications();
}

async function _markRoomAsRead(room){
  try {
    // Marcar como leídos en el servidor usando WebSocket si está disponible
    if(_socialWS?.readyState === WebSocket.OPEN){
      _socialWS.send(JSON.stringify({action: 'mark_read', room: room}));
      console.log(`[CHAT] 📨 Enviado mark_read para ${room} via WebSocket`);
    }

    // También intentar via HTTP como respaldo
    try {
      const markResponse = await fetch(\'/bank/api/messages/mark-room-read\', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        body: JSON.stringify({ room: room })
      });

      if (markResponse.ok) {
        console.log(`[CHAT] ✅ Marcado ${room} como leído via HTTP`);
      }
    } catch(httpErr) {
      console.warn('[CHAT] HTTP mark_read falló, usando solo WebSocket:', httpErr);
    }

    // Limpiar contador local inmediatamente
    delete _unreadCounts[room];
    _updateUnreadBadge();

    // Actualizar desde servidor después de un momento
    setTimeout(() => _pollUnread(), 1000);
  } catch (err) {
    console.error('[CHAT] Error al marcar mensajes como leídos:', err);
  }
}

async function loadAdvancedStats(){
  const el=document.getElementById('histAdvStatsContent');if(!el)return;
  el.innerHTML='<div class="empty">Cargando…</div>';
  try{
    const d=await req('GET','/api/stats/advanced');
    const bySec=(d.by_section||[]).map(r=>`<tr><td>${esc(r.section)}</td><td>${r.n}</td><td>${Math.round((r.avg_s||0)/60)} min</td></tr>`).join('');
    const byUser=(d.by_user||[]).slice(0,10).map(r=>`<tr><td>${esc(r.username)}</td><td>${r.n}</td><td>${Math.round((r.total_s||0)/3600)}h</td></tr>`).join('');
    el.innerHTML=`<div style="font-size:.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em;margin:8px 0 4px">Por sección</div>
      <div class="tblWrap"><table class="tbl"><thead><tr><th>Sección</th><th>Sesiones</th><th>Media</th></tr></thead><tbody>${bySec}</tbody></table></div>
      <div style="font-size:.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:.1em;margin:12px 0 4px">Top usuarios</div>
      <div class="tblWrap"><table class="tbl"><thead><tr><th>Usuario</th><th>Sesiones</th><th>Tiempo</th></tr></thead><tbody>${byUser}</tbody></table></div>`;
  }catch(e){el.innerHTML=`<div class="empty">Error: ${esc(e.message)}</div>`;}
}

/* ── Hook social/opo into existing nav() function ── */
(function(){
  const __nav=window.nav;
  if(typeof __nav==='function'){
    window.nav=function(view,el){
      __nav(view,el);
      if(view==='social')setTimeout(()=>{
        socialInit();
        _showPendingNotifications(); // Mostrar notificaciones pendientes
        // NO limpiar _unreadCounts automáticamente - solo cuando el usuario marque como leído
        _updateUnreadBadge();
        checkRoomsStatus().catch(()=>{});
        if(typeof window._rpPoll==='function')window._rpPoll();
      },80);
      if(view==='cuentos')setTimeout(()=>loadCuentosView(),80);
      if(view==='hist'&&me?.is_superadmin){document.getElementById('histAdvancedStatsPanel')?.style.setProperty('display','');}
    };
  }
})();

/* blink keyframe */
if(!document.getElementById('_blinkKf')){const s=document.createElement('style');s.id='_blinkKf';s.textContent='@keyframes blink{50%{opacity:.2}}';document.head.appendChild(s);}

function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}

/* ══════════════════════════════════════════════════════════════════════════
   APP PERMISSIONS — request audio + camera + notifications after login
   Requesting early (at login) means the browser shows the permission dialog
   while the user is actively interacting, which is required by browsers.
   The stream is kept alive silently so subsequent getUserMedia calls succeed
   instantly without showing the dialog again.
══════════════════════════════════════════════════════════════════════════ */
/* ══════════════════════════════════════════════════════════════════════════
   PERMISSION MANAGEMENT
   - Notification permission: requested on login
   - Audio/Video permissions: requested ONLY when needed (Social section, games with audio)
   - This improves UX by not asking for unnecessary permissions upfront
══════════════════════════════════════════════════════════════════════════ */

function _requestNotificationPermission(){
  // 1. Notification permission
  if('Notification' in window && Notification.permission === 'default'){
    Notification.requestPermission().catch(()=>{});
  }

  // 2. Unlock AudioContext (required by browsers — needs user gesture)
  try{
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const buf = ctx.createBuffer(1, 1, 22050);
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(ctx.destination);
    src.start(0);
    window._audioCtx = ctx;
  }catch(e){}
}

function _requestAppPermissions(){
  // Legacy function - now only requests notifications
  // Audio/Video permissions are requested on-demand
  _requestNotificationPermission();
}

/* ══════════════════════════════════════════════════════════════════════════
   ROOM NOTIFICATION SOUND — plays when a new room opens
   3-second ascending chime using Web Audio API
══════════════════════════════════════════════════════════════════════════ */
function _playRoomOpenSound(){
  try{
    const ctx = window._audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    window._audioCtx = ctx;
    if(ctx.state === 'suspended') ctx.resume();

    const now = ctx.currentTime;
    // Three ascending tones — friendly chime
    const notes = [
      { freq: 523.25, start: 0,    dur: 0.4 },  // C5
      { freq: 659.25, start: 0.35, dur: 0.4 },  // E5
      { freq: 783.99, start: 0.70, dur: 0.8 },  // G5
    ];

    notes.forEach(n => {
      const osc  = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(n.freq, now + n.start);

      // Envelope: quick attack, smooth decay
      gain.gain.setValueAtTime(0, now + n.start);
      gain.gain.linearRampToValueAtTime(0.35, now + n.start + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.001, now + n.start + n.dur);

      osc.start(now + n.start);
      osc.stop(now + n.start + n.dur + 0.05);
    });
  }catch(e){}
}
// --- script block 3 ---

(function(){
  /* v4 disabled — server injects a newer version */
  window.__roomsPollV4 = true;
  return; /* early exit */
  if(window.__roomsPollV4) return;
  window.__roomsPollV4 = true;
  var POLL_MS = 2000;  /* poll every 2s */
  var _seen = {};
  var _fabCreated = false;

  function tok(){ try{ return localStorage.getItem('dvd_token')||''; }catch(e){ return ''; } }
  function myName(){ return (window.me&&window.me.username)||''; }
  function esc(s){ return String(s||'').replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];}); }
  /* get translated string, fallback to Spanish */
  function tr(key, fallback){
    try{ var v=(window.T&&window.T[key]); return v||fallback; }catch(e){ return fallback; }
  }

  function injectCSS(){
    if(document.getElementById('_rpv4css')) return;
    var s=document.createElement('style'); s.id='_rpv4css';
    s.textContent='@keyframes _rpIn{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:scale(1)}}'
      +'@keyframes _rpPulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.6)}70%{box-shadow:0 0 0 8px rgba(34,197,94,0)}}'
      +'#_rpFab{position:fixed;bottom:80px;right:16px;z-index:99998;display:flex;flex-direction:column;align-items:flex-end;gap:8px}'
      +'#_rpBtn{width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#16a34a,#22c55e);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:1.4rem;box-shadow:0 4px 16px rgba(0,0,0,.5);animation:_rpPulse 2s infinite;transition:transform .15s;position:relative}'
      +'#_rpBtn:hover{transform:scale(1.1)}'
      +'#_rpBadge{position:absolute;top:-4px;right:-4px;background:#ef4444;color:#fff;border-radius:50%;min-width:20px;height:20px;font-size:.65rem;font-family:monospace;display:flex;align-items:center;justify-content:center;font-weight:700;border:2px solid #0a0a14;padding:0 3px}'
      +'#_rpPanel{background:#0f0f1a;border:1px solid rgba(34,197,94,.4);border-radius:14px;padding:0;width:290px;box-shadow:0 8px 32px rgba(0,0,0,.8);overflow:hidden;animation:_rpIn .2s ease;display:none}'
      +'#_rpPanel.open{display:block}'
      +'#_rpPHead{padding:10px 14px;border-bottom:1px solid rgba(255,255,255,.07);display:flex;align-items:center;justify-content:space-between}'
      +'#_rpPHead span{font-size:.65rem;color:#4ade80;text-transform:uppercase;letter-spacing:.1em;font-family:monospace}'
      +'#_rpPHead button{background:none;border:none;color:#666;cursor:pointer;font-size:.9rem;padding:0}'
      +'#_rpList{max-height:280px;overflow-y:auto;padding:6px}'
      +'#_rpEmpty{padding:14px;text-align:center;font-size:.72rem;color:#666}'
      +'._rpItem{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);margin-bottom:4px}'
      +'._rpItem:last-child{margin-bottom:0}'
      +'._rpDot{width:8px;height:8px;border-radius:50%;background:#4ade80;box-shadow:0 0 6px #4ade80;flex-shrink:0}'
      +'._rpInfo{flex:1;min-width:0}'
      +'._rpTitle{font-size:.78rem;color:#eee;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
      +'._rpSub{font-size:.58rem;color:#888;margin-top:1px}'
      +'._rpJoin{flex-shrink:0;background:rgba(34,197,94,.15);border:1px solid rgba(34,197,94,.4);color:#4ade80;border-radius:7px;padding:4px 10px;font-size:.62rem;cursor:pointer;white-space:nowrap}'
      +'._rpJoin:hover{background:rgba(34,197,94,.3)}';
    document.head.appendChild(s);
  }

  function createFAB(){
    if(_fabCreated || document.getElementById('_rpFab')) { _fabCreated=true; return; }
    _fabCreated = true;
    injectCSS();
    var fab=document.createElement('div'); fab.id='_rpFab';
    fab.innerHTML='<div id="_rpPanel">'
      +'<div id="_rpPHead"><span id="_rpPTitle">🎥 '+tr('fabRoomsTitle',tr('socialLiveRooms','Salas activas'))+'</span>'
      +'<button onclick="document.getElementById(\'_rpPanel\').classList.remove(\'open\')">✕</button></div>'
      +'<div id="_rpList"><div id="_rpEmpty"></div></div></div>'
      +'<button id="_rpBtn" onclick="window._rpToggle()" title="'+tr('fabRoomsCount',tr('socialLiveRooms','Salas activas'))+' = 0">'
      +'🎥<span id="_rpBadge">0</span></button>';
    document.body.appendChild(fab);
    document.addEventListener('click',function(e){
      var f=document.getElementById('_rpFab');
      if(f&&!f.contains(e.target)){var p=document.getElementById('_rpPanel');if(p)p.classList.remove('open');}
    });
  }

  window._rpToggle=function(){var p=document.getElementById('_rpPanel');if(p)p.classList.toggle('open');};

  /* Called by _renderRoomsList so FAB updates instantly via WS too */
  window._rpRenderFromApp=function(rooms){ renderFAB(rooms); };

  window._rpJoin=function(key,title){
    var p=document.getElementById('_rpPanel');if(p)p.classList.remove('open');
    if(typeof nav==='function') nav('social',document.getElementById('navSocial'));
    setTimeout(function(){if(typeof socialJoinRoom==='function') socialJoinRoom(key,title);},150);
  };

  function renderFAB(rooms){
    createFAB();
    var list=document.getElementById('_rpList');
    var badge=document.getElementById('_rpBadge');
    var empty=document.getElementById('_rpEmpty');
    var title=document.getElementById('_rpPTitle');
    var btn=document.getElementById('_rpBtn');
    if(!list) return;

    var myN=myName();
    var vis=rooms.filter(function(r){
      return r.mode==='public'||r.invited||(r.members&&r.members.indexOf(myN)!==-1);
    });
    var notIn=vis.filter(function(r){return!(r.members&&r.members.indexOf(myN)!==-1);});

    /* always show FAB — even with 0 rooms */
    var fab=document.getElementById('_rpFab');
    if(fab) fab.style.display='flex';

    /* badge: number of joinable rooms */
    if(badge){
      badge.textContent=vis.length;
      badge.style.background=vis.length?'#ef4444':'#555';
    }

    /* title */
    var liveLabel=tr('fabRoomsCount',tr('socialLiveRooms','Salas activas'));
    if(title) title.textContent='🎥 '+liveLabel+' = '+vis.length;
    if(btn) btn.title=liveLabel+' = '+vis.length;

    /* list */
    if(!vis.length){
      if(empty) empty.textContent=tr('fabRoomsEmpty',tr('socialNoRooms','Sin salas activas'))+' (0)';
      list.innerHTML='<div id="_rpEmpty" style="padding:14px;text-align:center;font-size:.72rem;color:#666">'
        +tr('fabRoomsCount',tr('socialLiveRooms','Salas abiertas'))+' = 0</div>';
      return;
    }
    if(empty) empty.textContent='';

    list.innerHTML=vis.map(function(r){
      var inRoom=r.members&&r.members.indexOf(myN)!==-1;
      var cnt=r.members?r.members.length:0;
      var inv=!!r.invited&&!inRoom;
      var joinLabel=tr('socialJoinRoom','Unirse');
      var inCallLabel=tr('socialEndVideo','En llamada');
      var action=inRoom
        ?'<span style="font-size:.6rem;color:#4ade80;font-weight:700">● '+inCallLabel+'</span>'
        :'<button class="_rpJoin" onclick="window._rpJoin(\''+esc(r.key)+'\',\''+esc(r.title||r.key)+'\')">▶ '+joinLabel+'</button>';
      var partLabel=cnt===1?(cnt+' '+tr('socialRoomParticipants','participante')):(cnt+' '+tr('socialRoomParticipants','participantes'));
      return '<div class="_rpItem">'
        +'<span class="_rpDot" style="background:'+(inRoom?'#4ade80':inv?'#d4a843':'#4ade80')+'"></span>'
        +'<div class="_rpInfo"><div class="_rpTitle">'+esc(r.title||r.key)+(r.mode==='private'?' 🔒':'')+(inv?' ✉':'')+'</div>'
        +'<div class="_rpSub">'+partLabel+(r.host?' · @'+esc(r.host):'')+'</div></div>'
        +action+'</div>';
    }).join('');
  }

  function notifyNew(r){
    if(_seen[r.key]) return;
    _seen[r.key]=true;
    var myN=myName();
    if(r.members&&r.members.indexOf(myN)!==-1) return;

    /* ── Play 3-second room-open chime ── */
    if(r.mode==='public'){
      try{
        if(typeof window._playRoomOpenSound==='function') window._playRoomOpenSound();
      }catch(e){}
    }

    /* ── Banner notification — 3s progress bar, then auto-dismiss ── */
    var BANNER_MS = 12000;
    var lbl=r.invited?('✉ '+tr('socialRoomInvite','Invitado a')+':'):('🎥 '+tr('socialLiveRooms','Sala abierta')+':');
    var joinLabel=tr('socialJoinRoom','Unirse');
    var color=r.invited?'#d4a843':'#4ade80';
    var borderColor=r.invited?'rgba(212,168,67,.5)':'rgba(34,197,94,.5)';

    var b=document.createElement('div');
    b.id='_rpNotif_'+r.key;
    b.style.cssText='position:fixed;bottom:148px;right:16px;z-index:99999;'
      +'background:#0f0f1a;border:1px solid '+borderColor+';border-radius:12px;'
      +'overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.7);max-width:280px;'
      +'animation:_rpIn .25s ease;';

    b.innerHTML=
      /* progress bar */
      '<div id="_rpProg_'+r.key+'" style="height:3px;background:'+color+';width:100%;'
        +'transition:width '+BANNER_MS+'ms linear;"></div>'
      /* content */
      +'<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;">'
        +'<div style="flex:1;min-width:0">'
          +'<div style="color:'+color+';font-size:.6rem;margin-bottom:2px;font-weight:600">'+lbl+'</div>'
          +'<div style="color:#eee;font-size:.78rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:serif">'+esc(r.title||r.key)+'</div>'
          +(r.host?'<div style="color:#888;font-size:.58rem;margin-top:1px">@'+esc(r.host)+'</div>':'')
        +'</div>'
        +'<button onclick="window._rpJoin(\''+esc(r.key)+'\',\''+esc(r.title||r.key)+'\')" '
          +'style="background:rgba(34,197,94,.2);border:1px solid rgba(34,197,94,.5);color:#4ade80;'
          +'border-radius:8px;padding:6px 12px;font-size:.68rem;cursor:pointer;flex-shrink:0;font-weight:600">▶ '+joinLabel+'</button>'
        +'<button onclick="document.getElementById(\'_rpNotif_'+r.key+'\')?.remove()" '
          +'style="background:none;border:none;color:#555;cursor:pointer;font-size:.9rem;padding:0 2px;flex-shrink:0">✕</button>'
      +'</div>';

    document.body.appendChild(b);

    /* start progress bar animation */
    requestAnimationFrame(function(){
      var prog=document.getElementById('_rpProg_'+r.key);
      if(prog) prog.style.width='0%';
    });

    /* auto-dismiss */
    setTimeout(function(){
      var el=document.getElementById('_rpNotif_'+r.key);
      if(el){ el.style.transition='opacity .4s'; el.style.opacity='0'; setTimeout(function(){el.remove();},400); }
    }, BANNER_MS);
  }

  function poll(){
    var t=tok(); if(!t) return;
    /* Use DB-backed endpoint — survives restarts; fallback to memory-only */
    var headers={'Authorization':'Bearer '+t,'ngrok-skip-browser-warning':'1'};
    var p=fetch(\'/bank/api/rooms/status\',{headers:headers})
      .then(function(r){
        if(r.ok) return r.json();
        /* fallback to memory endpoint if status not found */
        return fetch(\'/bank/api/rooms/list\',{headers:headers}).then(function(r2){return r2.ok?r2.json():null;});
      });
    p.then(function(data){
      if(!data) return;
      var rooms=data.rooms||[];
      rooms.forEach(function(r){
        var myN=myName();
        var vis=r.mode==='public'||r.invited||(r.members&&r.members.indexOf(myN)!==-1);
        if(vis) notifyNew(r);
      });
      renderFAB(rooms);
      try{if(typeof window._updateHdrRooms==='function') window._updateHdrRooms(rooms);}catch(e){}
      try{
        if(typeof window._renderRoomsList==='function'){
          var orig=window._rpRenderFromApp;
          window._rpRenderFromApp=null;
          window._renderRoomsList(rooms);
          window._rpRenderFromApp=orig;
        }
      }catch(e){}
    }).catch(function(){});
  }

  /* expose poll globally so Social view can trigger it on open */
  window._rpPoll = poll;

  /* start after 1s, then every POLL_MS */
  setTimeout(function(){
    createFAB(); /* create immediately so user sees it */
    renderFAB([]); /* show "0 rooms" right away */
    poll();
    setInterval(poll,POLL_MS);
  },1000);
})();

// --- script block 4 ---
