var svgNamespace = "http://www.w3.org/2000/svg";

function makeSvgElement(name, attributes, text) {
  var element = document.createElementNS(svgNamespace, name);
  Object.keys(attributes).forEach(function (attribute) {
    element.setAttribute(attribute, attributes[attribute]);
  });
  if (text !== undefined) {
    element.textContent = text;
  }
  return element;
}

function formatNumber(value) {
  return value.toLocaleString("en-US");
}

function renderChart(dashboardData) {
  var svg = document.getElementById("steps-chart");
  var chart = { left: 72, right: 1050, top: 18, bottom: 282, maximum: 4000000 };

  [0, 1000000, 2000000, 3000000, 4000000].forEach(function (value) {
    var y = chart.bottom - (value / chart.maximum) * (chart.bottom - chart.top);
    svg.appendChild(makeSvgElement("line", {
      x1: chart.left,
      y1: y,
      x2: chart.right,
      y2: y,
      "class": "chart-grid"
    }));
    if (value > 0) {
      svg.appendChild(makeSvgElement("text", {
        x: chart.left - 12,
        y: y + 4,
        "text-anchor": "end",
        "class": "chart-axis-label"
      }, (value / 1000000) + "M"));
    }
  });

  dashboardData.months.forEach(function (month, index) {
    var x = chart.left + (index / (dashboardData.months.length - 1)) * (chart.right - chart.left);
    svg.appendChild(makeSvgElement("text", {
      x: x,
      y: chart.bottom + 27,
      "text-anchor": "middle",
      "class": "chart-month-label"
    }, month));
  });

  dashboardData.stepSeries.forEach(function (series) {
    var path = "";
    var lastPoint = null;
    var finalPoint = null;

    series.values.forEach(function (value, index) {
      if (value == null) {
        lastPoint = null;
        return;
      }
      var point = {
        x: chart.left + (index / (dashboardData.months.length - 1)) * (chart.right - chart.left),
        y: chart.bottom - (value / chart.maximum) * (chart.bottom - chart.top)
      };
      path += (lastPoint ? " L " : " M ") + point.x + " " + point.y;
      lastPoint = point;
      finalPoint = point;
    });

    svg.appendChild(makeSvgElement("path", {
      d: path,
      stroke: series.color,
      "class": "chart-line"
    }));

    if (finalPoint) {
      svg.appendChild(makeSvgElement("circle", {
        cx: finalPoint.x,
        cy: finalPoint.y,
        r: 4,
        fill: series.color,
        "class": "chart-dot"
      }));

      svg.appendChild(makeSvgElement("text", {
        x: finalPoint.x + 12,
        y: finalPoint.y + 5,
        "class": "chart-series-label"
      }, series.label));
    }
  });
}

function renderSummaries(dashboardData) {
  var workoutContainer = document.getElementById("workout-totals");
  dashboardData.workouts.forEach(function (item) {
    var column = document.createElement("div");
    column.className = "workout-total";
    var year = document.createElement("span");
    year.className = "summary-badge";
    year.textContent = item.year;
    var count = document.createElement("span");
    count.className = "total-value";
    count.textContent = item.count;
    column.appendChild(year);
    column.appendChild(count);
    workoutContainer.appendChild(column);
  });

  var weeklyContainer = document.getElementById("weekly-totals");
  dashboardData.lastSevenDays.forEach(function (item) {
    var column = document.createElement("div");
    column.className = "weekly-total";
    var person = document.createElement("span");
    person.className = "summary-badge";
    person.textContent = item.label;
    var count = document.createElement("span");
    count.className = "weekly-value";
    count.textContent = formatNumber(item.count);
    column.appendChild(person);
    column.appendChild(count);
    weeklyContainer.appendChild(column);
  });
}

function renderDashboard(dashboardData) {
  document.title = "Movement — " + dashboardData.year;
  renderChart(dashboardData);
  renderSummaries(dashboardData);
}

function showDashboardError(message) {
  var error = document.getElementById("dashboard-error");
  error.textContent = message;
  error.hidden = false;
}

var request = new XMLHttpRequest();
request.open("GET", "/api/v1/dashboard");
request.onload = function () {
  if (request.status < 200 || request.status >= 300) {
    showDashboardError("Dashboard data could not be loaded (HTTP " + request.status + ").");
    return;
  }

  var dashboardData;
  try {
    dashboardData = JSON.parse(request.responseText);
  } catch (error) {
    showDashboardError("Dashboard data could not be read: " + error.message);
    return;
  }

  renderDashboard(dashboardData);
};
request.onerror = function () {
  showDashboardError("Dashboard data could not be loaded. Check the server connection and try again.");
};
request.send();
