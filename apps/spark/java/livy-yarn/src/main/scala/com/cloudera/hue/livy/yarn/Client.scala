package com.cloudera.hue.livy.yarn

import java.io.{BufferedReader, InputStreamReader}
import java.lang.ProcessBuilder.Redirect

import com.cloudera.hue.livy.{LivyConf, Logging, Utils}
import org.apache.hadoop.yarn.api.records.{ApplicationId, FinalApplicationStatus, YarnApplicationState}
import org.apache.hadoop.yarn.client.api.YarnClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.ConverterUtils

import scala.annotation.tailrec
import scala.concurrent.{ExecutionContext, Future}

object Client extends Logging {
  private val LIVY_JAR = "__livy__.jar"
  private val CONF_LIVY_JAR = "livy.yarn.jar"
  private val LOCAL_SCHEME = "local"
  private lazy val regex = """Application report for (\w+)""".r.unanchored

  private def livyJar(conf: LivyConf) = {
    if (conf.contains(CONF_LIVY_JAR)) {
      conf.get(CONF_LIVY_JAR)
    } else {
      Utils.jarOfClass(classOf[Client]).head
    }
  }
}

class FailedToSubmitApplication extends Exception

class Client(livyConf: LivyConf) extends Logging {
  import com.cloudera.hue.livy.yarn.Client._

  protected implicit def executor: ExecutionContext = ExecutionContext.global

  val yarnConf = new YarnConfiguration()
  val yarnClient = YarnClient.createYarnClient()
  yarnClient.init(yarnConf)
  yarnClient.start()

  def submitApplication(id: String, lang: String, callbackUrl: String): Future[Job] = {
    val url = f"$callbackUrl/sessions/$id/callback"

    val livyJar: String = livyConf.getOption("livy.yarn.jar")
      .getOrElse(Utils.jarOfClass(classOf[Client]).head)

    val builder: ProcessBuilder = new ProcessBuilder(
      "spark-submit",
      "--master", "yarn-cluster",
      "--class", "com.cloudera.hue.livy.repl.Main",
      "--driver-java-options", f"-Dlivy.repl.callback-url=$url -Dlivy.repl.port=0",
      livyJar,
      lang
    )

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectErrorStream(true)

    Future {

      val process = builder.start()

      val stdout = new BufferedReader(new InputStreamReader(process.getInputStream), 1)

      val applicationId = parseApplicationId(stdout).getOrElse(throw new FailedToSubmitApplication)

      // Application has been submitted, so we don't need to keep the process around anymore.
      stdout.close()
      process.destroy()

      new Job(yarnClient, ConverterUtils.toApplicationId(applicationId))
    }
  }

  def close() = {
    yarnClient.close()
  }

  @tailrec
  private def parseApplicationId(stdout: BufferedReader): Option[String] = {
    Option(stdout.readLine()) match {
      case Some(line) =>
        info(f"shell output: $line")

        line match {
          case regex(applicationId) => Some(applicationId)
          case _ => parseApplicationId(stdout)
        }
      case None =>
        None
    }
  }
}

class Job(yarnClient: YarnClient, appId: ApplicationId) {
  def waitForFinish(timeoutMs: Long): Option[ApplicationStatus] = {
    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      val status = getStatus
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
      if (getStatus == status) {
        return Some(status)
      }

      Thread.sleep(1000)
    }

    None
  }

  def waitForRPC(timeoutMs: Long): Option[(String, Int)] = {
    waitForStatus(Running(), timeoutMs)

    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      val statusResponse = yarnClient.getApplicationReport(appId)

      (statusResponse.getHost, statusResponse.getRpcPort) match {
        case ("N/A", _) | (_, -1) =>
        case (hostname, port) => return Some((hostname, port))
      }
    }

    None
  }

  def getHost: String = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    statusResponse.getHost
  }

  def getPort: Int = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    statusResponse.getRpcPort
  }

  private def getStatus: ApplicationStatus = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    convertState(statusResponse.getYarnApplicationState, statusResponse.getFinalApplicationStatus)
  }

  private def convertState(state: YarnApplicationState, status: FinalApplicationStatus): ApplicationStatus = {
    (state, status) match {
      case (YarnApplicationState.FINISHED, FinalApplicationStatus.SUCCEEDED) => SuccessfulFinish()
      case (YarnApplicationState.FINISHED, _) |
           (YarnApplicationState.KILLED, _) |
           (YarnApplicationState.FAILED, _) => UnsuccessfulFinish()
      case (YarnApplicationState.NEW, _) |
           (YarnApplicationState.NEW_SAVING, _) |
           (YarnApplicationState.SUBMITTED, _) => New()
      case (YarnApplicationState.RUNNING, _) => Running()
      case (YarnApplicationState.ACCEPTED, _) => Accepted()
    }
  }
}

trait ApplicationStatus
case class New() extends ApplicationStatus
case class Accepted() extends ApplicationStatus
case class Running() extends ApplicationStatus
case class SuccessfulFinish() extends ApplicationStatus
case class UnsuccessfulFinish() extends ApplicationStatus
