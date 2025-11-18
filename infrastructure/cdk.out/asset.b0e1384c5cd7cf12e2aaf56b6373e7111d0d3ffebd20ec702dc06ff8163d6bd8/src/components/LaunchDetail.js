import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const LaunchDetail = () => {
  const { id } = useParams();
  const [launch, setLaunch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLaunchDetail = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/launches/${id}/`);
        setLaunch(response.data);
      } catch (err) {
        setError('Error cargando detalles del lanzamiento');
        console.error('Error fetching launch details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLaunchDetail();
  }, [id]);

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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <Link to="/" className="text-blue-600 hover:text-blue-800 font-medium">
            ← Volver a la lista
          </Link>
        </div>
      </div>
    );
  }

  if (!launch) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Lanzamiento no encontrado</h2>
        <Link to="/" className="text-blue-600 hover:text-blue-800 font-medium">
          ← Volver a la lista
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Link 
        to="/" 
        className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6"
      >
        <span className="mr-2">←</span>
        Volver a la lista de lanzamientos
      </Link>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header con imagen y título */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-700 p-6 text-white">
          <div className="flex flex-col md:flex-row items-center">
            {launch.patch_image && (
              <img
                src={launch.patch_image}
                alt={`${launch.mission_name} patch`}
                className="w-24 h-24 mb-4 md:mb-0 md:mr-6 bg-white rounded-lg p-2"
              />
            )}
            <div>
              <h1 className="text-3xl font-bold mb-2">{launch.mission_name}</h1>
              <div className="flex items-center space-x-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(launch.status)}`}>
                  {getStatusText(launch.status)}
                </span>
                <span className="text-blue-100">
                  #{launch.flight_number}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Información detallada */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Información básica */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 border-b pb-2">
                Información del Lanzamiento
              </h3>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Cohete</label>
                <p className="text-gray-900">{launch.rocket_name || 'No disponible'}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Fecha de lanzamiento</label>
                <p className="text-gray-900">
                  {new Date(launch.launch_date).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZone: 'UTC'
                  }) + ' UTC'}
                </p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Plataforma de lanzamiento</label>
                <p className="text-gray-900">{launch.launchpad_name || 'No disponible'}</p>
                {launch.launchpad_full_name && launch.launchpad_full_name !== 'N/A' && (
                  <p className="text-sm text-gray-600">{launch.launchpad_full_name}</p>
                )}
              </div>
            </div>

            {/* Payloads y detalles */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900 border-b pb-2">
                Carga Útil
              </h3>
              
              {launch.payload_names && launch.payload_names.length > 0 ? (
                <div>
                  <label className="text-sm font-medium text-gray-500">Payloads</label>
                  <ul className="list-disc list-inside text-gray-900">
                    {launch.payload_names.map((payload, index) => (
                      <li key={index}>{payload}</li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p className="text-gray-500">No hay información de payloads disponible</p>
              )}
              
              {launch.payload_types && launch.payload_types.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Tipos de payload</label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {launch.payload_types.map((type, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                      >
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Descripción */}
          {launch.details && (
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 border-b pb-2 mb-4">
                Descripción
              </h3>
              <p className="text-gray-700 leading-relaxed">{launch.details}</p>
            </div>
          )}

          {/* Enlaces externos */}
          <div className="border-t pt-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Enlaces relacionados</h3>
            <div className="flex flex-wrap gap-4">
              {launch.webcast_url && (
                <a
                  href={launch.webcast_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <span className="mr-2">🎥</span>
                  Ver Webcast
                </a>
              )}
              
              {launch.article_url && (
                <a
                  href={launch.article_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <span className="mr-2">📰</span>
                  Leer Artículo
                </a>
              )}
              
              {launch.wikipedia_url && (
                <a
                  href={launch.wikipedia_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <span className="mr-2">🌐</span>
                  Wikipedia
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LaunchDetail;
