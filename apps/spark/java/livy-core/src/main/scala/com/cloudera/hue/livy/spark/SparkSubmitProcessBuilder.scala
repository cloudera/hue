package com.cloudera.hue.livy.spark

import com.cloudera.hue.livy.Logging

import scala.collection.JavaConversions._
import scala.collection.mutable.ArrayBuffer

class SparkProcessBuilder extends Logging {

  private[this] var _executable = "spark-submit"
  private[this] var _master: Option[String] = None
  private[this] var _deployMode: Option[String] = None
  private[this] var _className: Option[String] = None
  private[this] var _name: Option[String] = None
  private[this] var _jars: ArrayBuffer[String] = ArrayBuffer()
  private[this] var _pyFiles: ArrayBuffer[String] = ArrayBuffer()
  private[this] var _files: ArrayBuffer[String] = ArrayBuffer()
  private[this] var _conf: ArrayBuffer[(String, String)] = ArrayBuffer()
  private[this] var _driverMemory: Option[String] = None
  private[this] var _driverJavaOptions: Option[String] = None
  private[this] var _driverClassPath: ArrayBuffer[String] = ArrayBuffer()
  private[this] var _executorMemory: Option[String] = None
  private[this] var _proxyUser: Option[String] = None

  private[this] var _driverCores: Option[String] = None
  private[this] var _executorCores: Option[String] = None
  private[this] var _queue: Option[String] = None
  private[this] var _numExecutors: Option[String] = None
  private[this] var _archives: ArrayBuffer[String] = ArrayBuffer()

  private[this] var _env: ArrayBuffer[(String, String)] = ArrayBuffer()
  private[this] var _redirectOutput: Option[ProcessBuilder.Redirect] = None
  private[this] var _redirectError: Option[ProcessBuilder.Redirect] = None
  private[this] var _redirectErrorStream: Option[Boolean] = None

  def executable(executable: String): SparkProcessBuilder = {
    _executable = executable
    this
  }

  def master(masterUrl: String): SparkProcessBuilder = {
    _master = Some(masterUrl)
    this
  }

  def deployMode(deployMode: String): SparkProcessBuilder = {
    _deployMode = Some(deployMode)
    this
  }

  def className(className: String): SparkProcessBuilder = {
    _className = Some(className)
    this
  }

  def name(name: String): SparkProcessBuilder = {
    _name = Some(name)
    this
  }

  def jar(jar: String): SparkProcessBuilder = {
    this._jars += jar
    this
  }

  def jars(jars: Traversable[String]): SparkProcessBuilder = {
    this._jars ++= jars
    this
  }

  def pyFile(pyFile: String): SparkProcessBuilder = {
    this._pyFiles += pyFile
    this
  }

  def pyFiles(pyFiles: Traversable[String]): SparkProcessBuilder = {
    this._pyFiles ++= pyFiles
    this
  }

  def file(file: String): SparkProcessBuilder = {
    this._files += file
    this
  }

  def files(files: Traversable[String]): SparkProcessBuilder = {
    this._files ++= files
    this
  }

  def conf(key: String, value: String): SparkProcessBuilder = {
    this._conf += ((key, value))
    this
  }

  def conf(conf: Traversable[(String, String)]): SparkProcessBuilder = {
    this._conf ++= conf
    this
  }

  def driverMemory(driverMemory: String): SparkProcessBuilder = {
    _driverMemory = Some(driverMemory)
    this
  }

  def driverJavaOptions(driverJavaOptions: String): SparkProcessBuilder = {
    _driverJavaOptions = Some(driverJavaOptions)
    this
  }

  def driverClassPath(classPath: String): SparkProcessBuilder = {
    _driverClassPath += classPath
    this
  }

  def driverClassPaths(classPaths: Traversable[String]): SparkProcessBuilder = {
    _driverClassPath ++= classPaths
    this
  }

  def executorMemory(executorMemory: String): SparkProcessBuilder = {
    _executorMemory = Some(executorMemory)
    this
  }

  def proxyUser(proxyUser: String): SparkProcessBuilder = {
    _proxyUser = Some(proxyUser)
    this
  }

  def driverCores(driverCores: String): SparkProcessBuilder = {
    _driverCores = Some(driverCores)
    this
  }

  def executorCores(executorCores: String): SparkProcessBuilder = {
    _executorCores = Some(executorCores)
    this
  }

  def queue(queue: String): SparkProcessBuilder = {
    _queue = Some(queue)
    this
  }

  def archive(archive: String): SparkProcessBuilder = {
    _archives += archive
    this
  }

  def archives(archives: Traversable[String]): SparkProcessBuilder = {
    _archives ++= archives
    this
  }

  def env(key: String, value: String): SparkProcessBuilder = {
    _env += ((key, value))
    this
  }

  def redirectOutput(redirect: ProcessBuilder.Redirect): SparkProcessBuilder = {
    _redirectOutput = Some(redirect)
    this
  }

  def redirectError(redirect: ProcessBuilder.Redirect): SparkProcessBuilder = {
    _redirectError = Some(redirect)
    this
  }

  def redirectErrorStream(redirect: Boolean): SparkProcessBuilder = {
    _redirectErrorStream = Some(redirect)
    this
  }

  def start(file: String, args: Traversable[String]): Process = {
    var args_ = ArrayBuffer(_executable)

    def addOpt(option: String, value: Option[String]): Unit = {
      value.foreach { v =>
        args_ += option
        args_ += v
      }
    }

    def addList(option: String, values: Traversable[String]): Unit = {
      if (values.nonEmpty) {
        args_ += option
        args_ += values.mkString(",")
      }
    }

    addOpt("--master", _master)
    addOpt("--deploy-mode", _deployMode)
    addOpt("--name", _name)
    addList("--jars", _jars)
    addList("--py-files", _pyFiles)
    addList("--files", _files)
    addOpt("--class", _className)
    addList("--conf", _conf.map { case (key, value) => f"$key=$value" })
    addOpt("--driver-memory", _driverMemory)
    addOpt("--driver-java-options", _driverJavaOptions)
    addList("--driver-class-path", _driverClassPath)
    addOpt("--driver-cores", _driverCores)
    addOpt("--executor-memory", _executorMemory)
    addOpt("--proxy-user", _proxyUser)
    addOpt("--driver-cores", _driverCores)
    addOpt("--executor-cores", _executorCores)
    addOpt("--queue", _queue)
    addList("--archives", _archives)

    args_ += file
    args_ ++= args

    info("Running %s", args.mkString(" "))

    val pb = new ProcessBuilder(args_)
    val env = pb.environment()

    for ((key, value) <- _env) {
      env.put(key, value)
    }

    _redirectOutput.foreach(pb.redirectOutput)
    _redirectError.foreach(pb.redirectError)
    _redirectErrorStream.foreach(pb.redirectErrorStream)

    pb.start()
  }
}
