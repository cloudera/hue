
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TaskBrowser.scss';


const tasks = {
  'document cleanup': {
    params: [{ name: 'keep-days', type: 'integer' }],
  },
  'fileupload': {
    params: [{ name: 'file name', type: 'string' }],
  },
  'tmp clean up': {
    params: [
      { name: 'threshold for clean up', type: 'integer', max: 100 },
      { name: 'disk check interval', type: 'integer' },
    ],
  },
};

const ScheduleTaskPopup = ({ onClose, onSubmit }) => {
  const [selectedTask, setSelectedTask] = useState('');
  const [params, setParams] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setParams((prevParams) => ({
      ...prevParams,
      [name]: value,
    }));
  };

  const handleSubmit = () => {
    onSubmit(selectedTask, params);
    onClose();
  };

  return (
    <div className="popupStyle">
      <div className="popupContentStyle">
      <select value={selectedTask} onChange={(e) => setSelectedTask(e.target.value)}>
        <option value="">Select Task</option>
        {Object.keys(tasks).map((taskName) => (
          <option key={taskName} value={taskName}>{taskName}</option>
        ))}
      </select>
      {selectedTask && tasks[selectedTask].params.map((param) => (
        <input
          key={param.name}
          name={param.name}
          type="text"
          placeholder={param.name}
          onChange={(e) => {
            const { name, value } = e.target;
            setParams(prev => ({ ...prev, [name]: value }));
          }}
          value={params[param.name] || ''}
        />
      ))}
      <button onClick={handleSubmit}>Submit</button>
      <button onClick={onClose}>Close</button>
    </div>
    </div>
  );
};

const TaskBrowser = () => {
  const [showSchedulePopup, setShowSchedulePopup] = useState(false);
  const [scheduledTasks, setScheduledTasks] = useState([]); // Store an array of scheduled tasks

  const [showLogPopup, setShowLogPopup] = useState(false); // This should match where you use it
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [taskLogs, setTaskLogs] = useState("");

  const handleScheduleSubmit = (taskName, taskParams) => {
    const payload = {
      taskName,
      taskParams,
    };

    axios.post('/desktop/api2/handle_submit', payload)
    .catch(error => {
      console.error('Error scheduling task', error);
    });
  };

  // This function will open the schedule task popup
  const handleSchedulePopup = () => {
    setShowSchedulePopup(true);
  };

  // Add the function to handle showing logs
  const handleShowLogs = (taskId) => {
    // This function should set the current task ID and fetch the logs
    console.log("hi im in handlelogs");
    setCurrentTaskId(taskId);
    // Fetch the logs from the server
    axios.get(`/desktop/api2/get_task_logs/${taskId}/`)
      .then(response => {
        // Assuming the server response contains the logs in the data object
        setTaskLogs(response.data);
        setShowLogPopup(true); // Open the popup
      })
      .catch(error => {
        console.error('Error fetching logs:', error);
        // Handle the error appropriately
      });
  };

  return (
    <div>


      {showSchedulePopup && (
        <ScheduleTaskPopup
          onClose={() => setShowSchedulePopup(false)}
          onSubmit={handleScheduleSubmit}
        />
      )}

      <div style={{ margin: '20px 0' }}>
        <TaskBrowserTable tasks={scheduledTasks} handleShowLogs={handleShowLogs} handleSchedulePopup={handleSchedulePopup}/>
      </div>
      {showLogPopup && (
        <div className="popupStyle">
          <div className="popupContentStyle">
            <h2>Task Logs - {currentTaskId}</h2>
            <pre>{taskLogs}</pre>
            <button onClick={() => setShowLogPopup(false)}>Close</button>
          </div>
        </div>
      )}
    </div>

  );
};


// A helper function to calculate duration
const calculateDuration = (start, end) => {
  if (!start || !end) return 'N/A'; // If either start or end is missing

  const startDate = new Date(start);
  const endDate = new Date(end);
  const duration = endDate - startDate; // Duration in milliseconds

  if (isNaN(duration)) return 'Invalid Dates'; // If dates can't be parsed

  // Convert duration to hours, minutes, and seconds
  let seconds = Math.floor((duration / 1000) % 60);
  let minutes = Math.floor((duration / (1000 * 60)) % 60);
  let hours = Math.floor((duration / (1000 * 60 * 60)) % 24);

  // Build duration string
  let durationStr = '';
  if (hours > 0) durationStr += hours + 'h, ';
  if (minutes > 0 || hours > 0) durationStr += minutes + 'm, ';
  durationStr += seconds + 's';

  return durationStr;
};

function formatTimestamp(timestamp) {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true };
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', options);
}


// export const TaskBrowserTable = ({ tasks }) => {
export const TaskBrowserTable = ({ handleShowLogs, handleSchedulePopup }) => {

  // The tasks prop contains the array of scheduled tasks
  // logic to fetch tasks from database table

  const [tasks, setTasks] = useState([]);
  const [searchTerm, setSearchTerm] = useState(''); // state for the search term
  const [statusFilter, setStatusFilter] = useState({ success: false, failure: false, running: false, all: true }); // state to track status filter

  useEffect(() => {
    const fetchTasks = () => {
    axios.get('/desktop/api2/get_taskserver_tasks/')
        .then(response => {
            if (Array.isArray(response.data)) {
            //sort based on timestamp
            const sortedTasks = response.data.sort((a, b) => {
                // Assuming 'date_done' is the timestamp field and is in a comparable format
                return new Date(b.date_done) - new Date(a.date_done);
            });
            setTasks(sortedTasks);
          } else {
            console.error('Expected an array of tasks, but received:', response.data);
          }
        })
        .catch(error => {
            console.error('Error fetching tasks', error);
        });
    };

    fetchTasks();   //fetch tasks initially
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval); // Cleanup on unmount

  }, []);

  const handleTaskIdClick = (taskId) => {
    setCurrentTaskId(taskId);
    setShowLogsPopup(true);
    // Here, you could also fetch the logs immediately if you want to
    fetchTaskLogs(taskId);
  };



  const handleSearchChange = (e) => {
   console.log('Filtering tasks by:', e.target.value);
    setSearchTerm(e.target.value.toLowerCase());
    };

  // Function to handle status filter button clicks
  const handleStatusFilterChange = (status) => {
    setStatusFilter(prevStatusFilter => {
      const isAll = status === 'all';
      const newStatusFilter = {
        ...prevStatusFilter,
        [status]: isAll ? true : !prevStatusFilter[status],
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
  
  

  const filteredTasks = tasks.filter(task => {
    const taskNameMatch = task.result?.task_name?.toLowerCase().includes(searchTerm);
    const userIdMatch = task.result?.username?.toString().toLowerCase().includes(searchTerm);
    const taskIdMatch = task.task_id?.toString().toLowerCase().includes(searchTerm);
    // const statusMatch = statusFilter === 'all' || task.status.toLowerCase() === statusFilter;
    const statusMatch = statusFilter.all || 
                      (statusFilter.success && task.status.toLowerCase() === 'success') ||
                      (statusFilter.failure && task.status.toLowerCase() === 'failure') ||
                      (statusFilter.running && task.status.toLowerCase() === 'running');



    return (taskNameMatch || userIdMatch || taskIdMatch) && statusMatch;
  });





  // Render the table with the tasks data
  return (
    <div className="content-panel-inner">
    <div className="flex-container-style">
      <button onClick={handleSchedulePopup} className="btn schedule-task-button">Schedule Task</button>
      <input
        type="text"
        placeholder="Search by task name, user ID, or task ID..."
        onChange={handleSearchChange}
        className="button-input-style"
        style={{ flexGrow: 1 }} // flexGrow allows the input to take up available space
      />

      <label>
          <input
            type="checkbox"
            checked={statusFilter.success}
            onChange={() => handleStatusFilterChange('success')}
            className='hue-checkbox checkboxCompleted'
            style={{ opacity: 0, position: 'absolute', zIndex: -1 }}
          />
          <span className="custom-checkbox"></span> 
          <span className="checkbox-text">Succeeded</span>
        </label>
        <label>
          <input
            type="checkbox"
            checked={statusFilter.running}
            onChange={() => handleStatusFilterChange('running')}
            className='checkboxRunning'
            style={{ opacity: 0, position: 'absolute', zIndex: -1 }}
          />
          <span className="custom-checkbox"></span> 
          <span className="checkbox-text">Running</span>
        </label>
        <label>
          <input
            type="checkbox"
            checked={statusFilter.failure}
            onChange={() => handleStatusFilterChange('failure')}
            className='hue-checkbox checkboxFailed'
            style={{ opacity: 0, position: 'absolute', zIndex: -1 }}
          />
          <span className="custom-checkbox"></span> 
          <span className="checkbox-text">Failed</span>
        </label>
        <label>
          <input
            type="checkbox"
            checked={statusFilter.all}
            onChange={() => handleStatusFilterChange('all')}
            className='hue-checkbox'
            style={{ opacity: 0, position: 'absolute', zIndex: -1 }}
          />
        </label>
    </div>
      <table className="tableStyle hue-horizontally-scrollable ">
        <thead className="thStyle row-grayout-table-header">
          <tr>
            <th className="thStyle" style={{ width: '20%' }}>Task ID</th>
            <th className="thStyle" style={{ width: '3%' }}>User</th>
            <th className="thStyle" style={{ width: '5%' }}>Progress</th>
            <th className="thStyle" style={{ width: '7%' }}>Task Name</th>
            <th className="thStyle" style={{ width: '10%' }}>Parameters</th>
            <th className="thStyle" style={{ width: '5%' }}>Status</th>
            <th className="thStyle" style={{ width: '10%' }}>Started</th>
            <th className="thStyle" style={{ width: '5%' }}>Duration</th>
          </tr>
        </thead>
        <tbody className="tdStyle">
            {filteredTasks.map((task, index) => (
            // Determine the class based on the task's status

             <tr key={index}
             className={
                task.status === 'SUCCESS' ? 'row-success' :
                task.status === 'FAILURE' ? 'row-failure' :
                task.status === 'RUNNING' ? 'row-running' : ''
              }
             >
              <td className="tdStyle" onClick={() => handleShowLogs(task.task_id)}>
                {task.task_id}
              </td>
              <td className="tdStyle">{task.result?.username}</td>
              <td className="tdStyle">{task.progress}</td>
              <td className="tdStyle">{task.result?.task_name}</td>
              <td className="tdStyle">
                {task.result?.task_name === 'fileupload'
                  ? `{file name: ${task.result?.qqfilename}}`
                  : JSON.stringify(task.parameters)}
                {task.result?.task_name === 'document_cleanup'
                  ? `{keep days: ${task.result?.parameters}}`
                  : JSON.stringify(task.parameters)}
                {task.result?.task_name === 'tmp_cleanup'
                  ? `{keep days: ${task.result?.cleanup_threshold}}`
                  : JSON.stringify(task.parameters)}
              </td>
              <td className="tdStyle">
                <span className={`badgeStyle ${task.status === 'SUCCESS' ? 'badgeSuccess' : task.status === 'FAILURE' ? 'badgeFailure' : 'badgeRunning'}`}>

                  {task.status}
                </span>
              </td>
              <td className="tdStyle"> {formatTimestamp(task.result?.task_start)}</td>
              <td className="tdStyle">{calculateDuration(task.result?.task_start, task.date_done)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TaskBrowser;



