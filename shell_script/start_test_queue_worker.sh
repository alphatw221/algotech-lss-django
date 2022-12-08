#!/bin/bash

poetry run rq worker test_queue -u redis://:lss_dev@35.194.149.116:6379
