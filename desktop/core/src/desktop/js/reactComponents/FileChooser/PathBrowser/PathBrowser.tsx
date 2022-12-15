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

import React, { useRef, useEffect, useState, RefObject } from 'react';
import { Breadcrumb, Input } from 'antd';

import HdfsIcon from '../../../components/icons/HdfsIcon';
import S3Icon from '../../../components/icons/S3Icon';
import AdlsIcon from '../../../components/icons/AdlsIcon';

import { BreadcrumbData } from '../types';
import './PathBrowser.scss';

interface PathBrowserProps {
  breadcrumbs?: BreadcrumbData[];
  onFilePathChange: (path: string) => void;
}

const PathBrowser: React.FC<PathBrowserProps> = ({ breadcrumbs, onFilePathChange }) => {
  const [inputFieldDisplay, setInputFieldDisplay] = useState(false);

  const icons = {
    //hdfs file system begins with the first breadcrumb as "" (ex: /user/demo)
    '': <HdfsIcon />,
    abfs: <AdlsIcon />,
    s3: <S3Icon />
  };

  const useOutsideAlerter = (ref: RefObject<HTMLDivElement>) => {
    useEffect(() => {
      // Alert if clicked on outside of element
      const handleClickOutside = (event: MouseEvent) => {
        const current = ref?.current;
        if (current && !current.contains(event.target as Node)) {
          setInputFieldDisplay(false);
        }
      };
      // Bind the event listener
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        // Unbind the event listener on clean up
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }, [ref]);
  };

  const onEnteredCustomPath = e => {
    onFilePathChange(e.target.value);
  };

  const wrapperRef = useRef<HTMLDivElement>(null);
  useOutsideAlerter(wrapperRef);

  if (breadcrumbs) {
    return (
      <div className="path-browser" onClick={e => e.stopPropagation()}>
        {/* TODO: handle the case when there is a deep file tree or file/directory name is long (too many breadcrumbs cannot be displayed on the modal) */}
        {!inputFieldDisplay ? (
          <>
            {/* .substring() is used to remove //: in the case of s3:// or  abfs:// and so on in all the occurances*/}
            <div className="filesystem__icon">
              {icons[breadcrumbs[0].label.substring(0, breadcrumbs[0].label.length - 3)]}
            </div>
            <Breadcrumb className="path-browser__breadcrumb" separator=">">
              {breadcrumbs.map((item: BreadcrumbData, index: number) => {
                return (
                  <Breadcrumb.Item
                    key={index}
                    onClick={() => {
                      onFilePathChange(item.url);
                    }}
                  >
                    {index === 0 ? item.label.substring(0, item.label.length - 3) : item.label}
                  </Breadcrumb.Item>
                );
              })}
            </Breadcrumb>
            <div
              className="toggle-breadcrumb-input"
              onClick={() => {
                setInputFieldDisplay(true);
              }}
            ></div>
          </>
        ) : (
          <div ref={wrapperRef}>
            <Input
              prefix={icons[breadcrumbs[0].label.substring(0, breadcrumbs[0].label.length - 3)]}
              defaultValue={decodeURIComponent(breadcrumbs[breadcrumbs.length - 1].url)}
              onPressEnter={onEnteredCustomPath}
              className="path-browser__input"
            ></Input>
          </div>
        )}
      </div>
    );
  }
};

export default PathBrowser;
