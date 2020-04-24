(function () {
  /**
   * Component that renders the list of requests.
   */
  function TableView() {
    this.data = [];
    this.tpl = document.getElementById('table-template').innerHTML;
    this.emptyTpl = document.getElementById('table-empty-template').innerHTML;
    this.requestTableEl = document.getElementById('table');
    this.paginator = new TablePaginatorView(10);
    this.paginator.onPageChanged = this.render.bind(this);
  }

  TableView.prototype.render = renderTable;
  TableView.prototype.setData = setData;

  //export this
  window.TableView = TableView;

  /**
   * Table.setData
   *
   * @param {Object[]} data
   */
  function setData(data) {
    this.data = data;
    this.paginator.setData(data);
  }

    /*!
  * Sanitize and encode all HTML in a user-submitted string
  * (c) 2018 Chris Ferdinandi, MIT License, https://gomakethings.com
  * @param  {String} str  The user-submitted string
  * @return {String} str  The sanitized string
  */
  function sanitizeHTML(str) {
    var temp = document.createElement("div");
    temp.textContent = str;
    return temp.innerHTML;
  }

  /**
   * Table.render
   */
  function renderTable() {
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
        .replace(/{{name}}/g, sanitizeHTML(req.name))
        .replace(/{{title}}/g, sanitizeHTML(req.title));
    }

    requestAnimationFrame(function () {
      vm.requestTableEl.innerHTML = tableHtml;
      vm.paginator.render();
    });
  }

  /**
   * Responsible for rendering the pagination widget.
   */
  function TablePaginatorView(pageSize) {
    this.pageSize = pageSize;
    this.tpl = document.getElementById('table-paginator-template').innerHTML;
    this.el = document.getElementById('table-paginator');
  }

  TablePaginatorView.prototype.render = renderPaginator;
  TablePaginatorView.prototype.setData = setPaginatorData;
  TablePaginatorView.prototype.next = next;
  TablePaginatorView.prototype.prev = prev;
  TablePaginatorView.prototype.firstPage = firstPage;
  TablePaginatorView.prototype.lastPage = lastPage;
  TablePaginatorView.prototype.setFlags = setFlags;
  TablePaginatorView.prototype.getPage = getPage;
  TablePaginatorView.prototype.setupPaginationListeners = setupPaginationListeners;

  /**
   * TablePaginatorView.render
   */
  function renderPaginator() {
    this.setFlags();

    if (this.pages == 0) {
      this.el.innerHTML = '';
      return;
    }
    var html = this.tpl
      .replace(/{{currentPage}}/g, this.currentPage + 1)
      .replace(/{{nextPage}}/g, this.currentPage + 2)
      .replace(/{{previousPage}}/g, this.currentPage)
      .replace(/{{totalPages}}/g, this.totalPages)
      .replace(
        /{{hasMultiplePages}}/g,
        'has-multiple-pages-' + this.hasMultiplePages
      );

    if (!this.hasNext) {
      html = html.replace(/{{hasNext}}/g, 'disabled');
    }

    if (!this.showNext) {
      html = html.replace(/{{showNext}}/g, 'is-hidden');
    }

    if (!this.hasPrev) {
      html = html.replace(/{{hasPrev}}/g, 'disabled');
    }

    if (!this.showPrev) {
      html = html.replace(/{{showPrev}}/g, 'is-hidden');
    }

    if (this.currentPage === 0) {
      html = html.replace(/{{hasFirst}}/g, 'disabled');
      html = html.replace(/{{showFirst}}/g, 'is-hidden');
    } else if (this.currentPage === this.totalPages - 1) {
      html = html.replace(/{{hasLast}}/g, 'disabled');
      html = html.replace(/{{showLast}}/g, 'is-hidden');
    }

    if (this.totalPages == 1) {
      //show only current
      html = html.replace(/{{showFirst}}/g, 'is-hidden');
      html = html.replace(/{{showLast}}/g, 'is-hidden');
    }

    this.el.innerHTML = html;
    this.setupPaginationListeners();
  }

  /**
   * TablePaginatorView.setPaginatorData
   *
   * Fills in the paginated data array based on the given data source.
   * @param {Object[]} dataSource
   */
  function setPaginatorData(dataSource) {
    this.count = dataSource.length;
    this.pages = [];
    this.currentPage = 0;
    this.nextPage = 0;
    this.previousPage = 0;

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
    this.showPrev = false;
    this.showNext = false;

    if (this.totalPages == 1) {
      this.hasMultiplePages = false;
      this.hasNext = false;
      this.hasPrev = false;
      this.showPrev = false;
      this.showNext = false;
      return;
    }

    if (this.currentPage < this.totalPages - 1) {
      this.hasNext = true;
      if (this.currentPage + 2 != this.totalPages) {
        this.showNext = true;
      }
    }

    if (this.currentPage > 0) {
      this.hasPrev = true;
      if (this.currentPage != 1) {
        this.showPrev = true;
      }
    }
  }

  /**
   * TablePaginatorView.setupPaginationListeners
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
      .querySelector('.current-plus-button')
      .addEventListener('click', vm.next.bind(this));
    this.el
      .querySelector('.current-minus-button')
      .addEventListener('click', vm.prev.bind(this));
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
})();
