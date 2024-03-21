import React, { useState, useEffect } from 'react';
import { act } from '@testing-library/react';
import { i18nReact } from '../../../js/utils/i18nReact';
import axios from 'axios';
import { post, get, extractErrorMessage } from '../../../js/api/utils.ts';
import { calculateDuration, formatTimestamp } from '../../../js/utils/dateTimeUtils.ts';
import './TaskBrowser.scss';
import huePubSub from '../../../js/utils/huePubSub';
import Modal from 'antd/lib/modal/Modal';
import { Button, Tag, Input, Checkbox, Form, Select } from 'antd';
import 'antd/dist/antd.css';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import DangerButton from 'cuix/dist/components/Button/DangerButton';
import Table from 'cuix/dist/components/Table';

const { Option } = Select;

const tasks = {
  'document cleanup': {
    params: [{ name: 'keep-days', type: 'integer' }]
  },
  'tmp clean up': {
    params: [{ name: 'threshold for clean up', type: 'integer', max: 100 }]
  }
};

const ShowScheduleTaskPopup = ({ onClose, onSubmit, open }) => {
  const [selectedTask, setSelectedTask] = useState('');
  const [params, setParams] = useState({
    'keep-days': '30', // Default value for "keep days"
    'threshold for clean up': '90' // Default value for "threshold for clean up"
  });

  const handleChange = e => {
    const { name, value } = e.target;
    setParams(prevParams => ({
      ...prevParams,
      [name]: value
    }));
  };

  const handleSubmit = () => {
    onSubmit(selectedTask, params);
    onClose();
  };

  return (
    <Modal
      title={'Schedule Task'}
      open={open}
      onOk={handleSubmit}
      onCancel={onClose}
      okText={'Submit'}
      width={530}
      className="hue-file-chooser__modal"
    >
      <div className="task-selection">
        <Select
          value={selectedTask}
          onChange={setSelectedTask}
          placeholder="Select Task"
          style={{ width: '100%' }}
        >
          {Object.keys(tasks).map(taskName => (
            <Option key={taskName} value={taskName}>
              {taskName}
            </Option>
          ))}
        </Select>
      </div>
      <div className="vertical-spacer"></div>
      {selectedTask && (
        <div className="parameter-inputs">
          {tasks[selectedTask].params.map(param => (
            <div key={param.name} className="parameter-row">
              <Form.Item label={param.name}>
                <Input
                  name={param.name}
                  type="text"
                  placeholder={param.name}
                  onChange={handleChange}
                  value={params[param.name] || ''}
                />
              </Form.Item>
            </div>
          ))}
        </div>
      )}
    </Modal>
  );
};

const TaskBrowser: React.FC = (): React.ReactElement => {
  const [showSchedulePopup, showScheduleTaskPopup] = useState(false);
  const [scheduledTasks] = useState([]); // Store an array of scheduled tasks

  const [showLogPopup, setShowLogPopup] = useState(false); // This should match where you use it
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [taskLogs, setTaskLogs] = useState('');

  const handleScheduleSubmit = (taskName, taskParams) => {
    const payload = {
      taskName,
      taskParams
    };

    axios
      .post('/desktop/api2/handle_submit', payload, {
        transformResponse: [
          function (data) {
            try {
              return JSON.parse(data);
            } catch (e) {
              return data;
            }
          }
        ]
      })
      .then(() => {
        act(() => huePubSub.publish('hue.global.info', { message: `Task submitted successfully` }));
      })
      .catch(error => {
        const errorMessage = extractErrorMessage(error);
        act(() =>
          huePubSub.publish('hue.global.error', {
            message: `Failed to submit scheduling task ${errorMessage}`
          })
        );
      });
  };

  // This function will open the schedule task popup
  const handleSchedulePopup = () => {
    showScheduleTaskPopup(true);
  };

  const ShowTaskLogsHandler = taskId => {
    setCurrentTaskId(taskId);
    get(`/desktop/api2/get_task_logs/${taskId}/`)
      .then(response => {
        setTaskLogs(response.data);
        setShowLogPopup(true);
      })
      .catch(error => {
        act(() =>
          huePubSub.publish('hue.global.error', { message: `Error fetching task logs: ${error}` })
        );
      });
  };

  return (
    <div>
      {showSchedulePopup && (
        <ShowScheduleTaskPopup
          onClose={() => showScheduleTaskPopup(false)}
          onSubmit={handleScheduleSubmit}
          open={showSchedulePopup}
        />
      )}
      <div style={{ margin: '20px 0' }}>
        <TaskBrowserTable
          tasks={scheduledTasks}
          ShowTaskLogsHandler={ShowTaskLogsHandler}
          handleSchedulePopup={handleSchedulePopup}
        />
      </div>
      {showLogPopup && (
        <div className="popupStyle">
          <div className="popupContentStyle">
            <h2>Task Logs - {currentTaskId}</h2>
            <pre>{taskLogs}</pre>
            <Button onClick={() => setShowLogPopup(false)}>Close</Button>
          </div>
        </div>
      )}
    </div>
  );
};

interface TaskBrowserTableProps {
  ShowTaskLogsHandler: (taskId: string) => void;
  handleSchedulePopup: () => void;
}

export const TaskBrowserTable: React.FC<TaskBrowserTableProps> = ({
  ShowTaskLogsHandler,
  handleSchedulePopup
}) => {
  const [tasks, setTasks] = useState<Task_Status[]>([]);
  const [searchTerm, setSearchTerm] = useState(''); // state for the search term
  const [statusFilter, setStatusFilter] = useState({
    success: false,
    failure: false,
    running: false,
    all: true
  });
  const [selectedTasks, setSelectedTasks] = useState([]);

  // rowSelection object needed for the Table component to handle row selection
  const rowSelection = {
    selectedRowKeys: selectedTasks,
    onChange: selectedRowKeys => {
      setSelectedTasks(selectedRowKeys);
    }
  };

  const { t } = i18nReact.useTranslation();

  const columns = [
    {
      title: t('Task ID'),
      dataIndex: 'task_id',
      key: 'task_id',
      render: (text, record) => <a onClick={() => ShowTaskLogsHandler(record.task_id)}>{text}</a>
    },
    {
      title: t('User'),
      dataIndex: ['result', 'username'],
      key: 'user'
    },
    {
      title: t('Progress'),
      dataIndex: ['result', 'progress'],
      key: 'progress'
    },
    {
      title: t('Task Name'),
      dataIndex: ['result', 'task_name'],
      key: 'task_name'
    },
    {
      title: t('Parameters'),
      dataIndex: 'parameters',
      key: 'parameters',
      render: (text, record) => (
        <div>
          {record.result?.task_name === 'fileupload' && (
            <span>{`{file name: ${record.result?.qqfilename}}`}</span>
          )}
          {record.result?.task_name === 'document_cleanup' && (
            <span>{`{keep days: ${record.result?.parameters}}`}</span>
          )}
          {record.result?.task_name === 'tmp_cleanup' && (
            <span>{`{cleanup threshold: ${record.result?.parameters}}`}</span>
          )}
        </div>
      )
    },
    {
      title: t('Status'),
      dataIndex: 'status',
      key: 'status',
      render: status => <Tag color={statusTagColor(status)}>{status.toUpperCase()}</Tag>
    },
    {
      title: t('Started'),
      dataIndex: ['result', 'task_start'],
      key: 'started',
      render: text => formatTimestamp(text)
    },
    {
      title: t('Duration'),
      key: 'duration',
      render: (_, record) => calculateDuration(record.result?.task_start, record.date_done)
    }
  ];

  // Custom function to determine Tag color based on status
  const statusTagColor = status => {
    switch (status.toUpperCase()) {
      case 'SUCCESS':
        return 'success';
      case 'FAILURE':
        return 'error'; // Ant Design does not have 'failure', using 'error' instead
      case 'RUNNING':
        return 'warning';
      default:
        return '';
    }
  };

  // Function to calculate row class names based on status
  const getRowClassName = record => {
    switch (record.status.toUpperCase()) {
      case 'SUCCESS':
        return 'row-success';
      case 'FAILURE':
        return 'row-failure';
      case 'RUNNING':
        return 'row-running';
      default:
        return '';
    }
  };

  useEffect(() => {
    const fetchTasks = () => {
      get('/desktop/api2/get_taskserver_tasks/', null, {
        transformResponse: data => {
          return data;
        }
      })
        .then(tasks => {
          if (Array.isArray(tasks)) {
            const sortedTasks = tasks.sort((a, b) => {
              const dateA = new Date(a.date_done);
              const dateB = new Date(b.date_done);
              if (!isNaN(dateA) && !isNaN(dateB)) {
                return dateB - dateA;
              }
              return 0;
            });
            setTasks(sortedTasks);
          } else {
            act(() =>
              huePubSub.publish('hue.global.error', {
                message: `Expected an array of tasks, but received: ${tasks}`
              })
            );
          }
        })
        .catch(error => {
          const errorMessage = extractErrorMessage(error);
          act(() =>
            huePubSub.publish('hue.global.error', {
              message: `Error fetching tasks from redis ${errorMessage}`
            })
          );
        })
        .finally(() => {
          setTimeout(fetchTasks, 5000);
        });
    };

    fetchTasks(); //fetch tasks initially
  }, []);

  const handleSearchChange = e => {
    setSearchTerm(e.target.value.toLowerCase());
  };

  const handleStatusFilterChange = status => {
    setStatusFilter(prevStatusFilter => {
      const isAll = status === 'all';
      const newStatusFilter = {
        ...prevStatusFilter,
        [status]: isAll ? true : !prevStatusFilter[status]
      };

      if (isAll) {
        // If 'all' is selected, set everything else to false
        newStatusFilter.success = false;
        newStatusFilter.failure = false;
        newStatusFilter.running = false;
      } else {
        // If any specific status is toggled, set 'all' to false
        newStatusFilter.all = false;
      }

      // If no individual statuses are selected, default to 'all'
      if (!newStatusFilter.success && !newStatusFilter.failure && !newStatusFilter.running) {
        newStatusFilter.all = true;
      }

      return newStatusFilter;
    });
  };

  enum TaskStatus {
    Success = 'SUCCESS',
    Failure = 'FAILURE',
    Running = 'RUNNING'
  }

  interface Task_Status {
    result?: {
      task_name: string;
      username: string;
    };
    task_id: string;
    status: TaskStatus;
  }

  const filteredTasks = tasks.filter(task => {
    const taskNameMatch = task.result?.task_name?.toLowerCase().includes(searchTerm);
    const userIdMatch = task.result?.username?.toLowerCase().includes(searchTerm);
    const taskIdMatch = task.task_id?.toLowerCase().includes(searchTerm);
    const statusMatch =
      statusFilter.all ||
      (statusFilter.success && task.status === TaskStatus.Success) ||
      (statusFilter.failure && task.status === TaskStatus.Failure) ||
      (statusFilter.running && task.status === TaskStatus.Running);

    return (taskNameMatch || userIdMatch || taskIdMatch) && statusMatch;
  });

  const handleKillTask = taskId => {
    post(`/desktop/api2/kill_task/${taskId}/`)
      .then(response => {
        // Assuming the server response is in the expected format
        const { status, message } = response;
        if (status === 'success') {
          act(() =>
            huePubSub.publish('hue.global.error', { message: `Task: ${taskId} has been killed.` })
          );
        } else if (status === 'info') {
          act(() =>
            huePubSub.publish('', {
              message: `Task: ${taskId} has already been completed or revoked.`
            })
          );
        } else {
          act(() =>
            huePubSub.publish('hue.global.error', {
              message: `Task: ${taskId} could not be killed. ${message}`
            })
          );
        }
      })
      .catch(error => {
        const errorMessage = extractErrorMessage(error);
        act(() =>
          huePubSub.publish('hue.global.error', {
            message: `Task not killed - Error: ${errorMessage}`
          })
        );
      });
  };

  const handleKillSelectedTasks = () => {
    selectedTasks.forEach(taskId => {
      handleKillTask(taskId);
    });
    setSelectedTasks([]);
  };

  // Render the table with the tasks data
  return (
    <div className="content-panel-inner">
      <div className="flex-container-style">
        <PrimaryButton onClick={handleSchedulePopup}>Schedule Task</PrimaryButton>
        <DangerButton onClick={handleKillSelectedTasks}>Kill Task</DangerButton>
        <Input
          type="text"
          placeholder="Search by task name, user ID, or task ID..."
          onChange={handleSearchChange}
          className="button-input-style"
          style={{ flexGrow: 1 }}
        />
        <Checkbox
          checked={statusFilter.success}
          onChange={() => handleStatusFilterChange('success')}
        />
        <span className="success-text">Succeeded</span>
        <Checkbox
          checked={statusFilter.running}
          onChange={() => handleStatusFilterChange('running')}
        />
        <span className="running-text">Running</span>
        <Checkbox
          checked={statusFilter.failure}
          onChange={() => handleStatusFilterChange('failure')}
        />
        <span className="failed-text">Failed</span>
        <Checkbox checked={statusFilter.all} onChange={() => handleStatusFilterChange('all')} />
        All
      </div>
      <Table
        rowSelection={rowSelection}
        columns={columns}
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        dataSource={filteredTasks.map(({ children, ...task }) => task)}
        rowKey="task_id"
        rowClassName={getRowClassName}
        pagination={false}
        size="small"
      />
    </div>
  );
};

export default TaskBrowser;
