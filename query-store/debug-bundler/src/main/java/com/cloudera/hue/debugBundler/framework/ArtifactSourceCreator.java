// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import com.google.inject.Injector;

public interface ArtifactSourceCreator {
  ArtifactSource getSource(Injector injector);
}
