import requests
import os
from pathlib import Path

BASE_URL  = ''
TOKEN = ''

class labelstudioLoader():
    def __init__(self,*args, **kwargs) -> None:
        self.BASE_URL = kwargs.get("url") or (args[0] if args else None)
        self.TOKEN = kwargs.get("token") or (args[1] if len(args) > 1 else None)
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.TOKEN
        }


    # ========================
    # Project相關
    # ======================== 
    # OK
    def export_project(self, project_id, export_type='JSON', save_path=None, file_name=None, replace=False):
        """
        Export a project from LabelStudio.

        Args:
            project_id (int): The ID of the project to export.
            export_type (str, optional): The export type. Defaults to 'JSON'.
            save_path (str, optional): The directory path to save the exported file. If None, the content will not be saved to a file. Defaults to None.
            file_name (str, optional): The name of the exported file. Only applicable if save_path is provided. Defaults to None.

        Returns:
            dict: The JSON response containing the exported project data.
        """

        # Check if file already exists
        if os.path.exists(os.path.join(save_path, file_name)) and not replace:
            print(f"File already exists at {save_path}. Skipping export.")
            import json
            with open(os.path.join(save_path, file_name), 'r', encoding='utf-8') as f:
                d = json.load(f)
            return d
        
        endpoint = f"projects/{project_id}/export"
        url = self.BASE_URL + endpoint
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.TOKEN
        }
        
        params = {
            'exportType': export_type
        }

        response = requests.get(url, headers = headers, params=params)

        if response.ok and save_path is not None and file_name is not None:
            
            

            path = Path(save_path)
            path.mkdir(parents=True, exist_ok=True)
            file_path = path / file_name
            
            with open(file_path, 'wb') as file:
                file.write(response.content)

        return response.json()

    # OK
    def get_projects_list(self):
        """
        Retrieve a list of projects from LabelStudio.

        Returns:
            list: A list of dictionaries representing the projects.
        """
        headers = {
            'Authorization': self.TOKEN
        }
        url = self.BASE_URL + "projects/"
        results = []

        while url:
            response = requests.get(url, headers=headers)

            if response.ok:
                data = response.json()
                results += data['results']
                url = data['next']
            else:
                print(f"Failed to retrieve projects. Status code: {response.status_code}")
                return []

        return results
    
    # OK
    def delete_project(self, project_id):
        """
        Delete a project from LabelStudio.

        Args:
            project_id (int): The ID of the project to remove.

        Returns:
            bool: True if the project is successfully removed, False otherwise.
        """
        url = self.BASE_URL + f"projects/{project_id}/"
        response = requests.delete(url, headers=self.headers)

        if response.status_code == 204:
            return True
        else:
            print(f"Failed to remove project with ID {project_id}. Status code: {response.status_code}")
            return False

    # OK
    def check_if_project_exists(self, project_id):
        """
        Check if a project exists in LabelStudio.

        Args:
            project_id (int): The ID of the project to check.

        Returns:
            bool: True if the project exists, False otherwise.
        """
        url = self.BASE_URL + f"projects/{project_id}/"
        response = requests.head(url, headers=self.headers)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            print(f"Failed to check project existence for ID {project_id}. Status code: {response.status_code}")
            return False

    def remove_project_by_name(self, project_name):
        project_id = self.check_if_project_exist(project_name)
        if project_id:
            return requests.delete(self.BASE_URL + 'projects/'+str(project_id) +"/", headers = self.headers)
        else:
            return False
    
    def create_project(self, project_name, input_data=None):
        """
        Create a new project in LabelStudio.

        Args:
            project_name (str): The name of the project to create.
            input_data (dict): Additional fields to include in the request body.

        Returns:
            dict: The JSON response containing the newly created project data.
        """
        url = f'{self.BASE_URL}/projects/'
        data = {
                "title": project_name,
                "description": "",
                'label_config': "",
                "expert_instruction": "",
                "show_instruction": True,
                "show_skip_button": True,
                "enable_empty_annotation": True,
                "show_annotation_history": True,
                "organization": 1,
                'color': '#FFFFFF',
                "maximum_annotations": 1,
                "is_published": False,
                "model_version": "",
                "is_draft": False,
                "created_by": {'id': 2,
                    'first_name': '',
                    'last_name': '',
                    'email': 'neverleave0916@gmail.com',
                    'avatar': None},
                "min_annotations_to_start_training": 0,
                "show_collab_predictions": True,
                "sampling": "Sequential sampling",
                "show_ground_truth_first": False,
                "show_overlap_first": False,
                "overlap_cohort_percentage": 100,
                "task_data_login": None,
                "task_data_password": None,
                "control_weights": { },
                "evaluate_predictions_automatically": False,
                "skip_queue": "REQUEUE_FOR_OTHERS",
                "reveal_preannotations_interactively": False,
                "pinned_at": None
            }

        if input_data is not None:
            # Update data dictionary with provided input_data
            data.update(input_data)

        response = requests.post(url, headers=self.headers, data=data)

        if response.status_code == 201:
            return response.json()
        else:
            # Handle error or raise an exception
            # For simplicity, let's print an error message
            print(f"Failed to create project '{project_name}'. Status code: {response.status_code}")
            return None
        

#     def create_project(self, project_name, data=None, relation_value=""):
        
#         if data is None:
#             data = {
#                 "title": project_name,
#                 "description": "",
#                 'label_config': \
# f"""<View>
#   <Relations>
#     <Relation value="{relation_value}"/>
#   </Relations>
#   <Labels name="label" toName="text">
#     <Label value="GPE"/>
#     <Label value="PERSON"/>
#     <Label value="DATE"/>
#     <Label value="ORG"/>
#     <Label value="CARDINAL"/>
#     <Label value="NORP"/>
#     <Label value="LOC"/>
#     <Label value="TIME"/>
#     <Label value="FAC"/>
#     <Label value="MONEY"/>
#     <Label value="ORDINAL"/>
#     <Label value="EVENT-OTHER"/>
#     <Label value="WORK_OF_ART"/>
#     <Label value="QUANTITY"/>
#     <Label value="PERCENT"/>
#     <Label value="LANGUAGE"/>
#     <Label value="LAW"/>
#     <Label value="EVENT-MandA"/>
#     <Label value="EVENT-Financing"/>
#     <Label value="EVENT-CapitalIncrease"/>
#     <Label value="EVENT-Redirect"/>
#     <Label value="EVENT-OutOfStock"/>
#     <Label value="EVENT-PriceHikes"/>
#     <Label value="EVENT-PriceCut"/>
#     <Label value="EVENT-Plunge"/>
#     <Label value="EVENT-Hike"/>
#     <Label value="EVENT-Policy"/>
#     <Label value="EVENT-Inflation"/>
#     <Label value="EVENT-PowerShortage"/>
#     <Label value="EVENT-PowerOutage"/>
#     <Label value="EVENT-Strike"/>
#     <Label value="EVENT-War"/>
#     <Label value="EVENT-Lawsuit"/>
#     <Label value="PRODUCT"/>
#     <Label value="TECH"/>
#     <Label value="EQPT"/>
#     <Label value="MATL"/>
#   </Labels>
#   <Text name="text" value="$text"/>
# </View>
# """,
#                 "expert_instruction": "",
#                 "show_instruction": False,
#                 "show_skip_button": True,
#                 "enable_empty_annotation": True,
#                 "show_annotation_history": True,
#                 "organization": 1,
#                 'color': '#FFFFFF',
#                 "maximum_annotations": 1,
#                 "is_published": False,
#                 "model_version": "LighrNER1220",
#                 "is_draft": False,
#                 "created_by": {'id': 2,
#                     'first_name': '',
#                     'last_name': '',
#                     'email': 'neverleave0916@gmail.com',
#                     'avatar': None},
#                 "min_annotations_to_start_training": 0,
#                 "show_collab_predictions": True,
#                 "sampling": "Sequential sampling",
#                 "show_ground_truth_first": False,
#                 "show_overlap_first": False,
#                 "overlap_cohort_percentage": 100,
#                 "task_data_login": None,
#                 "task_data_password": None,
#                 "control_weights": { },
#                 "evaluate_predictions_automatically": False,
#                 "skip_queue": "REQUEUE_FOR_OTHERS",
#                 "reveal_preannotations_interactively": False,
#                 "pinned_at": None
#             }
#         # Create project
#         headers = {'Authorization': self.TOKEN}
#         r = requests.post(self.BASE_URL+"projects/", headers = headers, data = data)
#         return r

    # ========================
    # Import Export
    # ========================

    def import_data(project_id, data):
        # Import Data
        headers = {
            'Content-Type': 'application/json',
            'Authorization': TOKEN
        }
        res = requests.post(BASE_URL+"projects/"+str(project_id)+'/import', headers = headers, data=data)
        if res.status_code == 201:
            print("Imported data to project: " + project_id)
            print("Tasks imported: " + str(res.json()['task_count']))
        # {'task_count': 94, 'annotation_count': 0, 'prediction_count': 94, 'duration': 0.0929405689239502, 'file_upload_ids': [], 'could_be_tasks_list': False, 'found_formats': [], 'data_columns': []}
        return project_id, res.json()

    
    def import_to_labelstudio(self, project_name, data, create_if_not_exist = True, relation_value="", import_if_exist=False):
        import json
        data = json.dumps(data, ensure_ascii=False).encode('utf8')

        exist_result = self.check_if_project_exist(project_name)
        if exist_result and not import_if_exist:
            # skip import
            print ("Project exist: " + project_name + "  ID: "+str(exist_result))
            print ("Skip import")
            return "Project exist", None

        elif exist_result:
            print ("Project exist: " + project_name + "  ID: "+str(exist_result))
            project_id = str(exist_result)
        else:
            if create_if_not_exist:
                r = self.create_project(project_name, relation_value=relation_value)
                if r.status_code == 201:
                    print ("Create project: " + project_name + "  ID: "+str(r.json()['id']))
                    project_id = str(r.json()['id'])
                else:
                    print(r.json())
            else:
                return "Project does not exist"
        
        # Import Data
        res = requests.post(BASE_URL+"projects/"+str(project_id)+'/import', headers = self.headers, data=data)
        if res.status_code == 201:
            print("Imported data to project: " + project_name)
            print("Tasks imported: " + str(res.json()['task_count']))
        # {'task_count': 94, 'annotation_count': 0, 'prediction_count': 94, 'duration': 0.0929405689239502, 'file_upload_ids': [], 'could_be_tasks_list': False, 'found_formats': [], 'data_columns': []}
        return project_id, res.json()
