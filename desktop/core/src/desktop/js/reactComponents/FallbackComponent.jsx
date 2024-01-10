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
};

const thStyle = {
  border: '1px solid #ddd',
  padding: '8px',
  textAlign: 'left',
  backgroundColor: '#f2f2f2',
};

const tdStyle = {
  border: '1px solid #ddd',
  padding: '8px',
};

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
//     .then(response => {
//       const taskInfo = {
//         ...response.data,
//         time: response.data.time,
//         progress: response.data.progress,
//         triggered_by: response.data.triggered_by,
//         task_name: response.data.taskName,
//         parameters: response.data.taskParams,
//         status: response.data.status,
//         task_id: response.data.task_id, // Assuming the backend returns a unique task ID
//       };
//       console.log('task name')
//       setScheduledTasks(prevTasks => [...prevTasks, taskInfo]);
//     })
    .catch(error => {
      console.error('Error scheduling task', error);
    });
//     // Here you would call your backend to schedule the task
//     console.log(`Scheduling task ${taskName} with params`, taskParams);
//     // For now we'll just simulate scheduling a task
//     const taskInfo = {
//       taskName,
//       taskParams,
//       time: new Date().toLocaleTimeString(),
//       progress: 'Scheduled',
//       user: 'currentUser', // Replace with actual current user
//       status: 'In progress',
//       taskId: Math.random().toString(36).substr(2, 9), // Simulate a unique task ID
//     };
//     setScheduledTasks((prevTasks) => [...prevTasks, taskInfo]);
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


// export const TaskBrowserTable = ({ tasks }) => {
export const TaskBrowserTable = () => {
  // The tasks prop contains the array of scheduled tasks
  // logic to fetch tasks from database table

  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    const fetchTasks = () => {
    axios.get('/desktop/api2/get_taskserver_tasks/')
        .then(response => {
            setTasks(response.data);
        })
        .catch(error => {
            console.error('Error fetching tasks', error);
        });
    };

    fetchTasks();   //fetch tasks initially
    const interval = setInterval(fetchTasks, 5000);

    return () => clearInterval(interval); // Cleanup on unmount

  }, []);

  // Render the table with the tasks data
  return (
    <div>
      <h1 style={{ marginBottom: '10px' }}>Task Browser</h1>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thStyle}>Time</th>
            <th style={thStyle}>Progress</th>
            <th style={thStyle}>Triggered By</th>
            <th style={thStyle}>Task Name</th>
            <th style={thStyle}>Parameters</th>
            <th style={thStyle}>Status</th>
            <th style={thStyle}>Task ID</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task, index) => (
            <tr key={index} style={{ borderBottom: '1px solid #ddd', backgroundColor: index % 2 ? '#f9f9f9' : '#fff' }}>
              <td style={tdStyle}>{task.time}</td>
              <td style={tdStyle}>{task.progress}</td>
              <td style={tdStyle}>{task.triggered_by}</td>
              <td style={tdStyle}>{task.task_name}</td>
              <td style={tdStyle}>{JSON.stringify(task.parameters)}</td>
              <td style={tdStyle}>{task.status}</td>
              <td style={tdStyle}>{task.task_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TaskScheduler;


