import os

def which(file_name):
  for path in os.environ["PATH"].split(os.pathsep):
    full_path = os.path.join(path, file_name)
    if os.path.exists(full_path) and os.access(full_path, os.X_OK):
      return full_path
  return None
