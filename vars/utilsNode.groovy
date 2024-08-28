#!/usr/bin/env groovy

/* groovylint-disable NoWildcardImports, UnnecessaryGetter, LineLength, NoDef, Instanceof */
/* groovylint-disable MethodParameterTypeRequired, MethodReturnTypeRequired, DuplicateStringLiteral */
/* groovylint-disable CatchException, NestedBlockDepth, VariableTypeRequired */

import hudson.model.*
import jenkins.model.*
import hudson.FilePath.*

// Return list of online nodes with a particular label or name (i.e. string).
def getOnlineNodes(label) {
    return nodesByLabel(label)
}

// Return instance of an Node with this particular label or name (i.e. string).
def getNodeInstance(nodeName) {
    return Jenkins.getInstance().getNode(nodeName)
}

// Return list of workspaces under root workspace on this node.
def getListOfWorkspacesOnNode(nodeName) {
    return getNodeInstance(nodeName).workspaceRoot.listDirectories()
}

// Return a subset list of Jenkins jobs based on filters.
def getListOfJobs(jobType = 'WorkflowJob', boolean building = false, boolean concurrencyEnabled = false, boolean customWorkspaceExists = false) {
    return Jenkins.instance.getAllItems(TopLevelItem).findAll { item ->
        item instanceof Job && (item.isBuilding() == building) && ("${item.class}".contains(jobType)) \
        && (item.isConcurrentBuild() == concurrencyEnabled) \
        && (customWorkspaceExists == true ? item.getCustomWorkspace() : true)
    }
}

/* Method that temporarily disables the node. Set the TemporarilyOffline status to "true".
   This prevents any new jobs been queued on it and does not interfere with existing jobs that are running on this node.
   Then wait until the node is offline.
*/
def setNodeTemporarilyOffline(nodeName) {
    try {
        Slave node = getNodeInstance(nodeName)
        if (node.getComputer().isOnline()) {
            String offlineReason = 'Clean up of workspaces on node is executing. Node Temporarily disabled.'
            node.getComputer().setTemporarilyOffline(true, new hudson.slaves.OfflineCause.ByCLI(offlineReason))
            node.getComputer().waitUntilOffline()
        }
        printNodeStatus(node)
    }
    catch (Exception err) {
        println('  [' + nodeName + '] Critical Exception occurred when temporarily trying to offline ' + node.name + ':' + err.toString() + '. Halt branch of parallel.')
        raise new Exception(err)
    }
    finally {
        node = null
    }
}

/* Method that enables node. Set the TemporarilyOffline status to "false".
   This means that the node can accept new jobs again. Wait until node is online.
*/
def setNodeOnline(nodeName) {
    try {
        Slave node = getNodeInstance(nodeName)
        if (node.getComputer().isOffline()) {
            node.getComputer().setTemporarilyOffline(false, null)
            node.getComputer().waitUntilOnline()
        }
        printNodeStatus(node)
    }
    catch (Exception err) {
        println('  [' + nodeName + '] Critical Exception occurred when trying to online ' + node.name + ':' + err.toString() + '. Halt branch of parallel.')
        raise new Exception(err)
    }
    finally {
        node = null
    }
}

// Delete remote workspace on node if it exists. If exception thrown, ignore and continue on.
def deleteRemoteWorkspace(path) {
    def pathAsString = path.getRemote()
    if (path.exists()) {
        try {
            path.deleteRecursive()
            println('Deleted...' + pathAsString)
        }
        catch (Exception err) {
            println('Failed to delete ' + pathAsString + ':' + err.toString())
        }
    }
}

/* Method that checks if the node is idle or busy.
   No Busy executors on the node (i.e. idle) =>
    - Delete standard and custom workspaces.
   Busy executors on the node =>
    - Get list of pipeline jobs not building, concurrency enabled/disabled, custom workspace disabled.
    - Get list of freeStyleProject Job not building, concurrency enabled/disabled, custom job workspace.
    - For other workspaces that are left behind:
    - Check for concurrency matches of the type jobName(@[1-9]){1} or jobName(@tmp){1} or jobName(@[1-9]@tmp){1}.
    - Delete these workspaces.
*/
def deleteNodeWorkspaces(nodeName) {
    try {
        Slave node = getNodeInstance(nodeName)
        def listOfNodeWorkspaces = getListOfWorkspacesOnNode(nodeName)
        def booleanList = [true, false]

        if (node.getComputer().isIdle()) {
            println('Node ' + nodeName + ' is idle. Deleting all workspaces...')
            listOfNodeWorkspaces.each { String path ->
                deleteRemoteWorkspace(path)
            }
            booleanList.each { concurrencyVal ->
                getListOfJobs('FreeStyleProject', false, concurrencyVal, true).each { item ->
                    deleteRemoteWorkspace(node.getRootPath().child(item.customWorkspace))
                }
            }
        }
        else {
            println('Node ' + nodeName + ' is not idle. Delete workspaces not in use...')
            booleanList.each { concurrencyVal ->
                getListOfJobs('WorkflowJob', false, concurrencyVal, false).each { item ->
                    String jobName = item.getFullDisplayName()
                    deleteRemoteWorkspace(node.getWorkspaceFor(item))
                    if (concurrencyVal) {
                        List<String> concurrencyDuplicates = getListOfWorkspacesOnNode(nodeName).findAll { path ->
                           path =~ ~ /${jobName}(@[1-9]|@tmp|@[1-9]@tmp){1}/
                        }
                        concurrencyDuplicates.each { path ->
                            deleteRemoteWorkspace(path)
                        }
                    }
                }
            }
            booleanList.each { concurrencyVal ->
                getListOfJobs('FreeStyleProject', false, concurrencyVal, true).each { item ->
                    deleteRemoteWorkspace(node.getRootPath().child(item.customWorkspace))
                }
            }
        }
    }
    catch (Exception err) {
        println('  [' + nodeName + '] Critical Exception occurred in deletion of ' + err.toString() + '. Halt branch of parallel.')
        raise new Exception(err)
    }
}

// Method to print the channel, online and accepting tasks status of the node.
def printNodeStatus(Slave node) {
    println('Node: ' + node.name + '\t Channel Connected      : ' + node.getComputer().getChannel())
    println('Node: ' + node.name + '\t Online Status          : ' + node.getComputer().isOnline())
    println('Node: ' + node.name + '\t Accepting Tasks Status : ' + node.getComputer().isAcceptingTasks())
}
