
from flask import Flask, jsonify, request, render_template
from db import get_db_connection
import requests
import time
from db import get_db_connection
from apscheduler.schedulers.background import BackgroundScheduler

failure_counts = {}

app = Flask(__name__)

MONITORED_URLS = [
    "https://example.com",
    "https://httpbin.org/status/200",
    "https://jsonplaceholder.typicode.com/posts/1"
]



def automatic_health_check():
    print("\n--- Automatic ServiceWatch Check ---")

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT service_id, service_url
            FROM services
            WHERE is_active = TRUE
        """)

        services = cursor.fetchall()

        for service_id, url in services:
            start_time = time.perf_counter()

            try:
                response = requests.get(url, timeout=5)

                response_time = round(
                    (time.perf_counter() - start_time) * 1000, 2
                )

                cursor.execute("""
                    INSERT INTO monitoring_history
                    (service_id, status_code, response_time_ms,
                     is_available, error_message)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    service_id,
                    response.status_code,
                    response_time,
                    response.ok,
                    None
                ))

                connection.commit()

                if response.ok:
                    failure_counts[service_id] = 0

                    cursor.execute("""
                        UPDATE incidents
                        SET status = 'RESOLVED',
                            resolved_at = CURRENT_TIMESTAMP
                        WHERE service_id = %s
                          AND status = 'OPEN'
                    """, (service_id,))

                    if cursor.rowcount > 0:
                        connection.commit()
                        print(
                            f"INCIDENT RESOLVED for service ID: {service_id}"
                        )

                else:
                    failure_counts[service_id] = (
                        failure_counts.get(service_id, 0) + 1
                    )

                    create_incident_if_needed(
                        cursor, connection, service_id
                    )

                print(
                    f"URL: {url} | "
                    f"Status: {response.status_code} | "
                    f"Response: {response_time} ms | "
                    f"Available: {response.ok}"
                )

            except requests.RequestException as error:
                response_time = round(
                    (time.perf_counter() - start_time) * 1000, 2
                )

                failure_counts[service_id] = (
                    failure_counts.get(service_id, 0) + 1
                )

                print(f"URL: {url} | FAILED: {error}")

                cursor.execute("""
                    INSERT INTO monitoring_history
                    (service_id, status_code, response_time_ms,
                     is_available, error_message)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    service_id,
                    None,
                    response_time,
                    False,
                    str(error)
                ))

                connection.commit()

                create_incident_if_needed(
                    cursor, connection, service_id
                )

    except Exception as error:
        print("Database or monitoring error:", error)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def create_incident_if_needed(cursor, connection, service_id):
    count = failure_counts.get(service_id, 0)

    if count < 3:
        return

    cursor.execute("""
        SELECT incident_id
        FROM incidents
        WHERE service_id = %s
          AND status = 'OPEN'
        LIMIT 1
    """, (service_id,))

    if cursor.fetchone():
        return

    severity = 'CRITICAL' if count >= 5 else 'HIGH'

    cursor.execute("""
        INSERT INTO incidents
        (service_id, severity, status, description)
        VALUES (%s, %s, %s, %s)
    """, (
        service_id,
        severity,
        'OPEN',
        f'Service failed {count} consecutive checks'
    ))

    connection.commit()
    print(f"{severity} INCIDENT CREATED for service ID: {service_id}")




@app.route("/")
def home():
    return "ServiceWatch is running!"


@app.route("/check")
def check_service():
    url = "https://example.com"
    start_time = time.perf_counter()

    try:
        response = requests.get(url, timeout=5)
        response_time = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

        return jsonify({
            "service": url,
            "status_code": response.status_code,
            "response_time_ms": response_time,
            "available": response.ok
        })

    except requests.RequestException as error:
        return jsonify({
            "service": url,
            "available": False,
            "error": str(error)
        }), 502
    
@app.route("/check-all")
def check_all_services():
    automatic_health_check()

    return jsonify({
        "message": "Health check completed",
        "total_services": 10
    })

@app.route("/api/services", methods=["GET"])
def get_services():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(services)

@app.route("/api/services/<int:service_id>", methods=["GET"])
def get_service(service_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM services WHERE service_id = %s",
        (service_id,)
    )

    service = cursor.fetchone()

    cursor.close()
    connection.close()

    if service is None:
        return jsonify({"error": "Service not found"}), 404

    return jsonify(service)

@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM incidents
        ORDER BY opened_at DESC
    """)

    incidents = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(incidents)

@app.route("/api/services", methods=["POST"])
def add_service():
    data = request.get_json()

    service_name = data.get("service_name")
    service_url = data.get("service_url")

    if not service_name or not service_url:
        return jsonify({"error": "Service name and URL are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO services (service_name, service_url)
        VALUES (%s, %s)
    """, (service_name, service_url))

    connection.commit()

    new_service_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Service added successfully",
        "service_id": new_service_id
    }), 201



@app.route("/api/incidents/<int:incident_id>", methods=["PATCH"])
def update_incident(incident_id):
    data = request.get_json()

    status = data.get("status")
    assigned_to = data.get("assigned_to")
    escalate = data.get("escalate", False)

    if status not in ["OPEN", "IN_PROGRESS", "RESOLVED"]:
        return jsonify({"error": "Invalid incident status"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE incidents
            SET status = %s,
                assigned_to = %s,
                escalated_at = CASE
                    WHEN %s = 1 THEN CURRENT_TIMESTAMP
                    ELSE escalated_at
                END,
                resolved_at = CASE
                    WHEN %s = 'RESOLVED' THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END
            WHERE incident_id = %s
        """, (status, assigned_to, int(bool(escalate)), status, incident_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({"error": "Incident not found or no changes made"}), 404

        connection.commit()

        return jsonify({
            "message": "Incident updated successfully",
            "escalated": bool(escalate)
        }), 200

    except Exception as error:
        connection.rollback()
        print("Incident update error:", error)
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Uptime percentage
    cursor.execute("""
        SELECT
            service_id,
            COUNT(*) AS total_checks,
            ROUND(
                SUM(is_available = TRUE) * 100.0 / COUNT(*),
                2
            ) AS uptime_percentage
        FROM monitoring_history
        GROUP BY service_id
    """)
    uptime = cursor.fetchall()

    # P95 response time
    cursor.execute("""
        WITH ranked AS (
            SELECT
                service_id,
                response_time_ms,
                ROW_NUMBER() OVER (
                    PARTITION BY service_id
                    ORDER BY response_time_ms
                ) AS rn,
                COUNT(*) OVER (
                    PARTITION BY service_id
                ) AS total
            FROM monitoring_history
            WHERE response_time_ms IS NOT NULL
        )
        SELECT
            service_id,
            MAX(
                CASE
                    WHEN rn = CEIL(total * 0.95)
                    THEN response_time_ms
                END
            ) AS p95_response_time_ms
        FROM ranked
        GROUP BY service_id
    """)
    p95 = cursor.fetchall()

    # MTTR
    
    # MTTR
    cursor.execute("""
        SELECT
            service_id,
            COUNT(*) AS resolved_incidents,
            ROUND(
                AVG(
                    TIMESTAMPDIFF(
                        SECOND, opened_at, resolved_at
                    )
                ) / 60,
                2
            ) AS mttr_minutes
        FROM incidents
        WHERE status = 'RESOLVED'
          AND resolved_at IS NOT NULL
        GROUP BY service_id
    """)
    mttr = cursor.fetchall()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_incidents,
            SUM(status = 'OPEN') AS open_incidents,
            SUM(status = 'IN_PROGRESS') AS in_progress_incidents,
            SUM(status = 'RESOLVED') AS resolved_incidents
        FROM incidents
    """)

    incident_summary = cursor.fetchone()

    # Latest service health status
    cursor.execute("""
        SELECT
            s.service_id,
            s.service_name,
            mh.is_available,
            mh.status_code,
            mh.checked_at
        FROM services s
        LEFT JOIN monitoring_history mh
            ON mh.history_id = (
                SELECT MAX(history_id)
                FROM monitoring_history
                WHERE service_id = s.service_id
            )
        WHERE s.is_active = TRUE
    """)
    services = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({
        "services": services,
        "uptime": uptime,
        "p95_response_time": p95,
        "mttr": mttr,
        "incident_summary": incident_summary
    })


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    try:
        connection = get_db_connection()
        print("MySQL connected successfully!")
        connection.close()
    except Exception as error:
        print("MySQL connection failed:", error)
    
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        automatic_health_check,
        trigger="interval",
        seconds=60,
        id="service_health_check",
        max_instances=1
    )

    scheduler.start()
    print("ServiceWatch scheduler started. Checks run every 60 seconds.")

    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        scheduler.shutdown()

