#!/usr/bin/env python

from scapy.all import *
import argparse

class DNS_query:
    def __init__(self, query_id, req_type, req_ip, resp_ip, request, response, req_time, resp_time):
        self.query_id = query_id
        self.req_type =  req_type
        self.req_ip = req_ip
        self.resp_ip = resp_ip
        self.request =  request
        self.response = response
        self.req_time = req_time
        self.resp_time = resp_time

def check_query_id_exists(in_id, in_list):
    res = False
    list_idx = 0

    for obj in in_list:
        if in_id == getattr(obj, "query_id"):
            res = True
            break
        list_idx += 1

    return res, list_idx

def create_obj(in_pkt):
    ret_obj = None

    # create obj from a request
    if in_pkt.haslayer(DNSQR) and in_pkt[DNS].qr == 0: 
        ret_obj = DNS_query(in_pkt[DNS].id, in_pkt[DNSQR].qtype, in_pkt[IP].src, "", in_pkt[DNSQR].qname, [], in_pkt.time, "")

    # create obj from a response
    if in_pkt.haslayer(DNSRR) and in_pkt[DNS].qr == 1:
        num_responses = in_pkt.ancount
        resp_list = []
        for i in range(num_responses):
            resp_list.append(in_pkt[DNSRR][i].rdata)
                        
        ret_obj = DNS_query(in_pkt[DNS].id, 0, "", in_pkt[IP].src, "", resp_list, "", in_pkt.time)

    return ret_obj

def update_obj(in_pkt, in_obj):
    if in_pkt.haslayer(DNSQR) and in_pkt[DNS].qr == 0: 
        setattr(in_obj, "req_type", in_pkt[DNSQR].qtype)
        setattr(in_obj, "req_ip", in_pkt[IP].src)
        setattr(in_obj, "request", in_pkt[DNSQR].qname)
        setattr(in_obj, "req_time", in_pkt.time)

    if in_pkt.haslayer(DNSRR) and in_pkt[DNS].qr == 1:
        num_responses = in_pkt.ancount
        resp_list = []

        for i in range(num_responses):
            resp_list.append(in_pkt[DNSRR][i].rdata)

        setattr(in_obj, "resp_ip", in_pkt[IP].src)
        setattr(in_obj, "response", resp_list)
        setattr(in_obj, "resp_time", in_pkt.time)

    return in_obj

def write_csv(obj_list):
    f = open('dns_obj.csv', 'w')

    csv_output= "id,req_type,req_ip,resp_ip,request,response,req_time,resp_time\n"

    for obj in obj_list:
        csv_output += str(getattr(obj, "query_id")) + "," + str(getattr(obj, "req_type")) + "," + str(getattr(obj, "req_ip")) + "," +  str(getattr(obj, "resp_ip")) + "," + str(getattr(obj, "request")) + "," + str(getattr(obj, "response")).replace(",",";") + "," + str(getattr(obj, "req_time")) + "," + str(getattr(obj, "resp_time")) + "\n"

    f.write(csv_output)

    f.close()

    return

def process_pcap(pcap_path):
    pdns_pcap = rdpcap(pcap_path)

    obj_list = []

    for pkt in pdns_pcap:
        if pkt.haslayer(DNS):
            obj_exists = False
            obj_index = 0

            # check if query_id already in the list
            obj_exists, obj_index = check_query_id_exists(pkt[DNS].id, obj_list)               

            if obj_exists:
                # update obj
                obj_list[obj_index] = update_obj(pkt, obj_list[obj_index])
            else:
                # add new obj
                obj_list.append(create_obj(pkt))

    return obj_list

def dns_sniff(in_pkt):
    if in_pkt.haslayer(DNSQR) and in_pkt[DNS].qr == 0:
        print "Request " + str(in_pkt[DNS].id) + " : " + in_pkt[IP].src + " -> " + in_pkt[DNSQR].qname + " at " + str(in_pkt.time)

    if in_pkt.haslayer(DNSRR) and in_pkt[DNS].qr == 1:
        num_responses = in_pkt.ancount
        resp_list = []

        for i in range(num_responses):
            resp_list.append(in_pkt[DNSRR][i].rdata)

        print "Response " + str(in_pkt[DNS].id) + " : " + in_pkt[IP].src + " -> " + str(resp_list) + " at " + str(in_pkt.time)

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS requests and responses")
    parser.add_argument("-p", "--pcap", type=str, required=False, help="Path to pcap") 
    parser.add_argument("-i", "--interface", type=str, required=False, help="Interface to sniff") 
    args = parser.parse_args() # args.pcap, args.interface

    if args.pcap:
        dns_query_list = process_pcap(args.pcap)
           
        write_csv(dns_query_list)

    if args.interface:
        sniff(iface=args.interface, filter = "port 53", prn = dns_sniff, store = 0)

    quit()
