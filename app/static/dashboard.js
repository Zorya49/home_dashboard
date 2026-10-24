// Replace this sample object with values supplied by the dashboard endpoint.
var dashboardData = {
  year: 2026,
  months: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  stepSeries: [
    {
      label: "Me",
      color: "#343832",
      values: [42000, 60000, 76000, 101000, 128000, 145000, 141000, 160000, 179000, 232000, null, null]
    },
    {
      label: "Spouse",
      color: "#b29748",
      values: [8000, 19000, 39000, 112000, 145000, 160000, 194000, 228000, 276000, 368000, null, null]
    }
  ],
  workouts: [
    { year: 2024, count: 61 },
    { year: 2025, count: 73 },
    { year: 2026, count: 17 }
  ],
  lastSevenDays: [
    { label: "Me", count: 43724 },
    { label: "Spouse", count: 53371 }
  ]
};

var svgNamespace = "http://www.w3.org/2000/svg";

document.title = "Movement — " + dashboardData.year;

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

function renderChart() {
  var svg = document.getElementById("steps-chart");
  var chart = { left: 72, right: 1050, top: 18, bottom: 282, maximum: 400000 };

  [0, 100000, 200000, 300000, 400000].forEach(function (value) {
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
      }, (value / 1000) + "k"));
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

function renderSummaries() {
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

renderChart();
renderSummaries();
