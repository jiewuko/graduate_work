from diagrams import Diagram, Cluster
from diagrams.elastic.elasticsearch import Elasticsearch
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx

with Diagram():
    gateway = Nginx("Gateway")
    etl = Server('ETL')

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

    gateway >> auth_service
    gateway >> cinema_together_service
    gateway >> search_service

    admin_db >> etl >> search_service
