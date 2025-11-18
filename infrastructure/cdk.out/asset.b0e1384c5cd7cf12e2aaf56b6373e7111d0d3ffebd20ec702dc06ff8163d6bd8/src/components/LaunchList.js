import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const LaunchList = () => {
  const [launches, setLaunches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    rocket: ''
  });

  useEffect(() => {
    fetchLaunches();
  }, []);

  const fetchLaunches = async () => {
    try {
      const response = await axios.get('/api/launches/?limit=50');
      setLaunches(response.data.items || []);
    } catch (error) {
      console.error('Error fetching launches:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'upcoming':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'success':
        return 'Éxito';
      case 'failed':
        return 'Fallido';
      case 'upcoming':
        return 'Próximo';
      default:
        return status;
    }
  };

  const filteredLaunches = launches.filter(launch => {
    if (filters.status && launch.status !== filters.status) return false;
    if (filters.rocket && !launch.rocket_name?.toLowerCase().includes(filters.rocket.toLowerCase())) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 bg-white p-6 rounded-lg shadow">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Lanzamientos de SpaceX</h1>
        
        {/* Filtros */}
        <div className="flex space-x-4 mb-4">
          <select
            value={filters.status}
            onChange={(e) => setFilters({...filters, status: e.target.value})}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Todos los estados</option>
            <option value="success">Éxito</option>
            <option value="failed">Fallido</option>
            <option value="upcoming">Próximos</option>
          </select>
          
          <input
            type="text"
            placeholder="Filtrar por cohete..."
            value={filters.rocket}
            onChange={(e) => setFilters({...filters, rocket: e.target.value})}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-grow"
          />
        </div>
        
        <p className="text-gray-600">
          Mostrando {filteredLaunches.length} de {launches.length} lanzamientos
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredLaunches.map((launch) => (
          <div key={launch.launch_id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
            <div className="p-6">
              {launch.patch_image && (
                <img
                  src={launch.patch_image}
                  alt={`${launch.mission_name} patch`}
                  className="w-20 h-20 mx-auto mb-4"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              )}
              
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {launch.mission_name}
              </h2>
              
              <div className="space-y-2 mb-4">
                <p className="text-gray-600">
                  <strong>Cohete:</strong> {launch.rocket_name}
                </p>
                <p className="text-gray-600">
                  <strong>Fecha:</strong> {new Date(launch.launch_date).toLocaleDateString()}
                </p>
                <p className="text-gray-600">
                  <strong>Plataforma:</strong> {launch.launchpad_name}
                </p>
              </div>
              
              <div className="flex justify-between items-center">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(launch.status)}`}>
                  {getStatusText(launch.status)}
                </span>
                <Link
                  to={`/launch/${launch.launch_id}`}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Ver detalles →
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredLaunches.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No se encontraron lanzamientos con los filtros aplicados.</p>
        </div>
      )}
    </div>
  );
};

export default LaunchList;