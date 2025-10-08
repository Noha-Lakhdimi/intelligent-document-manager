import React from 'react'
import { FiHome, FiFileText, FiMessageCircle, FiTrash2 } from "react-icons/fi"
import { useLocation, Link } from 'react-router-dom'
import Logo from "../../assets/ONEP_logo2.jpg"

const Sidebar = () => {
  const location = useLocation();

  const links = [
    { to: "/Accueil", icon: <FiHome className="mr-3" />, label: "Accueil" },
    { to: "/MesDocuments", icon: <FiFileText className="mr-3" />, label: "Mes documents" },
    { to: "/Chat", icon: <FiMessageCircle className="mr-3" />, label: "Chat" },
    { to: "/Corbeille", icon: <FiTrash2 className="mr-3" />, label: "Corbeille" },
  ];

  return (
    <aside className="w-64 bg-white shadow-md flex flex-col justify-between h-screen border-r">
      {/* Top: Logo + Menu */}
      <div>
        <div className="flex items-center mb-10 mt-4 ml-4 space-x-3">
          <img 
            src={Logo} 
            alt="Logo AEP" 
            className="w-10 h-10 object-contain"
          />
          <h1 className="text-2xl font-semibold text-gray-800">AEP SmartFile</h1>
        </div>

        <nav className="mt-4">
          <ul className="space-y-2 px-4">
            {links.map((link, idx) => {
              const isActive = location.pathname === link.to;
              return (
                <li key={idx}>
                  <Link
                    to={link.to}
                    className={`flex items-center text-lg px-4 py-2 rounded transition ${
                      isActive
                        ? "bg-gray-200 text-gray-900 font-semibold"
                        : "text-gray-700 hover:bg-blue-100"
                    }`}
                  >
                    {link.icon}
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;
