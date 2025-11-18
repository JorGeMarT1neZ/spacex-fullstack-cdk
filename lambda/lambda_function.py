import os
import json
import boto3
import requests
from datetime import datetime, timezone
from decimal import Decimal
import logging

# Configuración de logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clients de AWS
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

class SpaceXDataProcessor:
    def __init__(self):
        self.spacex_api_url = os.environ.get('SPACEX_API_URL', 'https://api.spacexdata.com/v4/launches')
    
    def fetch_launches_data(self):
        """Obtiene datos de lanzamientos desde SpaceX API"""
        try:
            response = requests.get(self.spacex_api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching SpaceX data: {str(e)}")
            raise
    
    def transform_launch_data(self, launch):
        """Transforma los datos del lanzamiento al formato requerido"""
        try:
            # Información básica
            launch_id = launch.get('id', '')
            mission_name = launch.get('name', 'N/A')
            
            # Determinar estado
            success = launch.get('success')
            upcoming = launch.get('upcoming', False)
            
            if upcoming:
                status = 'upcoming'
            elif success is None:
                status = 'unknown'
            elif success:
                status = 'success'
            else:
                status = 'failed'
            
            # Fecha de lanzamiento
            launch_date_utc = launch.get('date_utc', '')
            launch_date_unix = launch.get('date_unix', 0)
            
            # Información del cohete
            rocket_name = launch.get('rocket', {}).get('name', 'N/A') if isinstance(launch.get('rocket'), dict) else 'N/A'
            
            # Información del launchpad
            launchpad_name = launch.get('launchpad', {}).get('name', 'N/A') if isinstance(launch.get('launchpad'), dict) else 'N/A'
            launchpad_full_name = launch.get('launchpad', {}).get('full_name', 'N/A') if isinstance(launch.get('launchpad'), dict) else 'N/A'
            
            # Payloads
            payloads = launch.get('payloads', [])
            payload_names = []
            payload_types = []
            
            for payload in payloads:
                if isinstance(payload, dict):
                    payload_names.append(payload.get('name', 'Unknown'))
                    payload_types.append(payload.get('type', 'Unknown'))
            
            # Links
            links = launch.get('links', {})
            patch_image = links.get('patch', {}).get('small', '')
            webcast_url = links.get('webcast', '')
            article_url = links.get('article', '')
            wikipedia_url = links.get('wikipedia', '')
            
            transformed_data = {
                'launch_id': launch_id,
                'mission_name': mission_name,
                'rocket_name': rocket_name,
                'launch_date': launch_date_utc,
                'launch_date_unix': Decimal(str(launch_date_unix)),
                'status': status,
                'launchpad_name': launchpad_name,
                'launchpad_full_name': launchpad_full_name,
                'payload_names': payload_names,
                'payload_types': payload_types,
                'patch_image': patch_image,
                'webcast_url': webcast_url,
                'article_url': article_url,
                'wikipedia_url': wikipedia_url,
                'details': launch.get('details', ''),
                'flight_number': Decimal(str(launch.get('flight_number', 0))),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error transforming launch data: {str(e)}")
            return None
    
    def upsert_launch_data(self, launch_data):
        """Inserta o actualiza datos en DynamoDB"""
        try:
            if not launch_data:
                return False
                
            response = table.put_item(Item=launch_data)
            return True
        except Exception as e:
            logger.error(f"Error upserting launch data: {str(e)}")
            return False
    
    def process_launches(self):
        """Procesa todos los lanzamientos"""
        try:
            launches = self.fetch_launches_data()
            processed_count = 0
            success_count = 0
            
            for launch in launches:
                processed_count += 1
                transformed_data = self.transform_launch_data(launch)
                
                if transformed_data and self.upsert_launch_data(transformed_data):
                    success_count += 1
            
            return {
                'total_processed': processed_count,
                'successful_upserts': success_count,
                'failed_upserts': processed_count - success_count
            }
            
        except Exception as e:
            logger.error(f"Error processing launches: {str(e)}")
            raise

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    processor = SpaceXDataProcessor()
    
    try:
        # Procesar lanzamientos
        result = processor.process_launches()
        
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'SpaceX data processed successfully',
                'result': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }
        
        logger.info(f"Processing completed: {result}")
        return response
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Failed to process SpaceX data',
                'details': str(e)
            })
        }
