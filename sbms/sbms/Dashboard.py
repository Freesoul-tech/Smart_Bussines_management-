"""Dashboard template kept as a Python string so the module remains valid."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>SBMS Dashboard</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">SBMS</a>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <a class="nav-link active" href="#">Dashboard</a>
            </li>
            <li class="nav-item"><a class="nav-link" href="#">Reports</a></li>
            <li class="nav-item"><a class="nav-link" href="#">Settings</a></li>
          </ul>
          <span class="navbar-text text-white">Admin ▼</span>
        </div>
      </div>
    </nav>

    <div class="container my-4">
      <div class="row text-center">
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h5>Revenue</h5>
              <h3>$12,500</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-danger text-white">
            <div class="card-body">
              <h5>Expenses</h5>
              <h3>$4,200</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h5>Customers</h5>
              <h3>320</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-dark">
            <div class="card-body">
              <h5>Inventory Alerts</h5>
              <h3>15</h3>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container my-4">
      <div class="row">
        <div class="col-md-6">
          <canvas id="salesChart"></canvas>
        </div>
        <div class="col-md-6">
          <canvas id="expensesChart"></canvas>
        </div>
      </div>
    </div>

    <div class="container my-4">
      <h4>Recent Activity</h4>
      <ul class="list-group">
        <li class="list-group-item">New Sale: Order # - Mk </li>
        <li class="list-group-item">New Customer: Jane Doe</li>
        <li class="list-group-item">Inventory Alert: Item #A12 low stock</li>
        <li class="list-group-item">Expense Recorded: Utilities - MK </li>
      </ul>
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-4">
      © 2026 SBMS | Help | Contact | Version 1.0
    </footer>

    <script>
      var ctx1 = document.getElementById("salesChart").getContext("2d");
      new Chart(ctx1, {
        type: "line",
        data: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May"],
          datasets: [{
            label: "Monthly Sales",
            data: [120, 90, 150, 200, 170],
            borderColor: "rgba(54, 162, 235, 1)",
            fill: false,
          }],
        },
      });

      var ctx2 = document.getElementById("expensesChart").getContext("2d");
      new Chart(ctx2, {
        type: "pie",
        data: {
          labels: ["Procurement", "Salaries", "Utilities", "Other"],
          datasets: [{
            data: [1200, 2500, 800, 700],
            backgroundColor: [
              "rgba(255, 99, 132, 0.6)",
              "rgba(54, 162, 235, 0.6)",
              "rgba(255, 206, 86, 0.6)",
              "rgba(75, 192, 192, 0.6)",
            ],
          }],
        },
      });
    </script>
  </body>
</html>
"""


__all__ = ["DASHBOARD_HTML"]
