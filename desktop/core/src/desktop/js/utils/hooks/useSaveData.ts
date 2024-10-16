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

import { useCallback, useEffect, useMemo, useState } from 'react';
import { ApiFetchOptions, post } from '../../api/utils';

export interface Options<T> {
  postOptions?: ApiFetchOptions<T>;
  skip?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseSaveData<T, U> {
  data?: T;
  loading: boolean;
  error?: Error;
  save: (body: U) => void;
}

const useSaveData = <T, U = unknown>(url?: string, options?: Options<T>): UseSaveData<T, U> => {
  const [localOptions, setLocalOptions] = useState<Options<T> | undefined>(options);
  const [data, setData] = useState<T | undefined>();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | undefined>();

  const postOptionsDefault: ApiFetchOptions<T> = {
    silenceErrors: false,
    ignoreSuccessErrors: true
  };

  const postOptions = useMemo(
    () => ({ ...postOptionsDefault, ...localOptions?.postOptions }),
    [localOptions]
  );

  const saveData = useCallback(
    async (body: U) => {
      // Avoid Posting data if the skip option is true
      // or if the URL is not provided
      if (options?.skip || !url) {
        return;
      }
      setLoading(true);
      setError(undefined);

      try {
        const response = await post<T, U>(url, body, postOptions);
        setData(response);
        if (localOptions?.onSuccess) {
          localOptions.onSuccess(response);
        }
      } catch (error) {
        setError(error);
        if (localOptions?.onError) {
          localOptions.onError(error);
        }
      } finally {
        setLoading(false);
      }
    },
    [url, localOptions, postOptions]
  );

  useEffect(() => {
    // set new options if they are different (deep comparison)
    if (JSON.stringify(options) !== JSON.stringify(localOptions)) {
      setLocalOptions(options);
    }
  }, [options]);

  return { data, loading, error, save: saveData };
};

export default useSaveData;
