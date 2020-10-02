// script to support the templates/donation_center/list.html file
(function () {
  var GEO_URL = "/api/v1/donationcentersgeo/";
  var LIST_URL = "/donaciones/";
  var LIST_BY_CITY_URL = "/donaciones_ciudad/";
  var TITLE = "Donación";

  /**
   * ListRequestView is the main component of the list.html page.
   *
   * @param {Object} map leaflet map instance
   */
  function ListRequestView(map, options) {
    this.map = map;
    this.mapOptions = options;
    // variable that holds the list of points we get from the backend
    this.cluster = undefined;
    // current search string
    this.currentSearchString = undefined;
    this.requestTableView = new TableView();
    this.loadingIndicator = new LoadingIndicatorView();
    // show the spinner while we bootstrap
    this.loadingIndicator.show();

    // Use Leaflet API here
    map.setZoom(13);

    map.addControl(
      new L.Control.Fullscreen({
        title: {
          false: 'Ver en Pantalla Completa',
          true: 'Salir de Pantalla Completa',
        },
      })
    );
    this.setupViewListeners();
    this.setupCitiesDropdown();
  }

  ListRequestView.prototype.setupViewListeners = setupViewListeners;
  ListRequestView.prototype.switchClusteringInit = switchClusteringInit;
  ListRequestView.prototype.geoFindMe = geoFindMe;
  ListRequestView.prototype.getQuery = getQuery;
  ListRequestView.prototype.requestGeoData = requestGeoData;
  ListRequestView.prototype.loadMarkersAndGroup = loadMarkersAndGroup;
  ListRequestView.prototype.loadMarkers = loadMarkers;
  ListRequestView.prototype.groupMarkerRequest = groupMarkerRequest;
  ListRequestView.prototype.setupCitiesDropdown = setupCitiesDropdown;

  // export
  window.ListRequestView = ListRequestView;

  // implementation

  /**
   * ListRequestView.setupViewListeners
   */
  function setupViewListeners() {
    var vm = this;

    this.map.on('moveend', function () {
      vm.requestGeoData(vm.map);
    });

    document
      .querySelector('#find-me')
      .addEventListener('click', this.geoFindMe.bind(this));

    document
      .getElementById('search-text-field')
      .addEventListener('keypress', function (e) {
        if (e.charCode == 13) {
          vm.getQuery();
        }
      });

    document
      .getElementById('search-button')
      .addEventListener('click', this.getQuery.bind(this));

    // document
    //   .getElementById('switchNormal')
    //   .addEventListener('click', this.groupMarkerRequest.bind(this));
  }

  function switchClusteringInit() {
    //We check if the browser support local Storage caching
    //in case does not, we disable the switch
    var switchElement = document.getElementById('switchNormal');

    if (typeof Storage === 'undefined') {
      switchElement.disabled = true;
    } else {
      switchElement.checked = false;
      var isGroupMarksActive = JSON.parse(
        localStorage.getItem('group_markers_setting')
      );
      if (isGroupMarksActive != null) {
        if (isGroupMarksActive) {
          switchElement.checked = true;
        }
      }
    }
  }

  function geoFindMe() {
    var status = document.querySelector('#status');

    function success(position) {
      var latitude = position.coords.latitude;
      var longitude = position.coords.longitude;

      var greenIcon = new L.Icon({
        iconUrl:
          '/static/icons/marker-icon-2x-green.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
      });

      console.log('${latitude} ' + longitude);

      // make sure there is only one marker for user's location
      if (typeof you !== 'undefined'){
        maps[0].removeLayer(you);
      }
      
      you = L.marker([latitude, longitude], {
        opacity: 0.8,
        icon: greenIcon,
        title: 'Tu ubicación',
      }).addTo(maps[0]);
      you.bindPopup('<b>Tu ubicación</b>').openPopup();
      maps[0].panTo(new L.LatLng(latitude, longitude), 14);
      status.textContent = 'Mostrando tu localización actual';
    }

    function error() {
      status.textContent = 'No puedo encontrarte, usá los botones del mapa';
    }

    if (!navigator.geolocation) {
      status.textContent = 'Tu navegador no soporta la geolocalización';
    } else {
      status.textContent = 'Buscando tu ubicación…';
      navigator.geolocation.getCurrentPosition(success, error);
    }
  }

  function getQuery() {
    this.currentSearchString = document
      .getElementById('search-text-field')
      .value.trim();
    this.requestGeoData();
  }

  function requestGeoData() {
    this.loadingIndicator.show();
    var vm = this;
    var map = this.map;
    var searchUrl = GEO_URL+'?in_bbox=' + map.getBounds().toBBoxString();

    if (vm.currentSearchString && vm.currentSearchString.length >= 3) {
      searchUrl += '&search_fields=name&search=' + vm.currentSearchString;
    }

    fetch(searchUrl)
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        vm.loadingIndicator.hide();

        if (vm.clusters) {
          map.removeLayer(vm.clusters);
        }

        if (map.getZoom() >= 13) {
          vm.clusters = vm.loadMarkers(map, data); //load markers without clustering
        } else {
          vm.clusters = vm.loadMarkersAndGroup(map, data);
        }

        vm.requestTableView.setData(data.features);
        vm.requestTableView.render();
      });
  }

  function loadMarkersAndGroup(map, data) {
    var markerClusters = L.markerClusterGroup();
    var layerGroup = L.geoJSON(data, {
      onEachFeature: function (feature, layer) {
        var popup =
          '<a class="subtitle" href="' + LIST_URL +
          feature.properties.pk +
          '"><h1>'+ TITLE +' #' +
          feature.properties.pk +
          '</h1></a><p class="has-text-weight-bold">Nombre: ' +
          feature.properties.name +
          '</p><p>' +
          feature.properties.title +
          '</p>' +
          '<a class="is-size-6" href="' + LIST_URL +
          feature.properties.pk +
          '">Ver '+ TITLE +'</a>';
        layer.bindPopup(popup);

        markerClusters.addLayer(layer);
      },
    });
    map.addLayer(markerClusters);

    return markerClusters;
  }

  function loadMarkers(map, data) {
    var layerGroup = L.geoJSON(data, {
      onEachFeature: function (feature, layer) {
        var popup =
          '<a class="subtitle" href="' + LIST_URL +
          feature.properties.pk +
          '"><h1>'+ TITLE +' #' +
          feature.properties.pk +
          '</h1></a><p class="has-text-weight-bold">Nombre: ' +
          feature.properties.name +
          '</p><p>' +
          feature.properties.title +
          '</p>' +
          '<a class="is-size-6" href="' + LIST_URL +
          feature.properties.pk +
          '">Ver '+ TITLE +'</a>';
        layer.bindPopup(popup);
      },
    }).addTo(map);

    return layerGroup;
  }

  function groupMarkerRequest() {
    //Update cached status
    var checkbox = document.getElementById('switchNormal');
    if (checkbox.checked != true) {
      localStorage.setItem('group_markers_setting', JSON.stringify(false));
    } else {
      localStorage.setItem('group_markers_setting', JSON.stringify(true));
    }

    // location.reload(); //refresh the page with the new map display setting
    this.requestGeoData(this.map);
  }

  function setupCitiesDropdown() {
    // based on https://codepen.io/airen/pen/arGXvz
    var datalist = document.querySelector('.cities-dropdown > datalist');
    var select = document.querySelector('.cities-dropdown > datalist > select');
    var options = select.options;

    /* input.onchange is triggered when the user selects something from the datalist */
    input = document.querySelector('input[name="cities"]');

    input.addEventListener('change', function () {
      var selectedValue = input.value;
      var selectedIndex;

      for (var i = 0; i < options.length; i++) {
        if (options[i].text == selectedValue) {
          selectedIndex = i;
          break;
        }
      }
      if (selectedIndex == undefined) {
        return;
      }
      var selectedOption = options[selectedIndex];
      location.assign(
        LIST_BY_CITY_URL + selectedOption.getAttribute('data-value')
      );
    });

    /* when user selects an option from the datalist, write it to text field */
    select.addEventListener('change', function () {
      input.value = options[this.selectedIndex].value;
    });
  }



  /**
   * This component controls the spinner.
   */
  function LoadingIndicatorView() {
    this.el = document.getElementById('loading-indicator');
  }

  LoadingIndicatorView.prototype.show = show;
  LoadingIndicatorView.prototype.hide = hide;

  function show() {
    this.el.classList.add('is-active');
  }

  function hide() {
    this.el.classList.remove('is-active');
  }
})();
