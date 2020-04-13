#!/bin/bash

# assuming the code is already set to break_everything mode
npm run test:lerna > fails.out 2>&1
cat fails.out | grep "FAIL " > fails.csv
rm fails.out
python get_failing_tests.py
