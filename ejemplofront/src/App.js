import React, { useState } from 'react';
import { Button, TextArea, Label } from 'semantic-ui-react';
import './App.css';

const App = () => {
  const [archivoTexto, setArchivoTexto] = useState('');
  const [imagenBase64, setImagenBase64] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file && (file.name.endsWith('.adsj') || file.name.endsWith('.ADSJ'))) {
      const reader = new FileReader();

      reader.onloadend = () => {
        setArchivoTexto(reader.result);
      };

      reader.readAsText(file);
    } else {
      alert('Por favor, selecciona un archivo con extensión .adsj');
    }
  };
 

  const handleLoadImage = () => {
    // Realizar la solicitud al backend para obtener la imagen en base64
    fetch('http://localhost:4000/imagen')
      .then(response => {
        if (!response.ok) {
          throw new Error('Error en la solicitud al servidor');
        }
        // Parsea la respuesta como JSON
        return response.json();
      })
      .then(data => {
        // Convierte el valor base64 a una URL de datos 
        const imageUrl = `data:image/jpeg;base64,${data.base64}`;
        
        // Establece la URL de datos en el estado
        setImagenBase64(imageUrl);
      })
      .catch(error => console.error('Error al cargar la imagen:', error));
  };
  

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div style={{ padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '8px', maxWidth: '400px', width: '100%' }}>
        <Label style={{ marginBottom: '10px', fontSize: '18px' }}>Archivo de Texto:</Label>
        <TextArea
          value={archivoTexto}
          placeholder="Archivo de Texto"
          disabled
          style={{ backgroundColor: '#fff', borderRadius: '4px' }}
        />

        <br />

        <Label style={{ marginTop: '20px', marginBottom: '10px', fontSize: '18px' }}>Seleccionar Archivo .ADSJ:</Label>
        <input
          type="file"
          accept=".ADSJ"
          onChange={handleFileChange}
          style={{ marginBottom: '20px' }}
        />

        <br /> 

        <Button primary onClick={handleLoadImage}>Cargar Imagen</Button>

        {imagenBase64 && (
          <img src={imagenBase64} alt="Imagen" width="100%" height="50%" />
        )}
      </div>
    </div>
  );
};

export default App;
