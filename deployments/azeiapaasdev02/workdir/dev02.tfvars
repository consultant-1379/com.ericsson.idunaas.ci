env_name = "azdev02"
region   = "West Europe"
acr_url  = "" # only for public envs. If it is private leave this empty "".
eiap_oss_namespace = "ossazdev02"
#### You cannot get the subnetID from the console
vnet_subnet_id = "/subscriptions/cbb29dd8-74cd-40e2-9038-169441e14025/resourceGroups/AzureEIAPaaSDev01-vnet-rg/providers/Microsoft.Network/virtualNetworks/ecn-AzureEIAPaaSDev01-westeurope/subnets/ecn-subnet-1"
/*If there are multiple subnets, use one subnet which has higher number of IPs
Azure AKS node pools supports only one subnet. We do not need a pod subnet since the pod CNI will be handled by kubenet in Azure */
#cluster_log_analytic_ws = "cfa593cf-3865-41a5-9f13-1663243c4d99" #Log analytic Workspace ID for the AKS cluster, usually given, if not create one.
privatecluster = true
k8s_version    = "1.23.8"
#
nginx_lb_ip   = "100.85.163.137"
nginx_version = "0.15.1"
nginx_subnet  = "ecn-subnet-2"
#
kube_downscaler_version = "0.6.0"
#
prometheus_version = "13.4.0"
#
k8s_dashboard_version = "6.0.0"
#
node_group_name   = "dev02ng" #should start with lowercase and max length 12 and only have characters a-z0-9
node_vm_size      = "Standard_D16s_v4"
node_max_count    = "11" #Should be within approved Total Regional Cores quota
node_min_count    = "2"  #Should be within approved Total Regional Cores quota
node_ssh_key_pair = "test-keypair.pem"
#
#
subscription_id = "cbb29dd8-74cd-40e2-9038-169441e14025"
tenant_id       = "92e84ceb-fbfd-47ab-be52-080c6b87953f"
armdocker_registry_username = 'USERNAME_REPLACE'
armdocker_registry_password = 'PASSWORD_REPLACE'
#