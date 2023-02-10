from boxsdk import JWTAuth, Client
from boxsdk.object.collaboration import CollaborationRole
from boxsdk.exception import BoxAPIException
from onswitch_data import creds
from onswitch_data.dynamodb import DatabaseConnection, Key

import json
import pandas as pd
import os

class UserDoesNotExistError(Exception):
    pass


box_folder_config = {"dynamodb_table_name":"box_folders", 
          "partition_key":"id",
          "indexes":['name-index'],
          "aws_region":"us-east-1"}


def check_folder_exists_ddb(name, folder_id=None):

    db = DatabaseConnection(region_name='us-east-1')
    if folder_id:
        f = db.query('box_folders', Key('id').eq(folder_id))
        if len(f) == 1:
            return f[0]
        else:
            return False
    path,name = os.path.split(name)
        
    folders = db.query('box_folders', Key('name').eq(name), IndexName='name-index')
    for f in folders:
        dirs = f['path_collection']['entries']
        full_path = '/'.join([d['name'] for d in dirs if d['name']!="All Files"]+[name])
        if full_path.lower() == os.path.join(path, name).lower():
            return f
    return False

class BoxAPI(object):
    project_docs_id = creds["boxAppSettings"]['project_docs_id']
    def __init__(self):
        self.primary_admin_id = creds["boxAppSettings"]['primary_admin_id']
        self.root_id = '0'
        self.project_docs_id = creds["boxAppSettings"]['project_docs_id']
        self.proj_folder_webhook_id = creds["boxAppSettings"]['proj_folder_webhook_id']
        self.company_records_id = creds["boxAppSettings"]['company_records_id']
        self.controlled_docs_id = creds["boxAppSettings"]['controlled_docs_id']
        self.department_docs_id = creds["boxAppSettings"]['department_docs_id']
        self.console_integration_id = creds["boxAppSettings"]['console_integration_id']
        self.folder_structure = creds["boxAppSettings"]['folder_structure']
        self.auth = JWTAuth(
                       client_id=creds["boxAppSettings"]["clientID"],
                       client_secret=creds["boxAppSettings"]["clientSecret"],
                       enterprise_id=creds['enterpriseID'],
                       jwt_key_id=creds["boxAppSettings"]["appAuth"]["publicKeyID"],
                       rsa_private_key_data=creds["boxAppSettings"]["appAuth"]["privateKey"],
                       rsa_private_key_passphrase=creds["boxAppSettings"]["appAuth"]["passphrase"]
                      )

        print(self.auth.access_token)
        self.client = Client(self.auth)
        self.current_user = self.client.user().get()
        self.api_call_count = 2
        self.authenticate_primary_admin()
        self.permission_levels = {"Viewer": CollaborationRole.VIEWER, 
                                  "Viewer Uploader": CollaborationRole.VIEWER_UPLOADER,
                                  "Editor" : CollaborationRole.EDITOR,
                                  "Uploader": CollaborationRole.UPLOADER,
                                  "Previewer": CollaborationRole.PREVIEWER,
                                  "Previewer Uploader" : CollaborationRole.PREVIEWER_UPLOADER,
                                  "Co-Owner": CollaborationRole.CO_OWNER}
           
    def _increment_count(self):
        self.api_call_count += 1

    def list_users(self):

        prev_id = None
        if not self.current_user.id == self.primary_admin_id:
            prev_id = self.current_user.id
            self.authenticate_primary_admin()

        users =  self.client.users()
        self._increment_count()
        if prev_id:
            self.authenticate_as_user(prev_id)

        return users

    def list_app_users(self):
        self._increment_count()
        return self.client.users(user_type='managed')

    def authenticate_primary_admin(self):
        user = self.client.user(user_id=self.primary_admin_id).get()
        self._increment_count()
        self.current_user = user
        primary_admin_client = self.client.as_user(user)
        self._increment_count()
        self.client = primary_admin_client

    def authenticate_as_user(self, user_id):
        user = self.client.user(user_id=user_id).get()
        self._increment_count()
        self.current_user = user
        user_client = self.client.as_user(user)
        self._increment_count()
        self.client = user_client

    def check_app_user_exists(self, name=None, user_id=None):
        if user_id:
            try:
                self._increment_count()
                return self.client.user(user_id=user_id).get()
            except BoxAPIException:
                return False
        
        if name:
            app_users = self.list_app_users()
            users_with_name = []
            for u in app_users:
                if u.name == name:
                    users_with_name.append(u)
            if len(users_with_name) == 0:
                return False
            else:
                return users_with_name

        raise ValueError('no args were given')

    def create_app_user(self, name, email=None):
        self._increment_count()
        if email:
            user = self.client.create_user(name, is_platform_access_only=True, external_app_user_id=email)
        else:
            user = self.client.create_user(name, is_platform_access_only=True)
        return user

    def check_folder_exists(self, path, **kwargs):
        
        if path.strip('/') == 'All Files':
            return True

        if kwargs.get("folder_id"):
            try:
                f = self.client.folder(kwargs.get("folder_id")).get()
                self._increment_count()
                return f.id
            except BoxAPIException:
                return False

        dirnames = path.split('/')

        last = dirnames[-1]

        dir_id = self.root_id
        if kwargs.get("start_id"):
            dir_id = kwargs.get("start_id")

        for dir_ in dirnames:
            items = self.client.folder(folder_id=dir_id).get_items()
            self._increment_count()
            for item in items:
                if item.name.lower() == dir_.lower():
                    print("found {}".format(dir_))
                    dir_id = item.id
                    if dir_.lower() == last.lower():
                        print('found {}'.format(path))
                        return dir_id
        print('did not find {}'.format(path))
        return False

    def create_folder(self, path, **kwargs):

        parent_folder, folder_name = os.path.split(path)
        parent_folder = parent_folder.strip()
        folder_name = folder_name.strip()
        if kwargs.get('parent_folder_id'):
            parent_folder_id = kwargs.get('parent_folder_id')

        elif parent_folder == "":
            parent_folder_id = self.root_id

        else:
            print("parent_folder_id not found")
            parent_folder_id = self.check_folder_exists(parent_folder)
            if not parent_folder_id:
                print('folder {} does not exist, making it now'.format(parent_folder))
                parent_folder_id = self.create_folder(parent_folder).id

        subfolder = self.client.folder(parent_folder_id).create_subfolder(folder_name)
        self._increment_count()
        print(f'Created subfolder {folder_name} with ID {subfolder.id}')
        return subfolder

    def check_collaboration_exists(self, folder_id, user_id, permission_level=None):
        collabs = self.client.folder(folder_id=folder_id).get_collaborations()
        self._increment_count()
        user = False
        permission = False
        for c in collabs:
            target_id = c.accessible_by.id
            if target_id == user_id:
                return c
        return user, permission

    def create_collaboration(self, folder_id, user_id, permission_level):
        user = self.client.user(user_id=user_id)
        self._increment_count()
        collaboration = self.client.folder(folder_id=folder_id).collaborate(user, self.permission_levels[permission_level], can_view_path=True, notify=False)
        self._increment_count()
        return collaboration

    def create_external_collaboration(self, folder_id, login, permission_level):
        collaboration = self.client.folder(folder_id=folder_id).collaborate_with_login(login, self.permission_levels[permission_level], can_view_path=True, notify=False)
        self._increment_count()
        return collaboration

    def create_internal_collaboration(self, folder_id, login, permission_level):
        collaboration = self.client.folder(folder_id=folder_id).collaborate_with_login(login, self.permission_levels[permission_level], can_view_path=True, notify=False)
        self._increment_count()
        return collaboration

    def load_folder_structure(self):
        fn = "/tmp/folder_structure.xlsx"
        with open(fn, 'wb') as f:
            self.client.file(self.folder_structure).get().download_to(f)
            self._increment_count()
        df = pd.read_excel(fn, sheet_name='folder_structure', skiprows=2)
        return df

    def check_project_folder_webhook(self):
        w = self.client.webhook(webhook_id=self.proj_folder_webhook_id).get()
        print(w.response_object)
        if not w:
            all_triggers = "FOLDER.CREATED,FOLDER.RENAMED,FOLDER.RESTORED,FOLDER.MOVED,COLLABORATION.CREATED,COLLABORATION.ACCEPTED,COLLABORATION.REMOVED,COLLABORATION.UPDATED,FOLDER.DELETED,FOLDER.TRASHED".split(',')
            proj_folder = self.client.folder(self.project_docs_id)
            webhook = self.client.create_webhook(proj_folder, all_triggers, creds["boxAppSettings"]['s3_url'])

    def generate_content_explorer(self, folder_id, user_id):
        self.authenticate_as_user(user_id)
        access_token = self.client.auth.access_token
    
        return folder_id, access_token
