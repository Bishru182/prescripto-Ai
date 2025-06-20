import React, { useState } from 'react';
import axios from 'axios';

function Land() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [result, setResult] = useState('');
  const [confidence, setConfidence] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setPreviewURL(URL.createObjectURL(file)); // Generate preview
    setResult('');      // Reset previous result on new file select
    setConfidence(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData);
      setResult(response.data.medicine);
      setConfidence(response.data.confidence);
    } catch (error) {
      console.error('Upload failed:', error);
      setResult('Error detecting medicine.');
      setConfidence(null);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <br />
      {previewURL && (
        <div style={{ marginTop: '20px' }}>
          <img
            src={previewURL}
            alt="Prescription Preview"
            style={{ maxWidth: '400px', borderRadius: '10px', marginTop: '10px' }}
          />
        </div>
      )}
      <br />
      <button onClick={handleUpload}>Upload Prescription</button>
      <br /><br />
      {result && (
        <h2>
          Detected Medicine: {result} {confidence !== null && ` (Confidence: ${confidence}%)`}
        </h2>
      )}
    </div>
  );
}

export default Land;
