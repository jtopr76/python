import json
from decimal import Decimal
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceMalformedRequest, SalesforceExpiredSession, SalesforceAuthenticationFailed
from onswitch_data.dynamodb import DatabaseConnection, Key
from onswitch_data.sync import prep_data
from onswitch_data import creds
from onswitch_data.utils import refresh_table


credentials = creds['sfdc']

class SFDCAPI():

    def __init__(self):
        """initializes connection with salesforce api
        """
        self.cred_ix = 0
        self._reconnect()

    def _reconnect(self):
        """reconnects to salesforce api
        """        
        c = credentials
        self.sf = Salesforce(username=c['USERNAME'], password=c['PASSWORD'], security_token=c['SECURITY_TOKEN'])

    def query(self, q):
        """Submits a query to salesforce SOQL api

        Args:
            q (str): SOQL query

        Returns:
            dict: json response from SFDC api
        """
        
        results = self.sf.query(q)
        return results

    def update_opportunity(self, id_, data):
        self.sf.Opportunity.update(id_, data)

def sync_opp(opp_id):

    q = """
        SELECT
        id,
        name,
        Display_In_SkyManager__c,
        project_name__c,
        portfolio_name__c,
        probability,
        accountid,
        partneraccountid,
        syncedquoteid,
        Synced_Quote__c,
        site__c,
        Current_Revenue__c,
        Current_Cost__c,
        CreatedDate,
        OS_GM__c,
        Total_Booking_GM__c,
        Total_Booking_Revenue__c,
        Ops_Status__c,
        System_Total_kW_AC__c,
        System_Total_kWp__c,
        Opportunity_Storage_kWh__c,
        Opportunity_Storage_kW__c,
        OS_Customer__c,
        Wrike_Folder_ID__c,
        Sharepoint_Folder_ID__c,
        Box_Folder_ID__c,
        Date_Cancelled__c,
        Mounting_Type_1_Mfr__c,
        Mounting_Type_1_Model__c,
        Mounting_Type_1_Tilt__c,
        Mounting_Type_1_Azimuth__c,
        Mounting_Type_1_System_Type__c,
        Mounting_Type_2_Mfr__c,
        Mounting_Type_2_Model__c,
        Mounting_Type_2_Tilt__c,
        Mounting_Type_2_Azimuth__c,
        Mounting_Type_2_System_Type__c
        FROM
        opportunity
        WHERE
        Id='{}'
        """.format(opp_id)

    sfdc_data = SFDCAPI().query(q)
    data = json.loads(json.dumps(sfdc_data['records']), parse_float=Decimal)
    db = DatabaseConnection(region_name='us-east-1')
    current_opps = db.query('sfdc_opportunities', Key('Id').eq(opp_id))
    for cr in current_opps:
        k = {'Id':cr['Id'],'AccountId':cr['AccountId']}
        db.delete_data('sfdc_opportunities', k)
    for d in data:
        if d['Wrike_Folder_ID__c'] == None:
            d['Wrike_Folder_ID__c'] = "placeholder"
    r = db.put_data('sfdc_opportunities', data)
    return data

def sync_quote(opp_id):
    q = """
        SELECT
        OpportunityId,
        Name,
        Active__c,
        Quote_Scope__c
        FROM
        Quote
        WHERE
        OpportunityId='{}'
        """.format(opp_id)

    sfdc_data = SFDCAPI().query(q)
    data = json.loads(json.dumps(sfdc_data['records']), parse_float=Decimal)
    db = DatabaseConnection(region_name='us-east-1')
    current_quotes = db.query('sfdc_quotes', Key('Id').eq(opp_id))
    for cr in current_quotes:
        k = {'OpportunityId':cr['OpportunityId'],'Name':cr['Name']}
        db.delete_data('sfdc_quotes', k)
    r = db.put_data('sfdc_quotes', data)
    return data

def sync_contact(email):

    q = """
        SELECT
        Name,
        Email,
        Phone,
        Id,
        AccountId,
        Title
        FROM
        Contact
        WHERE
        Email='{}'
        """.format(email)

    sfdc_data = SFDCAPI().query(q)
    data = json.loads(json.dumps(sfdc_data['records']), parse_float=Decimal)
    print(data)
    db = DatabaseConnection(region_name='us-east-1')
    current_contacts = db.query('sfdc_contacts', Key('Email').eq(email))
    print('got current contacts ', current_contacts)
    for cr in current_contacts:
        k = {'Email':cr['Email']}
        db.delete_data('sfdc_contacts', k)
    r = db.put_data('sfdc_contacts', data)
    return data

def sync_account(account_id):
    q = """
        SELECT
        Id,
        Name
        FROM
        Account
        WHERE
        Id='{}'
        """.format(account_id)

    sfdc_data = SFDCAPI().query(q)
    data = json.loads(json.dumps(sfdc_data['records']), parse_float=Decimal)
    db = DatabaseConnection(region_name='us-east-1')
    current_accounts = db.query('sfdc_accounts', Key('Id').eq(account_id))
    for cr in current_accounts:
        k = {'Id':cr['Id'],'Name':cr['Name']}
        db.delete_data('sfdc_accounts', k)
    r = db.put_data('sfdc_accounts', data)
    return data

def sync_site(site_id):
    q = """
        SELECT
        Id,
        name,
        account__c,
        utility__c,
        street_address__c, 
        city__c, 
        state__c, 
        zip__c
        FROM
        Site__c
        WHERE
        Id='{}'
        """.format(site_id)

    sfdc_data = SFDCAPI().query(q)
    data = json.loads(json.dumps(sfdc_data['records']), parse_float=Decimal)
    db = DatabaseConnection(region_name='us-east-1')
    current_sites = db.query('sfdc_sites', Key('Id').eq(site_id))
    for cr in current_sites:
        k = {'Id':cr['Id']}
        db.delete_data('sfdc_sites', k)
    r = db.put_data('sfdc_sites', data)
    return data

def sync_all_opps():
    q = """
        SELECT
        id,
        name,
        Display_In_SkyManager__c,
        project_name__c,
        probability,
        portfolio_name__c,
        accountid,
        partneraccountid,
        syncedquoteid,
        Synced_Quote__c,
        site__c,
        CreatedDate,
        Current_Revenue__c,
        Current_Cost__c,
        OS_GM__c,
        Ops_Status__c,
        System_Total_kW_AC__c,
        System_Total_kWp__c,
        Opportunity_Storage_kWh__c,
        Opportunity_Storage_kW__c,
        OS_Customer__c,
        Wrike_Folder_ID__c,
        Sharepoint_Folder_ID__c,
        Box_Folder_ID__c,
        Date_Cancelled__c,
        Mounting_Type_1_Mfr__c,
        Mounting_Type_1_Model__c,
        Mounting_Type_1_Tilt__c,
        Mounting_Type_1_Azimuth__c,
        Mounting_Type_1_System_Type__c,
        Mounting_Type_2_Mfr__c,
        Mounting_Type_2_Model__c,
        Mounting_Type_2_Tilt__c,
        Mounting_Type_2_Azimuth__c,
        Mounting_Type_2_System_Type__c
        FROM
        opportunity
        WHERE
        Ops_Status__c IN ('Design and Permit', 'Construction', 'Development') OR Display_In_Skymanager__c=true
        """

    sfdc_data = SFDCAPI().query(q)
    data = json.loads(json.dumps(sfdc_data['records']), parse_float=Decimal)
    db = DatabaseConnection(region_name='us-east-1')
    for d in data:
        if d['Wrike_Folder_ID__c'] == None:
            d['Wrike_Folder_ID__c'] = "placeholder"
        try:

            current_opps = db.query('sfdc_opportunities', Key('Id').eq(d['Id']))
            for cr in current_opps:
                k = {'Id':cr['Id'],'AccountId':cr['AccountId']}
                db.delete_data('sfdc_opportunities', k)
        except Exception as e:
            print('error occured: ', e)
            continue
    r = db.put_data('sfdc_opportunities', data)
    return data

def update_contact_roles(opp_id):
    if type(opp_id) == str:
        
        q = """
            SELECT
            OpportunityId,
            Contact.Name,
            Contact.Email, 
            Contact.Phone, 
            Contact.Title,
            contactid,
            role,
            isprimary
            FROM
            OpportunityContactRole
            WHERE
            OpportunityId='{}'
            """.format(opp_id)

    elif type(opp_id) == list:

        for o in range(len(opp_id)):
            opp_id[o] = "'" + opp_id[o] + "'"

        q = """
            SELECT
            OpportunityId,
            Contact.Name,
            Contact.Email, 
            Contact.Phone, 
            Contact.Title,
            contactid,
            role,
            isprimary
            FROM
            OpportunityContactRole
            WHERE
            OpportunityId IN ({})
            """.format(",".join(opp_id))

    sfdc_data = SFDCAPI().query(q)
    db = DatabaseConnection(region_name='us-east-1')

    if type(opp_id) == str:
        current_roles = db.query('opp_contact_roles_reverse', Key('OpportunityId').eq(opp_id))

    elif type(opp_id) == list:
        current_roles = []
        for o in opp_id:
            current_roles.extend(db.query('opp_contact_roles_reverse', Key('OpportunityId').eq(o)))

    data = prep_data(sfdc_data['records'])

    current_entries = [i['ContactId'] + "+" +  i['OpportunityId'] for i in current_roles]
    new_entries = [i['ContactId'] + "+" +  i['OpportunityId'] for i in data]
    entries_to_wipe = list(set(current_entries) - set(new_entries))

    for i in entries_to_wipe:
        c, o = i.split('+')
        if len(db.query("sfdc_opp_contact_roles", Key('ContactId').eq(c))) > 0:
            db.delete_data("sfdc_opp_contact_roles", {'ContactId':c, 'OpportunityId':o})

    for i in entries_to_wipe:
        c, o = i.split('+')
        if len(db.query("opp_contact_roles_reverse", Key('OpportunityId').eq(o))) > 0:
            db.delete_data("opp_contact_roles_reverse", {'ContactId':c, 'OpportunityId':o})

    db.put_data('sfdc_opp_contact_roles', data)
    db.put_data('opp_contact_roles_reverse', data)
    return sfdc_data

def update_account_roles(opp_id):
    if type(opp_id) == str:
        q = """
            SELECT
            opportunity__c,
            account__c,
            account_role__c,
            name
            FROM
            Opportunity_Account_Role__c
            WHERE
            opportunity__c='{}'
            """.format(opp_id)

    elif type(opp_id) == list:
        for o in range(len(opp_id)):
            opp_id[o] = "'" + opp_id[o] + "'"

        q = """
            SELECT
            opportunity__c,
            account__c,
            account_role__c,
            name
            FROM
            Opportunity_Account_Role__c
            WHERE
            opportunity__c IN ({})
            """.format(",".join(opp_id))

    sfdc_data = SFDCAPI().query(q)

    if len(sfdc_data['records']) == 0:
        return

    db = DatabaseConnection(region_name='us-east-1')

    if type(opp_id) == str:
        current_roles = db.query('sfdc_opp_account_roles', Key('Opportunity__c').eq(opp_id))

    if type(opp_id) == list:
        current_roles = []
        for o in opp_id:
            current_roles.extend(db.query('sfdc_opp_account_roles', Key('Opportunity__c').eq(o)))


    for cr in current_roles:
        k = {'Opportunity__c': cr['Opportunity__c'], 'Account_Role__c': cr['Account_Role__c']}
        db.delete_data('sfdc_opp_account_roles', k)
    data = prep_data(sfdc_data['records'])
    r = db.put_data('sfdc_opp_account_roles', data)
    return sfdc_data

def sync_all_sfdc_data():
    opps = sync_all_opps()
    for o in opps:
        sid = o.get('Site__c')
        acc_id = o.get('AccountId')
        try:
            update_account_roles(o['Id'])
            update_contact_roles(o['Id'])
            if sid:
                sync_site(sid)
            if acc_id:
                sync_account(acc_id)
        except Exception as e:
            print(e)
            continue
    db = DatabaseConnection(region_name='us-east-1')
    users = db.scan('users')
    for u in users:
        try:
            if u.get('Email'):
                sync_contact(u.get('Email'))
        except Exception as e:
            print(e)
            continue
    
if __name__=="__main__":
    sync_contact('denise.shurtleff@cambriawines.com')