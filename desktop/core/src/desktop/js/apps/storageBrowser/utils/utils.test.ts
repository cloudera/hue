// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import {
  isHDFS,
  isS3,
  isS3Root,
  isABFS,
  isABFSRoot,
  isGS,
  isGSRoot,
  isOFS,
  isOFSRoot,
  isOFSServiceID,
  isOFSVol,
  inTrash,
  inRestorableTrash,
  isFileSystemNonRoot
} from './utils';

describe('isHDFS function', () => {
  test('returns true for paths starting with "/"', () => {
    expect(isHDFS('/path/to/file')).toBe(true);
    expect(isHDFS('/')).toBe(true);
  });

  test('returns true for paths starting with "hdfs"', () => {
    expect(isHDFS('hdfs://path/to/file')).toBe(true);
    expect(isHDFS('hdfs://')).toBe(true);
    expect(isHDFS('HDFS://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isHDFS('s3a://path/to/file')).toBe(false);
    expect(isHDFS('file://path/to/file')).toBe(false);

    expect(isHDFS('')).toBe(false);
  });
});

describe('isOFS function', () => {
  test('returns true for paths starting with "ofs://"', () => {
    expect(isOFS('ofs://path/to/file')).toBe(true);
    expect(isOFS('ofs://')).toBe(true);
    expect(isOFS('OFS://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isOFS('/path/to/file')).toBe(false);
    expect(isOFS('hdfs://path/to/file')).toBe(false);
    expect(isOFS('gs://path/to/file')).toBe(false);
    expect(isOFS('s3a://path/to/file')).toBe(false);
    expect(isOFS('')).toBe(false);
  });
});

describe('isS3 function', () => {
  test('returns true for paths starting with "s3a://"', () => {
    expect(isS3('s3a://path/to/file')).toBe(true);
    expect(isS3('s3a://')).toBe(true);
    expect(isS3('S3A://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isS3('/path/to/file')).toBe(false);
    expect(isS3('hdfs://path/to/file')).toBe(false);
    expect(isS3('ofs://path/to/file')).toBe(false);
    expect(isS3('gs://path/to/file')).toBe(false);
    expect(isS3('')).toBe(false);
  });
});

describe('isGS function', () => {
  test('returns true for paths starting with "gs://"', () => {
    expect(isGS('gs://path/to/file')).toBe(true);
    expect(isGS('gs://')).toBe(true);
    expect(isGS('GS://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isGS('/path/to/file')).toBe(false);
    expect(isGS('hdfs://path/to/file')).toBe(false);
    expect(isGS('ofs://path/to/file')).toBe(false);
    expect(isGS('s3a://path/to/file')).toBe(false);
    expect(isGS('')).toBe(false);
  });
});

describe('isABFS function', () => {
  test('returns true for paths starting with "abfs://"', () => {
    expect(isABFS('abfs://path/to/file')).toBe(true);
    expect(isABFS('abfs://')).toBe(true);
    expect(isABFS('ABFS://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isABFS('/path/to/file')).toBe(false);
    expect(isABFS('hdfs://path/to/file')).toBe(false);
    expect(isABFS('ofs://path/to/file')).toBe(false);
    expect(isABFS('s3a://path/to/file')).toBe(false);
    expect(isABFS('')).toBe(false);
  });
});

describe('isS3Root function', () => {
  test('returns true if path equals to "s3a://"', () => {
    expect(isS3Root('s3a://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isS3Root('s3a://path/to/file')).toBe(false);
    expect(isS3Root('/path/to/file')).toBe(false);
    expect(isS3Root('hdfs://path/to/file')).toBe(false);
    expect(isS3Root('ofs://path/to/file')).toBe(false);
  });
});

describe('isGSRoot function', () => {
  test('returns true if path equals to "gs://"', () => {
    expect(isGSRoot('gs://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isGSRoot('s3a://path/to/file')).toBe(false);
    expect(isGSRoot('/path/to/file')).toBe(false);
    expect(isGSRoot('hdfs://path/to/file')).toBe(false);
    expect(isGSRoot('gs://path/to/file')).toBe(false);
  });
});

describe('isABFSRoot function', () => {
  test('returns true if path equals to "abfs://"', () => {
    expect(isABFSRoot('abfs://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isABFSRoot('s3a://path/to/file')).toBe(false);
    expect(isABFSRoot('/path/to/file')).toBe(false);
    expect(isABFSRoot('hdfs://path/to/file')).toBe(false);
    expect(isABFSRoot('abfs://path/to/file')).toBe(false);
  });
});

describe('isOFSRoot function', () => {
  test('returns true if path equals to "ofs://"', () => {
    expect(isOFSRoot('ofs://')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isOFSRoot('s3a://path/to/file')).toBe(false);
    expect(isOFSRoot('/path/to/file')).toBe(false);
    expect(isOFSRoot('hdfs://path/to/file')).toBe(false);
    expect(isOFSRoot('ofs://path/to/file')).toBe(false);
  });
});

describe('isOFSServiceID function', () => {
  test('returns true if path equals to ofs serviceID', () => {
    expect(isOFSServiceID('ofs://serviceID')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isOFSServiceID('s3a://path/to/file')).toBe(false);
    expect(isOFSServiceID('ofs://serviceID/volume')).toBe(false);
    expect(isOFSServiceID('hdfs://path/to/file')).toBe(false);
    expect(isOFSServiceID('ofs://')).toBe(false);
  });
});

describe('isOFSVol function', () => {
  test('returns true if path equals to ofs volume', () => {
    expect(isOFSVol('ofs://serviceID/volume')).toBe(true);
  });

  test('returns false for other paths', () => {
    expect(isOFSVol('ofs://serviceID/volume/file')).toBe(false);
    expect(isOFSVol('/path/to/file')).toBe(false);
    expect(isOFSVol('hdfs://path/to/file')).toBe(false);
    expect(isOFSVol('ofs://')).toBe(false);
  });
});

describe('inTrash function', () => {
  test('returns true if path is in trash folder"', () => {
    expect(inTrash('/user/path/.Trash')).toBe(true);
  });

  test('returns false if path not in trash', () => {
    expect(inTrash('/user/trash')).toBe(false);
    expect(inTrash('/path/to/.Trash')).toBe(false);
    expect(inTrash('hdfs://path/to/file')).toBe(false);
    expect(inTrash('ofs://path/to/file')).toBe(false);
  });
});

describe('inRestorableTrash function', () => {
  test('returns false if path is not in trash"', () => {
    expect(inRestorableTrash('hdfs://path/to/file')).toBe(false);
    expect(inRestorableTrash('hdfs://path/to/file')).toBe(false);
    expect(inRestorableTrash('ofs://path/to/file')).toBe(false);
  });

  test('returns false if path is trash root folder"', () => {
    expect(inRestorableTrash('/user/path/.Trash')).toBe(false);
    expect(inRestorableTrash('/user/path/.Trash/')).toBe(false);
  });

  test('returns true if path is trash but not trash root folder', () => {
    expect(inRestorableTrash('/user/path/.Trash/Current')).toBe(true);
    expect(inRestorableTrash('/user/path/.Trash/Current/user')).toBe(true);
    expect(inRestorableTrash('/user/path/.Trash/Current/user/path')).toBe(true);
  });
});

describe('isFileSystemNonRoot', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('returns true for non-root S3 path', () => {
    expect(isFileSystemNonRoot('s3a://bucket/folder')).toBe(true);
  });

  it('returns false for S3 root path', () => {
    expect(isFileSystemNonRoot('s3a://')).toBe(false);
  });

  it('returns true for non-root GS path', () => {
    expect(isFileSystemNonRoot('gs://folder')).toBe(true);
  });

  it('returns false for GS root path', () => {
    expect(isFileSystemNonRoot('gs://')).toBe(false);
  });

  it('returns true for non-root ABFS path', () => {
    expect(isFileSystemNonRoot('abfs://folder')).toBe(true);
  });

  it('returns false for ABFS root path', () => {
    expect(isFileSystemNonRoot('abfs://')).toBe(false);
  });

  it('returns true for OFS when not serviceID or volume', () => {
    expect(isFileSystemNonRoot('ofs://service/volume/folder')).toBe(true);
  });

  it('returns false for OFS serviceID', () => {
    expect(isFileSystemNonRoot('ofs://service')).toBe(false);
  });

  it('returns false for OFS volume', () => {
    expect(isFileSystemNonRoot('ofs://service/vol')).toBe(false);
  });

  it('returns true for HDFS (default case)', () => {
    expect(isFileSystemNonRoot('/hdfs')).toBe(true);
    expect(isFileSystemNonRoot('/')).toBe(true);
  });
});
