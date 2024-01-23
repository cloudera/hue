// 'use strict';
//
// import * as React from 'react';
//
//
// // This component is rendered if the react loadComponent can't find
// // which react component to use
// const FallbackComponent = () => {
//   return (
//     <div>Placeholder component 1
//     </div>
//   );
// };
//
// export default FallbackComponent;

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  border: '1px solid #ddd',
};

const thStyle = {
  padding: '8px',
  textAlign: 'left',
  backgroundColor: '#f2f2f2',
  borderBottom: '1px solid #ddd',
};

const tdStyle = {
  padding: '8px',
  borderBottom: '1px solid #ddd',
};

const badgeStyle = {
  display: 'inline-block', // Makes the element behave like a block but only take up as much width as necessary
  padding: '4px 8px', // Adds space inside the badge, first value is top and bottom, second is left and right
  borderRadius: '4px', // Gives the badge rounded corners
  color: 'white', // Text color
  backgroundColor: 'green', // Background color, you can replace this with appropriate color values
  textAlign: 'center', // Centers the text inside the badge
  minWidth: '75px', // Ensures the badge has at least this width
};

// Then use it for your status label
<td style={tdStyle}>
  <span style={badgeStyle}>SUCCEEDED</span>
</td>



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

const getBadgeStyle = (status) => ({
  display: 'inline-block',
  padding: '4px 8px',
  borderRadius: '4px',
  color: 'white',
  backgroundColor: status === 'SUCCESS' ? 'green' :
                    status === 'FAILURE' ? 'red' :
                    status === 'RUNNING' ? 'orange' : 'grey', // Default color
  textAlign: 'center',
  minWidth: '75px',
});

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
    <div className="popup">
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
          onChange={handleChange}
          value={params[param.name] || ''}
        />
      ))}
      <button onClick={handleSubmit}>Submit</button>
      <button onClick={onClose}>Close</button>
    </div>
  );
};

const TaskScheduler = () => {
  const [showSchedulePopup, setShowSchedulePopup] = useState(false);
  const [scheduledTasks, setScheduledTasks] = useState([]); // Store an array of scheduled tasks

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

  return (
    <div>
      <button onClick={() => setShowSchedulePopup(true)}>Schedule Task</button>
      {showSchedulePopup && (
        <ScheduleTaskPopup
          onClose={() => setShowSchedulePopup(false)}
          onSubmit={handleScheduleSubmit}
        />
      )}
{/*       <TaskBrowserTable tasks={scheduledTasks} />  */}{/* Pass the scheduled tasks to the table */}
      <div style={{ margin: '20px 0' }}>
        <TaskBrowserTable tasks={scheduledTasks} />
      </div>
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


// export const TaskBrowserTable = ({ tasks }) => {
export const TaskBrowserTable = () => {
  // The tasks prop contains the array of scheduled tasks
  // logic to fetch tasks from database table

  const [tasks, setTasks] = useState([]);
  const [searchTerm, setSearchTerm] = useState(''); // state for the search term
  const [statusFilter, setStatusFilter] = useState('all'); // state to track status filter
//   const [userIdFilter, setUserIdFilter] = useState(''); // state to track user_id filter
//   const [taskIdFilter, setTaskIdFilter] = useState(''); // state to track task_id filter

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

  const handleSearchChange = (e) => {
   console.log('Filtering tasks by:', e.target.value);
    setSearchTerm(e.target.value.toLowerCase());
    };

  // Function to handle status filter button clicks
  const handleStatusFilterChange = (status) => {
    setStatusFilter(status);
  };
//
//   const handleUserIdFilterChange = (e) => {
//     setUserIdFilter(e.target.value.toLowerCase());
//   };
//
//   const handleTaskIdFilterChange = (e) => {
//     setTaskIdFilter(e.target.value.toLowerCase());
//   };

  const filteredTasks = tasks.filter(task => {
    const taskNameMatch = task.result?.task_name?.toLowerCase().includes(searchTerm);
    const userIdMatch = task.result?.user_id?.toString().toLowerCase().includes(searchTerm);
    const taskIdMatch = task.task_id?.toString().toLowerCase().includes(searchTerm);
    const statusMatch = statusFilter === 'all' || task.status.toLowerCase() === statusFilter;

    return (taskNameMatch || userIdMatch || taskIdMatch) && statusMatch;
  });

  const buttonStyle = {
    marginRight: '2px',
    marginLeft: '2px',
  };

  // Style for the flex container
  const flexContainerStyle = {
    display: 'flex',
    alignItems: 'center', // This will align the items vertically
    marginBottom: '10px'
  };

  // Style for the buttons and input to have spacing
  const buttonInputStyle = {
    marginRight: '2px', // This provides spacing to the right of each element
    marginBottom: '0'   // Removes any default margin-bottom
  };




  // Render the table with the tasks data
  return (
//     <div>
// {/*       <h1 style={{ marginBottom: '10px' }}>Task Browser</h1> */}
    <div className="jobbrowser-full">
    <div className="content-panel-inner">
    <div className="hue-breadcrumbs-bar" style={flexContainerStyle}>
      <input
        type="text"
        placeholder="Search by task name, user ID, or task ID..."
        onChange={handleSearchChange}
        style={{ ...buttonInputStyle, flexGrow: 1 }} // flexGrow allows the input to take up available space
      />
      <button onClick={() => handleStatusFilterChange('success')} style={buttonInputStyle} className="btn btn-success">Succeeded</button>
          <button onClick={() => handleStatusFilterChange('failure')} style={buttonInputStyle} className="btn btn-danger">Failed</button>
          <button onClick={() => handleStatusFilterChange('running')} style={buttonInputStyle} className="btn btn-info">Running</button>
          <button onClick={() => handleStatusFilterChange('all')} style={buttonInputStyle} className="btn">All</button>
    </div>
    <div className="hue-jobs-table hue-horizontally-scrollable">
      <table style={tableStyle}>
        <thead className="thStyle">
          <tr>
            <th style={{ ...thStyle, width: '20%'}}>Task ID</th>
            <th style={{ ...thStyle, width: '3%'}}>User</th>
            <th style={{ ...thStyle, width: '5%'}}>Progress</th>
            <th style={{ ...thStyle, width: '7%'}}>Task Name</th>
            <th style={{ ...thStyle, width: '10%'}}>Parameters</th>
            <th style={{ ...thStyle, width: '5%'}}>Status</th>
            <th style={{ ...thStyle, width: '10%'}}>Started</th>
            <th style={{ ...thStyle, width: '5%'}}>Duration</th>
          </tr>
        </thead>
        <tbody className="tdStyle">
            {filteredTasks.map((task, index) => (
             <tr key={index}>
              <td style={tdStyle}>{task.task_id}</td>
              <td style={tdStyle}>{task.result?.username}</td>
              <td style={tdStyle}>{task.progress}</td>
              <td style={tdStyle}>{task.result?.task_name}</td>
              <td style={tdStyle}>
                {task.result?.task_name === 'fileupload'
                  ? `{file name: ${task.result?.qqfilename}}`
                  : JSON.stringify(task.parameters)}
              </td>
              <td style={tdStyle}>
                <span style={getBadgeStyle(task.status)}>
                  {task.status}
                </span>
              </td>
              <td style={tdStyle}>{task.result?.task_start}</td>
              <td style={tdStyle}>{calculateDuration(task.result?.task_start, task.result?.task_end)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </div>
    </div>
  );
};

export default TaskScheduler;


