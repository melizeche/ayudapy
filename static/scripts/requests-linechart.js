(function () {
  var rlc = new RequestsLineChart();

  function fetchData(from, to) {
    fetch('/api/v1/stats-daily?date_from=' + from + '&date_to=' + to)
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        rlc.update(data);
      });
  }
  // let's fetch the requests from the API (defaults to a 30 days window)
  var fromDefault = moment().subtract(1, 'months');
  var toDefault = moment();
  var API_DATE_FMT = 'YYYY-MM-DD';

  fetchData(fromDefault.format(API_DATE_FMT), toDefault.format(API_DATE_FMT));

  var dp = new DatePicker(fromDefault, toDefault);
  dp.onSelected(function (event) {
    var date = event.data.date;
    var from = moment(date.start).format(API_DATE_FMT);
    var to = moment(date.end).format(API_DATE_FMT);
    fetchData(from, to);
  });

  function DatePicker(from, to) {
    this.calendar = bulmaCalendar.attach('.datepicker', {
      type: 'date',
      isRange: true,
      displayMode: 'default',
      labelFrom: 'Desde',
      labelTo: 'Hasta',
      dateFormat: 'DD/MM/YYYY',
      startDate: from.toDate(),
      endDate: to.toDate(),
    })[0];
    this.onSelected = onSelected;
  }

  /**
   * DatePicker.onSelected
   * @param {Function} handler
   */
  function onSelected(handler) {
    this.calendar.on('select', handler);
  }

  function RequestsLineChart() {
    var options = {
      series: [],
      chart: {
        height: 350,
        type: 'line',
        dropShadow: {
          enabled: true,
          color: '#000',
          top: 18,
          left: 7,
          blur: 10,
          opacity: 0.2,
        },
        toolbar: {
          show: false,
        },
      },
      colors: ['#77B6EA', '#545454'],
      dataLabels: {
        enabled: true,
      },
      stroke: {
        curve: 'smooth',
      },
      title: {
        text: 'Cantidad de pedidos activos y atendidos',
        align: 'left',
      },
      grid: {
        borderColor: '#e7e7e7',
        row: {
          colors: ['#f3f3f3', 'transparent'],
          opacity: 0.5,
        },
      },
      markers: {
        size: 1,
      },
      xaxis: {
        type: 'datetime',
      },
      yaxis: {
        title: {
          text: 'Total de Pedidos',
        },
      },
      legend: {
        position: 'top',
        horizontalAlign: 'right',
        floating: true,
        offsetY: -25,
        offsetX: -5,
      },
      noData: {
        text: 'No se encontraron registros',
      },
    };

    this.chart = new ApexCharts(
      document.querySelector('#requests-linechart'),
      options
    );
    this.chart.render();
  }

  RequestsLineChart.prototype.update = update;

  /**
   * RequestsLineChart.render
   *
   * @param {Object[]} data
   */
  function update(data) {
    var series = [
      {
        name: 'Activos',
        data: data.total_active.map(function (e) {
          return { x: e.date, y: e.total };
        }),
      },
      {
        name: 'Atendidos',
        data: data.total_resolved.map(function (e) {
          return { x: e.date, y: e.total };
        }),
      },
    ];
    this.chart.updateSeries(series);
  }
})();
