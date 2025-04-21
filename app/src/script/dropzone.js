Dropzone.autoDiscover = false;
let myDropzone = new Dropzone("#dropzone", { 
    paramName: 'file_uploads',
    maxFilesize: 18432, // Allow files up to 18 Gib
    acceptedFiles: '.ts, .mp4, .mkv',
    addRemoveLinks: true,
    dictRemoveFile: 'DELETE',
    clickable: "#dropbutton",
    maxFiles: 6
    }
);

myDropzone.on("success", function(file, response) {
    console.log('File uploaded successfully:', file.name);
    // Llamar a la función para actualizar la lista de archivos
    fetchUploadedFiles();
});

myDropzone.on("error", function(file, errorMessage) {
    alert("File " + file.name + " is too large or failed to upload!");
});