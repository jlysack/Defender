# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 09:19:37 2023

@author: Pat Zazzaro
"""

import rti.connextdds as dds
import rti.request as request
import argparse
import time
from interfaces import DDS


def requester_main(domain_id, n, primes_per_reply):
    participant = dds.DomainParticipant(domain_id)
    qos_provider = dds.QosProvider.default
    #type_provider = dds.QosProvider("USER_QOS_PROFILES.xml")
    #request_type = type_provider.type("DDS.IFF.IFFRequest")
    #reply_type = type_provider.type("DDS.IFF.IFFResponse")
    #status_type = type_provider.type("IFFDetermination_Status")

    #requester = request.Requester(
            #request_type,
           # reply_type,
           # participant,
           # service_name="PrimeCalculator",
           # datawriter_qos=qos_provider.datawriter_qos_from_profile("RequestReplyExampleProfiles::RequesterExampleProfile"),
          #  datareader_qos=qos_provider.datareader_qos_from_profile("RequestReplyExampleProfiles::RequesterExampleProfile"))

    print("Waiting to discover replier on domain {}...".format(domain_id))
    
    while request_id.matched_replier_count == 0:
        time.sleep(0.1)

    prime_number_request = dds.DynamicData(request_type)
    prime_number_request["n"] = n
    prime_number_request["primes_per_reply"] = primes_per_reply

    print(
        "Sending a request for the IFF Status of the UAV".format(
            n,
            primes_per_reply
        )
    )

    request_id = requester.send_request(prime_number_request)

    max_wait = dds.Duration.from_seconds(20)
    in_progress = True
    while in_progress:
        if not requester.wait_for_replies(max_wait, related_request_id=request_id):
            raise dds.TimeoutError("Timed out waiting for replies")

        for reply in (r.data for r in requester.take_replies(request_id) if r.info.valid):
            primes = reply["primes"]
            for prime in primes:
                print(prime)
            
            if reply["status"] != status_type["REPLY_IN_PROGRESS"]:
                in_progress = False
                if reply["status"] == status_type["REPLY_ERROR"]:
                    raise RuntimeError("Error in replier")
        
    print("DONE")
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IFF Request-Response Code: Requester (Main Tactical Assembly)"
    )
    parser.add_argument("-d", "--domain", type=int, default=0, help="DDS Domain ID (default: 0)")
    parser.add_argument(
        "-c", "--count", type=int, default=5, help="Number of primes per reply (min: 5, default: 5)"
    )
    parser.add_argument("n", type=int, help="Request will retrieve prime numbers <= n")

    args = parser.parse_args()
    assert 0 <= args.domain < 233
    assert args.count >= 5

    requester_main(args.domain, args.n, args.count)