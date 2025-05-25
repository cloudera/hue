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

import HdfsIcon from '../../components/icons/HdfsIcon';
import S3Icon from '../../components/icons/S3Icon';
import AdlsIcon from '../../components/icons/AdlsIcon';
import EditIcon from '@cloudera/cuix-core/icons/react/EditIcon';
import StatusSuccessTableIcon from '@cloudera/cuix-core/icons/react/StatusSuccessTableIcon';
import CopyPathIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';

import Breadcrumb from './Breadcrumb/Breadcrumb';
import './PathBrowser.scss';
import { getBreadcrumbs, getFileSystemAndPath, BreadcrumbData } from './PathBrowser.util';

const DEFAULT_URL_SCHEMA_SEPARATOR = '://';
const DEFAULT_PATH_SEPARATOR = '/';

interface PathBrowserProps {
  filePath: string;
  onFilepathChange: (path: string) => void;
  separator?: string;
  showIcon?: boolean;
  testId?: string;
}

const defaultProps = {
  testId: 'hue-path-browser'
};

const PathBrowser = ({
  filePath,
  onFilepathChange,
  separator = DEFAULT_PATH_SEPARATOR,
  showIcon = false,
  testId
}: PathBrowserProps): JSX.Element => {
  const [isEditMode, setIsEditMode] = useState(false);
  const [copied, setCopied] = useState(false);

  const icons = {
    hdfs: <HdfsIcon />,
    abfs: <AdlsIcon />,
    s3a: <S3Icon />
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

  const handleCopy = async () => {
    await navigator.clipboard.writeText(filePath);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
            data-testid={`${testId}-input`}
          />
        </div>
      );
    }

    return (
      <div className="hue-path-browser" data-testid={`${testId}`}>
        {showIcon && (
          <span
            data-testid={`${testId}__file-system-icon`}
            className="hue-path-browser__file-system-icon"
          >
            {icons[fileSystem]}
          </span>
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
                  {(index === 0 || index != breadcrumbs.length - 1) && (
                    <div
                      className="hue-path-browser__breadcrumb-separator"
                      data-testid={`${testId}-breadcrumb-separator`}
                    >
                      {index === 0 ? DEFAULT_URL_SCHEMA_SEPARATOR : separator}
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
                className="hue-path-browser__breadcrumb-separator"
                data-testid={`${testId}-breadcrumb-separator`}
              >
                {DEFAULT_URL_SCHEMA_SEPARATOR}
              </div>
              <Dropdown
                overlayClassName="hue-path-browser__dropdown cuix antd"
                menu={{
                  items: extractMenuItems(breadcrumbs.slice(1, breadcrumbs.length - 2)),
                  className: 'hue-path-browser__dropdown-menu'
                }}
                trigger={['hover', 'click']}
                data-testid={`${testId}-dropdown`}
              >
                <BorderlessButton
                  className="hue-path-browser__dropdown-button"
                  data-testid={`${testId}-dropdown-btn`}
                >
                  ..
                </BorderlessButton>
              </Dropdown>
              <div
                className="hue-path-browser__breadcrumb-separator"
                data-testid={`${testId}-breadcrumb-separator`}
              >
                {separator}
              </div>
              <Breadcrumb
                key={breadcrumbs[breadcrumbs.length - 2].url}
                label={breadcrumbs[breadcrumbs.length - 2].label}
                url={breadcrumbs[breadcrumbs.length - 2].url}
                onFilepathChange={onFilepathChange}
              />
              <div
                className="hue-path-browser__breadcrumb-separator"
                data-testid={`${testId}-breadcrumb-separator`}
              >
                {separator}
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
          onClick={() => setIsEditMode(true)}
          className="hue-path-browser__edit-path-btn"
          data-testid="hue-path-browser__edit-path-btn"
          title={'Edit Path'}
          icon={<EditIcon />}
        />
        <BorderlessButton
          onClick={handleCopy}
          className="hue-path-browser__copy-path-btn"
          title={copied ? 'Copied!' : 'Copy Path'}
          icon={
            copied ? (
              <StatusSuccessTableIcon data-testid="hue-path-browser__status-success-icon" />
            ) : (
              <CopyPathIcon data-testid="hue-path-browser__path-copy-icon" />
            )
          }
        />
      </div>
    );
  }

  return <></>;
};

PathBrowser.defaultProps = defaultProps;
export default PathBrowser;
