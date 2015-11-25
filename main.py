import os
import time
from threading import Thread
import consulrequest
import metadatarequest


def start_host_container_agent_register():
    curr_registered_services = []
    host_dict = {}
    sleep_time = os.environ.get("TIME", "10")
    consul_url = os.environ.get("CONSUL")
    while True:
        host_dict = metadatarequest.MetadataRequest.get_all_hosts(host_dict)
        register_containers = []
        need_register_containers, consul_client = metadatarequest.MetadataRequest.get_all_register_containers()
        try:
            if not consul_url:
                consul_url = host_dict[consul_client.host_uuid].agent_ip
        except KeyError:
            print("Cannot get consul client ip")
            break
        except AttributeError:
            print("Cannot get consul client container")
            break
        for i in need_register_containers:
            try:
                register_host = host_dict[i.host_uuid]
            except KeyError:
                print("No Matching Host, Ignored: "+i.name)
                continue
            register_containers.extend(consulrequest.ConsulRequest.agent_register_container(i,
                                                                                            register_host,
                                                                                            consul_url,
                                                                                            curr_registered_services))
        for n in curr_registered_services:
            if n not in register_containers:
                consulrequest.ConsulRequest.agent_deregister_service(n, consul_url)
                
        curr_registered_services = register_containers
        time.sleep(int(sleep_time))


def main():
    thread = Thread(target=start_host_container_agent_register)
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
