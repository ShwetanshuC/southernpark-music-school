(function () {
  "use strict";

  // Container aspect ratios (W/H) matching actual CSS display on site:
  //   heroslide   → 100vw × 80vh     ≈ 2:1
  //   homesection → ~580px × 288px   ≈ 2:1  (h-72 / h-96 half-grid)
  //   galleryphoto→ ~220px × 200px   ≈ 1.1:1
  //   facultymember→~220px × 240px   ≈ 0.92:1 (60% of 400px card)
  var CONTAINER_ASPECT = [
    { key: "heroslide",      aw: 16, ah: 8  },
    { key: "homesection",    aw: 2,  ah: 1  },
    { key: "galleryphoto",   aw: 11, ah: 10 },
    { key: "facultymember",  aw: 11, ah: 12 },
  ];

  function getContainerAspect() {
    var path = window.location.pathname.toLowerCase();
    for (var i = 0; i < CONTAINER_ASPECT.length; i++) {
      if (path.indexOf(CONTAINER_ASPECT[i].key) !== -1)
        return CONTAINER_ASPECT[i].aw / CONTAINER_ASPECT[i].ah;
    }
    return 1.5; // fallback
  }

  var FILE_INPUT_SELECTORS = [
    "input[type='file'][name='image']",
    "input[type='file'][name='photo']",
    "input[type='file'][name='image_file']",
    "input[type='file'][name$='-image']",
    "input[type='file'][name$='_image_file']",
  ];

  var URL_INPUT_SELECTORS = [
    "input[name='image_url']",
    "input[name$='-image_url']",
    "input[name$='_image_url']",
  ];

  function findFirst(container, selectors) {
    for (var i = 0; i < selectors.length; i++) {
      var el = container.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("input[name='image_focal_y'], input[name$='-image_focal_y']").forEach(initPicker);
  });

  function initPicker(input) {
    if (input.dataset.focalInit) return;
    input.dataset.focalInit = "1";

    var form = input.closest("form") || document;
    var containerAspect = getContainerAspect();

    // Compute preview box dimensions capped at 420×300
    var MAX_W = 420, MAX_H = 300;
    var rawH = Math.round(MAX_W / containerAspect);
    var BOX_W, BOX_H;
    if (rawH > MAX_H) {
      BOX_H = MAX_H;
      BOX_W = Math.round(MAX_H * containerAspect);
    } else {
      BOX_H = rawH;
      BOX_W = MAX_W;
    }

    // cropFrac will be recomputed when image loads; use fallback until then
    var cropFrac = 0.6;
    var WINDOW_H = Math.round(BOX_H * cropFrac);
    var HALF_W   = Math.round(WINDOW_H / 2);

    var imageFileInput = findFirst(form, FILE_INPUT_SELECTORS);
    var imageUrlInput  = findFirst(form, URL_INPUT_SELECTORS);

    // ── Build preview DOM ──────────────────────────────────────────────
    var wrap = document.createElement("div");
    wrap.style.cssText = "margin-top:10px;";

    var previewBox = document.createElement("div");
    previewBox.style.cssText = [
      "position:relative", "width:100%", "max-width:" + BOX_W + "px",
      "height:" + BOX_H + "px", "background:#1a1714",
      "border:1px solid #3a322c", "border-radius:4px",
      "overflow:hidden", "cursor:ns-resize",
      "user-select:none", "-webkit-user-select:none",
    ].join(";");

    var previewImg = document.createElement("img");
    previewImg.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;pointer-events:none;";

    var shadeTop = document.createElement("div");
    shadeTop.style.cssText = "position:absolute;left:0;right:0;top:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";

    var shadeBot = document.createElement("div");
    shadeBot.style.cssText = "position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";

    var barTop = document.createElement("div");
    barTop.style.cssText = [
      "position:absolute", "left:0", "right:0", "height:3px",
      "background:#C2410C", "pointer-events:none", "z-index:2",
      "box-shadow:0 0 6px rgba(194,65,12,0.7)",
    ].join(";");

    var barBot = document.createElement("div");
    barBot.style.cssText = [
      "position:absolute", "left:0", "right:0", "height:3px",
      "background:#C2410C", "pointer-events:none", "z-index:2",
      "box-shadow:0 0 6px rgba(194,65,12,0.7)",
    ].join(";");

    var handle = document.createElement("div");
    handle.style.cssText = [
      "position:absolute", "left:50%", "transform:translateX(-50%)",
      "background:#C2410C", "border-radius:8px",
      "width:52px", "height:18px",
      "display:flex", "align-items:center", "justify-content:center",
      "z-index:3", "pointer-events:none",
    ].join(";");
    handle.innerHTML = '<svg width="16" height="10" viewBox="0 0 16 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 3.5h12M2 6.5h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

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
    hint.textContent = "Drag up or down to set which part of the image is visible. The area between the orange bars is what visitors see.";

    wrap.appendChild(previewBox);
    wrap.appendChild(hint);

    var row = input.closest(".form-row") || input.parentNode;
    row.parentNode.insertBefore(wrap, row.nextSibling);

    // ── Focal application ──────────────────────────────────────────────
    function applyFocal(pct) {
      pct = Math.max(0, Math.min(100, pct));
      var centerPx = (pct / 100) * BOX_H;
      centerPx = Math.max(HALF_W, Math.min(BOX_H - HALF_W, centerPx));
      var topPx = centerPx - HALF_W;
      var botPx = centerPx + HALF_W;

      shadeTop.style.height = topPx + "px";
      barTop.style.top      = topPx + "px";
      shadeBot.style.height = (BOX_H - botPx) + "px";
      barBot.style.top      = (botPx - 3) + "px";
      handle.style.top      = (centerPx - 9) + "px";
      previewImg.style.objectPosition = "center " + pct + "%";

      if (pct < 15)      badge.textContent = "Top";
      else if (pct < 35) badge.textContent = "Upper";
      else if (pct < 65) badge.textContent = "Center";
      else if (pct < 85) badge.textContent = "Lower";
      else               badge.textContent = "Bottom";
    }

    function setFocal(pct) {
      pct = Math.round(Math.max(0, Math.min(100, pct)));
      input.value = pct;
      applyFocal(pct);
    }

    // ── Recompute cropFrac after image loads ───────────────────────────
    previewImg.addEventListener("load", function () {
      var IW = previewImg.naturalWidth;
      var IH = previewImg.naturalHeight;
      if (!IW || !IH) return;
      var imageAspect = IW / IH;
      // object-fit:cover: if image is narrower than container, scale by width → partial height visible
      if (imageAspect < containerAspect) {
        cropFrac = imageAspect / containerAspect;
      } else {
        cropFrac = 1.0; // landscape image fills full height
      }
      WINDOW_H = Math.max(4, Math.round(BOX_H * cropFrac));
      HALF_W   = Math.round(WINDOW_H / 2);
      applyFocal(parseInt(input.value) || 50);
    });

    // ── Drag interaction ───────────────────────────────────────────────
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
        var container = imageFileInput.closest("p.file-upload") || imageFileInput.closest(".field-box") || imageFileInput.parentElement;
        if (container) {
          var link = container.querySelector("a[href]");
          if (link && link.href && link.href !== window.location.href) return link.href;
        }
      }
      if (imageUrlInput && imageUrlInput.value.trim()) return imageUrlInput.value.trim();
      return null;
    }

    if (imageFileInput) imageFileInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    if (imageUrlInput)  imageUrlInput.addEventListener("input",   function () { showImage(getCurrentImageUrl()); });

    showImage(getCurrentImageUrl());
    applyFocal(parseInt(input.value) || 50);
  }

})();
