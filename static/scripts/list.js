// script to support the templates/list.html file
(function () {
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
    this.requestTableView = new RequestsTableView();
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
    const status = document.querySelector('#status');

    function success(position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      console.log('${latitude} ' + longitude);
      you = L.marker([latitude, longitude], {
	opacity: 0.3,
	title: 'Tu ubicación',
      }).addTo(maps[0]);
      you.bindPopup('Tu ubicación').openPopup();
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
    var searchUrl =
      '/api/v1/helprequestsgeo/?in_bbox=' + map.getBounds().toBBoxString();

    if (vm.currentSearchString && vm.currentSearchString.length >= 3) {
      searchUrl += '&search_fields=message&search=' + vm.currentSearchString;
    }

    fetch(searchUrl)
      .then((response) => response.json())
      .then((data) => {
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
	  '<a class="subtitle" href="/pedidos/' +
	  feature.properties.pk +
	  '"><h1>Pedido #' +
	  feature.properties.pk +
	  '</h1></a><p class="has-text-weight-bold">Nombre: ' +
	  feature.properties.name +
	  '</p><p>' +
	  feature.properties.title +
	  '</p>' +
	  '<a class="is-size-6" href="/pedidos/' +
	  feature.properties.pk +
	  '">Ver Pedido</a>';
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
	  '<a class="subtitle" href="/pedidos/' +
	  feature.properties.pk +
	  '"><h1>Pedido #' +
	  feature.properties.pk +
	  '</h1></a><p class="has-text-weight-bold">Nombre: ' +
	  feature.properties.name +
	  '</p><p>' +
	  feature.properties.title +
	  '</p>' +
	  '<a class="is-size-6" href="/pedidos/' +
	  feature.properties.pk +
	  '">Ver Pedido</a>';
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
	'/pedidos_ciudad/' + selectedOption.getAttribute('data-value')
      );
    });

    /* when user selects an option from the datalist, write it to text field */
    select.addEventListener('change', function () {
      input.value = options[this.selectedIndex].value;
    });
  }

  /**
   * Component that renders the list of requests.
   */
  function RequestsTableView() {
    this.data = [];
    this.tpl = document.getElementById('requests-table-template').innerHTML;
    this.emptyTpl = document.getElementById(
      'requests-table-empty-template'
    ).innerHTML;
    this.requestTableEl = document.getElementById('requests-table');
    this.paginator = new RequestsTablePaginatorView(10);
    this.paginator.onPageChanged = this.render.bind(this);
  }

  RequestsTableView.prototype.render = renderRequestsTable;
  RequestsTableView.prototype.setData = setData;

  /**
   * RequestsTable.setData
   *
   * @param {Object[]} data
   */
  function setData(data) {
    this.data = data;
    this.paginator.setData(data);
  }

  /**
   * RequestsTable.render
   */
  function renderRequestsTable() {
    var vm = this;
    var tableHtml = '';
    var req;
    var i;
    var now = moment();
    var data = vm.paginator.getPage();

    if (data.length == 0) {
      tableHtml = this.emptyTpl;
    }

    for (i = 0; i < data.length; i++) {
      req = data[i].properties;

      tableHtml += this.tpl
	.replace(/{{id}}/g, req.pk)
	.replace(/{{added}}/g, moment(req.added).from(now))
	.replace(/{{name}}/g, req.name)
	.replace(/{{title}}/g, req.title);
    }

    requestAnimationFrame(function () {
      vm.requestTableEl.innerHTML = tableHtml;
      vm.paginator.render();
    });
  }

  /**
   * Responsible for rendering the pagination widget.
   */
  function RequestsTablePaginatorView(pageSize) {
    this.pageSize = pageSize;
    this.tpl = document.getElementById(
      'requests-table-paginator-template'
    ).innerHTML;
    this.el = document.getElementById('requests-table-paginator');

    // The following should be defined by the parent component.
    this.onNextPage = undefined;
    this.onPrevPage = undefined;
    this.onFirstPage = undefined;
    this.onLastPage = undefined;
  }

  RequestsTablePaginatorView.prototype.render = renderPaginator;
  RequestsTablePaginatorView.prototype.setData = setPaginatorData;
  RequestsTablePaginatorView.prototype.next = next;
  RequestsTablePaginatorView.prototype.prev = prev;
  RequestsTablePaginatorView.prototype.firstPage = firstPage;
  RequestsTablePaginatorView.prototype.lastPage = lastPage;
  RequestsTablePaginatorView.prototype.setFlags = setFlags;
  RequestsTablePaginatorView.prototype.getPage = getPage;
  RequestsTablePaginatorView.prototype.setupPaginationListeners = setupPaginationListeners;

  /**
   * RequestsTablePaginatorView.render
   */
  function renderPaginator() {
    this.setFlags();

    if (this.pages == 0) {
      this.el.innerHTML = '';
      return;
    }
    var html = this.tpl
      .replace(/{{currentPage}}/g, this.currentPage + 1)
      .replace(/{{totalPages}}/g, this.totalPages)
      .replace(
	/{{hasMultiplePages}}/g,
	'has-multiple-pages-' + this.hasMultiplePages
      );

    if (!this.hasNext) {
      html = html.replace(/{{hasNext}}/g, 'disabled');
    }

    if (!this.hasPrev) {
      html = html.replace(/{{hasPrev}}/g, 'disabled');
    }

    if (this.currentPage === 0) {
      html = html.replace(/{{hasFirst}}/g, 'disabled');
    } else if (this.currentPage === this.totalPages - 1) {
      html = html.replace(/{{hasLast}}/g, 'disabled');
    }

    this.el.innerHTML = html;
    this.setupPaginationListeners();
  }

  /**
   * RequestsTablePaginatorView.setPaginatorData
   *
   * Fills in the paginated data array based on the given data source.
   * @param {Object[]} dataSource
   */
  function setPaginatorData(dataSource) {
    this.count = dataSource.length;
    this.pages = [];
    this.currentPage = 0;

    if (dataSource.length == 0) {
      return;
    }
    this.totalPages = Math.ceil(this.count / this.pageSize);
    var page = [];

    if (this.totalPages == 1) {
      this.pages.push(dataSource);
      return;
    }

    for (var i = 0; i < this.count; i++) {
      page.push(dataSource[i]);

      if (page.length == this.pageSize) {
	this.pages.push(page);
	page = [];
      }
    }

    if (page.length > 0) {
      this.pages.push(page);
    }
  }

  function setFlags() {
    this.hasMultiplePages = true;
    this.hasNext = false;
    this.hasPrev = false;

    if (this.totalPages == 1) {
      this.hasMultiplePages = false;
      this.hasNext = false;
      this.hasPrev = false;
      return;
    }

    if (this.currentPage < this.totalPages - 1) {
      this.hasNext = true;
    }

    if (this.currentPage > 0) {
      this.hasPrev = true;
    }
  }

  /**
   * RequestsTablePaginatorView.setupPaginationListeners
   */
  function setupPaginationListeners() {
    var vm = this;
    this.el
      .querySelector('.next-button')
      .addEventListener('click', vm.next.bind(this));
    this.el
      .querySelector('.prev-button')
      .addEventListener('click', vm.prev.bind(this));
    this.el
      .querySelector('.first-button')
      .addEventListener('click', vm.firstPage.bind(this));
    this.el
      .querySelector('.last-button')
      .addEventListener('click', vm.lastPage.bind(this));
  }

  /**
   * @returns {Object[]}
   */
  function getPage() {
    if (this.pages.length == 0) {
      return [];
    }
    return this.pages[this.currentPage];
  }

  function next() {
    this.currentPage += 1;
    this.onPageChanged();
  }

  function prev() {
    this.currentPage -= 1;
    this.onPageChanged();
  }

  function firstPage() {
    this.currentPage = 0;
    this.onPageChanged();
  }

  function lastPage() {
    this.currentPage = this.totalPages - 1;
    this.onPageChanged();
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
