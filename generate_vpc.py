import pandas as pd
import random
from datetime import datetime, timedelta
import sqlite3

# Function to generate synthetic VPC log data


def generate_vpc_logs(num_entries):
    logs = []
    start_time = datetime.now() - timedelta(days=1)
    for _ in range(num_entries):
        log = {
            "version": random.choice([2, 3, 4]),
            "account_id": random.randint(100000000000, 999999999999),
            "interface_id": f"eni-{random.randint(10000000, 99999999)}",
            "srcaddr": f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
            "dstaddr": f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
            "srcport": random.randint(1024, 65535),
            "dstport": random.randint(1024, 65535),
            "protocol": random.choice([6, 17, 1]),  # TCP, UDP, ICMP
            "packets": random.randint(1, 1000),
            "bytes": random.randint(100, 1000000),
            "start": (start_time + timedelta(seconds=random.randint(0, 86400))).strftime('%Y-%m-%dT%H:%M:%S'),
            "end": (start_time + timedelta(seconds=random.randint(0, 86400))).strftime('%Y-%m-%dT%H:%M:%S'),
            "action": random.choice(["ACCEPT", "REJECT"]),
            "log_status": random.choice(["OK", "NODATA", "SKIP"])
        }
        logs.append(log)
    return logs

# Generate 200 synthetic VPC log entries
vpc_logs = generate_vpc_logs(1000)

# Convert to DataFrame
vpc_logs_df = pd.DataFrame(vpc_logs)



# Save the DataFrame to a SQLite database file
db_filename = "synthetic_vpc_logs.db"
vpc_logs_df.to_sql('vpc_logs', sqlite3.connect(db_filename), if_exists='replace', index=False)

print(f"Database file saved as: {db_filename}")
