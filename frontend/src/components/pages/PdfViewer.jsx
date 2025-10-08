import React, { useState, useEffect } from "react";

const dummyMetadata = {
    objet: "Étude de faisabilité",
    mission: "Audit technique",
    nature_du_document: "Rapport",
    région: "Casablanca",
  };  

const PdfPreview = ({ fileUrl }) => {
  return (
    <iframe
      src={fileUrl}
      width="100%"
      height="600px"
      title="Aperçu PDF"
      style={{ border: "1px solid #ccc", borderRadius: 4 }}
    />
  );
};

const MetadataPanel = ({ metadata }) => {
  return (
    <div className="metadata-panel px-4 py-2">
      <h3 className="text-lg font-semibold mb-4">Tags extraits</h3>
      <div className="flex flex-wrap gap-2">
        {Object.entries(metadata).map(([key, value]) => (
          <span
            key={key}
            className="bg-gray-200 text-gray-800 text-sm px-3 py-1 rounded-full"
          >
            {value}
          </span>
        ))}
      </div>
    </div>
  );
};


const Home = () => {
  const [history, setHistory] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [metadata, setMetadata] = useState(null);

  useEffect(() => {
    setHistory([
      { name: "rapport1.pdf", url: "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf"},
      { name: "document2.pdf", url: "sample.pdf" },
      { name: "image1.png", url: "/uploads/image1.png" },
    ]);
  }, []);

  const handleFileClick = async (file) => {
    setSelectedFile(file);
    if (file.name.toLowerCase().endsWith(".pdf")) {
      setMetadata(dummyMetadata);
    } else {
      setMetadata(null);
    }
  };

  const closePreview = () => {
    setSelectedFile(null);
    setMetadata(null);
  };

  return (
    <div className="container" style={{ padding: 20 }}>
      <h2>Documents récents</h2>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        {history.map((file, idx) => (
          <div
            key={idx}
            onClick={() => handleFileClick(file)}
            style={{
              cursor: "pointer",
              padding: 10,
              border: "1px solid #ccc",
              borderRadius: 4,
              width: 200,
            }}
            title={file.name}
          >
            <p>{file.name}</p>
          </div>
        ))}
      </div>

      {/* Vue détail fichier sélectionné */}
      {selectedFile && (
        <div
          className="preview-modal"
          style={{
            position: "fixed",
            top: 40,
            left: 40,
            right: 40,
            bottom: 40,
            backgroundColor: "white",
            border: "1px solid #ddd",
            borderRadius: 6,
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
            display: "flex",
            gap: 20,
            zIndex: 1000,
            padding: 20,
          }}
        >
          <div style={{ flex: 2, overflow: "auto" }}>
            {selectedFile.name.toLowerCase().endsWith(".pdf") ? (
              <PdfPreview fileUrl={selectedFile.url} />
            ) : (
              <p>Aperçu non disponible pour ce type de fichier</p>
            )}
          </div>

          <div
            style={{
              flex: 1,
              borderLeft: "1px solid #ccc",
              overflowY: "auto",
              maxHeight: "100%",
            }}
          >
            {metadata ? (
              <MetadataPanel metadata={metadata} />
            ) : (
              <p>Aucune métadonnée disponible</p>
            )}
          </div>

          <button
            onClick={closePreview}
            style={{
              position: "absolute",
              top: 10,
              right: 10,
              border: "none",
              background: "red",
              color: "white",
              fontWeight: "bold",
              borderRadius: 4,
              padding: "4px 8px",
              cursor: "pointer",
            }}
          >
            X
          </button>
        </div>
      )}
    </div>
  );
};

export default Home;
