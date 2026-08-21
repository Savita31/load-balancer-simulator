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