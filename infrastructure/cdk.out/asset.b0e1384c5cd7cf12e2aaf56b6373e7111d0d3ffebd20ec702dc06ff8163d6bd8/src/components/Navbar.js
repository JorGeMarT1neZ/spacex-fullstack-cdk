import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-3 py-2">
        <div className="flex justify-between items-center py-1">
          <Link to="/" className="text-xl font-bold">
            SpaceX Launches
          </Link>
          <div className="space-x-4">
            <Link to="/" className="hover:text-blue-200 transition">                                                                                        
              Lanzamientos
            </Link>
            <Link to="/statistics" className="hover:text-blue-200 transition">                                                                                 
              Estadísticas
            </Link>
            <a 
              href="http://localhost:8000/swagger/"                                                                                                          
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-200 transition">
              API Docs
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;