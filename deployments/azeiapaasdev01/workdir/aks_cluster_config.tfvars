env_name            = "azeiapaasdev01"
region              = "West Europe"
eiap_resource_group = "azeiapaasdev01-eiap-rg"
acr_url             = "" # only for public envs. If it is private leave this empty ""
eiap_oss_namespace  = "ossazdev01"
vnet_subnet_id = "/subscriptions/cbb29dd8-74cd-40e2-9038-169441e14025/resourceGroups/AzureEIAPaaSDev01-vnet-rg/providers/Microsoft.Network/virtualNetworks/ecn-AzureEIAPaaSDev01-westeurope/subnets/ecn-subnet-1"
privatecluster = true
#
nginx_lb_ip   = "100.85.163.135"
nginx_subnet  = "ecn-subnet-2"
#
prometheus_hostname = "monitoring-azdev01.internal.ericsson.com"
prometheus_tls_crt_path = "com.ericsson.idunaas.ci/deployments/azeiapaasdev01/workdir/certificates/monitoring-azdev01.internal.ericsson.com.crt"
prometheus_tls_key_path = "com.ericsson.idunaas.ci/deployments/azeiapaasdev01/workdir/certificates/monitoring-azdev01.internal.ericsson.com.key"
#
node_group_name = "azdev01ng" #should start with lowercase and max length 12 and only have characters a-z0-9
#
subscription_id   = "cbb29dd8-74cd-40e2-9038-169441e14025"
tenant_id         = "92e84ceb-fbfd-47ab-be52-080c6b87953f"
#
backup_server_ip        = "100.85.163.120" # Chose an IP from the node pool subnet for the backup server.
backup_server_name      = "AZWEULX1100" # Leave an empty line at the end of the file for the cat command to merge file with a new line.
