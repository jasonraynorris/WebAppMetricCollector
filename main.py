from collect_http_metrics import HTTPMetricCollector
import yaml
import threading

with open("config.yml", 'r') as yamlfile:
    cfg = yaml.load(yamlfile, Loader=yaml.Loader)
    metric_collectors = []
    for ap in cfg["application_targets"]:
        metric_collectors.append(HTTPMetricCollector(ap["interval_timer"],
                                                     ap["host_target"],
                                                     ap["host_target_port"],
                                                     ap["ssl"],
                                                     ap["log_output_file"],
                                                     ap["request_file"],
                                                     cfg["source_site"]["site_name"],
                                                     cfg["source_site"]["site_number"],
                                                     cfg["source_site"]["site_region"],
                                                     ap["name"],
                                                     ap["max_log_size"],
                                                     ap["max_connection_thread_count"]))
    for metric_collector in metric_collectors:
        threading.Thread(target=metric_collector.start_collection).start()