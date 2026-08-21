# TCP Load Balancer Simulator

A Python-based TCP socket load balancer simulator that distributes client requests across multiple backend servers using different load-balancing strategies.

The project also includes health checking, automatic server failure detection and recovery, metrics collection, a Metrics API, and a real-time monitoring dashboard.

---

## Features

- TCP socket-based load balancing
- Multiple backend servers
- Round Robin load balancing
- Least Connections load balancing
- Random server selection
- Weighted Round Robin
- Configurable server weights
- Concurrent client request handling
- Backend health checking
- Automatic server failure detection
- Automatic server recovery detection
- Active connection tracking
- Request and latency metrics
- Metrics REST API
- Web-based monitoring dashboard
- Concurrent load testing

---

## Architecture

```text
                         Client
                           |
                           | TCP
                           v
                  +-------------------+
                  |   Load Balancer   |
                  |    TCP :9000      |
                  +---------+---------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
       +-----------+  +-----------+  +-----------+
       | Server 1  |  | Server 2  |  | Server 3  |
       |   :8001   |  |   :8002   |  |   :8003   |
       +-----------+  +-----------+  +-----------+
             |              |              |
             +--------------+--------------+
                            |
                     Health Checker
                            |
                            v
                  +-------------------+
                  |    Metrics API    |
                  |     :9001         |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |     Dashboard     |
                  |     :8080         |
                  +-------------------+


                  ---

## Project Files

### Client

- `client/client.py` — Sends requests to the load balancer.
- `client/load_test.py` — Sends many concurrent requests for load testing.
- `client/strategy_test.py` — Tests the load-balancing strategies.

### Backend Server

- `server/backend_server.py` — Runs the backend servers that receive and process requests.

### Load Balancer

- `load_balancer/load_balancer.py` — Main load balancer. Accepts client connections and forwards requests to backend servers.
- `load_balancer/strategies.py` — Contains the four load-balancing algorithms:
  - Round Robin
  - Least Connections
  - Random
  - Weighted Round Robin
- `load_balancer/health_checker.py` — Checks whether backend servers are healthy.
- `load_balancer/metrics.py` — Collects request and latency statistics.
- `load_balancer/server_info.py` — Stores backend server information.

### Monitoring

- `monitoring/metrics_server.py` — Provides the Metrics API on port `9001`.
- `monitoring/dashboard.html` — Displays the load balancer metrics in the browser.

### Configuration

- `config/config.py` — Contains project configuration.

### Tests

- `tests/test_strategies.py` — Tests the load-balancing strategies.

### Other Files

- `README.md` — Project documentation.
- `.gitignore` — Prevents unnecessary files from being uploaded to GitHub.
- `requirements.txt` — Lists Python dependencies.
