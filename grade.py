#!/usr/bin/env python3
import os
import signal
from subprocess import Popen, PIPE

import subprocess
import enum
import collections
import time
import sys


class TestResultType(enum.Enum):
    TRANSFER_ERROR = 0
    TRANSFER_TIMEOUT = 1
    SLOW_TRANSFER = 2
    FAST_TRANSFER = 3

TestArguments = collections.namedtuple('TestArguments', "file loss delay buffer")
TestCase = collections.namedtuple("TestCase", "args secs")
TestResult = collections.namedtuple("TestResult", "type duration")

def run_test_case(case: TestCase) -> TestResult:
    full_credit_time = case.secs * 1.5
    half_credit_time = case.secs * 2.0
    start_time = time.time()

    test_args = ["python3", "tester.py", "--file", case.args.file, "--loss",
                 case.args.loss, "--buffer", case.args.buffer,
                 "--delay", case.args.delay]

    try:
        subprocess.run(test_args, timeout=half_credit_time, check=True,
                       stdout=subprocess.PIPE)
    except subprocess.TimeoutExpired:
        return TestResult(TestResultType.TRANSFER_TIMEOUT, None)
    except subprocess.CalledProcessError:
        return TestResult(TestResultType.TRANSFER_ERROR, None)

    end_time = time.time()
    duration = end_time - start_time
    if duration <= full_credit_time:
        result_type = TestResultType.FAST_TRANSFER
    else:
        result_type = TestResultType.SLOW_TRANSFER
    return TestResult(result_type, duration)


TEST_CASES = [
    TestCase(TestArguments("grading_data/test-1.bin", "0.15", "0.05", "10"), 9),
    TestCase(TestArguments("grading_data/test-1.bin", "0.5", "0.05", "10"), 15),
    TestCase(TestArguments("grading_data/test-2.bin", "0.15", "0.01", "20"), 12),
    TestCase(TestArguments("grading_data/test-3.bin", "0.01", "0.01", "50"), 16),
    TestCase(TestArguments("grading_data/test-3.bin", "0.05", "0.01", "50"), 40),
    TestCase(TestArguments("grading_data/test-4.bin", "0.02", "0.01", "50"), 50),
    TestCase(TestArguments("grading_data/test-4.bin", "0.05", "0.02", "50"), 50),
    TestCase(TestArguments("grading_data/test-5.bin", "0.05", "0.01", "50"), 70),
    TestCase(TestArguments("grading_data/test-6.bin", "0.02", "0.01", "50"), 80),
    TestCase(TestArguments("grading_data/test-6.bin", "0.03", "0.01", "50"), 80),

    # TestCase(TestArguments("grading_data/test-1.bin", "0", ".5", "10"), 9),
    # TestCase(TestArguments("grading_data/test-1.bin", "0", ".5", "10"), 15),
    # TestCase(TestArguments("grading_data/test-2.bin", "0", "0.1", "20"), 12),
    # TestCase(TestArguments("grading_data/test-3.bin", "0", ".01", "30"), 16),
    # TestCase(TestArguments("grading_data/test-3.bin", "0", ".01", "30"), 25),
    # TestCase(TestArguments("grading_data/test-4.bin", "0", ".1", "40"), 9),
    # TestCase(TestArguments("grading_data/test-4.bin", "0", ".2", "40"), 15),
    # TestCase(TestArguments("grading_data/test-5.bin", "0", ".01", "500"), 45),
    # TestCase(TestArguments("grading_data/test-6.bin", "0", ".02", "600"), 52),
    # TestCase(TestArguments("grading_data/test-6.bin", "0", ".01", "300"), 60),



    # TestCase(TestArguments("grading_data/test-1.bin", "0", ".5", "10"), 7),
    # TestCase(TestArguments("grading_data/test-2.bin", "0", "0.1", "20"), 5),
    # TestCase(TestArguments("grading_data/test-3.bin", "0", ".01", "30"), 6),
    # TestCase(TestArguments("grading_data/test-4.bin", "0.1", ".1", "40"), 6),
    # TestCase(TestArguments("grading_data/test-5.bin", "0.1", ".01", "50"), 32),
    # TestCase(TestArguments("grading_data/test-6.bin", "0", ".01", "60"), 12),
]

TOTAL_SCORE = 0
SUC_CASE = 0
MAX_SCORE = 20
MAX_CASE = 10
TOTAL_TIME = 0
TIME_LIST = []
for CASE_NUM, A_CASE in enumerate(TEST_CASES):
    FULL_CREDIT_TIME = A_CASE.secs * 1.5
    HALF_CREDIT_TIME = FULL_CREDIT_TIME * 1.5
    print("Test case: {}".format(CASE_NUM + 1))
    print("  - File: {}".format(A_CASE.args.file))
    print("  - Loss: {}%".format(100 * float(A_CASE.args.loss)))
    print("  - Delay: {} seconds".format(A_CASE.args.delay))
    print("  - Buffer: {} packets".format(A_CASE.args.buffer))
    print("  - Full credit: {} secs".format(round(FULL_CREDIT_TIME)))
    print("  - Half credit: {} secs".format(round(HALF_CREDIT_TIME)))
    print("----------")

    port = 9999
    process = Popen(["lsof", "-i", ":{0}".format(port)], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    for process in str(stdout.decode("utf-8")).split("\n")[1:]:
        data = [x for x in process.split(" ") if x != '']
        if (len(data) <= 1):
            continue

        os.kill(int(data[1]), signal.SIGKILL)


    CASE_RESULT = run_test_case(A_CASE)
    TIME_LIST.append(CASE_RESULT.duration)
    if CASE_RESULT.duration:
        TOTAL_TIME += CASE_RESULT.duration
    if CASE_RESULT.type == TestResultType.TRANSFER_ERROR:
        print("  ! 0 points, file was transferred incorrectly")
    elif CASE_RESULT.type == TestResultType.TRANSFER_TIMEOUT:
        print("  ! 0 points, file not transferred in {} secs".format(
            round(HALF_CREDIT_TIME)))
    elif CASE_RESULT.type == TestResultType.SLOW_TRANSFER:
        print("  ~ 1 point, transferred in {} secs".format(round(CASE_RESULT.duration)))
        TOTAL_SCORE += 1
        SUC_CASE += 1
    elif CASE_RESULT.type == TestResultType.FAST_TRANSFER:
        print("  * 2 points, transferred in {} secs".format(round(CASE_RESULT.duration)))
        TOTAL_SCORE += 1
        SUC_CASE += 1
    print("")

print("==========")
print("Success Case: {} / {}".format(SUC_CASE, MAX_CASE))

print("Time: {} ".format(TIME_LIST))
print("Total Time: {} ".format(TOTAL_TIME))
sys.exit(0 if TOTAL_SCORE == MAX_SCORE else 1)
