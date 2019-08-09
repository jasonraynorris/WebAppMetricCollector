from collect_http_metrics import HTTPMetricCollector
import yaml
import threading

with open("config.yml", 'r') as yamlfile:
    cfg = yaml.load(yamlfile, Loader=yaml.Loader)
    metric_collectors = []
    for ap, v in cfg["application_targets"].items():
        metric_collectors.append(HTTPMetricCollector(v["interval_timer"],
                                                     v["host_target"],
                                                     v["host_target_port"],
                                                     v["ssl"],
                                                     v["log_output_file"],
                                                     v["request_file"],
                                                     cfg["source_location"]["name"],
                                                     cfg["source_location"]["number"],
                                                     cfg["source_location"]["region"],
                                                     v["name"], v["max_log_size"],
                                                     v["max_connection_thread_count"]))
    for metric_collector in metric_collectors:
        threading.Thread(target=metric_collector.start_collection).start()