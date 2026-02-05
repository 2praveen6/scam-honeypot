from fastapi import Request
from fastapi.responses import HTMLResponse
from app.db import SessionLocal
from app.db_models import HoneypotSession
import json

def get_dashboard_html():
    db = SessionLocal()
    sessions = db.query(HoneypotSession).order_by(HoneypotSession.created_at.desc()).all()
    
    rows = ""
    total_scams = 0
    all_upis = set()
    all_phones = set()
    
    for s in sessions:
        if s.scam_detected:
            total_scams += 1
        
        upi_list = json.loads(s.upi_ids or "[]")
        phone_list = json.loads(s.phone_numbers or "[]")
        all_upis.update(upi_list)
        all_phones.update(phone_list)
        
        rows += f"""
        <tr>
            <td>{s.session_id[:8]}...</td>
            <td>{'🔴 SCAM' if s.scam_detected else '🟢 SAFE'}</td>
            <td>{s.total_messages}</td>
            <td>{', '.join(upi_list) or 'None'}</td>
            <td>{', '.join(phone_list) or 'None'}</td>
            <td>{s.created_at.strftime('%Y-%m-%d %H:%M')}</td>
        </tr>
        """
    
    db.close()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛡️ Honeypot Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-label {{
                color: #666;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            th {{
                background: #667eea;
                color: white;
                padding: 15px;
                text-align: left;
            }}
            td {{
                padding: 15px;
                border-bottom: 1px solid #f0f0f0;
            }}
            tr:hover {{
                background: #f8f8ff;
            }}
            .refresh-btn {{
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Scam Honeypot Dashboard</h1>
                <p style="color: #666;">Real-time Intelligence Gathering System</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(sessions)}</div>
                    <div class="stat-label">Total Sessions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_scams}</div>
                    <div class="stat-label">Scams Detected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(all_upis)}</div>
                    <div class="stat-label">UPI IDs Collected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(all_phones)}</div>
                    <div class="stat-label">Phone Numbers</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Session ID</th>
                        <th>Status</th>
                        <th>Messages</th>
                        <th>UPI IDs</th>
                        <th>Phone Numbers</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {rows if rows else '<tr><td colspan="6" style="text-align:center;">No data yet</td></tr>'}
                </tbody>
            </table>
            
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </div>
        
        <script>
            setTimeout(() => location.reload(), 30000); // Auto-refresh every 30s
        </script>
    </body>
    </html>
    """