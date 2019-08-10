# WebAppMetricCollector
Author: Jason Ray Norris
<br>
<hr>
The intention of this code is to collect metrics from a client system and report those metrics back to a central location.
<hr>
<b>!WARNING!: The config file is included as an example.  The example targets are currently google and hp.  Please do not use without evaluating the config.</b>
<h6>Usage 1.0</h6>
Please read over the configuration files.
You can currently execute from main.py or collect_http_metrics.py.
<br>
<hr>
<h6>Config 1.1</h6>

Please note the configuration file config.yml.
1. Each application target will create a threaded instance.
2. The request_file is located in the /Requests folder.
3. It is not recommended to set the interval timer less than 60.
4. If max_connection_thread_count is exceed, the threads will stop until a low threshold of 5 is met.  This is intended to control leaking.

<pre>
source_location:
    name: source_location_example_name
    number: source_location_example_number
    region: source_location_example_region
    host_name: source_location_example_name

application_targets:
    app1:
      name: Google
      host_target: www.google.com
      host_target_port: 80
      ssl: False
      request_file: http_get_google_example.txt
      interval_timer : 60
      log_level : Informational
      log_output_file : app1_log_output
      max_log_size : 50000
      max_connection_thread_count : 20
    app2:
      name: HP
      host_target: www.hp.com
      host_target_port: 443
      ssl: True
      request_file: http_get_hp_example.txt
      interval_timer : 60
      log_level : Informational
      log_output_file : app2_log_output
      max_log_size : 50000
      max_connection_thread_count : 20
</pre>
<br>


<hr>
<h6>Logging 1.1</h6>
The logging functions are currently per application.  I have not made it circular *yet.  When max log size is reached, the file will be recreated in order to keep disk impact minimized.
<br>
Logs are stored in the /logs folder.
<h6>Cool Stuff To Know 1.2</h6>
The HTTP UserAgent will be generated using:
<pre>
(site_region+site_number+site_name)

</pre>



