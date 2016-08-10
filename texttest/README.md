Integration tests for GO CD Dashboard
=====================================

Before you can run these tests you will need to install [TextTest](http://texttest.org). In your personal config file $HOME/.texttest/config add a line like this:

[checkout_location]
    gocddash:${HOME}/workspace/gocddash
[end]

note this should be a valid path on your machine, and point to the location of this respository.

Install other prerequisites:

    sudo pip3 install docker-py
    sudo apt-get install lynx

Then start TextTest in this working directory with this command:

    texttest -a dash -d .

This should open a graphical test browser that you can use to manage your test cases, and trigger test runs.

