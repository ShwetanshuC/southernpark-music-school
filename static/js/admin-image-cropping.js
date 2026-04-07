(function($) {
  "use strict";

  function getCropField($fileInput) {
    var fieldName = $fileInput.data("field-name");
    return $("input.image-ratio").filter(function() {
      var $this = $(this);
      return $this
        .attr("name")
        .replace($this.data("my-name"), $this.data("image-field")) === fieldName;
    }).first();
  }

  function unhideCropField($cropField) {
    if (!$cropField.length) {
      return;
    }
    $cropField.show();
    $cropField.parents("div.form-row:first").show();
  }

  function destroyExistingCrop(imageId) {
    if (!imageId) {
      return;
    }
    var existing = image_cropping.jcrop[imageId];
    if (existing && typeof existing.destroy === "function") {
      existing.destroy();
      delete image_cropping.jcrop[imageId];
    }
    $("#" + imageId).remove();
  }

  function refreshCroppingForFile($fileInput) {
    var $cropField = getCropField($fileInput);
    if (!$cropField.length) {
      return;
    }

    var file = $fileInput[0].files && $fileInput[0].files[0];
    if (!file) {
      return;
    }

    var reader = new FileReader();
    reader.onload = function(event) {
      var thumbnailUrl = event.target.result;
      var previewImage = new Image();
      previewImage.onload = function() {
        var width = previewImage.naturalWidth || previewImage.width;
        var height = previewImage.naturalHeight || previewImage.height;

        $fileInput
          .data("thumbnail-url", thumbnailUrl)
          .data("org-width", width)
          .data("org-height", height)
          .data("max-width", width)
          .data("max-height", height);

        unhideCropField($cropField);

        var imageId = $cropField.attr("id") + "-image";
        destroyExistingCrop(imageId);
        image_cropping.init();
      };
      previewImage.src = thumbnailUrl;
    };
    reader.readAsDataURL(file);
  }

  $(document).on("change", "input.crop-thumb[type=file]", function() {
    refreshCroppingForFile($(this));
  });
})(jQuery);
