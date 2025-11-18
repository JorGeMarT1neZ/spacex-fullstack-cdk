import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Statistics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/statistics/');
        setStats(response.data);
      } catch (err) {
        setError('Error cargando estadísticas');
        console.error('Error fetching statistics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

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
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay datos estadísticos disponibles</p>
      </div>
    );
  }

  // Calcular porcentajes para la barra de progreso
  const totalCompleted = stats.total_launches - stats.upcoming;
  const successPercentage = totalCompleted > 0 ? (stats.successful / totalCompleted) * 100 : 0;
  const failedPercentage = totalCompleted > 0 ? (stats.failed / totalCompleted) * 100 : 0;

  return (
    <div className="space-y-8">
      <div className="bg-white p-6 rounded-lg shadow">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Estadísticas de Lanzamientos</h1>
        
        {/* Grid de estadísticas principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-blue-50 p-6 rounded-lg text-center border border-blue-200">
            <div className="text-3xl font-bold text-blue-600 mb-2">{stats.total_launches}</div>
            <div className="text-gray-700 font-medium">Total de Lanzamientos</div>
          </div>
          
          <div className="bg-green-50 p-6 rounded-lg text-center border border-green-200">
            <div className="text-3xl font-bold text-green-600 mb-2">{stats.successful}</div>
            <div className="text-gray-700 font-medium">Exitosos</div>
          </div>
          
          <div className="bg-red-50 p-6 rounded-lg text-center border border-red-200">
            <div className="text-3xl font-bold text-red-600 mb-2">{stats.failed}</div>
            <div className="text-gray-700 font-medium">Fallidos</div>
          </div>
          
          <div className="bg-purple-50 p-6 rounded-lg text-center border border-purple-200">
            <div className="text-3xl font-bold text-purple-600 mb-2">{stats.upcoming}</div>
            <div className="text-gray-700 font-medium">Próximos</div>
          </div>
        </div>

        {/* Tasa de éxito */}
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-6 rounded-lg border border-yellow-200 mb-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-yellow-600 mb-2">
              {stats.success_rate?.toFixed(2)}%
            </div>
            <div className="text-gray-700 font-medium text-lg">Tasa de Éxito</div>
            <p className="text-gray-600 text-sm mt-2">
              Basado en {totalCompleted} lanzamientos completados
            </p>
          </div>
        </div>

        {/* Barra de progreso de éxito/fallo */}
        {totalCompleted > 0 && (
          <div className="mb-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Distribución de Resultados</h3>
            <div className="bg-gray-200 rounded-full h-6 overflow-hidden">
              <div 
                className="bg-green-500 h-6 transition-all duration-500 ease-out"
                style={{ width: `${successPercentage}%` }}
                title={`${stats.successful} exitosos (${successPercentage.toFixed(1)}%)`}
              ></div>
              <div 
                className="bg-red-500 h-6 -mt-6 transition-all duration-500 ease-out"
                style={{ width: `${failedPercentage}%`, marginLeft: `${successPercentage}%` }}
                title={`${stats.failed} fallidos (${failedPercentage.toFixed(1)}%)`}
              ></div>
            </div>
            <div className="flex justify-between text-sm text-gray-600 mt-2">
              <span>Exitosos: {stats.successful} ({successPercentage.toFixed(1)}%)</span>
              <span>Fallidos: {stats.failed} ({failedPercentage.toFixed(1)}%)</span>
            </div>
          </div>
        )}

        {/* Estadísticas por cohete */}
        {stats.rockets && Object.keys(stats.rockets).length > 0 && (
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Lanzamientos por Cohete</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(stats.rockets)
                .sort(([,a], [,b]) => b - a)
                .map(([rocket, count]) => (
                  <div key={rocket} className="bg-gray-50 p-4 rounded-lg border">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900">{rocket}</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
                        {count}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${(count / stats.total_launches) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-right text-xs text-gray-500 mt-1">
                      {((count / stats.total_launches) * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Información de actualización */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center">
            Última actualización: {stats.last_updated ? 
              new Date(stats.last_updated).toLocaleString('es-ES') : 
              'Desconocida'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default Statistics;
