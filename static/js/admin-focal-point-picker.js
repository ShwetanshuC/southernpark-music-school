(function () {
  "use strict";

  // Actual rendered pixel dimensions of each image container on the live site.
  // desktop: 1440×900 viewport  |  mobile: 375×667 (iPhone SE / common reference)
  // Derived from the site's CSS:
  //   hero:    100vw × 80vh  → 1440×720 desktop, 375×534 mobile
  //   about:   md:grid-cols-2 col × h-72  → 596×288 desktop, 375×288 mobile
  //   history: md:grid-cols-2 col × h-96  → 596×384 desktop, 375×384 mobile
  //   gallery: auto-fill grid min 220px × 200px  → 260×200 desk, 375×200 mobile (1-col)
  //   faculty: auto-fill grid min 220px, card 400px tall, photo 60%  → 240×240 desk, 375×276 mobile
  var CONFIGS = {
    heroslide:           { desktop: [1440, 720], mobile: [375, 534] },
    galleryphoto:        { desktop: [260,  200], mobile: [375, 200] },
    facultymember:       { desktop: [240,  240], mobile: [375, 276] },
    homesection_about:   { desktop: [596,  288], mobile: [375, 288] },
    homesection_history: { desktop: [596,  384], mobile: [375, 384] },
    homesection:         { desktop: [596,  336], mobile: [375, 336] },
  };

  var PREVIEW_MAX_W = 460;
  var PREVIEW_MAX_H = 260;

  function getConfig() {
    var path = window.location.pathname.toLowerCase();
    if (path.indexOf("heroslide")     !== -1) return CONFIGS.heroslide;
    if (path.indexOf("galleryphoto")  !== -1) return CONFIGS.galleryphoto;
    if (path.indexOf("facultymember") !== -1) return CONFIGS.facultymember;
    if (path.indexOf("homesection")   !== -1) {
      // Detect section type from readonly field rendered by Django admin
      var el = document.querySelector(".field-section_type .readonly, .field-section_type p.readonly");
      if (el) {
        var t = el.textContent.trim().toLowerCase();
        if (t.indexOf("history") !== -1) return CONFIGS.homesection_history;
        if (t.indexOf("about")   !== -1) return CONFIGS.homesection_about;
      }
      return CONFIGS.homesection;
    }
    return CONFIGS.heroslide;
  }

  // Compute preview box pixel size that fits within PREVIEW_MAX_W × PREVIEW_MAX_H
  function boxSize(dims) {
    var aspect = dims[0] / dims[1];
    var w = PREVIEW_MAX_W;
    var h = Math.round(w / aspect);
    if (h > PREVIEW_MAX_H) { h = PREVIEW_MAX_H; w = Math.round(h * aspect); }
    return [w, h];
  }

  var FILE_INPUT_SELECTORS = [
    "input[type='file'][name='image']",
    "input[type='file'][name='photo']",
    "input[type='file'][name$='-image']",
    "input[type='file'][name$='_image_file']",
  ];
  var URL_INPUT_SELECTORS = [
    "input[name='image_url']",
    "input[name$='-image_url']",
  ];

  function findFirst(container, selectors) {
    for (var i = 0; i < selectors.length; i++) {
      var el = container.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(
      "input[name='image_focal_y'], input[name$='-image_focal_y']"
    ).forEach(initPicker);
  });

  // SVG icons
  var ICON_DESKTOP = [
    '<svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">',
    '<rect x="0.5" y="0.5" width="13" height="8" rx="1" stroke="currentColor" stroke-width="1.1"/>',
    '<path d="M4.5 10.5H9.5M7 9V10.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>',
    '</svg>',
  ].join("");
  var ICON_MOBILE = [
    '<svg width="8" height="13" viewBox="0 0 8 13" fill="none" xmlns="http://www.w3.org/2000/svg">',
    '<rect x="0.5" y="0.5" width="7" height="12" rx="1.5" stroke="currentColor" stroke-width="1.1"/>',
    '<circle cx="4" cy="10.5" r="0.8" fill="currentColor"/>',
    '</svg>',
  ].join("");

  function initPicker(input) {
    if (input.dataset.focalInit) return;
    input.dataset.focalInit = "1";

    var form = input.closest("form") || document;
    var config = getConfig();
    var currentView = "desktop";
    var imgNaturalAspect = 0; // set once image loads

    var imageFileInput = findFirst(form, FILE_INPUT_SELECTORS);
    var imageUrlInput  = findFirst(form, URL_INPUT_SELECTORS);

    // Compute fraction of the image height that's visible in the current viewport
    function getCropFrac() {
      if (!imgNaturalAspect) return 0.6; // placeholder before image loads
      var ca = config[currentView][0] / config[currentView][1];
      return imgNaturalAspect < ca ? imgNaturalAspect / ca : 1.0;
    }

    // ── Outer wrapper ────────────────────────────────────────────────
    var wrap = document.createElement("div");
    wrap.style.cssText = "margin-top:10px;";

    // ── Toggle bar ───────────────────────────────────────────────────
    var toggleBar = document.createElement("div");
    toggleBar.style.cssText = "display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap;";

    var viewLabel = document.createElement("span");
    viewLabel.style.cssText = [
      "font-size:10px", "font-weight:700", "letter-spacing:0.07em",
      "text-transform:uppercase", "color:#5a4f49", "margin-right:2px",
    ].join(";");
    viewLabel.textContent = "Preview:";

    function makeViewBtn(view, label, iconHtml) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.setAttribute("data-view", view);
      btn.style.cssText = [
        "display:inline-flex", "align-items:center", "gap:5px",
        "padding:5px 11px", "border-radius:4px",
        "font-size:11px", "font-weight:600", "letter-spacing:0.04em",
        "cursor:pointer", "border:1px solid #3a322c",
        "background:#201d1a", "color:#a89284",
        "transition:background 0.12s,color 0.12s,border-color 0.12s",
      ].join(";");
      btn.innerHTML = iconHtml + "<span>" + label + "</span>";
      btn.addEventListener("click", function () { switchView(view); });
      return btn;
    }

    var btnDesktop = makeViewBtn("desktop", "Desktop", ICON_DESKTOP);
    var btnMobile  = makeViewBtn("mobile",  "Mobile",  ICON_MOBILE);

    // Dimension + crop-fraction label
    var infoLabel = document.createElement("span");
    infoLabel.style.cssText = "font-size:10px;color:#5a4f49;margin-left:4px;font-family:monospace;white-space:nowrap;";

    toggleBar.appendChild(viewLabel);
    toggleBar.appendChild(btnDesktop);
    toggleBar.appendChild(btnMobile);
    toggleBar.appendChild(infoLabel);
    wrap.appendChild(toggleBar);

    // ── Preview box ───────────────────────────────────────────────────
    var previewBox = document.createElement("div");
    previewBox.style.cssText = [
      "position:relative", "width:100%",
      "background:#1a1714", "border:1px solid #3a322c", "border-radius:4px",
      "overflow:hidden", "cursor:ns-resize",
      "user-select:none", "-webkit-user-select:none",
      "transition:max-width 0.2s ease, height 0.2s ease",
    ].join(";");

    var previewImg = document.createElement("img");
    previewImg.style.cssText = [
      "width:100%", "height:100%", "object-fit:cover",
      "display:block", "pointer-events:none",
    ].join(";");

    var shadeTop = document.createElement("div");
    shadeTop.style.cssText = [
      "position:absolute", "left:0", "right:0", "top:0",
      "background:rgba(0,0,0,0.55)", "pointer-events:none", "z-index:1",
    ].join(";");

    var shadeBot = document.createElement("div");
    shadeBot.style.cssText = [
      "position:absolute", "left:0", "right:0", "bottom:0",
      "background:rgba(0,0,0,0.55)", "pointer-events:none", "z-index:1",
    ].join(";");

    var barTop = document.createElement("div");
    barTop.style.cssText = [
      "position:absolute", "left:0", "right:0", "height:3px",
      "background:#C2410C", "pointer-events:none", "z-index:2",
      "box-shadow:0 0 6px rgba(194,65,12,0.7)",
    ].join(";");

    var barBot = document.createElement("div");
    barBot.style.cssText = barTop.style.cssText;

    var handle = document.createElement("div");
    handle.style.cssText = [
      "position:absolute", "left:50%", "transform:translateX(-50%)",
      "background:#C2410C", "border-radius:8px",
      "width:52px", "height:18px",
      "display:flex", "align-items:center", "justify-content:center",
      "z-index:3", "pointer-events:none",
    ].join(";");
    handle.innerHTML = [
      '<svg width="16" height="10" viewBox="0 0 16 10" fill="none">',
      '<path d="M2 3.5h12M2 6.5h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>',
      "</svg>",
    ].join("");

    var badge = document.createElement("div");
    badge.style.cssText = [
      "position:absolute", "right:8px", "top:8px",
      "background:#C2410C", "color:#fff",
      "font-size:10px", "font-weight:700", "letter-spacing:0.08em",
      "text-transform:uppercase", "padding:3px 8px", "border-radius:3px",
      "z-index:4", "pointer-events:none",
    ].join(";");

    var placeholder = document.createElement("div");
    placeholder.style.cssText = [
      "position:absolute", "inset:0",
      "display:flex", "align-items:center", "justify-content:center",
      "color:#5a4f49", "font-size:11px", "font-weight:600",
      "letter-spacing:0.06em", "text-transform:uppercase",
      "text-align:center", "padding:0 16px", "z-index:0",
    ].join(";");
    placeholder.textContent = "Upload an image above to see the preview";

    previewBox.appendChild(previewImg);
    previewBox.appendChild(placeholder);
    previewBox.appendChild(shadeTop);
    previewBox.appendChild(shadeBot);
    previewBox.appendChild(barTop);
    previewBox.appendChild(barBot);
    previewBox.appendChild(handle);
    previewBox.appendChild(badge);

    var hint = document.createElement("p");
    hint.style.cssText = "margin:6px 0 0;font-size:11px;color:#8c7d74;";
    hint.textContent = "Drag up or down to set focal point. The area between the orange bars is what visitors see on each device.";

    wrap.appendChild(previewBox);
    wrap.appendChild(hint);

    var row = input.closest(".form-row") || input.parentNode;
    row.parentNode.insertBefore(wrap, row.nextSibling);

    // ── View switch ───────────────────────────────────────────────────
    function updateInfoLabel() {
      var dims = config[currentView];
      var frac = getCropFrac();
      var pct = Math.round(frac * 100);
      infoLabel.textContent = dims[0] + "×" + dims[1] + "px — " + pct + "% of image height visible";
      // Warn when very little is visible (heavy crop)
      infoLabel.style.color = pct < 50 ? "#C2410C" : "#5a4f49";
    }

    function switchView(view) {
      currentView = view;
      // Resize preview box
      var sz = boxSize(config[view]);
      previewBox.style.maxWidth = sz[0] + "px";
      previewBox.style.height   = sz[1] + "px";
      // Button active states
      [btnDesktop, btnMobile].forEach(function (b) {
        var active = b.getAttribute("data-view") === view;
        b.style.background  = active ? "#C2410C" : "#201d1a";
        b.style.borderColor = active ? "#C2410C" : "#3a322c";
        b.style.color       = active ? "#fff"    : "#a89284";
      });
      updateInfoLabel();
      applyFocal(parseInt(input.value) || 50);
    }

    // ── Focal point application ───────────────────────────────────────
    function applyFocal(pct) {
      pct = Math.max(0, Math.min(100, pct));
      var BOX_H = previewBox.clientHeight || parseInt(previewBox.style.height) || 200;
      var cropF = getCropFrac();
      var windowH = Math.max(4, Math.round(BOX_H * cropF));
      var half    = Math.round(windowH / 2);
      var centerPx = Math.round((pct / 100) * BOX_H);
      centerPx = Math.max(half, Math.min(BOX_H - half, centerPx));
      var topPx = centerPx - half;
      var botPx = centerPx + half;

      shadeTop.style.height = topPx + "px";
      barTop.style.top      = topPx + "px";
      shadeBot.style.height = (BOX_H - botPx) + "px";
      barBot.style.top      = (botPx - 3) + "px";
      handle.style.top      = (centerPx - 9) + "px";
      previewImg.style.objectPosition = "center " + pct + "%";

      badge.textContent =
        pct < 15 ? "Top" : pct < 35 ? "Upper" : pct < 65 ? "Center" : pct < 85 ? "Lower" : "Bottom";
    }

    function setFocal(pct) {
      pct = Math.round(Math.max(0, Math.min(100, pct)));
      input.value = pct;
      applyFocal(pct);
    }

    // ── Image load → recalculate crop fraction ────────────────────────
    previewImg.addEventListener("load", function () {
      var IW = previewImg.naturalWidth, IH = previewImg.naturalHeight;
      if (!IW || !IH) return;
      imgNaturalAspect = IW / IH;
      updateInfoLabel();
      applyFocal(parseInt(input.value) || 50);
    });

    // ── Drag ─────────────────────────────────────────────────────────
    var dragging = false;
    function pctFromEvent(e) {
      var rect = previewBox.getBoundingClientRect();
      var clientY = e.touches ? e.touches[0].clientY : e.clientY;
      return ((clientY - rect.top) / rect.height) * 100;
    }
    previewBox.addEventListener("mousedown",  function (e) { dragging = true; setFocal(pctFromEvent(e)); e.preventDefault(); });
    document.addEventListener("mousemove",    function (e) { if (dragging) setFocal(pctFromEvent(e)); });
    document.addEventListener("mouseup",      function ()  { dragging = false; });
    previewBox.addEventListener("touchstart", function (e) { dragging = true; setFocal(pctFromEvent(e)); e.preventDefault(); }, { passive: false });
    document.addEventListener("touchmove",    function (e) { if (dragging) setFocal(pctFromEvent(e)); }, { passive: true });
    document.addEventListener("touchend",     function ()  { dragging = false; });

    // ── Image source resolution ────────────────────────────────────────
    function showImage(src) {
      if (!src) {
        previewImg.removeAttribute("src");
        previewImg.style.display = "none";
        placeholder.style.display = "flex";
        return;
      }
      previewImg.src = src;
      previewImg.style.display = "block";
      placeholder.style.display = "none";
    }

    function getCurrentImageUrl() {
      if (imageFileInput && imageFileInput.files && imageFileInput.files.length)
        return URL.createObjectURL(imageFileInput.files[0]);
      if (imageFileInput) {
        var c = imageFileInput.closest("p.file-upload")
             || imageFileInput.closest(".field-box")
             || imageFileInput.parentElement;
        if (c) {
          var a = c.querySelector("a[href]");
          if (a && a.href && a.href !== window.location.href) return a.href;
        }
      }
      if (imageUrlInput && imageUrlInput.value.trim()) return imageUrlInput.value.trim();
      return null;
    }

    if (imageFileInput) imageFileInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    if (imageUrlInput)  imageUrlInput.addEventListener("input",   function () { showImage(getCurrentImageUrl()); });

    // ── Init ──────────────────────────────────────────────────────────
    switchView("desktop");
    showImage(getCurrentImageUrl());
  }

})();
