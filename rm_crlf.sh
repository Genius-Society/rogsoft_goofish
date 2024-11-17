#!/bin/bash

find "./bilimon" -type f -name "*.sh" -exec sed -i 's/\r$//' {} \;