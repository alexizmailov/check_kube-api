#!/usr/bin/env python3

# A simple script to check against the kubernetes API, at present it can check EITHER:
#
# -c nodescordoned (for cordoned nodes)
# OR
# -c podsready (for pods not in a ready state)
#
# Requires a kubeconfig file to be passed to the script with -k or --kubeconfig, e.g:
#
# -k kube-monitoring.yaml
#
# -m NUMBER - limits output to NUMBER in case we have an outage and MANY broken pods
#
# Exit codes:
# 0 - No cordoned nodes or all pods are ok
# 1 - Cordoned nodes or pods not ready detected
# 2 - kubectl or API error

import argparse, subprocess

parser = argparse.ArgumentParser(description="Kubernetes checker")
parser.add_argument('-k', '--kubeconfig', help='Path to kubernetes config yaml file')
parser.add_argument('-c', '--check', help='Check cordoned state or pods status')
parser.add_argument('-m', '--maxpods', type=int, help='Limit number of broken pods in output')
args = parser.parse_args()

# Arguments
if args.kubeconfig:
  kubeconfig = args.kubeconfig
else:
  print("-k Path-to-kubeconfig is required")
  exit(2)

if args.check:
  check = args.check
  if check not in "nodescordoned podsready":
    print("-c nodescordoned | podsready argument is required")
    exit(2)
else:
  print("-c nodescordoned | podsready argument is required")
  exit(2)


# Checking cordoned nodes
if check == 'nodescordoned':
  nodes = []
  command = "kubectl --kubeconfig %s get nodes" % kubeconfig

  process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  OUTPUT, err = process.communicate()
  if process.returncode != 0:
    print("CRITICAL: API error")
    exit(2)


  node_list = OUTPUT.decode('utf8').split('\n')

  del node_list[0] # Item 0 is a title: NAME          STATUS   ROLES    AGE    VERSION
  for node in node_list:
    node = " ".join(node.split()).split() # Converts multiple spaces in rows into single ones
    if len(node) and node[1] != "Ready":  # If there are any nodes and column 2 != "Ready"
      nodes.append(node[0])               # Add them to the list of bad nodes
  if len(nodes):                          # If there are more than 0 of "not Ready" nodes
    print("WARNING: cordoned nodes found: %s" % (" ".join(nodes)))
    exit(1)
  else:
    print("OK: no cordoned nodes")
    exit(0)
# End of checking cordoned nodes

# Checking pods
elif check == 'podsready':
  pods = []
  command = "kubectl --kubeconfig %s get pods --no-headers --all-namespaces" % kubeconfig

  process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  OUTPUT, err = process.communicate()
  if process.returncode != 0:
    print("CRITICAL: API error")
    exit(2)



  pods_list = OUTPUT.decode('utf8').split('\n')

  if args.maxpods: # If max number of results specified - limit the output
    MAX_PODS_SHOWN = args.maxpods
  else:
    MAX_PODS_SHOWN=len(pods_list)

  for line in pods_list:
    pod_info = " ".join(line.split()).split() # Converts multiple spaces in rows into single ones
    if len(pod_info): # If next line in output is not empty
            #kibana-dev-deployment-65f4d7b9f6-xs5j9                            1/1     Running       1          20h
      pod_status = pod_info[2].split("/") # Check pod status (column 3, values ^^^ from both sides of the slash)
      if pod_status[0] != pod_status[1]:  # if left value doesn't matche right one
        pods.append(pod_info[1])          # This pod is broken and goes to the list

  if len(pods): # if there are more than 0 of brken pods
    print("WARNING: Pods not ready: %s" % (" ".join(pods[0:MAX_PODS_SHOWN])))
    exit(1)
  else:
    print("OK: Pods are OK")
    exit(0)
# End of checking pods

# New check if you need it
# elif check == 'somenewcheck':

