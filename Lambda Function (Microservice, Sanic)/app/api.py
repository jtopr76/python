
from sanic.views import HTTPMethodView
from app.common import jwt_user, success_res, get_one_data, get_all_data

class Dashboard(HTTPMethodView):
  
  @jwt_user
  async def get(self, request, user):
    
    experiment_count_query = "SELECT count(*) FROM experiment WHERE e_account_id={u_account_id}".format(u_account_id=user["u_account_id"])
    project_count_query = "SELECT count(*) FROM project WHERE p_account_id={u_account_id}".format(u_account_id=user["u_account_id"])
    dataset_count_query = "SELECT count(*) FROM dataset WHERE d_account_id={u_account_id}".format(u_account_id=user["u_account_id"])
    
    experiment_latest_records = "SELECT * FROM experiment WHERE e_account_id={u_account_id} ORDER BY e_id DESC limit 10".format(u_account_id=user["u_account_id"])
    project_latest_records = "SELECT * FROM project WHERE p_account_id={u_account_id} ORDER BY p_id DESC limit 10".format(u_account_id=user["u_account_id"])
    dataset_latest_records = "SELECT * FROM dataset WHERE d_account_id={u_account_id} ORDER BY d_id DESC limit 10".format(u_account_id=user["u_account_id"])
    
    e_count_query = await get_one_data(experiment_count_query)
    p_count_query = await get_one_data(project_count_query)
    d_count_query = await get_one_data(dataset_count_query)

    e_latest_records = await get_all_data(experiment_latest_records)
    p_latest_records = await get_all_data(project_latest_records)
    d_latest_records = await get_all_data(dataset_latest_records)
    
    user_queries={
      "experiment_count":e_count_query["count(*)"], 
      "project_count":p_count_query["count(*)"], 
      "dataset_count":d_count_query["count(*)"], 
      "experiment_latest_records":e_latest_records,
      "project_latest_records":p_latest_records,
      "dataset_latest_records":d_latest_records
    }
    
    return success_res({"data":user_queries})

class AccountReporting(HTTPMethodView):
  
  async def get(self, request):
    account_id = None
    user = None
    if request.args.get("account_id"):
      account_id = request.args.get("account_id")
      user = await get_one_data("SELECT * FROM users WHERE u_account_id={u_account_id} ORDER BY u_last_login DESC".format(u_account_id=account_id))

    elif request.args.get("user_id"):
      user_id = request.args.get("user_id")
      user = await get_one_data("SELECT * FROM users WHERE u_id={user_id}".format(user_id=user_id))
      account_id = user['u_account_id']

    number_of_synthetic_datasets_generated_query = "SELECT count(*) FROM experiment WHERE e_account_id={account_id}".format(account_id=account_id)
    number_of_synthetic_datasets_generated = await get_one_data(number_of_synthetic_datasets_generated_query)

    number_of_errors_query = "SELECT count(*) FROM experiment WHERE e_account_id={account_id} AND e_status = 'error'".format(account_id=account_id)
    number_of_errors = await get_one_data(number_of_errors_query)

    last_experiment_query = "SELECT * FROM experiment WHERE e_account_id={account_id} ORDER BY e_id DESC".format(account_id=account_id)
    last_experiment = await get_one_data(last_experiment_query)

    response_data = {
      "last_login_timestamp": user["u_last_login"],
      "number_of_synthetic_datasets_generated": number_of_synthetic_datasets_generated["count(*)"],
      "number_of_errors": number_of_errors["count(*)"],
      "last_timestamp_of_synthetic_dataset": last_experiment["e_created"]
    }
    return success_res({"data":response_data})