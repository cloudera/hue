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

import { useCallback, useEffect, useState } from 'react';
import { AxiosError } from 'axios';
import { ApiFetchOptions, post, put, patch } from '../../../api/utils';
import { isJSON } from '../../jsonUtils';

export enum HttpMethod {
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH'
}

interface saveOptions<T, E> {
  url?: string;
  method?: HttpMethod;
  onSuccess?: (data: T) => void;
  onError?: (error: AxiosError) => void;
  postOptions?: ApiFetchOptions<T, E>;
}

export interface Options<T, E> extends saveOptions<T, E> {
  skip?: boolean;
}

interface UseSaveData<T, U, E> {
  data?: T;
  loading: boolean;
  error?: E;
  save: (body: U, saveOption?: saveOptions<T, E>) => void;
}

const useSaveData = <T, U = unknown, E = string>(
  url?: string,
  options?: Options<T, E>
): UseSaveData<T, U, E> => {
  const [localOptions, setLocalOptions] = useState<Options<T, E> | undefined>(options);
  const [data, setData] = useState<T | undefined>();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<E | undefined>();

  const requestOptionsDefault: ApiFetchOptions<T, E> = {
    silenceErrors: true,
    ignoreSuccessErrors: true
  };

  const saveData = useCallback(
    async (body: U, saveOptions?: saveOptions<T, E>) => {
      // Avoid sending data if the skip option is true
      // or if the URL is not provided
      const apiUrl = saveOptions?.url ?? url;
      if (options?.skip || !apiUrl) {
        return;
      }
      setLoading(true);
      setError(undefined);

      const requestOptions = {
        ...requestOptionsDefault,
        qsEncodeData: body instanceof FormData || isJSON(body) ? false : true,
        ...localOptions?.postOptions,
        ...saveOptions?.postOptions
      };

      const method = saveOptions?.method ?? localOptions?.method ?? HttpMethod.POST;

      try {
        const apiMethod = {
          [HttpMethod.POST]: post<T, U, E>,
          [HttpMethod.PUT]: put<T, U, E>,
          [HttpMethod.PATCH]: patch<T, U, E>
        }[method];

        const response = await apiMethod(apiUrl, body, requestOptions);

        setData(response);
        if (saveOptions?.onSuccess) {
          saveOptions.onSuccess(response);
        }
        if (localOptions?.onSuccess) {
          localOptions.onSuccess(response);
        }
      } catch (error) {
        setError(error as E);
        if (saveOptions?.onError) {
          saveOptions.onError(error as AxiosError);
        }
        if (localOptions?.onError) {
          localOptions.onError(error as AxiosError);
        }
      } finally {
        setLoading(false);
      }
    },
    [url, localOptions]
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
