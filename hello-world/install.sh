#!/bin/bash

# Create symlink to make hello-world executable from command line
ln -sf /usr/local/meth/packages/hello-world/hello-world.py /usr/local/bin/hello-world
chmod +x /usr/local/meth/packages/hello-world/hello-world.py
chmod +x /usr/local/bin/hello-world

echo "hello-world installed successfully!"
echo "Run 'hello-world' to test it"
