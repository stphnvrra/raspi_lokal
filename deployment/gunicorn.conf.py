"""
Gunicorn configuration optimized for Raspberry Pi 4B (4GB RAM).
"""
import multiprocessing

# Bind to all interfaces on port 8000
bind = "0.0.0.0:8000"

# Workers: For Pi 4 with 4GB RAM, use 2 workers
# Formula: (2 x CPU cores) + 1, but limited for memory
workers = 2

# Worker class: sync is most memory-efficient for Pi
worker_class = "sync"

# Threads per worker: Keep low for memory efficiency
threads = 2

# Worker timeout: Increase for slow AI responses
timeout = 180

# Graceful timeout
graceful_timeout = 30

# Keep-alive connections
keepalive = 5

# Maximum requests per worker before restart (prevents memory leaks)
max_requests = 500
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Process naming
proc_name = "lokal"

# Preload app for faster worker spawning (uses more memory but faster restarts)
preload_app = False  # Disabled for memory efficiency on Pi

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

