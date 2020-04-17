(function () {
  // We monkey patch Leaflet to make it work with django-pipeline cached storage
  // not a fancy solution, but it works.
  // see: https://github.com/makinacorpus/django-leaflet/issues/188

  function getStyle(el, style) {
    var value = el.style[style] || (el.currentStyle && el.currentStyle[style]);

    if ((!value || value === 'auto') && document.defaultView) {
      var css = document.defaultView.getComputedStyle(el, null);
      value = css ? css[style] : null;
    }
    return value === 'auto' ? null : value;
  }

  function create$1(tagName, className, container) {
    var el = document.createElement(tagName);
    el.className = className || '';

    if (container) {
      container.appendChild(el);
    }
    return el;
  }

  L.Icon.Default.prototype._detectIconPath = function () {
    var el = create$1('div', 'leaflet-default-icon-path', document.body);
    var path =
      getStyle(el, 'background-image') || getStyle(el, 'backgroundImage'); // IE8

    document.body.removeChild(el);

    if (path === null || path.indexOf('url') !== 0) {
      path = '';
    } else {
      path = path
        .replace(/^url\([\"\']?/, '')
        .replace(/marker-icon[\.[a-zA-Z0-9]*\.png[\"\']?\)$/, '');
    }

    return path;
  };
})();
