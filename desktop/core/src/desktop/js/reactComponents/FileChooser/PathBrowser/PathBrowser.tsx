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
import { Input, Button, Dropdown } from 'antd';
import type { MenuProps } from 'antd';

import HdfsIcon from '../../../components/icons/HdfsIcon';
import S3Icon from '../../../components/icons/S3Icon';
import AdlsIcon from '../../../components/icons/AdlsIcon';

import { BreadcrumbData } from '../types';
import OverflowingItem from './OverflowingItem';
import './PathBrowser.scss';

interface PathBrowserProps {
  breadcrumbs?: BreadcrumbData[];
  handleFilePathChange: (path: string) => void;
  seperator: string;
  showIcon: boolean;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-path-browser'
};

const PathBrowser: React.FC<PathBrowserProps> = ({
  breadcrumbs,
  handleFilePathChange,
  seperator,
  showIcon,
  testId
}) => {
  const [isEditMode, setIsEditMode] = useState(false);

  const icons = {
    //hdfs file system begins with the first breadcrumb as "/" (ex: /user/demo)
    '/': <HdfsIcon />,
    abfs: <AdlsIcon />,
    s3: <S3Icon />
  };

  const useOutsideAlerter = (ref: RefObject<HTMLDivElement>) => {
    useEffect(() => {
      // Alert if clicked on outside of element
      const handleClickOutside = (event: MouseEvent) => {
        const current = ref?.current;
        if (current && !current.contains(event.target as Node)) {
          setIsEditMode(false);
        }
      };
      // Bind the event listener
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        // Unbind the event listener on clean up
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }, []);
  };

  const extractFileSystem = (label: string) => {
    const fileSystemPrefix = label.substring(0, label.length - 3);
    //hdfs file system begins with the first breadcrumb as "/" (ex: /user/demo)
    if (fileSystemPrefix == '') {
      return label;
    } else {
      return fileSystemPrefix;
    }
  };

  const wrapperRef = useRef<HTMLDivElement>(null);
  useOutsideAlerter(wrapperRef);

  const extractMenuItems = (breadcrumbMenu: BreadcrumbData[]) => {
    const menu: MenuProps['items'] = breadcrumbMenu.map(breadcrumb => {
      return {
        key: breadcrumb.url,
        label: (
          <OverflowingItem
            key={breadcrumb.url}
            label={breadcrumb.label}
            url={breadcrumb.url}
            handleFilePathChange={handleFilePathChange}
            componentType="menu"
          />
        )
      };
    });
    return menu;
  };

  if (breadcrumbs) {
    return (
      <>
        {!isEditMode ? (
          <div className="hue-path-browser" data-testid={`${testId}`}>
            <div
              className={showIcon ? 'hue-filesystem__icon' : 'hide-hue-filesystem__icon'}
              data-testid={`${testId}-icon`}
            >
              {icons[extractFileSystem(breadcrumbs[0].label)]}
            </div>
            <div className="hue-path-browser__breadcrumb" data-testid={`${testId}-breadcrumb`}>
              {breadcrumbs.length <= 3 ? (
                breadcrumbs.map((item: BreadcrumbData, index: number) => {
                  return (
                    <>
                      <OverflowingItem
                        key={item.url}
                        label={index === 0 ? extractFileSystem(item.label) : item.label}
                        url={item.url}
                        handleFilePathChange={handleFilePathChange}
                        componentType="breadcrumb"
                        isLastBreadcrumb={index === breadcrumbs.length - 1 ? true : false}
                      />
                      {index != breadcrumbs.length - 1 ? (
                        <div
                          className="hue-path-browser__breadcrumb-seperator"
                          data-testid={`${testId}-breadcrumb-seperator`}
                        >
                          {seperator}
                        </div>
                      ) : (
                        <></>
                      )}
                    </>
                  );
                })
              ) : (
                <>
                  <OverflowingItem
                    label={extractFileSystem(breadcrumbs[0].label)}
                    url={breadcrumbs[0].url}
                    handleFilePathChange={handleFilePathChange}
                    componentType="breadcrumb"
                    key={breadcrumbs[0].url}
                  />
                  <div
                    className="hue-path-browser__breadcrumb-seperator"
                    data-testid={`${testId}-breadcrumb-seperator`}
                  >
                    {seperator}
                  </div>
                  <Dropdown
                    overlayClassName="hue-path-browser__dropdown"
                    menu={{
                      items: extractMenuItems(breadcrumbs.slice(1, breadcrumbs.length - 2)),
                      className: 'hue-path-browser__dropdown-menu'
                    }}
                    trigger={['hover', 'click']}
                    autoFocus
                    data-testid={`${testId}-dropdown`}
                  >
                    <Button
                      className="hue-path-browser__dropdown-button"
                      data-testid={`${testId}-dropdown-btn`}
                    >
                      ..
                    </Button>
                  </Dropdown>
                  <div
                    className="hue-path-browser__breadcrumb-seperator"
                    data-testid={`${testId}-breadcrumb-seperator`}
                  >
                    {seperator}
                  </div>
                  <OverflowingItem
                    key={breadcrumbs[breadcrumbs.length - 2].url}
                    label={breadcrumbs[breadcrumbs.length - 2].label}
                    url={breadcrumbs[breadcrumbs.length - 2].url}
                    handleFilePathChange={handleFilePathChange}
                    componentType="breadcrumb"
                  />
                  <div
                    className="hue-path-browser__breadcrumb-seperator"
                    data-testid={`${testId}-breadcrumb-seperator`}
                  >
                    {seperator}
                  </div>
                  <OverflowingItem
                    key={breadcrumbs[breadcrumbs.length - 1].url}
                    label={breadcrumbs[breadcrumbs.length - 1].label}
                    url={breadcrumbs[breadcrumbs.length - 1].url}
                    handleFilePathChange={handleFilePathChange}
                    componentType="breadcrumb"
                    isLastBreadcrumb
                  />
                </>
              )}
            </div>
            <Button
              className="hue-toggle-breadcrumb-input"
              title="Edit path"
              onClick={() => {
                setIsEditMode(true);
              }}
              data-testid={`${testId}-toggle-input-btn`}
            ></Button>
          </div>
        ) : (
          <div ref={wrapperRef}>
            <Input
              prefix={showIcon ? icons[extractFileSystem(breadcrumbs[0].label)] : <span />}
              defaultValue={decodeURIComponent(breadcrumbs[breadcrumbs.length - 1].url)}
              onPressEnter={customPath => {
                handleFilePathChange((customPath.target as HTMLInputElement).value);
              }}
              className="hue-path-browser__input"
              autoFocus
              data-testid={`${testId}-input`}
            ></Input>
          </div>
        )}
      </>
    );
  }
};

PathBrowser.defaultProps = defaultProps;
export default PathBrowser;
