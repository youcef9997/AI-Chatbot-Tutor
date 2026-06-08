# Responsible for limiting user input.
# User must wait 5 seconds in between requests.
# This is to reduce usage for both security and limited
# software resources 

import time

request_times = {}


def check_rate_limit(client_ip, cooldown_seconds=5):
   
    current_time = time.time()
    last_time = request_times.get(client_ip, 0)

    if current_time - last_time < cooldown_seconds:
        return False, "Please wait a moment before sending another request."

    request_times[client_ip] = current_time
    return True, None