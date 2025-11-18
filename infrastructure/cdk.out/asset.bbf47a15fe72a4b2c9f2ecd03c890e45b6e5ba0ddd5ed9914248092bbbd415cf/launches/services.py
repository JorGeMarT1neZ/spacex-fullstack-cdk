import boto3
import os
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DecimalEncoder:
    
    @staticmethod
    def encode_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class DynamoDBService:
    def __init__(self):
        self.table_name = os.environ.get('TABLE_NAME', 'spacex-launches')
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        try:
            # Configurar cliente DynamoDB
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=self.region,
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
            self.table = self.dynamodb.Table(self.table_name)
            
            # Verificar conexión
            self.table.table_status
            logger.info(f"DynamoDB Service initialized for table: {self.table_name}")
            
        except Exception as e:
            logger.error(f"Error initializing DynamoDB: {str(e)}")
            raise
    
    def get_all_launches(self, limit: int = 100, last_evaluated_key: Optional[Dict] = None) -> Dict[str, Any]:
        """Obtiene todos los lanzamientos con paginación"""
        try:
            scan_params = {
                'Limit': limit
            }
            
            if last_evaluated_key:
                scan_params['ExclusiveStartKey'] = last_evaluated_key
            
            response = self.table.scan(**scan_params)
            
            return {
                'items': response.get('Items', []),
                'last_evaluated_key': response.get('LastEvaluatedKey'),
                'count': response.get('Count', 0),
                'scanned_count': response.get('ScannedCount', 0)
            }
        except Exception as e:
            logger.error(f"Error getting all launches: {str(e)}")
            raise
    
    def get_launch_by_id(self, launch_id: str) -> Optional[Dict]:
        """Obtiene un lanzamiento por ID - VERSIÓN CORREGIDA"""
        try:
            # IMPORTANTE: Usar query en lugar de get_item para clave compuesta
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('launch_id').eq(launch_id),
                Limit=1
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except Exception as e:
            logger.error(f"Error getting launch by ID {launch_id}: {str(e)}")
            return None
    
    def get_launches_by_status(self, status: str, limit: int = 50) -> List[Dict]:
        """Obtiene lanzamientos por estado - VERSIÓN CORREGIDA"""
        try:
            # Usar expresión de filtro en scan
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('status').eq(status),
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error getting launches by status {status}: {str(e)}")
            return []
    
    def get_launches_by_rocket(self, rocket_name: str, limit: int = 50) -> List[Dict]:
        """Obtiene lanzamientos por cohete - VERSIÓN CORREGIDA"""
        try:
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('rocket_name').eq(rocket_name),
                Limit=limit
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Error getting launches by rocket {rocket_name}: {str(e)}")
            return []
    
    def get_upcoming_launches(self, limit: int = 10) -> List[Dict]:
        """Obtiene próximos lanzamientos"""
        return self.get_launches_by_status('upcoming', limit)
    
    def get_launch_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de lanzamientos - VERSIÓN OPTIMIZADA"""
        try:
            # Para estadísticas, usar contadores progresivos para evitar escanear toda la tabla
            items = []
            last_evaluated_key = None
            max_items = 1000  # Límite para evitar costos altos
            
            while len(items) < max_items:
                scan_params = {'Limit': 100}
                if last_evaluated_key:
                    scan_params['ExclusiveStartKey'] = last_evaluated_key
                
                response = self.table.scan(**scan_params)
                batch_items = response.get('Items', [])
                items.extend(batch_items)
                
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break
            
            total = len(items)
            successful = len([item for item in items if item.get('status') == 'success'])
            failed = len([item for item in items if item.get('status') == 'failed'])
            upcoming = len([item for item in items if item.get('status') == 'upcoming'])
            
            # Estadísticas por cohete
            rockets = {}
            for item in items:
                rocket = item.get('rocket_name', 'Unknown')
                rockets[rocket] = rockets.get(rocket, 0) + 1
            
            # Calcular tasa de éxito (excluyendo upcoming)
            total_completed = total - upcoming
            success_rate = (successful / total_completed * 100) if total_completed > 0 else 0
            
            return {
                'total_launches': total,
                'successful': successful,
                'failed': failed,
                'upcoming': upcoming,
                'success_rate': round(success_rate, 2),
                'rockets': rockets,
                'last_updated': datetime.utcnow().isoformat(),
                'sample_size': len(items)  # Para debugging
            }
        except Exception as e:
            logger.error(f"Error getting launch statistics: {str(e)}")
            return {
                'total_launches': 0,
                'successful': 0,
                'failed': 0,
                'upcoming': 0,
                'success_rate': 0,
                'rockets': {},
                'error': str(e)
            }
    
    def search_launches(self, query: str, limit: int = 20) -> List[Dict]:
        """Busca lanzamientos por término en nombre de misión"""
        try:
            all_items = []
            last_evaluated_key = None
            
            while len(all_items) < limit:
                scan_params = {'Limit': 50}
                if last_evaluated_key:
                    scan_params['ExclusiveStartKey'] = last_evaluated_key
                
                response = self.table.scan(**scan_params)
                items = response.get('Items', [])
                
                # Filtrar localmente por query
                filtered_items = [
                    item for item in items 
                    if query.lower() in item.get('mission_name', '').lower()
                ]
                all_items.extend(filtered_items)
                
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key or len(all_items) >= limit:
                    break
            
            return all_items[:limit]
        except Exception as e:
            logger.error(f"Error searching launches: {str(e)}")
            return []
    
    def get_recent_launches(self, limit: int = 10) -> List[Dict]:
        """Obtiene lanzamientos más recientes ordenados por fecha"""
        try:
            # Nota: Para ordenar por fecha necesitaríamos un GSI, por ahora usamos scan + sort local
            response = self.table.scan(Limit=limit * 3)  # Escanear más para luego filtrar
            items = response.get('Items', [])
            
            # Ordenar por fecha descendente
            sorted_items = sorted(
                items, 
                key=lambda x: x.get('launch_date', ''), 
                reverse=True
            )
            
            return sorted_items[:limit]
        except Exception as e:
            logger.error(f"Error getting recent launches: {str(e)}")
            return []