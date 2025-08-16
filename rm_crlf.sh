#!/bin/bash

find "./" -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;
