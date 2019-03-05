# stop all python containers
import docker

def main():
	client = docker.from_env()
	containers = client.containers.list()

	for c in containers:
		if c.name == 'bitcoind-backend' or c.name.startswith('ln_node'):
			c.stop()

if __name__ == "__main__":
	main()