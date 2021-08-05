from diagrams import Diagram, Cluster
from diagrams.elastic.elasticsearch import Elasticsearch
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL, ClickHouse, MongoDB
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx
from diagrams.onprem.queue import RabbitMQ

with Diagram():
    gateway = Nginx("Gateway")
    etl = Server('ETL')

    with Cluster("UGC service"):
        ugc_service = Server('Fast API')
        ugc_click_house_db = ClickHouse('UGC DB')
        ugc_mongo_db = MongoDB('Mongo DB')

        ugc_service >> ugc_click_house_db
        ugc_service >> ugc_mongo_db

    with Cluster("Movies search microservice"):
        search_service = Server('Fast API')
        search_elastic_db = Elasticsearch('Elasticsearch')
        search_redis = Redis("search_redis")
        search_service >> search_elastic_db
        search_service >> search_redis

    with Cluster("Admin microservice"):
        admin_service = Server('Django')
        admin_db = PostgreSQL('admin_db')
        admin_service >> admin_db

    with Cluster("Auth microservice"):
        auth_service = Server('Flask')
        db_auth = PostgreSQL("auth_users_db")
        redis_auth = Redis("auth_redis")
        auth_service >> redis_auth
        auth_service >> db_auth

    with Cluster("Cinema together microservice"):
        cinema_together_redis = Redis("cinema_together_redis")
        cinema_together_service = Server('Fast API')
        websocket = Server('Fast API websocket')
        db_cinema_together = PostgreSQL("cinema_together_db")

        cinema_together_service >> db_cinema_together
        cinema_together_service >> cinema_together_redis
        websocket >> db_cinema_together
        websocket >> cinema_together_redis

    with Cluster("Notification service"):
        notification_api_service = Server('Fast API')

        notification_admin_service = Server('Django admin')
        notification_admin_queue = RabbitMQ('Admin messages Queue')
        notification_admin_worker = RabbitMQ('Admin messages Queue')

        notification_worker = Server('Python')
        notification_queue = RabbitMQ('messages Queue')

        notification_api_service >> notification_queue
        notification_queue >> notification_worker

        notification_admin_service >> notification_admin_queue
        notification_admin_queue >> notification_admin_worker
        notification_admin_worker >> notification_api_service

    gateway >> auth_service
    gateway >> cinema_together_service
    gateway >> search_service

    admin_db >> etl >> search_service

    auth_service >> notification_api_service
    cinema_together_service >> notification_api_service
    admin_service >> notification_api_service
    search_service >> notification_api_service

    auth_service >> ugc_service
    cinema_together_service >> ugc_service
    admin_service >> ugc_service
    search_service >> ugc_service
