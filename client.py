import base64
import requests
import subprocess
import sys

# Get participant ID from command line.
if len(sys.argv) <= 1:
    print(
        "Error: No participant ID specified. Please specify participant ID as first argument.",
        file=sys.stderr,
    )
    sys.exit(1)
participant_id = sys.argv[1]
sys.argv = sys.argv[1:]

# Get participant ID from command line.
if len(sys.argv) <= 1:
    print(
        "Error: No server address specified. Please specify server address as second argument.",
        file=sys.stderr,
    )
    sys.exit(1)
server_address = sys.argv[1]
sys.argv = sys.argv[1:]

# Request a batch to prove.
print("Requesting batch.")
response = requests.get("{0}/get_batch/?participant_id={1}".format(server_address, participant_id))

# Exit if batch request failed.
if response.status_code != 200:
    print(
        "Batch request failed (HTTP status {0}): {1}".format(response.status_code, response.content.decode()),
        file=sys.stderr,
    )
    exit(response.status_code)

print("Received response:")
response_data = response.json()
print(response_data)

# We need to remember the request ID returned by the server to use it when submitting the proof.
request_id = response_data["request_id"]

# Compute the proof. This code is a stub simply reading pre-computed proof data from a file.
result = subprocess.run(
    ['./compute-proof-stub.sh', server_address+"/"+response_data["batch_file"]],
    capture_output=True,
)
if result.returncode != 0:
    print(
        "Proof computation failed, writing the following to stderr:\n{0}".format(result.stderr.decode()),
        file=sys.stderr,
    )
    exit(result.returncode)
proof = result.stdout

# Submit proof and metadata.
# This is an example to illustrate the format of the response.
# The values bear no meaning at all.
print("Submitting proof.")
submission_response = requests.post(
    "{0}/submit_proof/?participant_id={1}".format(server_address, participant_id),
    json={
        "request_id": request_id,
        "proof_data": base64.b64encode(proof).decode("utf-8"),  # Base64-encoded proof data
        "proving_time": 7200000,  # 2 hours
        "cost": 100000,           # 100.00 USD
        "price": 10100,           # 101.00 USD
        "acceleration": "GPU",    # GPU / FPGA / ASIC / ... If no acceleration was used (only CPU was used) use NONE.
        "deployment_version": 2,
    },
)
print("Received response:")
print(submission_response.content.decode("utf-8"))
