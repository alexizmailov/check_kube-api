A simple script to check against the kubernetes API, at present it can check EITHER:

-c nodescordoned (for cordoned nodes)

OR

-c podsready (for pods not in a ready state)

Requires a kubeconfig file to be passed to the script with -k or --kubeconfig, e.g:

-k kube-monitoring.yaml

-m NUMBER - limits output to NUMBER in case we have an outage and MANY broken pods

Exit codes:

0 - No cordoned nodes or all pods are ok

1 - Cordoned nodes or pods not ready detected

2 - kubectl or API error
