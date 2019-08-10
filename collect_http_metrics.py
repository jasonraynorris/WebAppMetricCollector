import socket
import ssl
import json
import time
import datetime
import yaml
import threading

print_out = True
debug = False

class HTTPMetricCollector(object):
    def __init__(self,interval, targethost,targetport,ssl_bool,log_file_name,request_file_name,site_name,site_number,site_region,application_name,max_log_size,max_connection_thread_count):
        self.max_connection_thread_count = max_connection_thread_count
        self.application_name = application_name
        self.site_region = site_region
        self.site_number = site_number
        self.site_name = site_name
        self.targethost = targethost
        self.targetport = targetport
        self.ssl_bool = ssl_bool
        self.interval = interval
        self.context = ssl.create_default_context()
        request_file = open("Requests\\" + request_file_name,"r")
        self.encoded_request = request_file.read().encode()
        self.max_log_size = max_log_size
        self.log_file_name = log_file_name;
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.stop_threads = False


    def log(self,message=""):
        self.log_file = open("logs\\" + self.log_file_name, "a+")
        if self.log_file.__sizeof__() > self.max_log_size:
            self.log_file = open("logs\\" + self.log_file_name, "w+")

        self.log_file.write(message)
        self.log_file.close()

    def start_collection(self):
        self.log()
        threads = []
        while True:
            try:
                if len(threads) > self.max_connection_thread_count:
                    self.stop_threads = True
                elif len(threads) < 5:
                    self.stop_threads = False
                threads.append(threading.Thread(target=self.collect_http_application_metric).start())
                time.sleep(self.interval)
            except Exception as ex:
                self.log(ex)
                time.sleep(self.interval)

    def collect_http_application_metric(self):
        time_stamp = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        start_tcp_handshake = time.time()
        with socket.create_connection((self.targethost, self.targetport)) as sock:
            cur_tcp_handshake_rtt = format((time.time() - start_tcp_handshake) * 1000,'.2f')
            target_ip, target_port = sock.getpeername()

            if self.ssl_bool:
                start_ssl_negotiation = time.time()
                with self.context.wrap_socket(sock, server_hostname=self.targethost) as ssock:
                    cur_ssl_negotiation_rtt = format(float((time.time() - start_ssl_negotiation)) * 1000,'.2f')
                    start_application_request = time.time()
                    """Sends all data before returning"""
                    ssock.sendall(self.encoded_request)
                    data_rx = ssock.recv(1024)
                    ssl_ver = ssock.version()
                    ssock.close()
            else:
                cur_ssl_negotiation_rtt = 0
                ssl_ver = "None"
                start_application_request = time.time()
                sock.sendall(self.encoded_request)
                sock.close()
            cur_request_to_return_rtt = format(float(time.time() - start_application_request) * 1000,'.2f')
            try:
                http_return_code = (data_rx.decode('utf-8').splitlines()[0])
            except:
                http_return_code = "None"
        cur_total_net_time_rtt = format(float(cur_tcp_handshake_rtt) + float(cur_ssl_negotiation_rtt),'.2f')
        cur_total_transaction_rtt = format(float(cur_total_net_time_rtt) + float(cur_request_to_return_rtt),'.2f')
        response_metrics = {
            "timestamp": str(time_stamp),
            "application_name": self.application_name,
            "interval_timer": str(self.interval),
            "localhost":{
                "hostname" : str(self.host_name),
                "host_ip" : str(self.host_ip),
            },
            "targethost": {
                "target_hostname": str(self.targethost),
                "target_ip": str(target_ip),
                "target_port": str(target_port),
            },
            "transaction": {
                "tcp_handshake_rtt" : str(cur_tcp_handshake_rtt),
                "ssl_bool": str(self.ssl_bool),
                "ssl_ver": ssl_ver,
                "ssl_negotiation_rtt": str(cur_ssl_negotiation_rtt),
                "application_rtt": str(cur_request_to_return_rtt),
                "total_transaction_rtt": str(cur_total_transaction_rtt),
                "http_return_code":str(http_return_code)
                },
            "location":{
                "site_name":self.site_name,
                "site_number":self.site_number,
                "site_region":self.site_region,
                   }

        }
        if print_out:
            print(self.encoded_request)
            print(json.dumps(response_metrics, indent=4))
        if debug:
            self.log("DEBUG:%s\n" % response_metrics)
        else:
            self.log()

if __name__ == '__main__':
    with open("config.yml", 'r') as yamlfile:
        cfg = yaml.load(yamlfile,Loader=yaml.Loader)
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
                                                          v["name"],v["max_log_size"],
                                                         v["max_connection_thread_count"]))
        for metric_collector in metric_collectors:
            threading.Thread(target=metric_collector.start_collection).start()




