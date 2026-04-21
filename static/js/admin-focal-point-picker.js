(function () {
  "use strict";

  // Rendered pixel dimensions of each image container on the live site.
  // desktop: 1440×900 viewport | mobile: 375×667 (iPhone SE)
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

  // Maps focal_y field name → which view to use for that picker
  // Fields ending in _mobile use the mobile viewport; others use desktop.
  function getViewDims(inputName) {
    var isMobile = inputName.indexOf("_mobile") !== -1;
    var cfg = detectModelConfig();
    return { dims: cfg[isMobile ? "mobile" : "desktop"], isMobile: isMobile };
  }

  function detectModelConfig() {
    var path = window.location.pathname.toLowerCase();
    if (path.indexOf("heroslide")     !== -1) return CONFIGS.heroslide;
    if (path.indexOf("galleryphoto")  !== -1) return CONFIGS.galleryphoto;
    if (path.indexOf("facultymember") !== -1) return CONFIGS.facultymember;
    if (path.indexOf("homesection")   !== -1) {
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

  function boxSize(dims) {
    var aspect = dims[0] / dims[1];
    var w = PREVIEW_MAX_W, h = Math.round(w / aspect);
    if (h > PREVIEW_MAX_H) { h = PREVIEW_MAX_H; w = Math.round(h * aspect); }
    return [w, h];
  }

  // File input selectors keyed by whether this is a mobile field
  var DESKTOP_FILE_SELECTORS = [
    "input[type='file'][name='image']",
    "input[type='file'][name='photo']",
    "input[type='file'][name$='-image']",
  ];
  var MOBILE_FILE_SELECTORS = [
    "input[type='file'][name='image_mobile']",
    "input[type='file'][name='photo_mobile']",
    "input[type='file'][name$='-image_mobile']",
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
      "input[name='image_focal_y'], input[name$='-image_focal_y']," +
      "input[name='image_focal_y_mobile'], input[name$='-image_focal_y_mobile']"
    ).forEach(initPicker);
  });

  // ── SVG icons ────────────────────────────────────────────────────────────
  var ICON_DESKTOP = [
    '<svg width="13" height="10" viewBox="0 0 13 10" fill="none">',
    '<rect x="0.5" y="0.5" width="12" height="7.5" rx="1" stroke="currentColor" stroke-width="1.1"/>',
    '<path d="M4 9.5H9M6.5 8V9.5" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>',
    '</svg>',
  ].join("");
  var ICON_MOBILE = [
    '<svg width="7" height="12" viewBox="0 0 7 12" fill="none">',
    '<rect x="0.5" y="0.5" width="6" height="11" rx="1.5" stroke="currentColor" stroke-width="1.1"/>',
    '<circle cx="3.5" cy="9.5" r="0.75" fill="currentColor"/>',
    '</svg>',
  ].join("");

  function initPicker(input) {
    if (input.dataset.focalInit) return;
    input.dataset.focalInit = "1";

    var form   = input.closest("form") || document;
    var vd     = getViewDims(input.name);     // { dims:[w,h], isMobile:bool }
    var dims   = vd.dims;
    var sz     = boxSize(dims);
    var imgNaturalAspect = 0;

    var fileSelectors = vd.isMobile ? MOBILE_FILE_SELECTORS : DESKTOP_FILE_SELECTORS;
    var imageFileInput = findFirst(form, fileSelectors);
    // Only look for image_url on desktop pickers (hero slides with URL option)
    var imageUrlInput  = vd.isMobile ? null : findFirst(form, URL_INPUT_SELECTORS);

    function getContainerAspect() { return dims[0] / dims[1]; }
    function getCropFrac() {
      if (!imgNaturalAspect) return 0.6;
      var ca = getContainerAspect();
      return imgNaturalAspect < ca ? imgNaturalAspect / ca : 1.0;
    }

    // ── Build wrapper ────────────────────────────────────────────────────
    var wrap = document.createElement("div");
    wrap.style.cssText = "margin-top:10px;";

    // ── Header row: label + dimensions + crop-% ──────────────────────────
    var header = document.createElement("div");
    header.style.cssText = [
      "display:flex", "align-items:center", "gap:8px",
      "margin-bottom:7px", "flex-wrap:wrap",
    ].join(";");

    var deviceBadge = document.createElement("span");
    deviceBadge.style.cssText = [
      "display:inline-flex", "align-items:center", "gap:5px",
      "padding:4px 10px", "border-radius:4px",
      "font-size:11px", "font-weight:700", "letter-spacing:0.05em",
      "background:" + (vd.isMobile ? "#1a2a3a" : "#1e1814"),
      "border:1px solid " + (vd.isMobile ? "#2a4a6a" : "#3a2a20"),
      "color:" + (vd.isMobile ? "#60a5fa" : "#fb923c"),
    ].join(";");
    deviceBadge.innerHTML = (vd.isMobile ? ICON_MOBILE : ICON_DESKTOP) +
      "<span>" + (vd.isMobile ? "Mobile" : "Desktop") + "</span>";

    var infoLabel = document.createElement("span");
    infoLabel.style.cssText = "font-size:10px;color:#5a4f49;font-family:monospace;";
    infoLabel.textContent = dims[0] + "×" + dims[1] + "px";

    var cropLabel = document.createElement("span");
    cropLabel.style.cssText = "font-size:10px;font-family:monospace;";

    function updateCropLabel() {
      var pct = Math.round(getCropFrac() * 100);
      cropLabel.textContent = "— " + pct + "% of image height visible";
      cropLabel.style.color = pct < 50 ? "#C2410C" : "#5a4f49";
    }
    updateCropLabel();

    header.appendChild(deviceBadge);
    header.appendChild(infoLabel);
    header.appendChild(cropLabel);
    wrap.appendChild(header);

    // ── Preview box ───────────────────────────────────────────────────────
    var previewBox = document.createElement("div");
    previewBox.style.cssText = [
      "position:relative", "width:100%",
      "max-width:" + sz[0] + "px",
      "height:" + sz[1] + "px",
      "background:#1a1714",
      "border:1px solid " + (vd.isMobile ? "#1e3050" : "#3a322c"),
      "border-radius:4px",
      "overflow:hidden", "cursor:ns-resize",
      "user-select:none", "-webkit-user-select:none",
    ].join(";");

    var previewImg = document.createElement("img");
    previewImg.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;pointer-events:none;";

    var shadeTop = document.createElement("div");
    shadeTop.style.cssText = "position:absolute;left:0;right:0;top:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";

    var shadeBot = document.createElement("div");
    shadeBot.style.cssText = "position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";

    var barColor = vd.isMobile ? "#2563eb" : "#C2410C";
    var barGlow  = vd.isMobile ? "rgba(37,99,235,0.6)" : "rgba(194,65,12,0.7)";

    var barTop = document.createElement("div");
    barTop.style.cssText = [
      "position:absolute", "left:0", "right:0", "height:3px",
      "background:" + barColor, "pointer-events:none", "z-index:2",
      "box-shadow:0 0 6px " + barGlow,
    ].join(";");

    var barBot = document.createElement("div");
    barBot.style.cssText = barTop.style.cssText;

    var handle = document.createElement("div");
    handle.style.cssText = [
      "position:absolute", "left:50%", "transform:translateX(-50%)",
      "background:" + barColor, "border-radius:8px",
      "width:52px", "height:18px",
      "display:flex", "align-items:center", "justify-content:center",
      "z-index:3", "pointer-events:none",
    ].join(";");
    handle.innerHTML = '<svg width="16" height="10" viewBox="0 0 16 10" fill="none"><path d="M2 3.5h12M2 6.5h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

    var badge = document.createElement("div");
    badge.style.cssText = [
      "position:absolute", "right:8px", "top:8px",
      "background:" + barColor, "color:#fff",
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
    hint.style.cssText = "margin:5px 0 0;font-size:11px;color:#8c7d74;";
    hint.textContent = "Drag up or down — the area between the bars is what visitors see on " +
      (vd.isMobile ? "mobile" : "desktop") + ".";

    wrap.appendChild(previewBox);
    wrap.appendChild(hint);

    var row = input.closest(".form-row") || input.parentNode;
    row.parentNode.insertBefore(wrap, row.nextSibling);

    // ── Focal application ─────────────────────────────────────────────────
    function applyFocal(pct) {
      pct = Math.max(0, Math.min(100, pct));
      var BOX_H = previewBox.clientHeight || sz[1];
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

    // ── Image load ────────────────────────────────────────────────────────
    previewImg.addEventListener("load", function () {
      var IW = previewImg.naturalWidth, IH = previewImg.naturalHeight;
      if (!IW || !IH) return;
      imgNaturalAspect = IW / IH;
      updateCropLabel();
      applyFocal(parseInt(input.value) || 50);
    });

    // ── Drag ─────────────────────────────────────────────────────────────
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

    // ── Image source ──────────────────────────────────────────────────────
    function showImage(src) {
      if (!src) {
        previewImg.removeAttribute("src"); previewImg.style.display = "none";
        placeholder.style.display = "flex"; return;
      }
      previewImg.src = src; previewImg.style.display = "block";
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

    // ── Init ──────────────────────────────────────────────────────────────
    showImage(getCurrentImageUrl());
    applyFocal(parseInt(input.value) || 50);
  }

})();
