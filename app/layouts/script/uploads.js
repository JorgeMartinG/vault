// function showMessage(message, type = 'success') {

//    const messageBox = document.createElement('div');
//    messageBox.className = `message-box ${type}`;
//    messageBox.textContent = message;
   
//    document.body.appendChild(messageBox);
   
//    setTimeout(() => {
//       messageBox.remove();
//    }, 3000); // Desaparece en 3 segundos
// }

// async function deleteUploadedFile(filename) {
//    try {
//       const response = await fetch(
//          'http://10.1.5.206:8000/api/files/' + filename, { method: 'DELETE'}
//       );
//       if (response.ok) {
//          showMessage('File deleted succesfully', 'success');
//       } else {
//          showMessage('Error deleting file: ' + response.statusText, 'error');
//       }
//    } catch (error) {
//       console.error('Error deleting file:', error);
//    }
// }

// async function fetchUploadedFiles() {
//    try {
//       const response = await fetch('http://10.1.5.206:8000/api/files/');
//       const data = await response.json();
//       const fileList = document.getElementById('fileList');
//       fileList.innerHTML = '';

//       if (data.files && data.files.length > 0) {
//          data.files.forEach(file => {
//             const listItem = document.createElement('li');
            
//             listItem.innerHTML = file.filename + ' ' + '(' + file.filesize + ')';

//             if (file.video_streams || file.audio_streams || file.subtitle_streams) {
//                const detailsList = document.createElement('ul');
               
//                if (file.video_streams && file.video_streams.length > 0) {
//                   file.video_streams.forEach((video, index) => {
//                      const videoItem = document.createElement('li');
//                      videoItem.innerHTML = `Video Stream ${index + 1}: ${video.codec.toUpperCase()}, Resolution: ${video.resolution}, FPS: ${video.fps}`;
//                      detailsList.appendChild(videoItem);
//                   });
//                }

//                if (file.audio_streams && file.audio_streams.length > 0) {
//                   file.audio_streams.forEach((audio, index) => {
//                      const audioItem = document.createElement('li');
//                      audioItem.innerHTML = `Audio Stream ${index + 1}: ${audio.codec.toUpperCase()}, Language: ${audio.language.toUpperCase()}`;
//                      detailsList.appendChild(audioItem);
//                   });
//                }

//                listItem.appendChild(detailsList);
//             }

//             // const processButton = document.createElement('button');
//             // processButton.innerHTML = 'Procesar';
//             // processButton.classList.add('process-button');
//             // processButton.onclick = async function() {
//             //     if (confirm(`¿Estás seguro de que quieres procesar ${file.filename}?`)) {
//             //         await processVideo(file.filename);
//             //     }
//             // };

//             const deleteButton = document.createElement('button');
//             deleteButton.innerHTML = 'Delete';
//             deleteButton.classList.add('delete-button'); // delete-button class
//             deleteButton.onclick = async function() {
//                if (confirm(`Are you sure you want to delete ${file.filename}?`)) {
//                   await deleteUploadedFile(file.filename);
//                   fetchUploadedFiles();
//                }
//             };

//             // listItem.appendChild(processButton);
//             listItem.appendChild(deleteButton);
//             fileList.appendChild(listItem);
//          });
//       } else {
//          const listItem = document.createElement('li');
//          listItem.textContent = 'No files uploaded yet';
//          fileList.appendChild(listItem);
//       }
//    } catch (error) {
//       console.error('Error fetching files:', error);
//    }
// }

// // async function processVideo(filename) {
// //     try {
// //         const response = await fetch(
// //             `http://10.1.5.206:8000/api/process/${filename}`,
// //             { method: 'POST' }
// //         );
        
// //         if (response.ok) {
// //             const data = await response.json();
// //             showMessage(`Video añadido a la cola de procesamiento: ${data.task_id}`, 'success');
            
// //             // Start polling for status updates
// //             pollProcessingStatus(data.task_id);
// //         } else {
// //             showMessage('Error al procesar el archivo: ' + response.statusText, 'error');
// //         }
// //     } catch (error) {
// //         console.error('Error procesando archivo:', error);
// //         showMessage('Error al procesar el archivo', 'error');
// //     }
// // }

// // async function pollProcessingStatus(taskId) {
// //     const pollInterval = setInterval(async () => {
// //         try {
// //             const response = await fetch(
// //                 `http://10.1.5.206:8000/api/process/status/${taskId}`
// //             );
            
// //             if (response.ok) {
// //                 const data = await response.json();
                
// //                 switch(data.status) {
// //                     case 'completed':
// //                         showMessage(`Procesamiento completado: ${data.filename}`, 'success');
// //                         clearInterval(pollInterval);
// //                         fetchUploadedFiles(); // Refresh the file list
// //                         break;
// //                     case 'error':
// //                         showMessage(`Error en el procesamiento: ${data.error}`, 'error');
// //                         clearInterval(pollInterval);
// //                         break;
// //                     case 'processing':
// //                         // Opcional: mostrar un indicador de progreso
// //                         break;
// //                 }
// //             }
// //         } catch (error) {
// //             console.error('Error checking status:', error);
// //             clearInterval(pollInterval);
// //         }
// //     }, 5000); // Check every 5 seconds
    
// //     // Stop polling after 1 hour to prevent infinite polling
// //     setTimeout(() => {
// //         clearInterval(pollInterval);
// //     }, 3600000);
// // }

// window.onload = fetchUploadedFiles;



// --------------------------
function showMessage(message, type = 'success') {

   const messageBox = document.createElement('div');
   messageBox.className = `message-box ${type}`;
   messageBox.textContent = message;
   
   document.body.appendChild(messageBox);
   
   setTimeout(() => {
      messageBox.remove();
   }, 3000); // Desaparece en 3 segundos
}

async function deleteUploadedFile(filename) {
   try {
      const response = await fetch(
         'http://10.1.5.206:8000/api/files/' + filename, { method: 'DELETE'}
      );
      if (response.ok) {
         showMessage('File deleted succesfully', 'success');
      } else {
         showMessage('Error deleting file: ' + response.statusText, 'error');
      }
   } catch (error) {
      console.error('Error deleting file:', error);
   }
}

async function fetchUploadedFiles() {
   try {
      const response = await fetch('http://10.1.5.206:8000/api/files/');
      const data = await response.json();
      const fileList = document.getElementById('fileList');
      fileList.innerHTML = '';

      if (data.files && data.files.length > 0) {
         data.files.forEach(file => {
            const listItem = document.createElement('li');
            
            listItem.innerHTML = file.filename + ' ' + '(' + file.filesize + ')';

            if (file.video_streams || file.audio_streams || file.subtitle_streams) {
               const detailsList = document.createElement('ul');
               
               if (file.video_streams && file.video_streams.length > 0) {
                  file.video_streams.forEach((video, index) => {
                     const videoItem = document.createElement('li');
                     videoItem.innerHTML = `Video Stream ${index + 1}: ${video.codec.toUpperCase()}, Resolution: ${video.resolution}, FPS: ${video.fps}`;
                     detailsList.appendChild(videoItem);
                  });
               }

               if (file.audio_streams && file.audio_streams.length > 0) {
                  file.audio_streams.forEach((audio, index) => {
                     const audioItem = document.createElement('li');
                     audioItem.innerHTML = `Audio Stream ${index + 1}: ${audio.codec.toUpperCase()}, Language: ${audio.language.toUpperCase()}`;
                     detailsList.appendChild(audioItem);
                  });
               }

               listItem.appendChild(detailsList);
            }

            const deleteButton = document.createElement('button');
            deleteButton.innerHTML = 'Delete';
            deleteButton.classList.add('delete-button'); // delete-button class
            deleteButton.onclick = async function() {
               if (confirm(`Are you sure you want to delete ${file.filename}?`)) {
                  await deleteUploadedFile(file.filename);
                  fetchUploadedFiles();
               }
            };

            listItem.appendChild(deleteButton);
            fileList.appendChild(listItem);
         });
      } else {
         const listItem = document.createElement('li');
         listItem.textContent = 'No files uploaded yet';
         fileList.appendChild(listItem);
      }
   } catch (error) {
      console.error('Error fetching files:', error);
   }
}

window.onload = fetchUploadedFiles;

