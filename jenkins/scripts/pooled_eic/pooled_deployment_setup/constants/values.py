TLS_CERT_KEY_FILE                   = "/home/certificateKey.pem"
TLS_CA_FILE                         = "/home/ca.crt"
MONGO_USERNAME                      = "pooluser"
MONGO_PASSWORD                      = "idunEricss0n"
MONGO_URI                           = "mongodb://10.117.246.172:3010/eicPooledClusterDB?authSourse=admin&ssl=false"
MINIO_URI                           = "10.117.246.166:9000"
# MINIO_ACCESS_KEY                  = "minio"
# MINIO_SECRET_KEY                  = "sts@£$%22mini"
MINIO_BUCKET                        = "eic-pooled"
MINIO_ACCESS_KEY                    = "minio"
# MINIO_SECRET_KEY                  = "sts@£$%22mini"
# MINIO_BUCKET                      = "eic"
######
PROMETHEUS_URI                      = "http://10.117.246.164:9099"
GRAFANA_CCD_RESOURCE_DASHBOARD      = "https://monitoring1.stsoss.seli.gic.ericsson.se:3000/d/BtVVluP7k/ccd-resource-allocation?orgId=1&var-dc=ews0&var-vpod=EIAP&var-program=DETS&var-cluster_id="

FEM2S11_JENKINS                     = "https://fem2s11-eiffel216.eiffel.gic.ericsson.se:8443"
HELMFILE_DEPLOY_JENKINS_JOB         = "https://fem2s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/EIC_Pooled_Deployments/job/EIAP_deploy_helmfile/"
SPINNAKER                           = "http://spinnaker.rnd.gic.ericsson.se/#/applications/??/executions/details/??"

JIRA_URL                            = "https://jira-oss.seli.wh.rnd.internal.ericsson.com"
JIRA_TEMPLATE                       = f"{JIRA_URL}/browse/dets-8320"
JIRA_PAT_TOKEN                      = "Mjk2MzU1ODEzMjQ0OqsavI73GVd758serPOMnOKMu+ae"

CONFLUENCE_URL                      = "https://confluence-oss.seli.wh.rnd.internal.ericsson.com"
ORDER_ACCESS_CONFLUENCE             = f"[Ordering and Accessing EIC Pooled Deployments|{CONFLUENCE_URL}/display/IDUN/Ordering+and+Accessing+EIC+Pooled+Deployments+on+EWS+KaaS]"
TROUBLESHOOT_CONFLUENCE             = f"[Troubleshooting Access on EIC Pooled Deployments|{CONFLUENCE_URL}/display/CI/Troubleshooting+your+access+on+an+EIC+Pooled+Deployments+on+EWS+KaaS]"

IDM_ROLE_URL                        = "https://idm.internal.ericsson.com/itim/ssui/#/manageAccess"


GUIDE                               = "Notes:\n\"How to Guide\""

ORDER                               = "Ordering / Accessing EIC Pooled Deployments"
TROUBLESHOOT                        = "Troubleshooting Access on EIC Pooled Deployments"

RANCHER                             = f"If access is required, users should request the IDM role in [*IDM*|{IDM_ROLE_URL}] and include the DETS booking ticket in the request."
IDM                                 = "Identity Manager - My Access (ericsson.com)"

USER_GROUP                          = "User Group - de-ts-ews-"

CERTIFICATE_FILES                   = "Please refer to original booking Jira ticket for access to certifictes files."
SITE_VALUES_FILE                    = "Please see attachments above for the site values file used for this installation."

SUPPORT                             = f"*FOR SUPPORT WITH BOOKING, PLEASE CLONE THE SUPPORT TEMPLATE*"
TEMPLATE                            = f"[*DETS-8320 TEMPLATE - EIC Pooled Deployment Support*|{JIRA_TEMPLATE}]"

PLEAE_SEE_USER_GUIDE                = "Please see below the user guide and the link for the EIC-SHARED-MASTER-PIPELINE, that can be used for upgrades and re-installations by your team:"

SHARED_PIPELINES_CONFLUENCE         = f"[Shared pipelines - Development Environment - PDUOSS Confluence (ericsson.com)|{CONFLUENCE_URL}/display/CI/Shared+pipelines]"
SHARED_PIPELINES_JENKINS            = f"{FEM2S11_JENKINS}/jenkins/job/EIC_Pooled_Deployments/view/Shared"

IDM_APPLIED_FOR                     = f"Ensure you have applied for access [*here*|{IDM_ROLE_URL}] and *received* the *stsoss-shared-pipeline* IDM role to allow access."

ACCESS                              = f"Access *will be removed* when the timebox ends."