import React, { useState, useEffect } from 'react';
import { FiUpload, FiFileText, FiSearch, FiX, FiTrash2, FiAlertCircle, FiChevronLeft, FiChevronRight } from 'react-icons/fi';

const PdfPreview = ({ fileUrl }) => {
  return (
    <iframe
      src={fileUrl}
      width="100%"
      height="100%"
      title="Aperçu PDF"
      style={{ border: "none", borderRadius: 4 }}
    />
  );
};

const MetadataPanel = ({ metadata, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-600 bg-red-50 rounded">
        <FiAlertCircle className="inline mr-2" />
        {error}
      </div>
    );
  }

  if (!metadata || Object.keys(metadata).length === 0) {
    return (
      <div className="p-4 text-gray-500">
        Aucun mots-clé disponible pour ce fichier
      </div>
    );
  }

  return (
    <div className="p-4 overflow-y-auto h-full">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">Mots-clés</h3>
      <div className="space-y-4">
        {Object.entries(metadata).map(([key, value]) => (
          <div key={key} className="bg-gray-50 p-3 rounded-lg">
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              {key.replace(/_/g, ' ')}
            </div>
            <div className="mt-1 text-sm text-gray-800">
              {value || <span className="text-gray-400">Non spécifié</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const Home = () => {
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadErrors, setUploadErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [metadataLoading, setMetadataLoading] = useState(false);
  const [metadataError, setMetadataError] = useState(null);

  const validExtensions = {
    pdf: "PDF",
    docx: "Word (DOCX)",
    xlsx: "Excel (XLSX)",
    xls: "Excel (XLS)",
    pptx: "PowerPoint (PPTX)",
    jpg: "JPG",
    jpeg: "JPEG",
    png: "PNG"
  };

  const conversionRequiredExtensions = {
    doc: "Veuillez convertir ce fichier DOC en DOCX avant l'upload",
    ppt: "Veuillez convertir ce fichier PPT en PPTX avant l'upload"
  };

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const fetchExistingFiles = async () => {
    try {
      const res = await fetch('http://localhost:8000/upload/existing_files');
      if (!res.ok) throw new Error('Erreur API fichiers existants');
      return await res.json();
    } catch (err) {
      console.error('Erreur récupération fichiers existants:', err);
      return [];
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/history');
      if (!res.ok) throw new Error('Erreur API historique');
      setHistory(await res.json());
    } catch (err) {
      console.error('Erreur récupération historique:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/stats');
      if (!res.ok) throw new Error('Erreur API stats');
      setStats(await res.json());
    } catch (err) {
      console.error('Erreur récupération stats:', err);
    }
  };

  const fetchMetadata = async (filename) => {
    setMetadataLoading(true);
    setMetadataError(null);
    try {
      const response = await fetch(`http://localhost:8000/upload/metadata/${encodeURIComponent(filename)}`);
      if (!response.ok) throw new Error('Erreur lors de la récupération des métadonnées');
      const data = await response.json();
      return data.success ? data.metadata : null;
    } catch (error) {
      console.error("Erreur:", error);
      setMetadataError(error.message);
      return null;
    } finally {
      setMetadataLoading(false);
    }
  };

  const validateFiles = async (filesToValidate) => {
    try {
      const existingFiles = await fetchExistingFiles();
      const validFiles = [];
      const errors = [];

      for (const file of filesToValidate) {
        const extension = file.name.split('.').pop().toLowerCase();
        const filePath = file.webkitRelativePath || file.name;

        const exists = existingFiles.some(existing => 
          existing.toLowerCase() === filePath.toLowerCase()
        );

        if (exists) {
          errors.push({
            file,
            message: `Le fichier existe déjà: ${filePath}`
          });
          continue;
        }

        if (!validExtensions[extension]) {
          errors.push({
            file,
            message: conversionRequiredExtensions[extension] || 
                    `Extension .${extension} non supportée`
          });
          continue;
        }

        validFiles.push(file);
      }

      return { validFiles, errors };
    } catch (err) {
      console.error("Erreur validation:", err);
      return { validFiles: [], errors: [{ message: "Erreur de validation" }] };
    }
  };

  const handleFilesChange = async (e) => {
    const { validFiles, errors } = await validateFiles(Array.from(e.target.files));
    setFiles(validFiles);
    setFolders([]);
    setUploadErrors(errors);
  };

  const handleFoldersChange = async (e) => {
    const { validFiles, errors } = await validateFiles(Array.from(e.target.files));
    setFolders(validFiles);
    setFiles([]);
    setUploadErrors(errors);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const removeFolderFile = (index) => {
    setFolders(prev => prev.filter((_, i) => i !== index));
  };

  const handleSend = async () => {
    const filesToUpload = files.length > 0 ? files : folders;
    if (filesToUpload.length === 0) return;

    setIsLoading(true);
    try {
      const { validFiles, errors } = await validateFiles(filesToUpload);
      
      if (errors.length > 0) {
        setUploadErrors(errors);
        alert(`${errors.length} fichier(s) déjà existant(s) ou invalides`);
        return;
      }

      let successfulUploads = 0;
      const newErrors = [];

      for (const file of validFiles) {
        try {
          const formData = new FormData();
          formData.append("file", file);
          
          if (folders.length > 0) {
            formData.append("relative_path", file.webkitRelativePath);
          }

          const endpoint = folders.length > 0 
            ? "http://localhost:8000/upload/folder/" 
            : "http://localhost:8000/upload/files/";

          const response = await fetch(endpoint, {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            throw new Error(await response.text());
          }

          successfulUploads++;
        } catch (error) {
          newErrors.push({
            file: file.name || file.webkitRelativePath,
            message: error.message
          });
        }
      }

      if (newErrors.length > 0) {
        setUploadErrors(newErrors);
        alert(`${successfulUploads} envoyé(s), ${newErrors.length} échec(s)`);
      } else {
        alert(`${successfulUploads} fichier(s) envoyé(s) avec succès !`);
        await fetchHistory();
        await fetchStats();
        clearAll();
      }
    } catch (error) {
      console.error("Erreur globale:", error);
      alert("Erreur critique lors de l'envoi");
    } finally {
      setIsLoading(false);
    }
  };

  const openFile = async (file) => {
    if (file.name.toLowerCase().endsWith('.pdf')) {
      const url = file instanceof File 
  ? URL.createObjectURL(file) 
  : `http://localhost:8000/upload/file/${encodeURIComponent(file.name)}`;
      
      setSelectedFile({
        name: file.name,
        url
      });
      
      const metadata = await fetchMetadata(file.name);
      setMetadata(metadata);
    } else {
      const url = file instanceof File 
        ? URL.createObjectURL(file) 
        : `http://localhost:8000/upload/${encodeURIComponent(file.name)}`;
      window.open(url, "_blank");
    }
  };

  const closePreview = () => {
    setSelectedFile(null);
    setMetadata(null);
    setMetadataError(null);
  };

  const clearAll = () => {
    setFiles([]);
    setFolders([]);
    setUploadErrors([]);
  };

  const hasSelectedFiles = files.length > 0 || folders.length > 0;

  return (
    <div className="p-6">
      <h2 className="text-3xl font-semibold text-gray-800 mb-8">Accueil</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Section Upload */}
        <div>
          <h3 className="text-xl font-medium text-gray-800 mb-4">Téléversement des documents</h3>
          <div className="border-2 border-dashed border-blue-400 rounded-lg p-6 bg-blue-50">
            <div className="flex flex-col items-center mb-4">
              <FiUpload size={48} className="text-blue-600 mb-2" />
              <p className="font-semibold text-gray-800 text-center">
                Glissez-déposez vos fichiers ou
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <label className="cursor-pointer flex-1">
                <div className="px-4 py-3 bg-white border border-blue-500 text-blue-600 rounded-lg hover:bg-blue-50 text-center">
                  <span>Sélectionner des fichiers</span>
                  <input 
                    type="file" 
                    multiple 
                    onChange={handleFilesChange} 
                    className="hidden" 
                  />
                </div>
              </label>
              <label className="cursor-pointer flex-1">
                <div className="px-4 py-3 bg-white border border-blue-500 text-blue-600 rounded-lg hover:bg-blue-50 text-center">
                  <span>Sélectionner un dossier</span>
                  <input 
                    type="file" 
                    webkitdirectory="true" 
                    directory="" 
                    onChange={handleFoldersChange} 
                    className="hidden" 
                  />
                </div>
              </label>
            </div>

            {uploadErrors.length > 0 && (
              <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded">
                <h4 className="font-medium text-red-800 flex items-center">
                  <FiAlertCircle className="mr-2" />
                  {uploadErrors.some(e => e.message.includes('existe déjà')) 
                    ? 'Fichiers existants/erreurs' 
                    : 'Erreurs de validation'}
                </h4>
                <ul className="mt-2 space-y-1 max-h-40 overflow-y-auto">
                  {uploadErrors.map((error, idx) => (
                    <li key={idx} className="text-sm text-red-700 flex">
                      <span className="font-medium truncate max-w-[180px]">
                        {error.file.name || error.file}
                      </span>
                      <span className="mx-2">-</span>
                      <span>{error.message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(files.length > 0 || folders.length > 0) && (
              <div className="mt-6">
                <h4 className="text-md font-semibold text-gray-700 mb-2">
                  {files.length > 0 ? 'Fichiers sélectionnés' : 'Contenu du dossier'}
                </h4>
                <div className="space-y-2 max-h-60 overflow-auto p-1">
                  {(files.length > 0 ? files : folders).map((file, idx) => (
                    <div 
                      key={idx} 
                      className="flex justify-between items-center bg-white rounded-md shadow-sm border p-3 hover:shadow-md transition"
                    >
                      <div 
                        onClick={() => openFile(file)} 
                        className="flex items-center space-x-3 overflow-hidden cursor-pointer flex-1"
                      >
                        <FiFileText className="text-blue-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">
                            {files.length > 0 ? file.name : file.webkitRelativePath || file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(file.size / 1024).toFixed(1)} Ko
                          </p>
                        </div>
                      </div>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          files.length > 0 ? removeFile(idx) : removeFolderFile(idx);
                        }} 
                        className="text-red-500 hover:text-red-700 p-1"
                      >
                        <FiX />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {hasSelectedFiles && (
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button 
                  onClick={handleSend} 
                  disabled={isLoading}
                  className={`flex items-center justify-center px-4 py-2 rounded-lg ${
                    isLoading 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  }`}
                >
                  {isLoading ? (
                    <>
                      <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                      Envoi en cours...
                    </>
                  ) : (
                    'Envoyer les fichiers'
                  )}
                </button>
                <button 
                  onClick={clearAll} 
                  disabled={isLoading}
                  className="flex items-center justify-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
                >
                  <FiTrash2 className="mr-2" />
                  Tout supprimer
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Section Historique */}
        <div>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
            <h3 className="text-xl font-semibold text-gray-800">Documents récents</h3>
            <div className="relative w-full sm:w-64">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher un document..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            {history.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                Aucun document récent trouvé
              </div>
            ) : (
              <div className="divide-y">
                {history
                  .filter(doc => doc.name.toLowerCase().includes(searchTerm.toLowerCase()))
                  .sort((a, b) => new Date(b.added_at) - new Date(a.added_at))
                  .slice(0, 6)
                  .map((doc, idx) => (
                    <div
                      key={idx}
                      onClick={() => openFile(doc)}
                      className="p-4 hover:bg-gray-50 cursor-pointer transition"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <FiFileText className="text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">
                            {doc.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            Ajouté le {new Date(doc.added_at).toLocaleDateString()}
                            {' • '}
                            {doc.size_kb} Ko
                          </p>
                        </div>
                        <FiChevronRight className="text-gray-400" />
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* Statistiques */}
          <div className="mt-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Statistiques</h3>
            {stats ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <p className="text-sm text-gray-500">Documents total</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.total_documents}</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <p className="text-sm text-gray-500">Ajoutés cette semaine</p>
                  <p className="text-2xl font-bold text-green-600">{stats.added_this_week}</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <p className="text-sm text-gray-500">Espace utilisé</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.used_space}</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                  <p className="text-sm text-gray-500">Dernier ajout</p>
                  <p className="text-md font-medium text-gray-800 truncate">
                    {stats.last_modified_file || 'Aucun'}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal PDF Viewer */}
      {selectedFile && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-black bg-opacity-50"></div>
          <div className="absolute inset-5 bg-white rounded-xl shadow-2xl flex flex-col">
            <div className="flex justify-between items-center border-b p-4">
              <h3 className="text-lg font-semibold text-gray-800 truncate">
                {selectedFile.name}
              </h3>
              <button
                onClick={closePreview}
                className="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
              >
                <FiX size={24} />
              </button>
            </div>
            <div className="flex-1 flex overflow-hidden">
              <div className="flex-1 overflow-auto">
                <PdfPreview fileUrl={selectedFile.url} />
              </div>
              <div className="w-80 border-l overflow-auto">
                <MetadataPanel 
                  metadata={metadata} 
                  isLoading={metadataLoading}
                  error={metadataError}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;