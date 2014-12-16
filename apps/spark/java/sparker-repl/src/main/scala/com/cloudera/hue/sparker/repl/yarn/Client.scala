package com.cloudera.hue.sparker.yarn

import java.util.Collections

import org.apache.hadoop.fs.Path
import org.apache.hadoop.yarn.api.records._
import org.apache.hadoop.yarn.client.api.YarnClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.{ConverterUtils, Records}

import scala.collection.JavaConversions._

class Client {
  def main(args: Array[String]) = {

    val packagePath = new Path(args(1))

    val yarnConf = new YarnConfiguration()
    val yarnClient = YarnClient.createYarnClient()
    yarnClient.init(yarnConf)
    yarnClient.start

    try {
      submitApplication(yarnClient, yarnConf, packagePath, List("echo hi"))
    } finally {
      yarnClient.close()
    }
  }

  def submitApplication(yarnClient: YarnClient, yarnConf: YarnConfiguration, packagePath: Path, cmds: List[String]) = {
    val app = yarnClient.createApplication()
    val newAppResponse = app.getNewApplicationResponse

    val appId = newAppResponse.getApplicationId

    val appContext = app.getApplicationSubmissionContext
    val containerCtx = Records.newRecord(classOf[ContainerLaunchContext])
    val resource = Records.newRecord(classOf[Resource])
    val packageResource = Records.newRecord(classOf[LocalResource])

    appContext.setApplicationName(appId.toString)

    val packageUrl = ConverterUtils.getYarnUrlFromPath(packagePath)
    val fileStatus = packagePath.getFileSystem(yarnConf).getFileStatus(packagePath)

    packageResource.setResource(packageUrl)
    packageResource.setSize(fileStatus.getLen)
    packageResource.setTimestamp(fileStatus.getModificationTime)
    packageResource.setType(LocalResourceType.ARCHIVE)
    packageResource.setVisibility(LocalResourceVisibility.APPLICATION)

    resource.setMemory(256)
    resource.setVirtualCores(1)
    appContext.setResource(resource)

    containerCtx.setCommands(cmds)
    containerCtx.setLocalResources(Collections.singletonMap("__package", packageResource))
    appContext.setApplicationId(appId)
    appContext.setAMContainerSpec(containerCtx)
    appContext.setApplicationType("sparker")
    yarnClient.submitApplication(appContext)
  }
}


/*
object Client {

  def main(args: Array[String]) = {
    val jarPath = new Path(args(1))

    val yarnConf = new YarnConfiguration()
    val yarnClient = YarnClient.createYarnClient()

    yarnClient.init(yarnConf)
    yarnClient.start()

    try {
      val app = yarnClient.createApplication()
      val amContainer: ContainerLaunchContext = Records.newRecord(Class[ContainerLaunchContext])
      amContainer.setCommands(
        Collections.singletonList(
          "$JAVA_HOME/bin/java" +
            " com.cloudera.hue.sparker.repl.yarn.ApplicationMaster" +
            " 1>" + ApplicationConstants.LOG_DIR_EXPANSION_VAR + "/stdout" +
            " 2>" + ApplicationConstants.LOG_DIR_EXPANSION_VAR + "/stdout"))

      val appMasterJar: LocalResource = Records.newRecord(Class[LocalResource])
      setupAppMasterJar(jarPath, appMasterJar)
      amContainer.setLocalResources(
        Collections.singletonMap("foo.jar", appMasterJar)
      )

      val appMasterEnv: Map[String, String] = Map()
      setupAppMasterEnv(appMasterEnv)
      amContainer.setEnvironment(appMasterEnv)

      val capability: Resource = Records.newRecord(Class[Resource])
      capability.setMemory(256)
      capability.setVirtualCores(1)

      val appContext = app.getApplicationSubmissionContext
      appContext.setApplicationName("foo")
      appContext.setAMContainerSpec(amContainer)
      appContext.setResource(capability)
      appContext.setQueue("default")

      val appId = appContext.getApplicationId
      yarnClient.submitApplication(appContext)

      var appReport = yarnClient.getApplicationReport(appId)
      var appState = appReport.getYarnApplicationState()

      while (
        appState != YarnApplicationState.FINISHED &&
        appState != YarnApplicationState.KILLED &&
        appState != YarnApplicationState.FAILED
      ) {
        Thread.sleep(100)
        appReport = yarnClient.getApplicationReport(appId)
        appState = appReport.getYarnApplicationState
      }

    } finally {
      yarnClient.close()
    }
  }

  private def setupAppMasterJar(value: Path, resource: LocalResource) = {

  }

  private def setupAppMasterEnv(conf: YarnConfiguration, appMasterEnv: Map[String, String]) = {
    var classpaths = conf.getStrings(YarnConfiguration.YARN_APPLICATION_CLASSPATH)

    if (classpaths == null) {
      classpaths = YarnConfiguration.DEFAULT_YARN_APPLICATION_CLASSPATH
    }

    classpaths.foreach {
      c => {
        Apps.addToEnvironment(appMasterEnv, Environment.CLASSPATH.name(), c.trim())
      }
    }

    Apps.addToEnvironment(appMasterEnv, Environment.CLASSPATH.name(),
      Environment.PWD.$() + File.separator + "*"
    )
  }


    /*

    try {
      val appContext = yarnClient.createApplication.getApplicationSubmissionContext
      val appId = appContext.getApplicationId

      val appName = "sparker-repl"
      val amPriority = 0
      val amQueue = "default"

      appContext.setApplicationName(appName)

      val priority: Priority = Records.newRecord(Class[Priority])
      priority.setPriority(amPriority)
      appContext.setPriority(priority)

      appContext.setQueue(amQueue)

      val amContainer: ContainerLaunchContext = Records.newRecord(Class[ContainerLaunchContext])
      appContext.setAMContainerSpec(amContainer)

      appContext.setUnmanagedAM(true)

      yarnClient.submitApplication(appContext)

      var appReport = monitorApplication(
        appId,
        util.EnumSet.of(
          YarnApplicationState.ACCEPTED,
          YarnApplicationState.KILLED,
          YarnApplicationState.FAILED,
          YarnApplicationState.FINISHED
        ))

      if (appReport.getYarnApplicationState == YarnApplicationState.ACCEPTED) {
        val attemptReport = monitorCurrentAppAttempt(appId, YarnApplicationAttemptState.LAUNCHED)
        val attemptId = attemptReport.getApplicationAttemptId

        launchAM(yarnClient, attemptId)

        appReport = monitorApplication(
          appId,
          util.EnumSet.of(
            YarnApplicationState.KILLED,
            YarnApplicationState.FAILED,
            YarnApplicationState.FINISHED
          )
        )
      }

      val appState = appReport.getYarnApplicationState
      val appStatus = appReport.getFinalApplicationStatus

      if (YarnApplicationState.FINISHED == appState && FinalApplicationStatus.SUCCEEDED == appStatus) {
        0
      } else {
        1
      }
    } finally {
      yarnClient.close()
    }
  }
    */

  /*
  private def launchAM(rmClient: YarnClient, attemptId: ApplicationAttemptId): Unit = {
    val credentials = new Credentials();
    val token = rmClient.getAMRMToken(attemptId.getApplicationId)
    credentials.addToken(token.getService, token)
    val tokenFile = File.createTempFile("unmanagedAMRMToken", "", new File(System.getProperty("user.dir")));
    //try {
      FileUtil.chmod(tokenFile.getAbsolutePath, "600")
    //}

    tokenFile.deleteOnExit()
    val os = new DataOutputStream(new FileOutputStream(tokenFile, true))
    credentials.writeTokenStorageToStream(os)
    os.close()

    val envAMList = List()
    var setClasspath = false
    val classpath = null

    sys.env.foreach {
      case(key, value) => {
      var value: String = value
        if (key == "CLASSPATH") {
          setClasspath = true
          if (classpath != null) {
            value = value + File.pathSeparator + classpath
          }
        }
        envAMList +: (key + "=" + value)
      }
    }

    if (!setClasspath && classpath != null) {
      envAMList +: ("CLASSPATH=" + classpath)
    }


  }

  private def monitorApplication(appId: ApplicationId, attemptState: util.EnumSet[YarnApplicationState]): ApplicationReport = {
    null
  }

  private def monitorCurrentAppAttempt(appId: ApplicationId, attemptState: YarnApplicationAttemptState): ApplicationAttemptReport = {
    null
  }
  */


}
*/
