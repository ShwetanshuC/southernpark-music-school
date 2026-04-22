(function () {
  "use strict";

  // Rendered pixel dimensions of each image container on the live site.
  var CONFIGS = {
    heroslide:           { desktop: [1440, 720], mobile: [375, 534] },
    galleryphoto:        { desktop: [260,  200], mobile: [375, 200] },
    facultymember:       { desktop: [240,  240], mobile: [375, 276] },
    homesection_about:   { desktop: [596,  288], mobile: [375, 288] },
    homesection_history: { desktop: [596,  384], mobile: [375, 384] },
    homesection:         { desktop: [596,  336], mobile: [375, 336] },
  };

  var PREVIEW_MAX_W = 460;
  var PREVIEW_MAX_IMG_H = 380; // max height for the full-image display

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

  // ── SVG icons ─────────────────────────────────────────────────────────────
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

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(
      "input[name='image_focal_y'], input[name$='-image_focal_y']," +
      "input[name='image_focal_y_mobile'], input[name$='-image_focal_y_mobile']"
    ).forEach(initPicker);
  });

  function initPicker(input) {
    if (input.dataset.focalInit) return;
    input.dataset.focalInit = "1";

    var form   = input.closest("form") || document;
    var vd     = getViewDims(input.name);
    var dims   = vd.dims;   // container dimensions [w, h] on the live site
    var imgNaturalAspect = 0; // set when image loads

    var fileSelectors = vd.isMobile ? MOBILE_FILE_SELECTORS : DESKTOP_FILE_SELECTORS;
    var imageFileInput = findFirst(form, fileSelectors);
    var imageUrlInput  = vd.isMobile ? null : findFirst(form, URL_INPUT_SELECTORS);

    var containerAspect = dims[0] / dims[1];
    var barColor = vd.isMobile ? "#2563eb" : "#C2410C";
    var barGlow  = vd.isMobile ? "rgba(37,99,235,0.5)" : "rgba(194,65,12,0.6)";

    // ── Build wrapper ──────────────────────────────────────────────────────
    var wrap = document.createElement("div");
    wrap.style.cssText = "margin-top:10px;";

    // ── Header ────────────────────────────────────────────────────────────
    var header = document.createElement("div");
    header.style.cssText = "display:flex;align-items:center;gap:8px;margin-bottom:7px;flex-wrap:wrap;";

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
    infoLabel.textContent = dims[0] + "\u00d7" + dims[1] + "px";

    var cropLabel = document.createElement("span");
    cropLabel.style.cssText = "font-size:10px;font-family:monospace;";

    function getCropFrac() {
      if (!imgNaturalAspect) return null;
      return imgNaturalAspect < containerAspect ? imgNaturalAspect / containerAspect : 1.0;
    }
    function updateCropLabel() {
      var cf = getCropFrac();
      if (cf === null) { cropLabel.textContent = ""; return; }
      var pct = Math.round(cf * 100);
      cropLabel.textContent = "\u2014 " + pct + "% of image height visible";
      cropLabel.style.color = pct < 50 ? "#C2410C" : "#5a4f49";
    }

    header.appendChild(deviceBadge);
    header.appendChild(infoLabel);
    header.appendChild(cropLabel);
    wrap.appendChild(header);

    // ── Preview container (shows FULL image, crop rect overlaid) ──────────
    // Height is determined by image aspect ratio once loaded; width is capped.
    var previewBox = document.createElement("div");
    previewBox.style.cssText = [
      "position:relative",
      "width:100%",
      "max-width:" + PREVIEW_MAX_W + "px",
      "background:#1a1714",
      "border:1px solid " + (vd.isMobile ? "#1e3050" : "#3a322c"),
      "border-radius:4px",
      "overflow:hidden",
      "cursor:ns-resize",
      "user-select:none", "-webkit-user-select:none",
    ].join(";");

    var previewImg = document.createElement("img");
    previewImg.style.cssText = [
      "display:block",
      "width:100%",
      "height:auto",       // natural aspect — full image visible
      "pointer-events:none",
    ].join(";");

    // Dimming overlays (outside the crop rectangle)
    var dimTop = document.createElement("div");
    dimTop.style.cssText = "position:absolute;left:0;right:0;top:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";
    var dimBot = document.createElement("div");
    dimBot.style.cssText = "position:absolute;left:0;right:0;bottom:0;background:rgba(0,0,0,0.55);pointer-events:none;z-index:1;";

    // Crop-window border lines
    var lineTop = document.createElement("div");
    lineTop.style.cssText = [
      "position:absolute", "left:0", "right:0", "height:2px",
      "background:" + barColor,
      "box-shadow:0 0 6px " + barGlow,
      "pointer-events:none", "z-index:2",
    ].join(";");
    var lineBot = document.createElement("div");
    lineBot.style.cssText = lineTop.style.cssText;

    // Drag handle (centered on crop rectangle)
    var handle = document.createElement("div");
    handle.style.cssText = [
      "position:absolute", "left:50%", "transform:translateX(-50%)",
      "background:" + barColor, "border-radius:8px",
      "width:52px", "height:18px",
      "display:flex", "align-items:center", "justify-content:center",
      "z-index:3", "pointer-events:none",
    ].join(";");
    handle.innerHTML = '<svg width="16" height="10" viewBox="0 0 16 10" fill="none"><path d="M2 3.5h12M2 6.5h12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

    // Position badge
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
      "text-align:center", "padding:0 16px", "min-height:80px",
    ].join(";");
    placeholder.textContent = "Upload an image above to see the preview";

    previewBox.appendChild(previewImg);
    previewBox.appendChild(placeholder);
    previewBox.appendChild(dimTop);
    previewBox.appendChild(dimBot);
    previewBox.appendChild(lineTop);
    previewBox.appendChild(lineBot);
    previewBox.appendChild(handle);
    previewBox.appendChild(badge);

    var hint = document.createElement("p");
    hint.style.cssText = "margin:5px 0 0;font-size:11px;color:#8c7d74;";
    hint.textContent = "Drag up or down — the highlighted area between the lines is what visitors see on " +
      (vd.isMobile ? "mobile" : "desktop") + ".";

    wrap.appendChild(previewBox);
    wrap.appendChild(hint);

    var row = input.closest(".form-row") || input.parentNode;
    row.parentNode.insertBefore(wrap, row.nextSibling);

    // ── Core: apply focal point ────────────────────────────────────────────
    // cropFrac = fraction of image height that is visible in the container.
    // When the image is wider than the container aspect, the full height is shown (cropFrac=1).
    // When the image is taller (more portrait) than the container, only a portion is shown.
    //
    // CSS object-position: center Y% semantics:
    //   The image is scaled so that the narrower axis fills the container.
    //   Y% of the (image height in preview) aligns with Y% of the container height.
    //   Equivalently: cropTop (in image coords) = focal_y/100 * (imgH - containerH_in_img_coords)
    //
    // In our preview (full image shown):
    //   fullH = previewBox.clientHeight  (= natural image height scaled to preview width)
    //   cropH = fullH * cropFrac
    //   cropTop = (focal_y/100) * (fullH - cropH)

    function applyFocal(pct) {
      pct = Math.max(0, Math.min(100, pct));
      var cf = getCropFrac();
      if (cf === null) return; // no image loaded yet

      var fullH = previewBox.clientHeight;
      if (!fullH) return;

      var cropH   = Math.round(fullH * cf);
      var cropTop = Math.round((pct / 100) * (fullH - cropH));
      var cropBot = cropTop + cropH;

      dimTop.style.height  = cropTop + "px";
      dimBot.style.height  = (fullH - cropBot) + "px";
      lineTop.style.top    = cropTop + "px";
      lineBot.style.top    = (cropBot - 2) + "px";
      handle.style.top     = (cropTop + Math.round(cropH / 2) - 9) + "px";

      badge.textContent =
        pct < 15 ? "Top" : pct < 35 ? "Upper" : pct < 65 ? "Center" : pct < 85 ? "Lower" : "Bottom";
    }

    function setFocal(pct) {
      pct = Math.round(Math.max(0, Math.min(100, pct)));
      input.value = pct;
      applyFocal(pct);
    }

    // Convert a clientY mouse/touch position → focal_y percentage
    // Click-to-center: we want the crop window to center on the click point.
    //   focal_y = clamp( (y_in_img - cropH/2) / (fullH - cropH) * 100, 0, 100 )
    function pctFromEvent(e) {
      var rect = previewBox.getBoundingClientRect();
      var clientY = e.touches ? e.touches[0].clientY : e.clientY;
      var yInImg = clientY - rect.top;
      var cf = getCropFrac();
      if (cf === null || cf >= 1) return (yInImg / rect.height) * 100;
      var cropH = rect.height * cf;
      var denom = rect.height - cropH;
      if (denom <= 0) return 50;
      return ((yInImg - cropH / 2) / denom) * 100;
    }

    // ── Drag ──────────────────────────────────────────────────────────────
    var dragging = false;
    previewBox.addEventListener("mousedown",  function (e) { dragging = true; setFocal(pctFromEvent(e)); e.preventDefault(); });
    document.addEventListener("mousemove",    function (e) { if (dragging) setFocal(pctFromEvent(e)); });
    document.addEventListener("mouseup",      function ()  { dragging = false; });
    previewBox.addEventListener("touchstart", function (e) { dragging = true; setFocal(pctFromEvent(e)); e.preventDefault(); }, { passive: false });
    document.addEventListener("touchmove",    function (e) { if (dragging) setFocal(pctFromEvent(e)); }, { passive: true });
    document.addEventListener("touchend",     function ()  { dragging = false; });

    // ── Image load ────────────────────────────────────────────────────────
    previewImg.addEventListener("load", function () {
      var IW = previewImg.naturalWidth, IH = previewImg.naturalHeight;
      if (!IW || !IH) return;
      imgNaturalAspect = IW / IH;

      // Cap preview height
      var previewW = Math.min(previewBox.parentElement ? previewBox.parentElement.clientWidth : PREVIEW_MAX_W, PREVIEW_MAX_W);
      var naturalH = previewW / imgNaturalAspect;
      if (naturalH > PREVIEW_MAX_IMG_H) {
        // constrain: set explicit height and use object-fit to show full image scaled down
        previewImg.style.height = PREVIEW_MAX_IMG_H + "px";
        previewImg.style.objectFit = "contain";
        previewImg.style.objectPosition = "center top";
        previewImg.style.background = "#1a1714";
      } else {
        previewImg.style.height = "";
        previewImg.style.objectFit = "";
        previewImg.style.objectPosition = "";
      }

      updateCropLabel();
      // Defer applyFocal one tick so the DOM height has settled
      setTimeout(function () { applyFocal(parseInt(input.value) || 50); }, 0);
    });

    previewImg.addEventListener("error", function () {
      previewImg.removeAttribute("src");
      previewImg.style.display = "none";
      placeholder.style.display = "flex";
      placeholder.textContent = "Image could not be loaded — try re-uploading.";
    });

    // ── Image source ──────────────────────────────────────────────────────
    function showImage(src) {
      if (!src) {
        previewImg.removeAttribute("src");
        previewImg.style.display = "none";
        placeholder.style.display = "flex";
        dimTop.style.height = "0"; dimBot.style.height = "0";
        lineTop.style.top = "-4px"; lineBot.style.top = "-4px";
        handle.style.top = "-20px";
        badge.textContent = "";
        return;
      }
      previewImg.src = src;
      previewImg.style.display = "block";
      placeholder.style.display = "none";
    }

    // Desktop file/URL inputs used as fallback for mobile pickers with no mobile image.
    var desktopFileInput = vd.isMobile ? findFirst(form, DESKTOP_FILE_SELECTORS) : null;
    var desktopUrlInput  = vd.isMobile ? findFirst(form, URL_INPUT_SELECTORS)    : null;

    function getUrlFromFileInput(fi) {
      if (!fi) return null;
      if (fi.files && fi.files.length) return URL.createObjectURL(fi.files[0]);
      // Only look inside the Django ClearableFileInput wrapper (p.file-upload).
      // Falling back to parentElement risks picking up unrelated admin nav links.
      var c = fi.closest("p.file-upload") || fi.closest(".field-box");
      if (c) {
        var a = c.querySelector("a[href]");
        if (a && a.href && a.href !== window.location.href) return a.href;
      }
      return null;
    }

    function getCurrentImageUrl() {
      // Primary source: mobile-specific file input (or desktop file input for desktop pickers)
      var url = getUrlFromFileInput(imageFileInput);
      if (url) return url;
      // URL text field
      if (imageUrlInput && imageUrlInput.value.trim()) return imageUrlInput.value.trim();
      // Fallback for mobile pickers: show desktop image so crop preview is never blank
      if (vd.isMobile) {
        var fallback = getUrlFromFileInput(desktopFileInput);
        if (fallback) return fallback;
        if (desktopUrlInput && desktopUrlInput.value.trim()) return desktopUrlInput.value.trim();
      }
      return null;
    }

    if (imageFileInput) imageFileInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    if (imageUrlInput)  imageUrlInput.addEventListener("input",   function () { showImage(getCurrentImageUrl()); });
    // Re-render mobile preview when the desktop image changes (fallback path)
    if (vd.isMobile && desktopFileInput) desktopFileInput.addEventListener("change", function () { showImage(getCurrentImageUrl()); });
    if (vd.isMobile && desktopUrlInput)  desktopUrlInput.addEventListener("input",   function () { showImage(getCurrentImageUrl()); });

    // ── Init ──────────────────────────────────────────────────────────────
    showImage(getCurrentImageUrl());
  }

})();
