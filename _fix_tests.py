"""Fix test_exams_auth.py to skip integration tests when server not running."""
import re

path = r"c:\dvdcoin\tests\test_exams_auth.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add skipif to all test classes that use the live server
skip_decorator = '''@pytest.mark.skipif(
    not os.environ.get("EXAMS_SERVER_RUNNING"),
    reason="Integration test requires exams server on localhost:8001"
)
'''

# Replace all @pytest.mark.unit\nclass TestExams... patterns
classes_to_skip = [
    "TestExamsLogin",
    "TestExamsMe", 
    "TestExamsSubscription",
    "TestExamsStats",
    "TestExamsAvailable",
    "TestExamsHealth",
    "TestExamsVerification",
    "TestExamsForgotPassword",
]

for cls in classes_to_skip:
    old = f"@pytest.mark.unit\nclass {cls}:"
    new = f"@pytest.mark.unit\n{skip_decorator}class {cls}:"
    if old in content:
        content = content.replace(old, new)
        print(f"  Fixed {cls}")
    else:
        print(f"  Already fixed or not found: {cls}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done!")
