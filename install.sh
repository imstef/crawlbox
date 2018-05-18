#!/bin/bash
# Add the crawlbox alias in .bashrc
touch ~/.bash_aliases
echo 'alias cbox="/var/www/crawlbox/main.py"' >> ~/.bash_aliases
echo 'Alias cbox successfully created'
source ~/.bashrc
echo 'Bashrc profile reloaded'
