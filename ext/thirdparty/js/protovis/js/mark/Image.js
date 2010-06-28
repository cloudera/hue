/**
 * Constructs a new dot mark with default properties. Images are not typically
 * constructed directly, but by adding to a panel or an existing mark via
 * {@link pv.Mark#add}.
 *
 * @class Represents an image. Images share the same layout and style properties as
 * bars, in conjunction with an external image such as PNG or JPEG. The image is
 * specified via the {@link #url} property. The fill, if specified, appears
 * beneath the image, while the optional stroke appears above the image.
 *
 * <p>TODO Restore support for dynamic images (such as heatmaps). These were
 * supported in the canvas implementation using the pixel buffer API; although
 * SVG does not support pixel manipulation, it is possible to embed a canvas
 * element in SVG using foreign objects.
 *
 * <p>TODO Allow different modes of image placement: "scale" -- scale and
 * preserve aspect ratio, "tile" -- repeat the image, "center" -- center the
 * image, "fill" -- scale without preserving aspect ratio.
 *
 * <p>See {@link pv.Bar} for details on positioning properties.
 *
 * @extends pv.Bar
 */
pv.Image = function() {
  pv.Bar.call(this);
};

pv.Image.prototype = pv.extend(pv.Bar)
    .property("url");

pv.Image.prototype.type = "image";

/**
 * The URL of the image to display. The set of supported image types is
 * browser-dependent; PNG and JPEG are recommended.
 *
 * @type string
 * @name pv.Image.prototype.url
 */

/**
 * Default properties for images. By default, there is no stroke or fill style.
 *
 * @type pv.Image
 */
pv.Image.prototype.defaults = new pv.Image()
    .extend(pv.Bar.prototype.defaults)
    .fillStyle(null);
