/**
 * Muestra un mensaje temporal en la interfaz.
 * @param {string} message - El mensaje a mostrar
 * @param {string} type - Tipo de mensaje ('success', 'error', 'info')
 * 
 * Estilos CSS necesarios:
 * #message-container {
 *     position: fixed;
 *     top: 20px;
 *     right: 20px;
 *     z-index: 1000;
 *     max-width: 300px;
 * }
 * 
 * .message {
 *     padding: 15px;
 *     margin-bottom: 10px;
 *     border-radius: 4px;
 *     box-shadow: 0 2px 5px rgba(0,0,0,0.2);
 *     animation: slideIn 0.5s ease;
 * }
 * 
 * .message.fade-out {
 *     animation: fadeOut 0.5s ease;
 * }
 * 
 * .message.success {
 *     background-color: #d4edda;
 *     border-left: 4px solid #28a745;
 *     color: #155724;
 * }
 * 
 * .message.error {
 *     background-color: #f8d7da;
 *     border-left: 4px solid #dc3545;
 *     color: #721c24;
 * }
 * 
 * .message.info {
 *     background-color: #cce5ff;
 *     border-left: 4px solid #0d6efd;
 *     color: #004085;
 * }
*/

function testMessage() {
    showMessage("This is a test message.")
}
function showMessage(message, type = 'info') {
    document.querySelector(".message")?.remove(); // -> Delete message if there is already one.

    let msgZone = document.getElementById('msg-zone');
    const msgElement = document.createElement('div');
    msgElement.textContent = message;
    msgElement.className = "message " + type;
    

    const closeBtn = document.createElement('button');
    // closeBtn.textContent = 'X';
    closeBtn.className = 'close-btn';
    
    msgElement.appendChild(closeBtn);
    msgZone.appendChild(msgElement);

    closeBtn.addEventListener('click', function() {
        msgElement.remove();
    });

    setTimeout(function() {
        msgElement.remove();
    }, 2000);
}

// API functions.
// ---- [Uploaded files functions] ----
async function fetchUploadedFiles() {
    try {
        const response = await fetch(CONFIG.API_URL + CONFIG.ENDPOINTS.FILES, {method: 'GET'});;
        const data = await response.json();
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
 
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `${file.filename} (${file.size})`;
 
                if (file.video_streams || file.audio_streams) {
                    const detailsList = document.createElement('ul');
                    
                    if (file.video_streams?.length > 0) {
                        file.video_streams.forEach((video, index) => {
                            const videoItem = document.createElement('li');
                            videoItem.innerHTML = `Video Stream ${index + 1}: ${video.codec.toUpperCase()}, Resolution: ${video.resolution}, FPS: ${video.fps}`;
                            detailsList.appendChild(videoItem);
                        });
                    }
 
                    if (file.audio_streams?.length > 0) {
                        file.audio_streams.forEach((audio, index) => {
                            const audioItem = document.createElement('li');
                            audioItem.innerHTML = `Audio Stream ${index + 1}: ${audio.codec.toUpperCase()}, Language: ${audio.language.toUpperCase()}`;
                            detailsList.appendChild(audioItem);
                        });
                    }
 
                    listItem.appendChild(detailsList);
                }
 
                const processButton = document.createElement('button');
                processButton.innerHTML = 'Process';
                processButton.classList.add('process-button');
                processButton.onclick = async function() {
                    if (confirm(`Are you sure you want to process ${file.filename}?`)) {
                        await processVideo(file.filename);
                    }
                };
 
                const deleteButton = document.createElement('button');
                deleteButton.innerHTML = 'Delete';
                deleteButton.classList.add('delete-button');
                deleteButton.onclick = async function() {
                    if (confirm(`Are you sure you want to delete ${file.filename}?`)) {
                        await deleteUploadedFile(file.filename);
                        fetchUploadedFiles();
                    }
                };
 
                listItem.appendChild(processButton);
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

async function deleteUploadedFile(filename) {
    try {
        const response = await fetch(CONFIG.API_URL + CONFIG.ENDPOINTS.FILES + filename, {method: 'DELETE'});
        if (response.ok) {
            showMessage('File has been deleted', 'success');
        } else {
            showMessage('Error deleting file: ' + response.statusText, 'error');
        }
    } catch (error) {
        console.error('Error deleting file:', error);
  }
}

// ---- [Processed files functions] ----
async function fetchProcessedFiles() {
    try {
        const response = await fetch(CONFIG.API_URL + CONFIG.ENDPOINTS.PROCESS.READY, {method: 'GET'});
        const data = await response.json();
        const processedList = document.getElementById('processedList');
        processedList.innerHTML = '';
 
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `${file.filename} (${file.size})`;
 
                if (file.video_streams || file.audio_streams) {
                    const detailsList = document.createElement('ul');
                    
                    if (file.video_streams?.length > 0) {
                        file.video_streams.forEach((video, index) => {
                            const videoItem = document.createElement('li');
                            videoItem.innerHTML = `Video Stream ${index + 1}: ${video.codec.toUpperCase()}, Resolution: ${video.resolution}, FPS: ${video.fps}`;
                            detailsList.appendChild(videoItem);
                        });
                    }
 
                    if (file.audio_streams?.length > 0) {
                        file.audio_streams.forEach((audio, index) => {
                            const audioItem = document.createElement('li');
                            audioItem.innerHTML = `Audio Stream ${index + 1}: ${audio.codec.toUpperCase()}, Language: ${audio.language.toUpperCase()}`;
                            detailsList.appendChild(audioItem);
                        });
                    }
 
                    listItem.appendChild(detailsList);
                }
 
                processedList.appendChild(listItem);
            });
        } else {
            const listItem = document.createElement('li');
            listItem.textContent = 'No processed files yet';
            processedList.appendChild(listItem);
        }
    } catch (error) {
        console.error('Error fetching processed files:', error);
    }
 }

async function processVideo(filename) {
    try {
        const response = await fetch(CONFIG.API_URL + CONFIG.ENDPOINTS.PROCESS.ADD + filename, { 
                method: 'POST',
                headers: {'Content-Type': 'application/json',
                }, 
                credentials: 'include'
            });
        if (response.ok) {
            const data = await response.json();
            showMessage(`Video added to processing queue: ${data.task_id}`, 'success');
            pollProcessingStatus(data.task_id);

        } else {
            showMessage('Error processing file: ' + response.statusText, 'error');
        }
    } catch (error) {
        console.error('Error processing file:', error);
        showMessage('Error processing file', 'error');
    }
 }

async function pollProcessingStatus(taskId) {
   const pollInterval = setInterval(async () => {
       try {
            const response = await fetch(CONFIG.API_URL + CONFIG.ENDPOINTS.PROCESS.STATUS + taskId, {method: 'GET'});
            if (response.ok) {
               const data = await response.json();
               
               switch(data.status) {
                   case 'completed':
                       showMessage(`Processing completed: ${data.filename}`, 'success');
                       clearInterval(pollInterval);
                       fetchProcessedFiles(); // Refresh processed files list
                       break;
                   case 'error':
                       showMessage(`Processing error: ${data.error}`, 'error');
                       clearInterval(pollInterval);
                       break;
               }
           }
       } catch (error) {
           console.error('Error checking status:', error);
           clearInterval(pollInterval);
       }
   }, 5000); // Check every 5 seconds
}

// Inicializar la carga de archivos
window.onload = () => {
   fetchUploadedFiles();
   fetchProcessedFiles();
};

