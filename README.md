# Data Collection for Prover Market Design

This repository contains the specification of the API and an example RPC client code for collecting data from provers
participating in the experiment related to the Auction Design for Prover Markets project.
We implement the experiment with a simple RPC server that publishes transaction batches and receives the
corresponding proofs from participants. The server records the responses in a database for later analysis.

## Basic Workflow

We (Matter Labs) run the RPC server and the participants run one client each. We assign a unique ID to each participant
that they will use as a parameter in all API calls. For each participant, the server makes transaction batches available
(one at a time) for which the participant computes validity proofs. Once the participant (using their client) has
submitted a validity proof for a batch, the server makes the next batch available.

Concretely, the workflow is the following:

1. Server publishes a transaction batch.
2. Client obtains the batch URL using a `get_batch` RPC.
3. Client downloads the batch data from the obtained URL.
4. Client computes the validity proof for the downloaded batch.
5. Client submits the computed proof with associated metadata to the server using a `submit_proof` RPC.
6. Server verifies the received proof (and discards it if invalid).
7. Server inserts the metadata into its local database.

## API

The server provides two endpoints, one for each RPC:

### `get_batch`

#### Request
The client invokes the `get_batch` RPC by making a HTTP GET request to
```
http://<server-address>:<server-port>/get_batch/?participant_id=<participant-id>
```
where &lt;participant-id> is the ID assigned to the participant making the request.
The `participant-id` is an identifier that each participant receives prior to starting the experiment.
The address and port of the server will also be announced separately to each participant.

#### Response

The following responses are possible to a `get_batch` request.

- **200 &lt;JSON object&gt;**

  If the request succeeds, the API returns the path from which the batch to be proven can be downloaded (`batch_file`), along with
  the identifier of the request itself (`request_id`). Participants must use the request identifier when submitting the
  corresponding proof. Here is an example response to a `get_batch` request.
  ```json
  {
    "batch_file": "static/kzW-rcrKfzsoD1uE9C-bOAu1/bh7U9Rbcz0wuh8dykQOFfVQ2",
    "request_id": 2
  }
  ```
  This response indicates that the batch data can be downloaded from
  ```
  http://<server-address>:<server-port>/static/kzW-rcrKfzsoD1uE9C-bOAu1/bh7U9Rbcz0wuh8dykQOFfVQ2
  ```
  and that submission of the proof of the batch must include `2` in the `request_id` field (see [`submit_proof`](#submit_proof)) 

- **422 participant `participant_id` does not exist**

  The participant ID specified as a parameter in the URL does not exist.

- **429 no more batches left to prove**

  The request returns this error if the server does not have any more unproven batches to serve.

### `submit_proof`

#### Request
The client invokes the `submit_proof` RPC by making an HTTP POST request to
```
http://<server-address>:<server-port>/get_batch/?participant_id=<participant-id>
```
where &lt;participant-id> is the ID assigned to the participant making the request.
The body of the request is a JSON object containing the proof and associated metadata.
We present the JSON object format using the following example submission.
```json
{
  "request_id": 2,                    // ID returned by the get_batch request for which this is the proof
  "proof_data": "jTV0NXNOwhr...etc",  // Base64-encoded proof data
  "proving_time": 7200000,            // 2 hours (in milliseconds)
  "cost": 100000,                     // 100.00 USD (in cents)
  "price": 10100,                     // 101.00 USD (in cents)
  "deployment_version": "3.1-GPU"     // Identifier of the deployment that produced the proof
}
```
The values used in the above example are purely for illustration of the response format and bear no meaning at all.
The detailed meaning of the fields is the following.
- `request_id`: The value of the `request_id` field of the JSON object returned by an invocation of `get_batch`.
  This value is required to pair the submission with the corresponding request on the server.
- `proof_data`: The binary data produced by the prover, encoded as base64 string.
- `proving_time`: The number of milliseconds it took to generate the proof. This **excludes** the time required for
  downloading the batch. However, it must **include** the time for allocating the necessary resources (if
  needed for this proof), processing the batch, performing and the actual proof generation, all the way until
  the proof is ready to be submitted.
- `cost`: The direct monetary cost of computing the proof in US Dollar **cents**. It includes all the costs that are
  incurred **per proof**, excluding constant one-time investments necessary to start the proving.
  
  The `cost` **includes** items such as
  - Rental cost for cloud machines (if cloud is used)
  - Electricity to power the prover machines
  - Cooling
  - Network communication (e.g. ISP fees)
  - Rent for the space where the machines are located
  - Maintenance of the prover hardware and software
  All these costs must be considered in proportion to what was actually used by the proving. For example, if the prover
  hardware is co-located with other machines in the same room, only a fraction of the rent for that room and air
  conditioning that corresponds to the consumption of the prover hardware must be considered.
  
  The `cost` **excludes** items such as
  - Cost of proving hardware itself
  - Engineers' compensation for setting up the proving system
    (note that this is different from the engineer continuously maintaining the proving hardware and software,
    which should flow into the proving cost)
- `price`: The minimal price for which the participant is willing to perform the proof computation, including
  the participant's profit margin. If this was an auction, the `price` would be the minimal value the participant would
  be willing to bid.
- `deployment_version`: Identifier of the deployment that produced the proof. This can be an arbitrary number or string
  that identifies a particular deployment of hardware and software that has produced the submitted proof. If the
  participant uses different deployments for proof computation (e.g. GPU-accelerated one and a CPU-only one, or
  deployments with different numbers of machines), this field should be used to distinguish them. The value of this
  field need not fully describe the deployments. It can merely serve as a reference to a description of the deployment
  stored elsewhere and communicated separately to the experiment operator.


> **Note**: In the current setup, where batches are proven one by one, the request ID is not strictly necessary, as the
> participant ID is sufficient to associate the submitted proof with the appropriate data structures. However, if we
> support making multiple requests and proving multiple batches in parallel one day, the submitting the request ID
> becomes necessary. We thus always require specifying the request ID to keep the API stable.

#### Response

The following responses are possible to a `submit_proof` request.

- **200 proof submitted successfully**
- **422 participant `participant_id` does not exist**
- **422 request `request_id` does not exist**
- **422 invalid proof**

## Client

We provide a simple client implementation that can be used almost directly with minimal modifications.
Feel free to also completely ignore the client and implement another one - the API specification should provide all the
necessary information.

The provided client fetches a batch, initiates the computation of the validity proof, and submits the proof back to the
server. To run the client, execute the following command.
```shell
python3 client.py participant-id http://<server-address>:<server-port>
```

The computation of the proof is handled by the `compute-proof-stub.sh` script. It is a stub that always outputs an
example proof of the same example batch. Both the example batch and the example proof can be downloaded respectively
from `http://<server-address>:<server-port>/static/example-batch.bin`
and `http://<server-address>:<server-port>/static/example-proof.bin`.
Note that while the script always downloads the batch based on the information received from the server,
it will always produce the same proof. Therefore, submitting the proof to the server will result in a
`422 invalid proof` response.