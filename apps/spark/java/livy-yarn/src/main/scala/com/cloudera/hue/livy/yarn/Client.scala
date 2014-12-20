package com.cloudera.hue.livy.yarn

import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.hadoop.yarn.api.ApplicationConstants
import org.apache.hadoop.yarn.api.ApplicationConstants.Environment
import org.apache.hadoop.yarn.api.records._
import org.apache.hadoop.yarn.client.api.YarnClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.{ConverterUtils, Records}
import org.slf4j.LoggerFactory

import scala.collection.JavaConversions._

object Client extends Logging {

  def main(args: Array[String]): Unit = {
    println(args.length)
    args.foreach(println(_))

    val packagePath = new Path(args(1))

    val yarnConf = new YarnConfiguration()
    val client = new Client(yarnConf)

    try {
      val job = client.submitApplication(
        packagePath,
        List(
          "__package/bin/run-am.sh 1>%s/stdout 2>%s/stderr" format (
            ApplicationConstants.LOG_DIR_EXPANSION_VAR,
            ApplicationConstants.LOG_DIR_EXPANSION_VAR
          )
        )
      )

      info("waiting for job to start")

      job.waitForStatus(Running(), 500) match {
        case Some(Running()) => {
          info("job started successfully")
        }
        case Some(appStatus) => {
          warn("unable to start job successfully. job has status %s" format appStatus)
        }
        case None => {
          warn("timed out waiting for job to start")
        }
      }

      job.waitForFinish(100000) match {
        case Some(SuccessfulFinish()) => {
          info("job finished successfully")
        }
        case Some(appStatus) => {
          info("job finished unsuccessfully %s" format appStatus)
        }
        case None => {
          info("timed out")
        }
      }

    } finally {
      client.close()
    }
  }
}

class Client(yarnConf: YarnConfiguration) {

  import Client._

  val yarnClient = YarnClient.createYarnClient()
  yarnClient.init(yarnConf)
  yarnClient.start()

  def submitApplication(packagePath: Path, cmds: List[String]): Job = {
    val app = yarnClient.createApplication()
    val newAppResponse = app.getNewApplicationResponse

    val appId = newAppResponse.getApplicationId

    info("preparing to submit %s" format appId)

    val appContext = app.getApplicationSubmissionContext
    appContext.setApplicationName(appId.toString)

    val containerCtx = Records.newRecord(classOf[ContainerLaunchContext])
    val resource = Records.newRecord(classOf[Resource])

    info("Copy app master jar from local filesystem and add to the local environment")
    /*
    val localResources = Map(
      "app" => uploadLocalResource()
    )
    Map


    addToLocalResources(fs, appMasterJar, appMasterJarPath, appId, localResources, null)
    */

    val packageResource = Records.newRecord(classOf[LocalResource])

    val packageUrl = ConverterUtils.getYarnUrlFromPath(packagePath)
    val fileStatus = packagePath.getFileSystem(yarnConf).getFileStatus(packagePath)

    packageResource.setResource(packageUrl)
    info("set package url to %s for %s" format (packageUrl, appId))
    packageResource.setSize(fileStatus.getLen)
    info("set package size to %s for %s" format (fileStatus.getLen, appId))
    packageResource.setTimestamp(fileStatus.getModificationTime)
    packageResource.setType(LocalResourceType.ARCHIVE)
    packageResource.setVisibility(LocalResourceVisibility.APPLICATION)

    resource.setMemory(256)
    resource.setVirtualCores(1)
    appContext.setResource(resource)

    containerCtx.setCommands(cmds)
    containerCtx.setLocalResources(Map("__package" -> packageResource))

    appContext.setApplicationId(appId)
    appContext.setAMContainerSpec(containerCtx)
    appContext.setApplicationType("livy")

    info("submitting application request for %s" format appId)

    yarnClient.submitApplication(appContext)

    new Job(yarnClient, appId)
  }

  def close(): Unit = {
    yarnClient.close()
  }

  private def addToLocalResources(fs: FileSystem, fileSrcPath: String, fileDstPath: String, appId: String): LocalResource = {
    val appName = "livy"
    val suffix = appName + "/" + appId + "/" + fileDstPath

    val dst = new Path(fs.getHomeDirectory, suffix)

    fs.copyFromLocalFile(new Path(fileSrcPath), dst)

    val srcFileStatus = fs.getFileStatus(dst)
    LocalResource.newInstance(
      ConverterUtils.getYarnUrlFromURI(dst.toUri),
      LocalResourceType.FILE,
      LocalResourceVisibility.APPLICATION,
      srcFileStatus.getLen,
      srcFileStatus.getModificationTime
    )
  }
}

class Job(client: YarnClient, appId: ApplicationId) {

  def waitForFinish(timeoutMs: Long): Option[ApplicationStatus] = {
    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      val status = getStatus()
      status match {
        case SuccessfulFinish() | UnsuccessfulFinish() => {
          return Some(status)
        }
        case _ =>
      }

      Thread.sleep(1000)
    }

    None
  }

  def waitForStatus(status: ApplicationStatus, timeoutMs: Long): Option[ApplicationStatus] = {
    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      if (getStatus() == status) {
        return Some(status)
      }

      Thread.sleep(1000)
    }

    None
  }

  private def getStatus(): ApplicationStatus = {
    val statusResponse = client.getApplicationReport(appId)
    convertState(statusResponse.getYarnApplicationState, statusResponse.getFinalApplicationStatus)
  }

  private def convertState(state: YarnApplicationState, status: FinalApplicationStatus): ApplicationStatus = {
    (state, status) match {
      case (YarnApplicationState.FINISHED, FinalApplicationStatus.SUCCEEDED) => SuccessfulFinish()
      case (YarnApplicationState.KILLED, _) | (YarnApplicationState.FAILED, _) => UnsuccessfulFinish()
      case (YarnApplicationState.NEW, _) | (YarnApplicationState.SUBMITTED, _) => New()
      case _ => Running()
    }
  }
}

trait ApplicationStatus
case class New() extends ApplicationStatus
case class Running() extends ApplicationStatus
case class SuccessfulFinish() extends ApplicationStatus
case class UnsuccessfulFinish() extends ApplicationStatus




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
