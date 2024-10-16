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
import { ApiFetchOptions, get } from '../../api/utils';

export interface Options<T, U> {
  urlPrefix?: string;
  params?: U;
  fetchOptions?: ApiFetchOptions<T>;
  skip?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseLoadDataProps<T> {
  data?: T;
  loading: boolean;
  error?: Error;
  reloadData: () => void;
}

const useLoadData = <T, U = unknown>(
  url?: string,
  options?: Options<T, U>
): UseLoadDataProps<T> => {
  const [localOptions, setLocalOptions] = useState<Options<T, U> | undefined>(options);
  const [data, setData] = useState<T | undefined>();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | undefined>();

  const fetchOptionsDefault: ApiFetchOptions<T> = {
    silenceErrors: false,
    ignoreSuccessErrors: true
  };

  const fetchOptions = useMemo(
    () => ({ ...fetchOptionsDefault, ...localOptions?.fetchOptions }),
    [localOptions]
  );

  const loadData = useCallback(
    async (isForced: boolean = false) => {
      // Avoid fetching data if the skip option is true
      // or if the URL is not provided
      if ((options?.skip && !isForced) || !url) {
        return;
      }
      setLoading(true);
      setError(undefined);

      try {
        const fetchUrl = localOptions?.urlPrefix ? `${localOptions.urlPrefix}${url}` : url;
        const response = await get<T, U>(fetchUrl, localOptions?.params, fetchOptions);
        setData(response);
        if (localOptions?.onSuccess) {
          localOptions.onSuccess(response);
        }
      } catch (error) {
        setError(error instanceof Error ? error : new Error(error));
        if (localOptions?.onError) {
          localOptions.onError(error);
        }
      } finally {
        setLoading(false);
      }
    },
    [url, localOptions, fetchOptions]
  );

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    // set new options if they are different (deep comparison)
    if (JSON.stringify(options) !== JSON.stringify(localOptions)) {
      setLocalOptions(options);
    }
  }, [options]);

  return { data, loading, error, reloadData: () => loadData(true) };
};

export default useLoadData;
