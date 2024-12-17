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
import { Input, Dropdown } from 'antd';
import { BorderlessButton } from 'cuix/dist/components/Button';
import { MenuItemType } from 'antd/lib/menu/hooks/useItems';

import HdfsIcon from '../../../components/icons/HdfsIcon';
import S3Icon from '../../../components/icons/S3Icon';
import AdlsIcon from '../../../components/icons/AdlsIcon';

import { BreadcrumbData } from '../types';
import Breadcrumb from './Breadcrumb/Breadcrumb';
import './PathBrowser.scss';
import { getBreadcrumbs, getFileSystemAndPath } from './PathBrowser.util';

interface PathBrowserProps {
  filePath: string;
  onFilepathChange: (path: string) => void;
  seperator: string;
  showIcon: boolean;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-path-browser'
};

const PathBrowser = ({
  filePath,
  onFilepathChange,
  seperator,
  showIcon,
  testId
}: PathBrowserProps): JSX.Element => {
  const [isEditMode, setIsEditMode] = useState(false);

  const icons = {
    hdfs: <HdfsIcon />,
    abfs: <AdlsIcon />,
    s3: <S3Icon />
  };

  const { fileSystem, path } = getFileSystemAndPath(filePath);
  const breadcrumbs = getBreadcrumbs(fileSystem, path);

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

  const breadcrumbInputRef = useRef<HTMLDivElement>(null);
  useOutsideAlerter(breadcrumbInputRef);

  const extractMenuItems = (breadcrumbMenu: BreadcrumbData[]) => {
    const menu: MenuItemType[] = breadcrumbMenu.map(breadcrumb => {
      return {
        key: breadcrumb.url,
        label: breadcrumb.label,
        onClick: () => onFilepathChange(breadcrumb.url)
      };
    });
    return menu;
  };

  if (breadcrumbs) {
    if (isEditMode) {
      return (
        <div ref={breadcrumbInputRef}>
          <Input
            prefix={showIcon ? icons[fileSystem] : <span />}
            defaultValue={filePath}
            onPressEnter={event => {
              onFilepathChange((event.target as HTMLInputElement).value);
            }}
            className="hue-path-browser__input"
            autoFocus
            data-testid={`${testId}-input`}
          />
        </div>
      );
    }

    return (
      <div className="hue-path-browser" data-testid={`${testId}`}>
        {showIcon && (
          <div
            className="hue-path-browser__file-system-icon"
            data-testid={`${testId}__file-system-icon`}
          >
            {icons[fileSystem]}
          </div>
        )}
        <div className="hue-path-browser__breadcrumbs" data-testid={`${testId}-breadcrumb`}>
          {breadcrumbs.length <= 3 ? (
            breadcrumbs.map((item: BreadcrumbData, index: number) => {
              return (
                <React.Fragment key={item.url + index}>
                  <Breadcrumb
                    key={item.url}
                    label={item.label}
                    url={item.url}
                    onFilepathChange={onFilepathChange}
                  />
                  {index != breadcrumbs.length - 1 && (
                    <div
                      className="hue-path-browser__breadcrumb-seperator"
                      data-testid={`${testId}-breadcrumb-seperator`}
                    >
                      {seperator}
                    </div>
                  )}
                </React.Fragment>
              );
            })
          ) : (
            <>
              <Breadcrumb
                label={breadcrumbs[0].label}
                url={breadcrumbs[0].url}
                onFilepathChange={onFilepathChange}
                key={breadcrumbs[0].url}
              />
              <div
                className="hue-path-browser__breadcrumb-seperator"
                data-testid={`${testId}-breadcrumb-seperator`}
              >
                {seperator}
              </div>
              <Dropdown
                overlayClassName="hue-path-browser__dropdown cuix antd"
                menu={{
                  items: extractMenuItems(breadcrumbs.slice(1, breadcrumbs.length - 2)),
                  className: 'hue-path-browser__dropdown-menu'
                }}
                trigger={['hover', 'click']}
                autoFocus
                data-testid={`${testId}-dropdown`}
              >
                <BorderlessButton
                  data-event=""
                  className="hue-path-browser__dropdown-button"
                  data-testid={`${testId}-dropdown-btn`}
                >
                  ..
                </BorderlessButton>
              </Dropdown>
              <div
                className="hue-path-browser__breadcrumb-seperator"
                data-testid={`${testId}-breadcrumb-seperator`}
              >
                {seperator}
              </div>
              <Breadcrumb
                key={breadcrumbs[breadcrumbs.length - 2].url}
                label={breadcrumbs[breadcrumbs.length - 2].label}
                url={breadcrumbs[breadcrumbs.length - 2].url}
                onFilepathChange={onFilepathChange}
              />
              <div
                className="hue-path-browser__breadcrumb-seperator"
                data-testid={`${testId}-breadcrumb-seperator`}
              >
                {seperator}
              </div>
              <Breadcrumb
                key={breadcrumbs[breadcrumbs.length - 1].url}
                label={breadcrumbs[breadcrumbs.length - 1].label}
                url={breadcrumbs[breadcrumbs.length - 1].url}
                onFilepathChange={onFilepathChange}
              />
            </>
          )}
        </div>
        <BorderlessButton
          data-event=""
          className="hue-path-browser__toggle-breadcrumb-input-btn"
          aria-label="hue-path-browser__toggle-breadcrumb-input-btn"
          title="Edit path"
          onClick={() => {
            setIsEditMode(true);
          }}
          data-testid={`${testId}-toggle-input-btn`}
        ></BorderlessButton>
      </div>
    );
  }

  return <></>;
};

PathBrowser.defaultProps = defaultProps;
export default PathBrowser;
