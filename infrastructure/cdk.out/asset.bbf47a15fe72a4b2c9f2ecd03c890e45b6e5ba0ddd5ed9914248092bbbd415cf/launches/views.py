import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services import DynamoDBService, DecimalEncoder

class LaunchListView(APIView):
    """
    Lista todos los lanzamientos con paginación
    """
    def __init__(self):
        self.db_service = DynamoDBService()
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'limit', 
                openapi.IN_QUERY, 
                description="Número de items por página (max 100)", 
                type=openapi.TYPE_INTEGER,
                default=20
            ),
            openapi.Parameter(
                'last_key', 
                openapi.IN_QUERY, 
                description="Última clave evaluada para paginación", 
                type=openapi.TYPE_STRING
            ),
        ],
        responses={200: 'Lista de lanzamientos'}
    )
    def get(self, request):
        limit = min(int(request.GET.get('limit', 20)), 100)  # Máximo 100 items
        last_key = request.GET.get('last_key')
        
        try:
            if last_key:
                # Decodificar last_key desde string JSON
                last_key = json.loads(last_key)
            
            result = self.db_service.get_all_launches(limit=limit, last_evaluated_key=last_key)
            
            # Serializar items usando el encoder personalizado
            serialized_items = []
            for item in result['items']:
                serialized_item = json.loads(json.dumps(item, default=DecimalEncoder.encode_decimal))
                serialized_items.append(serialized_item)
            
            response_data = {
                'items': serialized_items,
                'count': result['count'],
                'scanned_count': result['scanned_count'],
                'last_evaluated_key': result['last_evaluated_key']
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving launches: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LaunchDetailView(APIView):
    """
    Obtiene detalles de un lanzamiento específico
    """
    def __init__(self):
        self.db_service = DynamoDBService()
    
    @swagger_auto_schema(
        responses={
            200: 'Detalles del lanzamiento',
            404: 'Lanzamiento no encontrado'
        }
    )
    def get(self, request, launch_id):
        try:
            launch = self.db_service.get_launch_by_id(launch_id)
            if not launch:
                return Response(
                    {'error': f'Launch with ID {launch_id} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Serializar usando el encoder personalizado
            serialized_launch = json.loads(json.dumps(launch, default=DecimalEncoder.encode_decimal))
            return Response(serialized_launch)
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving launch: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LaunchStatisticsView(APIView):
    """
    Obtiene estadísticas de lanzamientos
    """
    def __init__(self):
        self.db_service = DynamoDBService()
    
    @swagger_auto_schema(
        responses={200: 'Estadísticas de lanzamientos'}
    )
    def get(self, request):
        try:
            stats = self.db_service.get_launch_statistics()
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': f'Error retrieving statistics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LaunchFilterView(APIView):
    """
    Filtra lanzamientos por estado o cohete
    """
    def __init__(self):
        self.db_service = DynamoDBService()
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status', 
                openapi.IN_QUERY, 
                description="Filtrar por estado (success, failed, upcoming)", 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'rocket', 
                openapi.IN_QUERY, 
                description="Filtrar por nombre de cohete", 
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'limit', 
                openapi.IN_QUERY, 
                description="Límite de resultados", 
                type=openapi.TYPE_INTEGER,
                default=50
            ),
        ],
        responses={200: 'Lanzamientos filtrados'}
    )
    def get(self, request):
        status_filter = request.GET.get('status')
        rocket_filter = request.GET.get('rocket')
        limit = int(request.GET.get('limit', 50))
        
        try:
            if status_filter:
                launches = self.db_service.get_launches_by_status(status_filter, limit=limit)
            elif rocket_filter:
                launches = self.db_service.get_launches_by_rocket(rocket_filter, limit=limit)
            else:
                return Response(
                    {'error': 'Must provide status or rocket filter parameter'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serializar items
            serialized_launches = []
            for launch in launches:
                serialized_launch = json.loads(json.dumps(launch, default=DecimalEncoder.encode_decimal))
                serialized_launches.append(serialized_launch)
            
            return Response({
                'items': serialized_launches, 
                'count': len(serialized_launches),
                'filters': {
                    'status': status_filter,
                    'rocket': rocket_filter
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error filtering launches: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpcomingLaunchesView(APIView):
    """
    Obtiene próximos lanzamientos
    """
    def __init__(self):
        self.db_service = DynamoDBService()
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'limit', 
                openapi.IN_QUERY, 
                description="Límite de resultados", 
                type=openapi.TYPE_INTEGER,
                default=10
            ),
        ],
        responses={200: 'Próximos lanzamientos'}
    )
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        
        try:
            launches = self.db_service.get_upcoming_launches(limit=limit)
            
            # Serializar items
            serialized_launches = []
            for launch in launches:
                serialized_launch = json.loads(json.dumps(launch, default=DecimalEncoder.encode_decimal))
                serialized_launches.append(serialized_launch)
            
            return Response({
                'items': serialized_launches,
                'count': len(serialized_launches)
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving upcoming launches: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SearchLaunchesView(APIView):
    """
    Busca lanzamientos por término en nombre de misión
    """
    def __init__(self):
        self.db_service = DynamoDBService()
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q', 
                openapi.IN_QUERY, 
                description="Término de búsqueda", 
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'limit', 
                openapi.IN_QUERY, 
                description="Límite de resultados", 
                type=openapi.TYPE_INTEGER,
                default=20
            ),
        ],
        responses={200: 'Resultados de búsqueda'}
    )
    def get(self, request):
        query = request.GET.get('q')
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            launches = self.db_service.search_launches(query, limit=limit)
            
            # Serializar items
            serialized_launches = []
            for launch in launches:
                serialized_launch = json.loads(json.dumps(launch, default=DecimalEncoder.encode_decimal))
                serialized_launches.append(serialized_launch)
            
            return Response({
                'items': serialized_launches,
                'count': len(serialized_launches),
                'query': query
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error searching launches: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
