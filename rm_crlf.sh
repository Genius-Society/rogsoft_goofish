#!/bin/bash

find "./wemediamon" -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;