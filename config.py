Configration_Type= "Local"


if Configration_Type == "Local":
    user = "postgres"
    password = "first"
    host = "localhost"
    port = "5432"
    schema_name = "loreal"
    database = "postgres"
    redis_password="JUSTWIN12"
    redis_host="localhost"
    redis_port="6379"
    local_path = "/mnt/c/etl/Etl_version0.1"
    bucket = "tmp-etl"
    # life_cycle_bucket = "processed-loreal-etl"
    

# elif Configration_Type == "Server":
#     user = "postgres"
#     password = "MaishaKanisha1819$"
#     host = "tpnretail.can7hv0elab6.us-east-2.rds.amazonaws.com"
#     port = "5432"
#     schema_name = "loreal"
#     database = "loreal"
#     redis_password="JUSTWIN12"
#     redis_host="localhost"
#     redis_port="6379"
#     local_path = "/mnt/c/loreal/LorealEtl"
#     bucket = "loreal-etl"
#     life_cycle_bucket = "processed-loreal-etl"