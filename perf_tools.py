import socket
import ssl
import os
import time
import datetime
import sys
from urllib3.util.url import parse_url
import argparse

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

# define our clear function
def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def build_http_request(req_type, url, headers=None, body=""):
    url = parse_url(url)
    hostname = str(url.hostname)
    path = url.path or "/"
    #port = url.port or 80
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


def collect_http_application_metric(timetowait_in_sec, iterations, targethost, file_out_metrics_name,request):
    """Prepare static vars"""
    context = ssl.create_default_context()
    encoded_request = request.encode()
    file_out_metrics = open(file_out_metrics_name,"w+")
    min_tcp_handshake_rtt = 9999
    max_tcp_handshake_rtt = 0
    min_ssl_negotiation_rtt = 9999
    max_ssl_negotiation_rtt = 0
    min_total_net_time_rtt = 9999
    max_total_net_time_rtt = 0
    min_request_to_return_rtt = 9999
    max_request_to_return_rtt = 0
    min_total_transaction_rtt = 9999
    max_total_transaction_rtt = 0
    min_total_exec_time = 9999
    max_total_exec_time = 0
    """"""
    """Run single"""
    file_out_metrics.write("timestamp,tcp_handshake,ssl_negotiation,total_net_time,return_code,request_to_response,total_transaction,total_execution\n")
    """"""
    """Run loop"""
    for x in range(iterations):
        start_total_exec_time = time.time()
        timestamp = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        start_tcp_handshake = time.time()
        with socket.create_connection((targethost, 443)) as sock:
            cur_tcp_handshake_rtt = format((time.time() - start_tcp_handshake) * 1000,'.2f')
            start_ssl_negotiation = time.time()
            with context.wrap_socket(sock, server_hostname=targethost) as ssock:
                cur_ssl_negotiation_rtt = format(float((time.time() - start_ssl_negotiation)) * 1000,'.2f')
                ssock_ver = str(ssock.version())

                start_application_request = time.time()
                """Sends all data before returning"""
                ssock.sendall(encoded_request)
                data_rx = ssock.recv(1024)
                cur_request_to_return_rtt = format(float(time.time() - start_application_request) * 1000,'.2f')
                """"""
                #start_application_response = time.time()

                #cur_end_application_response_tto = format((time.time() - start_application_response) * 1000,'.2f')
                ssock.close()

                http_return_code = (data_rx.decode('utf-8').splitlines()[0])



        cur_total_exec_time = format(float(time.time() - start_total_exec_time) * 1000, ".2f")
        cur_total_net_time_rtt = format(float(cur_tcp_handshake_rtt) + float(cur_ssl_negotiation_rtt),'.2f')
        #cur_request_to_return_rtt = format(float(cur_end_application_request_tto) + float(cur_end_application_response_tto),'.2f')
        cur_total_transaction_rtt = format(float(cur_total_net_time_rtt) + float(cur_request_to_return_rtt),'.2f')
        """
        Get TCP HSHAKE Min/Max
        """
        if float(cur_tcp_handshake_rtt) < min_tcp_handshake_rtt:
            min_tcp_handshake_rtt = float(cur_tcp_handshake_rtt)
        if float(cur_tcp_handshake_rtt) > max_tcp_handshake_rtt:
            max_tcp_handshake_rtt = float(cur_tcp_handshake_rtt)
        """
        Get SSL Min/Max
        """
        if float(cur_ssl_negotiation_rtt) < min_ssl_negotiation_rtt:
            min_ssl_negotiation_rtt = float(cur_ssl_negotiation_rtt)
        if float(cur_ssl_negotiation_rtt) > max_ssl_negotiation_rtt:
            max_ssl_negotiation_rtt = float(cur_ssl_negotiation_rtt)
        """
        Get Net Time Min/Max
        """
        if float(cur_total_net_time_rtt) < min_total_net_time_rtt:
            min_total_net_time_rtt = float(cur_total_net_time_rtt)
        if float(cur_total_net_time_rtt) > max_total_net_time_rtt:
            max_total_net_time_rtt = float(cur_total_net_time_rtt)
        """
        Get Http Request Min/Max
        """
        # if float(cur_end_application_request_tto) < min_end_application_request_tto:
        #     min_end_application_request_tto = float(cur_end_application_request_tto)
        # if float(cur_end_application_request_tto) > max_end_application_request_tto:
        #     max_end_application_request_tto = float(cur_end_application_request_tto)
        # """
        # Get Http Response Min/Max
        # """
        # if float(cur_end_application_response_tto) < min_end_application_response_tto:
        #     min_end_application_response_tto = float(cur_end_application_response_tto)
        # if float(cur_end_application_response_tto) > max_end_application_response_tto:
        #     max_end_application_response_tto = float(cur_end_application_response_tto)
        """
        Get Http Request+Response Min/Max
        """
        if float(cur_request_to_return_rtt) < min_request_to_return_rtt:
            min_request_to_return_rtt = float(cur_request_to_return_rtt)
        if float(cur_request_to_return_rtt) > max_request_to_return_rtt:
            max_request_to_return_rtt = float(cur_request_to_return_rtt)
        """
        Get Transaction Min/Max
        """
        if float(cur_total_transaction_rtt) < min_total_transaction_rtt:
            min_total_transaction_rtt = float(cur_total_transaction_rtt)
        if float(cur_total_transaction_rtt) > max_total_transaction_rtt:
            max_total_transaction_rtt = float(cur_total_transaction_rtt)
        """
        Get Execution Min/Max
        """
        if float(cur_total_exec_time) < min_total_exec_time:
            min_total_exec_time = float(cur_total_exec_time)
        if float(cur_total_exec_time) > max_total_exec_time:
            max_total_exec_time = float(cur_total_exec_time)
        """Always save/archive total transaction returns for Min and Max"""
        #print("%20s%20s%20s%20s%20s%40s%15s%15s%20s%15s\n" % (timestamp,str(out_tcp_handshake_rtt * 1000)[:5]+"ms",str(out_ssl_neg_tto * 1000)[:5]+"ms",ssock_ver,str(total_net_time * 1000)[:5]+"ms",http_return_code,str(out_end_application_request_tto * 1000)[:5]+"ms",str(out_end_application_response_tto * 1000)[:5]+"ms",str(request_to_return * 1000)[:5]+"ms",str(total_transaction * 1000)[:5]+"ms"))
        # if(x % 10 == 0):
        #     clear()
        #     print("\r")
        #     print("%14s|%30s|%30s|%30s|%30s|%30s|%30s|%30s|%30s" % ("data_points", "tcp_handshake",
        #                                                                                 "ssl_negotiation", "total_net_time",
        #                                                                                 "http_request",
        #                                                                                 "http_response",
        #                                                                                 "http_request&response",
        #                                                                                 "total_transaction",
        #                                                                                 "total_execution"))
        #     # print("%10s%20s%20s%10s%20s%40s%20s%20s%20s%20s\n" % ("","<---->", "<---->", "", "<---->", "","----->","<-----","<---->","<---->"))
        #     print("\033[4m%14s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|\033[0m" % (
        #     "", "CUR","MIN","MAX","CUR","MIN","MAX","CUR","MIN","MAX","CUR","MIN","MAX","CUR","MIN","MAX",
        #     "CUR","MIN","MAX","CUR","MIN","MAX","CUR","MIN","MAX"))
        #
        # print("%14s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s|%10s%10s%10s" %
        #                                                                     (str(x+1) + "/"+ str(iterations),
        #
        #                                                                     str(cur_tcp_handshake_rtt),
        #                                                                     str(min_tcp_handshake),
        #                                                                     str(max_tcp_handshake),
        #
        #                                                                     str(cur_ssl_negotiation_rtt),
        #                                                                     str(min_ssl_negotiation_rtt),
        #                                                                     str(max_ssl_negotiation_rtt),
        #
        #                                                                     str(cur_total_net_time_rtt),
        #                                                                     str(min_total_net_time_rtt),
        #                                                                     str(max_total_net_time_rtt),
        #
        #                                                                     str(cur_end_application_request_tto),
        #                                                                     str(min_end_application_request_tto),
        #                                                                     str(max_end_application_request_tto),
        #
        #                                                                     str(cur_end_application_response_tto),
        #                                                                     str(min_end_application_response_tto),
        #                                                                     str(max_end_application_response_tto),
        #
        #                                                                     str(cur_request_to_return_rtt),
        #                                                                     str(min_request_to_return_rtt),
        #                                                                     str(max_request_to_return_rtt),
        #
        #                                                                     str(cur_total_transaction_rtt),
        #                                                                     str(min_total_transaction_rtt),
        #                                                                     str(max_total_transaction_rtt),
        #
        #                                                                     str(cur_total_exec_time),
        #                                                                     str(min_total_exec_time),
        #                                                                     str(max_total_exec_time)
        #                                                                   ))
        clear()
        print("\n")
        print(request)
        print(UNDERLINE +
                          "iteration_count:%-14s\n"
                          "sleep_timer:%-14s\033[0;0m\n\n"
                          "<-->"
              "|\033[;7m         tcp_handshake:\033[1;34m%-10s \033[0;0m|min:\033[0;32m%-10s\033[0;0m |max:\033[1;31m%-10s\033[0;0m\n"
                          "      |+\033[1;35m%s\033[0;0m\n"
                          "      |\n"
                          "<-----|-->"                          
              "|\033[;7m       ssl_negotiation:\033[1;34m%-10s \033[0;0m|min:\033[0;32m%-10s\033[0;0m |max:\033[1;31m%-10s\033[0;0m\n"
                          "           |Negotiated Suite:%s\n"

                          "<----------|+\033[1;35m%s\033[0;0m\n"
                          "           |\n"
                          "<----------|-->"

              "|\033[;7m          request and response:\033[1;34m%-10s \033[0;0m|min:\033[0;32m%-10s\033[0;0m |max:\033[1;31m%-10s\033[0;0m\n"
                          "               |HTTP Response:%s\n"
                          "               |=\033[1;35m%s\033[0;0m\n"
                          "<--------------|\n\n"                                             
            "******************************************************************\n"
              "|\033[;7m        total_net_time:\033[1;34m%-10s \033[0;0m|min:\033[0;32m%-10s\033[0;0m |max:\033[1;31m%-10s\033[0;0m\n"            
              "|\033[;7m     total_transaction:\033[1;34m%-10s \033[0;0m|min:\033[0;32m%-10s\033[0;0m |max:\033[1;31m%-10s\033[0;0m\n"
              "|\033[;7m       total_execution:\033[1;34m%-10s \033[0;0m|min:\033[0;32m%-10s\033[0;0m |max:\033[1;31m%-10s\033[0;0m" %
                                                                            ((str(x+1) + "/"+ str(iterations),
                                                                              str(sleeptimer)+"/second",

                                                                            str(cur_tcp_handshake_rtt)+"ms",
                                                                            str(min_tcp_handshake_rtt)+"ms",
                                                                            str(max_tcp_handshake_rtt)+"ms",

                                                                             str(format(float(cur_tcp_handshake_rtt),'.2f'))+"ms",

                                                                            str(cur_ssl_negotiation_rtt)+"ms",
                                                                            str(min_ssl_negotiation_rtt)+"ms",
                                                                            str(max_ssl_negotiation_rtt)+"ms",
                                                                              str(ssock_ver),
                                                                            str(format(float(cur_total_net_time_rtt),'.2f'))+"ms",

                                                                             str(cur_request_to_return_rtt)+"ms",
                                                                             str(min_request_to_return_rtt)+"ms",
                                                                             str(max_request_to_return_rtt)+"ms",

                                                                            # str(cur_end_application_request_tto),
                                                                            # str(min_end_application_request_tto),
                                                                            # str(max_end_application_request_tto),
                                                                            #
                                                                            # str(format(float(cur_total_net_time_rtt)+float(cur_end_application_request_tto),'.2f')),
                                                                            #
                                                                            # str(cur_end_application_response_tto),
                                                                            # str(min_end_application_response_tto),
                                                                            # str(max_end_application_response_tto),
                                                                              http_return_code,
                                                                             str(format(float(cur_total_transaction_rtt),'.2f'))+"ms",

                                                                             str(cur_total_net_time_rtt)+"ms",
                                                                             str(min_total_net_time_rtt)+"ms",
                                                                             str(max_total_net_time_rtt)+"ms",


                                                                            str(cur_total_transaction_rtt)+"ms",
                                                                            str(min_total_transaction_rtt)+"ms",
                                                                            str(max_total_transaction_rtt)+"ms",

                                                                            str(cur_total_exec_time)+"ms",
                                                                            str(min_total_exec_time)+"ms",
                                                                            str(max_total_exec_time)+"ms"

                                       )))
        file_out_metrics.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (timestamp,str(cur_tcp_handshake_rtt),str(cur_ssl_negotiation_rtt),ssock_ver,str(cur_total_net_time_rtt),http_return_code,str(cur_request_to_return_rtt),str(cur_total_transaction_rtt),str(cur_total_exec_time)))
        time.sleep(timetowait_in_sec)
    """
    Close
    """
    file_out_metrics.close()



# post = True
# post_data_file_name = "data.json"
#
# post_data_file = open("data.json","r")
# request_file_name = "http_request_example.txt"
#request = build_http_request(req_type="GET", url="www.hertz.com/", headers={"Content-Type":"application/json","User-Agent":"PerformanceTester"}, body="")
#request = build_http_request(req_type="POST", url="www.hertz.com", headers={"Content-Type":"application/json","User-Agent":"PerformanceTester"}, body=post_data_file.read())

"""
Input Collection Scripting
"""
# sleeptimer = float(input("Enter sleep timer between iterations in seconds(floating points):"))
# iteration_count = int(input("Enter total iterations:"))
# target = input("Enter target(example:www.google.com):")
# request_input_file_name = input("request_file_name(example:http_get_example.txt):")
# request_file = open(request_input_file_name,"r",newline="\r\n")
# log_output_file_name = input("log_output_file_name(example:http_app_stack_metrics.csv):")
"""
Test VARS
"""
sleeptimer = 1
iteration_count = 15
target = "www.hp.com"
request_file = open("http_get_example.txt","r",newline="\r\n")
log_output_file_name = "text_out.csv"

"""
use file or request builder?
"""
#request = build_http_request(req_type=request_type, url=url, headers=headers, body=body)
request_from_file = (request_file.read())
#request_from_function = (request)
collect_http_application_metric(sleeptimer,iteration_count,target,log_output_file_name,request_from_file)


# parser = argparse.ArgumentParser(description='This is used to collect complete static performance metrics on http applications')
# parser.add_argument('-s','--sleep', help='Time in seconds to sleep between test iterations', required=True)
# parser.add_argument('-i','--iterations', help='Total iteration count before completing test', required=True)
# parser.add_argument('-t','--target', help='Target host(example:www.hertz.com)', required=True)
# parser.add_argument('-rf','--inrequestfile', help='File containing http request(example:http_get_example.txt)', required=True)
# parser.add_argument('-mf','--outmetricfile', help='File name for storing comma dilemeted metric data', required=False)
# args = vars(parser.parse_args())

# collect_http_application_metric(float(args["sleep"]),int(args["iterations"]),str(args["target"]),str(args["outmetricfile"]),str(args["inrequestfile"]))


