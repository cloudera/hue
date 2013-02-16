import re

from jobsub.models import OozieDesign, OozieMapreduceAction, OozieStreamingAction,\
                          OozieJavaAction

from oozie.models import Mapreduce, Java, Streaming


def convert_jobsub_design(jobsub_design):
  """Creates an oozie action from a jobsub design"""
  action = jobsub_design.get_root_action()
  if action is None:
    return None
  if action.action_type == OozieMapreduceAction.ACTION_TYPE:
    action = _convert_jobsub_mapreduce_action(action)
  elif action.action_type == OozieStreamingAction.ACTION_TYPE:
    action = _convert_jobsub_streaming_action(action)
  elif action.action_type == OozieJavaAction.ACTION_TYPE:
    action = _convert_jobsub_java_action(action)
  else:
    return None
  action.name = jobsub_design.name
  action.description = jobsub_design.description
  return action

VARIABLE_NAME_REGEX = re.compile('(?<!\$)\$(\w+)')
def _translate_jobsub_contents(contents):
  return VARIABLE_NAME_REGEX.sub(r'${\1}', contents)

def _convert_jobsub_mapreduce_action(jobsub_action):
  action = Mapreduce(files=_translate_jobsub_contents(jobsub_action.files),
    archives=_translate_jobsub_contents(jobsub_action.archives),
    jar_path=_translate_jobsub_contents(jobsub_action.jar_path),
    job_properties=_translate_jobsub_contents(jobsub_action.job_properties))
  action.node_type = Mapreduce.node_type
  return action

def _convert_jobsub_streaming_action(jobsub_action):
  action = Streaming(files=_translate_jobsub_contents(jobsub_action.files),
    archives=_translate_jobsub_contents(jobsub_action.archives),
    job_properties=_translate_jobsub_contents(jobsub_action.job_properties),
    mapper=_translate_jobsub_contents(jobsub_action.mapper),
    reducer=_translate_jobsub_contents(jobsub_action.reducer))
  action.node_type = Streaming.node_type
  return action

def _convert_jobsub_java_action(jobsub_action):
  action = Java(files=_translate_jobsub_contents(jobsub_action.files),
    archives=_translate_jobsub_contents(jobsub_action.archives),
    jar_path=_translate_jobsub_contents(jobsub_action.jar_path),
    main_class=_translate_jobsub_contents(jobsub_action.main_class),
    args=_translate_jobsub_contents(jobsub_action.args),
    java_opts=_translate_jobsub_contents(jobsub_action.java_opts),
    job_properties=_translate_jobsub_contents(jobsub_action.job_properties))
  action.node_type = Java.node_type
  return action