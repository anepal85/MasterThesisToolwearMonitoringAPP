import requests
import os
from label_studio_converter import brush
from PIL import Image
import numpy as np
import urllib.parse

LABEL_STUDIO_URL = 'http://localhost:8080'
#API_KEY = '52297494adebaf4e6826df8e743b072fb508a2e1'

def get_headers(api_key):
    return {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }

# headers = {
#     'Authorization': f'Token {API_KEY}',
#     'Content-Type': 'application/json'
# }

def create_segmentation_project(project_name, api_key):
    project_data = {
        "title": project_name,
        "description": "Project for segmenting images with masks",
        "label_config": """
        <View>
            <Image name="image" value="$image" zoom="true" zoomControl="true" rotateControl="false"/>
            <BrushLabels name="tag" toName="image">
                <Label value="TWDamaged" background="#FFA39E"/>
            </BrushLabels>
        </View>
        """
    }
    headers = get_headers(api_key)
    response = requests.post(f"{LABEL_STUDIO_URL}/api/projects", headers=headers, json=project_data)
    response.raise_for_status()
    project = response.json()
    print(f"Project created with ID: {project['id']}")
    return project

def create_local_storage(project_id, root_folder, api_key):
    folder = root_folder.replace('/', '\\')
    storage_data = {
        "type": "local",
        "path": folder,
        "project": project_id,
        "use_blob_urls": True
    }
    headers = get_headers(api_key)
    response = requests.post(f"{LABEL_STUDIO_URL}/api/storages/localfiles", headers=headers, json=storage_data)
    response.raise_for_status()
    storage = response.json()
    return storage

def get_local_storages(project_id, api_key):
    headers = get_headers(api_key)
    response = requests.get(f"{LABEL_STUDIO_URL}/api/storages/localfiles?project={project_id}", headers=headers)
    response.raise_for_status()
    storages = response.json()
    return storages

def get_local_storage_root_folder(project_id, api_key):
    storages = get_local_storages(project_id, api_key)

    if storages and isinstance(storages, list):
        for storage in storages:
            if 'path' in storage:
                return storage['path'].replace('\\', '/')
    
    return None


def sync_local_storage(storage_id, api_key):
    headers = get_headers(api_key)
    response = requests.post(f"{LABEL_STUDIO_URL}/api/storages/localfiles/{storage_id}/sync", headers=headers)
    response.raise_for_status()

def resize_mask(mask, target_size):
    return mask.resize(target_size, resample=Image.NEAREST)

def create_rle_annotation(image_path, mask_path, label_name, from_name, to_name):
    image = Image.open(image_path)
    mask = Image.open(mask_path).convert('L')  
    resized_mask = resize_mask(mask, image.size)
    mask_np = np.array(resized_mask, dtype=np.uint8)
    rle = brush.mask2rle(mask_np)
    
    annotation = {
        "result": [{
            "original_width": image.size[0],
            "original_height": image.size[1],
            "image_rotation": 0,
            "value": {
                "format": "rle",
                "rle": rle,
                "brushlabels": [label_name]
            },
            "from_name": from_name,
            "to_name": to_name,
            "type": "brushlabels"
        }]
    }
    return annotation
def get_existing_tasks(project_id, api_key):
    headers = get_headers(api_key)
    response = requests.get(f"{LABEL_STUDIO_URL}/api/projects/{project_id}/tasks", headers=headers)
    response.raise_for_status()
    tasks = response.json()
    return {task['data']['image']: task['id'] for task in tasks}

def upload_image_task(project_id, image_url, api_key):
    task_data = {
        "data": {
            "image": image_url
        }
    }
    headers = get_headers(api_key)
    response = requests.post(f"{LABEL_STUDIO_URL}/api/projects/{project_id}/tasks", headers=headers, json=task_data)
    response.raise_for_status()
    task = response.json()
    return task['id']

def upload_annotation(task_id, annotation, api_key):
    annotation_data = {
        "task": task_id,
        "result": annotation['result']
    }
    headers = get_headers(api_key)
    response = requests.post(f"{LABEL_STUDIO_URL}/api/tasks/{task_id}/annotations", headers=headers, json=annotation_data)
    response.raise_for_status()

def get_file_paths(folder, extension):
    file_paths = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file).replace(os.sep, '/'))
    return file_paths

def encode_image_url(image_path, root_folder):
    relative_image_path = os.path.relpath(image_path, root_folder)
    encoded_image_path = urllib.parse.quote(relative_image_path)
    encoded_like_image_path_from_local_storage = encoded_image_path.replace('/', '%C5')
    return f"/data/local-files/?d={encoded_like_image_path_from_local_storage}"

def create_and_upload_annotations(new_images, new_masks, task_ids, label_name, from_name, to_name, api_key):
    if len(new_images) != len(new_masks):
        raise ValueError("The number of images and masks does not match.")

    for image_path, mask_path, task_id in zip(new_images, new_masks, task_ids):
        #task_id = upload_image_task(project_id, image_url, api_key)
        annotation = create_rle_annotation(image_path, mask_path, label_name, from_name, to_name)
        upload_annotation(task_id, annotation, api_key)

def task_has_annotation(task_id, api_key):
    headers = get_headers(api_key)
    response = requests.get(f"{LABEL_STUDIO_URL}/api/tasks/{task_id}/annotations", headers=headers)
    response.raise_for_status()
    annotations = response.json()
    return len(annotations) > 0


# def create_and_upload_annotations(images_folder, masks_folder, root_folder, project_id, label_name, from_name, to_name, api_key):
#     images_folder = images_folder.replace('/', '\\')
#     masks_folder = masks_folder.replace('/', '\\')
#     root_folder = root_folder.replace('/', '\\',)

#     images = get_file_paths(images_folder, ".jpg")
#     masks = get_file_paths(masks_folder, ".tif")

#     if len(images) != len(masks):
#         raise ValueError("The number of images and masks does not match.")
        
#     storage = create_local_storage(project_id, images_folder, api_key)
#     sync_local_storage(storage['id'], api_key)

#     existing_tasks = get_existing_tasks(project_id, api_key)
#     print(f"Existing Tasks: {existing_tasks}")

#     for image_path, mask_path in zip(images, masks):
#         relative_image_path = os.path.relpath(image_path, root_folder)#.replace(os.sep, '/')
#         # Encode the path correctly for URL
#         encoded_image_path = urllib.parse.quote(relative_image_path)
#         encoded_like_image_path_from_local_sotrage = encoded_image_path.replace('/', '%C5') 
#         image_url = f"/data/local-files/?d={encoded_like_image_path_from_local_sotrage}"

#         if image_url in existing_tasks:
#             task_id = existing_tasks[image_url]
#             if not task_has_annotation(task_id, api_key):
#                 annotation = create_rle_annotation(image_path, mask_path, label_name, from_name, to_name)
#                 upload_annotation(task_id, annotation, api_key)
#             else:
#                 print(f"Annotation already exists for task ID: {task_id}")
#         else:
#             task_id = upload_image_task(project_id, image_url, api_key)

#             annotation = create_rle_annotation(image_path, mask_path, label_name, from_name, to_name)
#             upload_annotation(task_id, annotation, api_key)


