package com.cloudera.hue.sparker.repl

import java.io.{BufferedReader, StringWriter}

import org.apache.spark.repl.SparkILoop
import org.json4s.DefaultFormats
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
    //println(compact(render(Map("state" -> "ready"))))

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

      if (line eq null) {
        return false                // assume null means EOF
      }

      val request = parseOpt(line) match {
        case Some(request) => request;
        case None => {
          println(compact(render(Map("type" -> "error", "msg" -> "invalid json"))))
          return true
        }
      }

      implicit val formats = DefaultFormats
      val type_ = (request \ "type").extract[Option[String]]

      type_ match {
        case Some("stdin") => {
          (request \ "statement").extract[Option[String]] match {
            case Some(statement) => {
              command(statement) match {
                case Result(false, _) => false
                case Result(true, finalLine) => {
                  finalLine match {
                    case Some(line) => addReplay(line)
                    case _ =>
                  }

                  var output: String = outString.getBuffer.toString
                  output = output.substring("scala> ".length + 1, output.length - 1)
                  outString.getBuffer.setLength(0)
                  println(compact(render(Map("type" -> "stdout", "stdout" -> output))))

                  true
                }
              }
            }
            case _ => {
              println(compact(render(Map("type" -> "error", "msg" -> "missing statement"))))
              true
            }
          }
        }
        case _ => {
          println(compact(render(Map("type" -> "error", "msg" -> "unknown type"))))
          true
        }
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
        println(compact(render(Map("state" -> "quit"))))
      }
    }
    innerLoop()
  }

}
