
import os
import yaml
from pprint import pprint

os.system('scp root@172.16.60.10:/etc/hosts hosts')
def parse_hosts_file(file_path):
    host_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
            # Skip commented lines or empty lines
            if line.strip().startswith('#') or not line.strip():
                continue

            # Split the line by whitespace
            parts = line.split()

            # Extract the IP and hosts
            ip = parts[0]
            hosts = parts[1:]

            # Add hosts to the dictionary
            if ip in host_dict:
                host_dict[ip].extend(hosts)
            else:
                host_dict[ip] = hosts

    return host_dict


# Usage example
hosts_file_path = 'hosts'  # Replace with the path to your hosts file

result = parse_hosts_file(hosts_file_path)
for ip, hosts in result.items():
    print(f'{ip}: {", ".join(hosts)}')



# Prepare the data in the format required by hostAliases
host_aliases = []
for ip, hosts in result.items():
    host_alias = {
        "ip": ip,
        "hostnames": hosts
    }
    host_aliases.append(host_alias)

# Create the YAML content
yaml_content = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
        "name": "example-pod"
    },
    "spec": {
        "hostAliases": host_aliases,
        "containers": [
            # Add your containers here
        ]
    }
}

# Save the YAML content to a file
with open('host_aliases.yaml', 'w') as file:
    yaml.dump(yaml_content, file)