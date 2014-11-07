package com.cloudera.hue.sparker.repl

import java.io.{BufferedReader, StringWriter}

import org.apache.spark.repl.SparkILoop
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._

import scala.tools.nsc.SparkHelper
import scala.tools.nsc.interpreter.{Formatting, _}
import scala.tools.nsc.util.ClassPath

class SparkerILoop(in0: BufferedReader, outString: StringWriter) extends SparkILoop(in0, new JPrintWriter(outString)) {

  class SparkerILoopInterpreter extends SparkILoopInterpreter {
    outer =>

    override lazy val formatting = new Formatting {
      def prompt = SparkerILoop.this.prompt
    }
    override protected def parentClassLoader = SparkHelper.explicitParentLoader(settings).getOrElse(classOf[SparkILoop].getClassLoader)

    /*
    override def interpret(line: String, synthetic: Boolean): IR.Result = {
      val result = super.interpret(line, synthetic)
      print("interpret: " + result + "\n")
      result
    }
    */
  }

  /** Create a new interpreter. */
  override def createInterpreter() {
    require(settings != null)

    if (addedClasspath != "") settings.classpath.append(addedClasspath)
    // work around for Scala bug
    val totalClassPath = SparkILoop.getAddedJars.foldLeft(
      settings.classpath.value)((l, r) => ClassPath.join(l, r))
    this.settings.classpath.value = totalClassPath

    intp = new SparkerILoopInterpreter
  }

  private val replayQuestionMessage =
    """|That entry seems to have slain the compiler.  Shall I replay
      |your session? I can re-run each line except the last one.
      |[y/n]
    """.trim.stripMargin

  private def crashRecovery(ex: Throwable): Boolean = {
    echo(ex.toString)
    ex match {
      case _: NoSuchMethodError | _: NoClassDefFoundError =>
        echo("\nUnrecoverable error.")
        throw ex
      case _  =>
        def fn(): Boolean =
          try in.readYesOrNo(replayQuestionMessage, { echo("\nYou must enter y or n.") ; fn() })
          catch { case _: RuntimeException => false }

        if (fn()) replay()
        else echo("\nAbandoning crashed session.")
    }
    true
  }

  override def loop(): Unit = {
    println(compact(render(Map("type" -> "ready"))))

    def readOneLine() = {
      out.flush()
      in readLine prompt
    }
    // return false if repl should exit
    def processLine(line: String): Boolean = {
      if (isAsync) {
        if (!awaitInitialized()) return false
        runThunks()
      }

      if (line eq null) false               // assume null means EOF
      else command(line) match {
        case Result(false, _)           => false
        case Result(_, Some(finalLine)) => {
          var output: String = outString.getBuffer.toString
          output = output.substring("scala> ".length + 1, output.length - 1)
          outString.getBuffer.setLength(0)
          println(compact(render(Map("type" -> "result", "input" -> finalLine, "output" -> output))))
          addReplay(finalLine)
        } ; true
        case _                          => true
      }
    }
    def innerLoop() {
      outString.getBuffer.setLength(0)
      val shouldContinue = try {
        processLine(readOneLine())
      } catch {case t: Throwable => crashRecovery(t)}
      if (shouldContinue)
        innerLoop()
      else {
        println(compact(render(Map("type" -> "done"))))
      }
    }
    innerLoop()
  }

}
