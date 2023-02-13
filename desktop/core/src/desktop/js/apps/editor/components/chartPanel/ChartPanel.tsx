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

import { Button, Select, Divider } from 'antd';
import React, { useState, useMemo } from 'react';

import ImportIcon from '../../../../components/icons/ImportIcon';
import Toolbar, { ToolbarButton, ToolbarDivider } from '../../../../reactComponents/Toolbar/Toolbar';
import PushDrawer, { DrawerHeader } from '../../../../reactComponents/PushDrawer/PushDrawer';
import { useHuePubSub } from '../../../../reactComponents/useHuePubSub';
import huePubSub from '../../../../utils/huePubSub';
import {
  ExecutableChartUpdatedEvent,
  ExecutableTransitionedEvent,
  EXECUTABLE_CHART_UPDATED_TOPIC,
  EXECUTABLE_RESULT_UPDATED_TOPIC,
  EXECUTABLE_TRANSITIONED_TOPIC
} from '../../execution/events';
import ExecutionResult from '../../execution/ExecutionResult';
import SqlExecutable, { ExecutionStatus } from '../../execution/sqlExecutable';

import './ChartPanel.scss';

const MAX_NUMBER_OF_ROWS = 100;

const { Option } = Select;

const isLoading = (statusTransition: ExecutableTransitionedEvent | undefined) => {
  const newStatus = statusTransition?.newStatus;
  const result = statusTransition?.executable.getResult();
  const waitingForActiveExecutableResultToUpdate =
    newStatus === ExecutionStatus.available && result?.cleanedMeta?.length === 0;

  return (
    // newStatus === undefined ||
    newStatus === ExecutionStatus.starting ||
    newStatus === ExecutionStatus.waiting ||
    newStatus === ExecutionStatus.running ||
    waitingForActiveExecutableResultToUpdate
  );
};

export interface ChartPanelProps {
  activeExecutable: SqlExecutable | (() => SqlExecutable);
  testId?: string;
}
const defaultProps = {
  testId: 'chart-panel'
};

const ChartPanel = ({ activeExecutable, testId }: ChartPanelProps) => {
  const executable = typeof activeExecutable === 'function' ? activeExecutable() : activeExecutable;
  const result: ExecutionResult = executable?.result;

  const { chartType } = executable.chartSettings;

  const handleChartTypeChange = (value: string | number) => {
    huePubSub.publish<ExecutableChartUpdatedEvent>(EXECUTABLE_CHART_UPDATED_TOPIC, {
      chartType: value.toString()
    });
  };

  // We use the pubsub to rerender the ChartPanel after the executable result is updated, e.g.
  // when the user clicks the execute button.
  useHuePubSub({ topic: EXECUTABLE_RESULT_UPDATED_TOPIC });

  // We use the pubsub to rerender the ChartPanel after the executable status changes.
  // This will also indirectly rerender the component when the result is updated
  const statusTransition: ExecutableTransitionedEvent | undefined = useHuePubSub({
    topic: EXECUTABLE_TRANSITIONED_TOPIC
  });

  const loading = isLoading(statusTransition);
  const expired = statusTransition?.newStatus === ExecutionStatus.expired;
  const noData = !loading && !expired && (!result || result?.rows?.length === 0);
  const tooMuchDataToRender = result?.rows?.length > MAX_NUMBER_OF_ROWS;
  const showChart = result?.rows?.length && !tooMuchDataToRender;

  const [configIsOpen, setConfigIsOpen] = useState(false);

  const toggleConfigDrawer = () => {
    setConfigIsOpen(open => !open);
  };

  const close = () => {
    setConfigIsOpen(false);
  };

  console.info('executable', executable);

  const handleChange = (value: string) => {
    console.log(`selected ${value}`);
  };

  const items = [
    { label: 'item 1', key: 'item-1' }, // remember to pass the key prop
    { label: 'item 2', key: 'item-2' }, // which is required
    {
      label: 'sub menu',
      key: 'submenu',
      children: [{ label: 'item 3', key: 'submenu-item-1' }]
    }
  ];

  const drawerConfig = useMemo(
    () => ({
      width: '277px',
      isOpen: configIsOpen,
      header: () => <DrawerHeader onClose={close} title={'Chart settings'} />,
      content: () => <div>I'm the drawer</div>
    }),
    [configIsOpen]
  );

  return (
    <div className="hue-chart-panel antd-reset antd">
      <Toolbar testId={`${testId}-toolbar`} content={() => <>
        <ToolbarButton type="link">Add a chart name</ToolbarButton>
        <div className="hue-toolbar__spacer"></div>
        <ToolbarDivider/>
        <ToolbarButton icon={<ImportIcon/>} type="link">Configure</ToolbarButton>
        <ToolbarButton icon={<ImportIcon/>} iconPosition="right" type="link">Share</ToolbarButton>
        <ToolbarButton type="link">Download</ToolbarButton>
      </>} />
      <PushDrawer leftDrawer={drawerConfig} mainContent={() => <div>I'm the main content</div>} />

      {/* <div
        className={classNames('hue-chart-panel-settings', {
          'hue-chart-panel-settings--showing': configIsOpen
        })}
      >
        Hello
      </div>
      <div 
        className={classNames('hue-chart-panel-content', {
          'hue-chart-panel-content--narrow': configIsOpen
        })}      
      >
        <div>
          Bbl ablabl b alblab lba lba lbalbla lb alblba lba lb lablablkbsbjasid iun iasn diuas
          diouahs iudhais hdiuah siudhiuashd aoiuh aoisuhd oiaushd iuash diuh aisudh iaushd iuahs
          diuahs doiuahs oiduha siudh aoisuhd oiu
          {loading ? 'LOADING' : ''}
          {expired ? 'EXPIRED' : ''}
          {noData ? 'NO DATA' : ''}
          {tooMuchDataToRender ? 'TOO MUCH DATA' : ''}
          {showChart ? JSON.stringify(result.rows) : ''}
        </div>
      </div> */}
      {/* testig drawer
      <div style={{ marginTop: 16 }}>
        <Button type="primary" onClick={showDrawer}>
          Open
        </Button>
      </div>
      <Drawer
        title="Chart settings"
        placement="left"
        closable={true}
        onClose={onClose}
        open={open}
        getContainer={false}
        mask={false}
      >
        <p>Some contents...</p>
      </Drawer> */}

      {/* <Segmented
        value={chartType}
        onChange={handleChartTypeChange}
        options={[
          {
            label: <BarChartOutlined />,
            value: 'bar-chart'
          },
          {
            label: <LineChartOutlined />,
            value: 'line-chart'
          },
          {
            label: <PieChartOutlined />,
            value: 'pie-chart'
          },
          {
            label: <DotChartOutlined />,
            value: 'scatter-plot'
          },
          {
            label: <HeatMapOutlined />,
            value: 'heat-map'
          },
          {
            label: <PushpinOutlined />,
            value: 'markers'
          }
        ]}
      /> 
      
      <Select defaultValue="lucy" style={{ width: 120 }}  onChange={handleChange}>
        <Option value="jack">Jack</Option>
        <Option value="lucy">Lucy</Option>
        <Option value="disabled" disabled>
          Disabled
        </Option>
        <Option value="Yiminghe">yiminghe</Option>
      </Select>        
      
      <Menu items={items} /> */}
    </div>
  );
};

ChartPanel.defaultProps = defaultProps;

export default ChartPanel;
