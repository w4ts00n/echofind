## ECHOFIND

Echofind is a web application created in django. Its main purpose is to allow users to search through certain type of videos, like interviews or short clips, making it easy to revisit particular content with specific phrases. 
The main technology which is responsible for creating transcriptions is [whisper](https://github.com/openai/whisper), a general-purpose speech recognition model.

## Technology choices
Besides [whisper](https://github.com/openai/whisper), I used a lot of different technologies such as Firebase, AWS and Elasticsearch,  and while the choice could have been limited to a single provider, I decided to explore multiple solutions to try out different approaches for fun and to improve my skills.

One of the most important choices was to use **Hashicorp Vault**. It made managing and storing secrets incredibly easy, significantly improving the overall workflow.

## Setup
Since whisper requires the command-line tool [ffmpeg](https://ffmpeg.org), you need to have it installed on your system. You can install it from most package managers:

```py
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```


Before running the application, make sure to create a `.env` file with the following environment variables:
```env
VAULT_TOKEN=hvs.123456789abcdef # Token for authentication with Hashicorp Vault
VAULT_URL=https://your-project-cluster-public-vault.hashicorp.cloud:8200 # URL of the Hashicorp Vault instance
VAULT_PATH=secrets/myapp # Path to secrets in Vault
VAULT_NAMESPACE=my-namespace # Namespace in Vault
PGUSER=my-user # Username for Postgres database
PGPASSWORD=mypassword # Password for Postgres database
PGHOST=PGHOST=mydbinstance.us-west-2.rds.amazonaws.com # Host of the Postgres database
PGDATABASE=mydatabase # Name of Postgres database
```

To quickly test my app, you can try [neon.tech](https://neon.tech), which provides instant credentials for a free Postgres instance. 
