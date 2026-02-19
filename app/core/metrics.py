from prometheus_client import Counter, Gauge, Histogram

# some example metrics; routers and services should import and increment them

request_count = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
)

active_sources = Gauge("sources_active", "Number of active sources")

scrape_duration = Histogram("scrape_duration_seconds", "Duration of RSS scrape")
