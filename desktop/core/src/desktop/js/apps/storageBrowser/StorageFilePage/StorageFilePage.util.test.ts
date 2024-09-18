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

import { downloadFile } from './StorageFilePage.util';
import { get } from '../../../api/utils';

const mockedFile = new Blob(['test content'], { type: 'text/plain' });
const mockedResponse = { data: mockedFile, type: 'text/plain' };
const mockedHost = 'http://example.com';
const mockedFileName = 'file.txt';
const mockedURL = `${mockedHost}/${mockedFileName}`;

jest.mock('../../../api/utils', () => ({
  get: jest.fn()
}));

const createObjectURLMock = jest.fn();
const revokeObjectURLMock = jest.fn();

createObjectURLMock.mockReturnValue(mockedURL);

Object.defineProperty(URL, 'createObjectURL', {
  value: createObjectURLMock,
  writable: true
});

Object.defineProperty(URL, 'revokeObjectURL', {
  value: revokeObjectURLMock,
  writable: true
});

const createElementMock = jest.spyOn(document, 'createElement').mockImplementation(() => {
  return {
    href: '',
    download: '',
    click: jest.fn()
  };
});

describe('downloadFile', () => {
  it('should download a file', async () => {
    get.mockResolvedValue({ data: mockedResponse, type: 'text/plain' });

    await downloadFile(mockedURL);

    expect(get).toHaveBeenCalledWith(mockedURL, { responseType: 'blob' });
    expect(createObjectURLMock).toHaveBeenCalledWith(mockedFile);

    const anchorElement = createElementMock.mock.results[0].value;
    expect(anchorElement.href).toBe(mockedURL);
    expect(anchorElement.download).toBe(mockedFileName);
    expect(anchorElement.click).toHaveBeenCalled();

    expect(revokeObjectURLMock).toHaveBeenCalledWith(mockedURL);
  });

  it('should log an error when the file cannot be downloaded', async () => {
    const mockedConsoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('Failed to download file');
    get.mockRejectedValue(error);

    await downloadFile(mockedURL);

    expect(mockedConsoleError).toHaveBeenCalled();
  });
});
