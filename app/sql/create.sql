-- Tabla para archivos subidos
CREATE TABLE uploaded_files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    video_codec VARCHAR(50),
    audio_codec VARCHAR(50),
    resolution VARCHAR(20),
    fps VARCHAR(10),
    duration INT,
    UNIQUE KEY unique_filename (filename)
);

-- Tabla para archivos procesados
CREATE TABLE processed_files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_file_id INT,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    process_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    video_codec VARCHAR(50),
    audio_codec VARCHAR(50),
    resolution VARCHAR(20),
    fps VARCHAR(10),
    duration INT,
    FOREIGN KEY (original_file_id) REFERENCES uploaded_files(id),
    UNIQUE KEY unique_filename (filename)
);

-- Tabla para la cola de procesamiento
CREATE TABLE processing_queue (
    id VARCHAR(36) PRIMARY KEY,  -- UUID
    file_id INT,
    status ENUM('pending', 'processing', 'completed', 'error') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (file_id) REFERENCES uploaded_files(id)
);