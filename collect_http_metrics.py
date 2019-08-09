import socket
import ssl
import json
import time
from urllib3.util.url import parse_url

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

class HTTPMetricCollector(object):
    def __init__(self,sleeptimer,iteration_count,target,log_output_file_name,request_from_file):
        self.collect_http_application_metric(timetowait_in_sec=sleeptimer, iterations=iteration_count, targethost=target, file_out_metrics_name=log_output_file_name,request=request_from_file)
    def build_http_request(self,req_type, url, headers=None, body=""):
        url = parse_url(url)
        hostname = str(url.hostname)
        path = url.path or "/"
        uri = path
        if headers:
            formatted_headers = "".join("{}:{}\r\n".format(k, v) for k, v in headers.items()) + "\r\n" + "\r\n"
        else:
            formatted_headers = "\r\n" + "\r\n"

        requestGet = "GET " + uri + " HTTP/1.1" + "\r\n" +\
                     "Host:" + hostname + "\r\n" +\
                     formatted_headers

        requestPost = "POST " + uri + " HTTP/1.1" + "\r\n" +\
                      "Host: " + hostname + "\r\n" +\
                      "Content-Length: " + str(len(body)) + "\r\n" +\
                      formatted_headers+\
                      body + "\r\n" + "\r\n"

        if req_type=="POST":
            print("********************************************\n" + repr(requestPost))
            print("********************************************\n" + "*****************REQUEST********************\n" + "********************************************\n" + requestPost + "********************************************\n")
            return requestPost.encode()
        else:
            print("********************************************\n" + repr(requestGet))
            print("********************************************\n" + "*****************REQUEST********************\n" + "********************************************\n" + requestGet + "********************************************\n")
            return requestGet.encode()

    def collect_http_application_metric(self,timetowait_in_sec, iterations, targethost, file_out_metrics_name,request):
        """Prepare static vars"""
        context = ssl.create_default_context()
        encoded_request = request.encode()
        file_out_metrics = open(file_out_metrics_name,"w+")
        """"""
        """Run loop"""
        for x in range(iterations):
            start_tcp_handshake = time.time()
            with socket.create_connection((targethost, 443)) as sock:
                cur_tcp_handshake_rtt = format((time.time() - start_tcp_handshake) * 1000,'.2f')
                start_ssl_negotiation = time.time()
                with context.wrap_socket(sock, server_hostname=targethost) as ssock:
                    cur_ssl_negotiation_rtt = format(float((time.time() - start_ssl_negotiation)) * 1000,'.2f')
                    start_application_request = time.time()
                    """Sends all data before returning"""
                    ssock.sendall(encoded_request)
                    data_rx = ssock.recv(1024)
                    cur_request_to_return_rtt = format(float(time.time() - start_application_request) * 1000,'.2f')
                    """"""
                    ssock.close()
                    http_return_code = (data_rx.decode('utf-8').splitlines()[0])
            cur_total_net_time_rtt = format(float(cur_tcp_handshake_rtt) + float(cur_ssl_negotiation_rtt),'.2f')
            cur_total_transaction_rtt = format(float(cur_total_net_time_rtt) + float(cur_request_to_return_rtt),'.2f')
            response_metrics = {
                "tcp_handshake_rtt" : str(cur_tcp_handshake_rtt),
                "ssl_negotiation_rtt)": str(cur_ssl_negotiation_rtt),
                "application_rtt": str(cur_request_to_return_rtt),
                "total_transaction_rtt": str(cur_total_transaction_rtt),
                "http_return_code":str(http_return_code)
            }
            #file_out_metrics.write(str(response_metrics))
            time.sleep(timetowait_in_sec)
            print(json.dumps(response_metrics))
        """
        Close
        """
        file_out_metrics.close()

"""
Test VARS
"""
sleeptimer = 1
iteration_count = 15
target = "www.hp.com"
request_file = open("http_get_example.txt","r",newline="\r\n")
log_output_file_name = "text_out.csv"

request_from_file = (request_file.read())
HTTPMetricCollector(sleeptimer,iteration_count,target,log_output_file_name,request_from_file)



