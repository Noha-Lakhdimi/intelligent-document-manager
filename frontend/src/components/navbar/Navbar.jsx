import React from "react";

const Navbar = ({ searchTerm, onSearch, onCreateFolder, onAddFile, onAddFolder }) => {
  return (
    <nav className="bg-white shadow-md p-4 flex items-center justify-between sticky top-0 z-50 h-16">
      {/* Recherche */}
      <div className="flex items-center space-x-2 flex-grow max-w-md">
        <input
          type="text"
          placeholder="Rechercher dans tous les fichiers..."
          value={searchTerm}
          onChange={(e) => onSearch(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm"
        />
      </div>

      {/* Boutons */}
      <div className="flex items-center space-x-4 ml-4">
        <button
          onClick={onCreateFolder}
          className="px-3 py-1 border border-gray-400 rounded hover:bg-gray-100"
        >
          Créer dossier
        </button>

        <label
          htmlFor="upload-file"
          className="cursor-pointer px-3 py-1 border border-gray-400 rounded hover:bg-gray-100"
        >
          Ajouter fichier
        </label>
        <input
          id="upload-file"
          type="file"
          onChange={onAddFile}
          className="hidden"
        />

        <label
          htmlFor="upload-folder"
          className="cursor-pointer px-3 py-1 border border-gray-400 rounded hover:bg-gray-100"
        >
          Ajouter dossier
        </label>
        <input
          id="upload-folder"
          type="file"
          webkitdirectory="true"
          directory=""
          onChange={onAddFolder}
          className="hidden"
        />
      </div>
    </nav>
  );
};

export default Navbar;
