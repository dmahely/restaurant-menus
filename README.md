# Restaurant Menus

_This project is part of the curriculum of Udacity’s Full Stack Web Developer Nanodegree. It's not a required project._ This project uses Python and SQLAlchemy to create a database of restaurant menus and a simple CRUD web application.

# Before Running the Program
You must have Python installed on your machine. Check your Python version by running `python -V`.

# Running the Program
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
2. Install [Vagrant](https://www.vagrantup.com)
3. Install [Git](https://git-scm.com/downloads)
4. Download [this repository](https://github.com/udacity/fullstack-nanodegree-vm). Click on the green `Clone or download` button, then click on `Download ZIP`. There's no need to log in or make a GitHub account. This will give you a directory named `fullstack`. You will most likely find it in your `Downloads` folder.
5. Navigate to the `vagrant` directory inside of `fullstack`.
6. Open the terminal app on your Mac or the command prompt on your Windows machine and run `vagrant up`. This may take some time.
7. Run `vagrant ssh`.
8. Run `cd /vagrant`. This will take you to the shared folder between your VM and host machine.
9. Download my repository (dmahely/restaurant-menus) and place the files in `fullstack/vagrant/`.
10. Run `python webserver.py`.
11. Go to [http://localhost:9999/restaurants](http://localhost:9999/restaurants) in your browser.

# After Running the Program
You should see a plain HTML page that has the names of restaurants. You can edit, delete, and add restaurants.

# Acknowledgements
I wrote most of the code, except for the database population code, which was supplied to me by Udacity.
