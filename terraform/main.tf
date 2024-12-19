terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {}

resource "docker_container" "airflow" {
  name  = "airflow-container"
  image = "apache/airflow:2.7.1"
  
  ports {
    internal = 8080
    external = 8080
  }

  volumes {
    container_path = "/opt/airflow/dags"
    host_path      = "${path.cwd}/dags"
  }
} 