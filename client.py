import grpc
import proof_pb2
import proof_pb2_grpc
import numpy as np

def register_with_server():
    # Get parameters g, h, q
    # g and h generate groups G and H of prime order q
    parameters_request = proof_pb2.ParametersRequest()
    parameters_response = stub.Parameters(parameters_request)

    # Check if parameters were received
    if parameters_response.g and parameters_response.h and parameters_response.q:
        print(f"Received parameters: g={parameters_response.g}, h={parameters_response.h}, q={parameters_response.q}")

        # Choose numerical password x
        x = input("Enter numerical password x: ")
        try:
            x = int(x)
        except ValueError:
            print("Invalid input for x. Please enter a valid integer.")
            return

        # Generate y1 = g^x and y2 = h^x
        y1 = parameters_response.g ** x
        y2 = parameters_response.h ** x

        # Send y1 and y2 as registration
        registration_request = proof_pb2.RegistrationRequest(y1=y1, y2=y2)
        if registration_request:
            # Print y1 and y2 for client's reference
            print('Successful registration.')
            print(f"Y1: {y1}")
            print(f"Y2: {y2}")
            return g, h, q, x

    else:
        print("Server has not produced values for g, h and q") 

def login_to_server(g, h, q):
    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')
    stub = proof_pb2_grpc.ChaumPedersenServiceStub(channel)

    # Choose numerical password x
    x = input("Enter numerical password x: ")
    try:
        x = int(x)
    except ValueError:
        print("Invalid input for x. Please enter a valid integer.")
        return

    # Generate commitment values
    k = np.random.randint(np.iinfo(np.int32).min, np.iinfo(np.int32).max)
    r1 = g ** k
    r2 = h ** k

    # Send commitment to server
    commitment_request = proof_pb2.CommitmentChallengeRequest(r1=r1, r2=r2)
    if commitment_request:
        print('Successful commitment.')
        print(f"R1: {r1}")
        print(f"R2: {r2}")

    # Get parameter c
    # c is a random number generated by the server
    c = stub.CommitmentChallenge(commitment_request)
    print(f'c: {c}')

    # Generate zkp
    s = (k - c*x) % q

    # Send proof to server
    proof_request = proof_pb2.VerifyProofRequest(s=s)
    print('Proof sent')
    print(f's = {s}')

    if proof_request:
        print('Successful login. Proof accepted by server.')
    else:
        print('Login failed. Proof not accepted by server.')


if __name__ == '__main__':
    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')
    stub = proof_pb2_grpc.ChaumPedersenServiceStub(channel)

    # Register with the server
    g, h, q, x = register_with_server()

    # Close communication with server
    channel.close()

    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')
    stub = proof_pb2_grpc.ChaumPedersenServiceStub(channel)

    # Login to the server
    login_to_server(g, h, q)

    # Close communication with server
    channel.close()