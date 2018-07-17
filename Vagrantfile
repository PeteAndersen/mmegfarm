# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<-SCRIPT
#!/usr/bin/env bash
# Install packages
echo "Installing software packages..."
sudo apt-get -qq update
sudo apt-get -qq upgrade -y
sudo apt-get -qq install -y postgresql-10 postgresql-contrib-10 redis-server git make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev

# Postgresql setup
# Allow listening on all interfaces
echo "Setting up postgresql database and roles..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "/etc/postgresql/10/main/postgresql.conf"
# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" | sudo tee --append /etc/postgresql/10/main/pg_hba.conf > /dev/null

sudo service postgresql restart

# Set up database and user
sudo -u postgres psql --command="CREATE DATABASE mmegfarm_dev WITH ENCODING 'UTF8' LC_CTYPE 'en_US.UTF-8' LC_COLLATE 'en_US.UTF8' TEMPLATE=template0;"
sudo -u postgres psql --command="CREATE USER mmeg_user WITH PASSWORD 'intentionallyweak';"
sudo -u postgres psql --command="GRANT ALL PRIVILEGES ON DATABASE mmegfarm_dev TO mmeg_user;"

# Install pyenv + friends
curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
echo 'export PATH="/home/vagrant/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

# Repeat above commands because 'source ~/.bashrc' doesn't work here
export PATH="/home/vagrant/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install python + init virtualenv
pyenv install 3.7.0
pyenv virtualenv 3.7.0 mmegfarm-3.7.0
pyenv activate mmegfarm-3.7.0

echo "Setting up python environment..."
pip install -qq -r /vagrant/requirements_dev.txt
SCRIPT

Vagrant.configure("2") do |config|
    config.vm.box = "bento/ubuntu-18.04"
    config.vm.provider "virtualbox" do |v|
        v.memory = 2048
        v.cpus = 2
    end

    config.vm.network "private_network", ip: "10.243.243.10"
    config.vm.network "forwarded_port", guest: 5432, host: 5432  # postgres
    config.vm.network "forwarded_port", guest: 6379, host: 6379  # redis
    config.vm.network "forwarded_port", guest: 8000, host: 8000  # manage.py runserver using remote python interpreter
    config.vm.provision "shell", privileged: false, inline: $script
end
