export interface LocalFileUploadResponse {
  local_file_url: string;
  file_type: string;
}

export interface FileFormatResponse {
  fieldSeparator: string;
  hasHeader: boolean;
  quoteChar: string;
  recordSeparator: string;
  status: number;
  type: string;
}

export interface FileMetaData {
  path: string;
  type?: string;
  source?: string;
}

export type GuessFieldTypesColumn = {
  name: string;
  type: string;
  unique: boolean;
  keep: boolean;
  operations: any[];
  required: boolean;
  multiValued: boolean;
  showProperties: boolean;
  nested: any[];
  level: number;
  length: number;
  keyType: string;
  isPartition: boolean;
  partitionValue: string;
  comment: string;
  scale: number;
  precision: number;
};

export interface GuessFieldTypesResponse {
  columns: GuessFieldTypesColumn[];
  sample: string[][];
}
