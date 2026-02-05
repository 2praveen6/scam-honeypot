def get_dashboard_html():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Scam Honeypot Dashboard</title>
  <style>
    body { font-family: Arial; padding: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px; }
    th { background: #f2f2f2; }
  </style>
</head>

<body>
  <h2>🚨 Live Scam Dashboard</h2>

  <table>
    <thead>
      <tr>
        <th>Session ID</th>
        <th>Message</th>
        <th>UPI IDs</th>
        <th>Phone Numbers</th>
        <th>Timestamp</th>
      </tr>
    </thead>
    <tbody id="sessionsTable"></tbody>
  </table>

<script>
  const ws = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws/dashboard"
  );

  ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    const table = document.getElementById("sessionsTable");
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${data.session_id}</td>
      <td>${data.message}</td>
      <td>${data.upi_ids.join(", ")}</td>
      <td>${data.phone_numbers.join(", ")}</td>
      <td>${data.timestamp}</td>
    `;

    table.prepend(row);
  };
</script>

</body>
</html>
"""
