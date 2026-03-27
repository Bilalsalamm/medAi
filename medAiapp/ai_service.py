"""
AI Prediction Service - Integrates with Kaggle Multi-Model API for diagnosis
Supports: Bone Fracture, Brain MRI, Skin Lesion, Chest X-Ray
"""
import requests
import logging
from django.core.files.storage import default_storage
import io

logger = logging.getLogger(__name__)

KAGGLE_API_URL = "https://nathan-censorial-surreally.ngrok-free.dev/diagnose"
API_TIMEOUT = 120  # Increased to 120 seconds for complex model inference

# Modality mapping
MODALITY_MAP = {
    'Fracture': 'Fracture',
    'MRI': 'MRI',
    'Skin': 'Skin',
    'XRay': 'XRay',
    'chest_xray': 'XRay',
    'brain_mri': 'MRI',
    'skin_lesion': 'Skin',
    'bone': 'Fracture',
}

def get_ai_prediction(image_path, modality='XRay'):
    """
    Send image to Kaggle Multi-Model API for AI diagnosis
    
    Args:
        image_path: Path to the image file (from Report.xray_image)
        modality: Type of medical imaging (Fracture, MRI, Skin, XRay)
    
    Returns:
        dict: Contains diagnosis, confidence, report, and modality
        None: If prediction fails
    """
    try:
        # Normalize modality
        normalized_modality = MODALITY_MAP.get(modality, 'XRay')
        
        # Read the image file from Django storage
        if default_storage.exists(image_path):
            image_file = default_storage.open(image_path, 'rb')
            image_data = image_file.read()
            image_file.close()
        else:
            logger.error(f"Image file not found: {image_path}")
            return None
        
        logger.info(f"Sending {normalized_modality} image to Kaggle API: {image_path}")
        
        # Prepare the file for the API request
        files = {
            'file': ('image.jpg', io.BytesIO(image_data), 'image/jpeg')
        }
        
        # Add modality parameter
        params = {
            'modality': normalized_modality
        }
        
        headers = {
            'User-Agent': 'medAi-django-app/1.0'
        }
        
        logger.info(f"API Call to: {KAGGLE_API_URL} with modality: {normalized_modality}")
        
        response = requests.post(
            KAGGLE_API_URL,
            files=files,
            params=params,
            headers=headers,
            timeout=API_TIMEOUT,
            verify=False  # Allow self-signed certificates (ngrok)
        )
        
        logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"API returned: {result}")
            
            # Parse the response and return standardized format
            prediction = {
                'modality': result.get('modality', normalized_modality),
                'diagnosis': result.get('diagnosis', 'Unable to predict'),
                'confidence': result.get('confidence', '0%'),
                'report': result.get('report', 'No report available'),
                'raw_response': result
            }
            
            logger.info(f"AI prediction successful: {prediction['diagnosis']}")
            return prediction
        else:
            logger.error(f"API returned status code: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            return None
            
    except requests.exceptions.Timeout as e:
        logger.error(f"API request timed out after {API_TIMEOUT}s: {str(e)}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to API: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in AI prediction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


