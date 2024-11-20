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
         'http://192.168.0.8:8000/api/files/' + filename, { method: 'DELETE'}
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

// async function fetchCpuLoad() {
//    const response = await fetch("/api/cpu-usage");
//    const data = await response.json();
//    document.getElementById("cpu-usage").textContent = data.cpu_percent + '%';
// }

// setInterval(fetchCpuLoad, 1000)

async function fetchUploadedFiles() {
   try {
      const response = await fetch('http://192.168.0.8:8000/api/files/');
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
