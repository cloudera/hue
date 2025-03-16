// // Extend the Window interface to include the CSRF_TOKEN property
// declare global {
//   interface Window {
//     CSRF_TOKEN: string;
//   }
// }

// interface FetchWithCsrfOptions extends RequestInit {
//   headers?: HeadersInit;
// }

// async function fetchWithCsrf(url: string, options: FetchWithCsrfOptions = {}): Promise<Response> {
//   const headers = new Headers(options.headers || {});
//   headers.append('X-CSRFToken', window.CSRF_TOKEN);

//   return fetch(url, {
//     ...options,
//     headers: headers
//   });
// }

// export { fetchWithCsrf };



// remove file