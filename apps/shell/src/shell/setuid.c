/*
 Licensed to Cloudera, Inc. under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  Cloudera, Inc. licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

#include <errno.h>
#include <grp.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <sys/stat.h>

static int min_uid = 500;

void log_error(const char *format, ...) {
  va_list args;
  va_start(args, format);
  vfprintf(stderr, format, args);
  va_end(args);
  fprintf(stderr, "\n");
}

/**
 * Gets the name of the currently executing binary. The caller is responsible for freeing
 * the returned pointer.
 */
char *get_executable_name() {
  char buffer[PATH_MAX];
  snprintf(buffer, PATH_MAX, "/proc/%u/exe", getpid());

  char *filename = (char *) calloc(1, PATH_MAX);
  if (filename == NULL) {
    log_error("Error: calloc returned null, system out of memory.");
    return NULL;
  }

  ssize_t len = readlink(buffer, filename, PATH_MAX);
  if (len == -1) {
    log_error("Can't get executable name from \"%s\": %s", buffer, strerror(errno));
    free(filename);
    return NULL;
  }

  if (len >= PATH_MAX) {
    log_error("Executable name %.*s is longer than %d characters.", PATH_MAX, filename, PATH_MAX);
    free(filename);
    return NULL;
  }

  return filename;
}

/**
 * Check the permissions on the setuid binary to make sure that security is
 * promisable. For this, we need the binary to
 *    * be user-owned by root
 *    * others do not have write permissions
 *    * be setuid
 */
int check_binary_permissions() {

  char *executable_file = get_executable_name();
  if (executable_file == NULL) {
    return -1;
  }

  struct stat filestat;
  if (stat(executable_file, &filestat) != 0) {
    log_error("Could not stat the executable %s : %s", executable_file, strerror(errno));
    free(executable_file);
    return -1;
  }

  // check others do not have write permissions
  if ((filestat.st_mode & S_IWOTH) == S_IWOTH) {
    log_error("The setuid binary should not be writable by others.");
    free(executable_file);
    return -1;
  }

  // Binary should be setuid executable
  if ((filestat.st_mode & S_ISUID) == 0) {
    log_error("The setuid binary should be set setuid.");
    free(executable_file);
    return -1;
  }

  free(executable_file);
  return 0;
}

int chown_delegation_token_files(char *delegation_token_files, int uid, int gid) {
  char *modifiable_delegation_token_files = strdup(delegation_token_files);
  if (modifiable_delegation_token_files == NULL) {
    log_error("Error: strdup returned NULL, system out of memory.");
    return -1;
  }

  char *delegation_token_file = strtok(modifiable_delegation_token_files, ",");
  while (delegation_token_file != NULL) {
    int chown_result = chown(delegation_token_file, uid, gid);
    if (chown_result != 0) {
      log_error("Could not change ownership of file \"%s\" to UID %d and GID %d : %s", delegation_token_file, uid, gid, strerror(errno));
      free(modifiable_delegation_token_files);
      return -1;
    }
    delegation_token_file = strtok(NULL, ",");
  }
  free(modifiable_delegation_token_files);
  return 0;
}


/**
 * Set the real/effective gid and uid.
 * This is a no-op if the current gid/uid are the same as what's asked for.
 */
int set_gid_uid(int gid, int uid) {
  if (getgid() != gid || getegid() != gid) {
    gid_t group = gid;

    if (setgroups(1, &group) != 0) {
      log_error("Error: Could not set groups list to [%d] : %s", gid, strerror(errno));
      return -1;
    }

    if (setregid(gid, gid) != 0) {
      log_error("Error: Could not set real and effective group ID to %d : %s", gid, strerror(errno));
      return -1;
    }
  }

  if (getuid() != uid || geteuid() != uid) {
    if (setreuid(uid, uid) != 0) {
      log_error("Error: Could not set real and effective user ID to %d : %s", uid, strerror(errno));
      return -1;
    }
  }

  return 0;
}

int main(int argc, char **argv) {
  
  if (argc < 4){
    log_error("Usage: setuid <desired user ID> <desired group ID> <executable> <arguments for executable>");
    return -1;
  }

  // Because strtol can return the overflow/underflow error codes if it parses those integers correctly,
  // we have to set errno to 0 before the call. The function will set errno to a non-zero value if an
  // error occurs.
  errno = 0;
  int uid = strtol(argv[1], (char **)NULL, 10);
  if (errno != 0) {
    log_error("Error: Invalid value for UID: \"%s\" : %s", argv[1], strerror(errno));
    return -1;
  }

  // See comment above for why we have to set errno to 0 before calling strtol.
  errno = 0;
  int gid = strtol(argv[2], (char **)NULL, 10);
  if (errno != 0) {
    log_error("Error: Invalid value for GID: \"%s\" : %s", argv[2], strerror(errno));
    return -1;
  }

  if (uid < min_uid) {
    log_error("Error: value %d for UID is less than the minimum UID allowed (%d)", uid, min_uid);
    return -1;
  }

  if (check_binary_permissions() != 0) {
    log_error("Error: permissions on setuid binary are not correct. Exiting.");
    return -1;
  }

  char *delegation_token_files = getenv("HADOOP_TOKEN_FILE_LOCATION");
  if (delegation_token_files != NULL) {
    int chown_result = chown_delegation_token_files(delegation_token_files, uid, gid);
    if (chown_result != 0) {
      log_error("Error: Could not change ownership of delegation token files, exiting.");
      return -1;
    }
  }

  int set_gid_uid_result = set_gid_uid(gid, uid);
  if (set_gid_uid_result != 0) {
    log_error("Error: Could not correctly change to running as correct user, exiting.");
    return -1;
  }

  int executable_index = 3;
  const char *executable = argv[executable_index];
  char **param_list = (char **) calloc(argc - executable_index + 1, sizeof(char *));

  if (param_list == NULL) {
    log_error("Error: calloc returned null, system out of memory.");
    return -1;
  }

  int i;
  for (i = 0; i < argc - executable_index; i++) {
    param_list[i] = argv[executable_index + i];
  }

  int result = execvp(executable, param_list);

  log_error("Error: exec returned %d with error: %s", result, strerror(errno));
  return 0;
}

