import { SupportedFileTypes } from '../../../utils/constants/storageBrowser';
import { getFileMetaData, getFileType } from './StorageFilePage.util';

jest.mock('../../../utils/dateTimeUtils', () => ({
  ...jest.requireActual('../../../utils/dateTimeUtils'),
  formatTimestamp: () => 'November 25, 2021 at 00:00 AM'
}));

describe('getFileMetaData', () => {
  const defaultFileStats = {
    atime: 1637859451,
    blockSize: 1024,
    group: 'group1',
    mode: 16384,
    mtime: 1637859451,
    path: '/path/to/file',
    replication: 1,
    rwx: 'rwxr-xr-x',
    size: 1024,
    type: 'file',
    user: 'user1'
  };
  const mockTranslation = jest.fn((key: string) => key);

  it('should return correct metadata structure', () => {
    const result = getFileMetaData(mockTranslation, defaultFileStats);

    expect(result[0][0]).toEqual({
      name: 'size',
      label: 'Size',
      value: '1.00 KB'
    });
    expect(result[0][1]).toEqual({
      name: 'user',
      label: 'Created By',
      value: 'user1'
    });

    expect(result[1][0]).toEqual({
      name: 'group',
      label: 'Group',
      value: 'group1'
    });
    expect(result[1][1]).toEqual({
      name: 'permissions',
      label: 'Permissions',
      value: 'rwxr-xr-x'
    });
    expect(result[1][2]).toEqual({
      name: 'mtime',
      label: 'Last Modified',
      value: 'November 25, 2021 at 00:00 AM'
    });
  });
});

describe('getFileType', () => {
  it('should return the correct file type for supported extensions', () => {
    const fileName = 'image.jpg';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.IMAGE);
  });

  it('should return the correct file type for text extensions', () => {
    const fileName = 'text.txt';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.TEXT);
  });

  it('should return the correct file type for document extensions', () => {
    const fileName = 'document.pdf';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.DOCUMENT);
  });

  it('should return the correct file type for audio extensions', () => {
    const fileName = 'audio.mp3';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.AUDIO);
  });

  it('should return the correct file type for video extensions', () => {
    const fileName = 'video.mp4';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.VIDEO);
  });

  it('should return OTHER for unsupported extensions', () => {
    const fileName = 'file.xyz';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.OTHER);
  });

  it('should return OTHER if file has no extension', () => {
    const fileName = 'fileWithoutExtension';
    const result = getFileType(fileName);
    expect(result).toBe(SupportedFileTypes.OTHER);
  });
});
