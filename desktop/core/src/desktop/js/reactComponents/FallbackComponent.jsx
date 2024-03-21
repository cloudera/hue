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

import React, { useState } from 'react';
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

    axios.post('/api/handle_submit', payload)
    .then(response => {
      const taskInfo = {
        ...response.data,
        taskname: taskName,
        time: response.data.time,
        progress: response.data.progress,
        user: response.data.user, // Replace with actual current user
        status: response.data.status,
        taskId: response.data.taskId, // Assuming the backend returns a unique task ID
      };
      setScheduledTasks(prevTasks => [...prevTasks, taskInfo]);
    })
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


export const TaskBrowserTable = ({ tasks }) => {
  // The tasks prop contains the array of scheduled tasks

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
              <td style={tdStyle}>{task.user}</td>
              <td style={tdStyle}>{task.taskName}</td>
              <td style={tdStyle}>{JSON.stringify(task.taskParams)}</td>
              <td style={tdStyle}>{task.status}</td>
              <td style={tdStyle}>{task.taskId}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TaskScheduler;























// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
//
// const TasksTable = () => {
//   const [tasks, setTasks] = useState([]);
//
//   useEffect(() => {
//     // Here you would fetch the task data from your backend API
//     // For the example, we're using static data
//     const fetchedTasks = [
//       { id: 1,
//         name: 'Task 1',
//         parameter: 'Parameter for Task 1',
//         schedule: 'Interval for Task 1',
//         triggeredBy: 'Triggered by for Task 1',
//         isActive: true,
//         lastTriggered: 'Last triggered time for Task 1' },
//         { id: 2,
//         name: 'Task 2',
//         parameter: 'Parameter for Task 2',
//         schedule: 'Interval for Task 2',
//         triggeredBy: 'Triggered by for Task 2',
//         isActive: true,
//         lastTriggered: 'Last triggered time for Task 2' }
//       // ...more tasks
//     ];
//     setTasks(fetchedTasks);
//   }, []);
//
//   const triggerTask = (taskId) => {
//     console.log(`Triggering task with ID: ${taskId}`);
//     // Here you would implement the API call to trigger the task
//   };
//
//   return (
//     <table style={{ borderCollapse: 'collapse', width: '100%' }}>
//       <thead>
//         <tr>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Tasks</th>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Parameters</th>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Schedule interval</th>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Triggered by</th>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Is active</th>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Last triggered</th>
//           <th style={{ border: '1px solid black', padding: '8px', backgroundColor: '#f2f2f2' }}>Actions</th>
//         </tr>
//       </thead>
//       <tbody>
//         {tasks.map(task => (
//         <>
//           <tr key={task.id} style={{ borderBottom: '1px solid #ddd' }}>
//             <td style={{ border: '1px solid black', padding: '8px' }}>{task.name}</td>
//             <td style={{ border: '1px solid black', padding: '8px' }}>{task.parameter}</td>
//             <td style={{ border: '1px solid black', padding: '8px' }}>{task.schedule}</td>
//             <td style={{ border: '1px solid black', padding: '8px' }}>{task.triggeredBy}</td>
//             <td style={{ border: '1px solid black', padding: '8px' }}>{task.isActive ? '✅' : '❌'}</td>
//             <td style={{ border: '1px solid black', padding: '8px' }}>{task.lastTriggered}</td>
//             <td>
//               <button onClick={() => triggerTask(task.id)}>Trigger Task</button>
//             </td>
//           </tr>
//         </>
//         ))}
//       </tbody>
//     </table>
//   );
// };
//
// // export default TasksTable;
//
//
//
//
//
// // UploadProgress Component
// const UploadProgress = ({ uploadUuid }) => {
//   const [progress, setProgress] = useState(0);
//
//   useEffect(() => {
//     const checkUploadProgress = () => {
// //       axios.get(`/upload/progress/${uploadUuid}/`)
//       axios.get(`/upload/progress/${uploadUuid}/`)
//         .then(response => {
//           const newProgress = response.data.progress;
//           setProgress(response.data.progress);
//           if (newProgress >= 100) {
//             console.log('Upload complete, stopping progress checks.');
//             clearInterval(intervalId);
//           }
//         })
//         .catch(error => {
//           console.error('Error getting upload progress', error);
//           clearInterval(intervalId);
//         });
//     };
//
//     const intervalId = setInterval(() => {
//       console.log('Checking upload progress...');
//       checkUploadProgress();
//     }, 1000);
// //     const intervalId = setInterval(checkUploadProgress, 1000);
//
//     return () => {
//       console.log('Clearing interval on component unmount.');
//       clearInterval(intervalId);
//     };
//   }, [uploadUuid]);
//
//   return (
//     <div>
//       <h2>Upload Progress</h2>
//       <div style={{ width: '100%', backgroundColor: '#ddd' }}>
//         <div style={{ width: `${progress}%`, backgroundColor: 'green', height: '20px' }}>
//           {progress}%
//         </div>
//       </div>
//     </div>
//   );
// };
//
// // UploadManager Component
// const UploadManager = () => {
//   const [uploadUuid, setUploadUuid] = useState(null);
//
//   const startUpload = () => {
//     axios.post('/dummy_upload/')
//       .then(response => {
//         setUploadUuid(response.data.uuid);
//       })
//       .catch(error => {
//         console.error('Error starting upload', error);
//       });
//   };
//
//   return (
//     <div>
//       <button onClick={startUpload}>Start Upload</button>
//       {uploadUuid && <UploadProgress uploadUuid={uploadUuid} />}
//     </div>
//   );
// };
//
// // FallbackComponent (or any other name you choose)
// const FallbackComponent = () => {
//   const [showUploadManager, setShowUploadManager] = useState(false);
//
//   return (
//     <div>
//       <h1>Tasks Dashboard</h1>
//       <TasksTable />
//       <button onClick={() => setShowUploadManager(true)}>Show Upload Manager</button>
//       {showUploadManager && (
//         <div>
//           <h1>Upload Manager</h1>
//           <UploadManager />
//         </div>
//       )}
//     </div>
//   );
// };
//
// export default FallbackComponent;

