import { Divider } from 'antd';
import React, { FunctionComponent } from 'react';

import './ToolbarDivider.scss';

interface ToolbarDividerProps {
  testId?: string;
}

const defaultProps = {
  testId: 'hue-toolbar-divier'
};

const ToolbarDivider: FunctionComponent<ToolbarDividerProps> = ({ testId }: ToolbarDividerProps) => (
  <li className="hue-toolbar-divider" data-testid={testId}>
    <Divider type="vertical" />
  </li>
);

ToolbarDivider.defaultProps = defaultProps;
export default  ToolbarDivider;